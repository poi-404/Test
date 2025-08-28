import abc
import json
import logging
import uuid
from typing import Any, AsyncGenerator

import httpx

from app.schemas.llmapi.base import ChatMessage, LLMResponse, StreamChunk
from app.core.context_logger import REQUEST_ID_VAR

logger = logging.getLogger(__name__)


class BaseLLMClient(abc.ABC):
    """
    所有LLM客户端的抽象基类。
    定义了统一的接口和基于httpx的异步网络I/O。
    """
    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    @abc.abstractmethod
    def _prepare_request(
        self,
        messages: list[ChatMessage],
        model_name: str,
        stream: bool,
        **kwargs: Any
    ) -> httpx.Request:
        """
        [子类必须实现] 准备httpx请求对象。
        此方法负责构建特定于每个API的URL, headers, params, json payload等。
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def _parse_response(self, response: httpx.Response) -> LLMResponse:
        """
        [子类必须实现] 解析非流式响应。
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def _parse_stream_chunk(self, line: str) -> StreamChunk | None:
        """
        [子类必须实现] 解析单行流式响应。
        """
        raise NotImplementedError

    def _extract_think_answer(self, text: str) -> tuple[str, str]:
        """
        [通用逻辑] 如果响应将think内置在answer中，从完整文本中提取思考和回答部分。
        """
        think = ""
        answer = text
        if "</think>" in text:  # 未匹配到标记则不作修改
            parts = text.split("</think>", 1)
            think = parts[0].replace("<think>", "").strip()
            answer = parts[1].strip()
        return think, answer

    async def _get_response(self, request: httpx.Request) -> LLMResponse:
        """
        [通用逻辑] 发送非流式请求并获取解析后的响应。
        """
        try:
            response = await self._client.send(request)
            response.raise_for_status()  # 如果状态码不是2xx，则抛出异常
            return await self._parse_response(response)
        except httpx.HTTPStatusError as e:
            logger.error(
                f"LLM API请求失败，状态码: {e.response.status_code}, "
                f"响应: {e.response.text}"
            )
            raise  # 重新抛出异常，让上层处理
        except Exception as e:
            logger.error(f"调用LLM时发生未知错误: {e}", exc_info=True)
            raise

    async def _get_stream_response(self, request: httpx.Request) -> AsyncGenerator[StreamChunk, None]:
        """
        [通用逻辑] 发送流式请求并逐块返回解析后的响应。
        """
        request_content_str = request.content.decode("utf-8")
        request_content_json = json.loads(request_content_str)
        try:
            async with self._client.stream(request.method, request.url, headers=request.headers, json=request_content_json, timeout=120) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line and line.startswith("data:"):
                        chunk = await self._parse_stream_chunk(line)
                        if chunk:
                            yield chunk

        except httpx.HTTPStatusError as e:
            logger.error(f"LLM流式API请求失败，状态码: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"处理LLM流式响应时发生错误: {e}", exc_info=True)
            raise

    async def chat(
        self,
        prompt: str,
        history: list[ChatMessage] = None,
        model_name: str = "default",
        stream: bool = False,
        **kwargs: Any
    ) -> LLMResponse | AsyncGenerator[StreamChunk, None]:
        """
        统一的调用入口。
        """
        request_id = str(uuid.uuid4())
        request_id_token = REQUEST_ID_VAR.set(request_id)
        logger.info(f"开始处理LLM请求。")
        try:
            # 构建消息列表
            messages = history or []
            messages.append(ChatMessage(role="user", content=prompt))
            # 准备请求参数
            request = self._prepare_request(messages, model_name, stream, **kwargs)
            if stream:
                return self._get_stream_response(request)
            else:
                response = await self._get_response(request)

                logger.info("成功完成LLM非流式请求。")
                return response

        except Exception as e:
            logger.error(f"LLM请求处理失败: {e}", exc_info=True)
            # 重新抛出异常，让上层处理HTTP响应
            raise
        finally:
            # 无论成功还是失败，都要在最后清理request_id上下文
            REQUEST_ID_VAR.reset(request_id_token)
