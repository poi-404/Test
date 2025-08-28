"""
研发网大模型客户端

"""
import json
import logging
import httpx
from typing import Any, Optional

from app.core.config import settings
from app.services.llmapi.base import BaseLLMClient
from app.schemas.llmapi.base import ChatMessage, LLMResponse, StreamChunk

logger = logging.getLogger(__name__)


class DevnetLLMClient(BaseLLMClient):
    """
    研发网大模型客户端
    """

    def _get_model_info(self, model_name: str) -> tuple[str, str]:
        if model_name == "deepseek":
            return settings.llm.thinking_model, settings.llm.thinking_url
        else:
            return settings.llm.instruct_model, settings.llm.instruct_url

    def _prepare_request(
        self,
        messages: list[ChatMessage],
        model_name: str,
        stream: bool,
        **kwargs: Any
    ) -> httpx.Request:
        """
        实现基类方法。准备请求体。

        Args:
            messages (list[ChatMessage]): 对话消息列表
            model_name (str): 模型名称
            stream (bool): 是否启用流式响应
            **kwargs: 其他参数，如top_p、max_tokens等

        Returns:
            httpx.Request: 准备好的请求对象
        """
        model, url = self._get_model_info(model_name)
        payload = {
            "model": model,
            "messages": [msg.model_dump() for msg in messages],
            "stream": stream,
            "top_p": kwargs.get("top_p", settings.llm.default_top_p)
        }
        # 要求输出的最大tokens
        # 设定值与实际输入tokens相加不能超过模型context tokens，否则接口会报错
        if kwargs.get("max_tokens"):
            payload["max_tokens"] = kwargs.get("max_tokens")

        return httpx.Request("POST", url, json=payload, headers={"Content-Type": "application/json"})

    async def _parse_response(self, response: httpx.Response) -> LLMResponse:
        """
        实现基类方法。解析非流式响应。

        Args:
            response (httpx.Response): 非流式响应对象

        Returns:
            LLMResponse: 解析后的响应对象
        """
        # 前提是接口的响应体能直接解析为JSON
        # 如果含有影响解析的字符，需要提前处理
        try:
            data = response.json()
            full_text = data["choices"][0]["message"]["content"]
            think, answer = self._extract_think_answer(full_text)
            return LLMResponse(think=think, answer=answer)
        except (KeyError, IndexError) as e:
            logger.error(f"解析研发网非流式响应失败: {data}", exc_info=True)
            raise ValueError("解析研发网非流式响应失败") from e

    async def _parse_stream_chunk(self, line: str) -> Optional[StreamChunk]:
        """
        实现基类方法。解析流式响应块。

        Args:
            line (str): 流式响应的一行数据，格式为 "data: {json字符串}"

        Returns:
            Optional[StreamChunk]: 解析后的流式块对象，如果解析失败则返回None
        """
        try:
            data_str = line[6:]
            if data_str.strip() == "[DONE]":
                return StreamChunk(content="", is_final=True)

            data = json.loads(data_str)
            delta = data["choices"][0]["delta"]
            content = delta.get("content", "")

            is_final = data["choices"][0].get("finish_reason") is not None

            return StreamChunk(content=content, is_final=is_final)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"解析Devnet流式块失败: {line}", exc_info=True)
            return None