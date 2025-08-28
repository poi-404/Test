import json
import logging
import httpx
from typing import Any, Optional

from app.core.config import settings
from app.services.llmapi.base import BaseLLMClient
from app.schemas.llmapi.base import ChatMessage, LLMResponse, StreamChunk

logger = logging.getLogger(__name__)

class Qwen3LLMClient(BaseLLMClient):
    """信通人工智能平台大模型客户端"""

    # ----------------- 修改 --------------------
    def _add_thinking_flag(self, model_name: str, messages: list[ChatMessage]) -> list[ChatMessage]:
        if model_name != "deepseek" and messages:
            messages[-1].content += " /no_think"
        return messages
        # return settings.LLM_THINKING_MODEL if model_name == "deepseek" else settings.LLM_INSTRUCT_MODEL
    # ----------------- 修改 --------------------

    def _prepare_request(
        self,
        messages: list[ChatMessage],
        model_name: str,
        stream: bool,
        **kwargs: Any
    ) -> httpx.Request:
        messages = self._add_thinking_flag(model_name, messages)
        
        payload = {
            "model": settings.llm.qwen3_model,   # 修改
            "messages": [msg.model_dump() for msg in messages],
            "stream": stream,
            "enable_thinking": False
        }
        # 添加额外参数
        if "temperature" in kwargs:
            payload["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            payload["max_tokens"] = kwargs["max_tokens"]
        if "presence_penalty" in kwargs:
            payload["presence_penalty"] = kwargs["presence_penalty"]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.llm.qwen3_key}",
        }

        return httpx.Request("POST", settings.llm.qwen3_url, json=payload, headers=headers)

    # ----------------- 修改 --------------------+9+96
    async def _parse_response(self, response: httpx.Response) -> LLMResponse:
        data = response.json()
        try:
            # 注意路径变化： 'choice' -> 'choices' in new standard
            answer = data["choices"][0]["message"]["content"]
            think = data["choices"][0]["message"]["reasoning_content"]
            return LLMResponse(think=think, answer=answer)
        except (KeyError, IndexError) as e:
            logger.error(f"解析AI平台非流式响应失败: {data}", exc_info=True)
            raise ValueError("Invalid response structure from AI Platform LLM") from e

    # ----------------- 修改 --------------------
    async def _parse_stream_chunk(self, line: str) -> Optional[StreamChunk]:
        try:
            data_str = line[5:].strip() # "data:" or "data: "
            # print(data_str)
            if not data_str or data_str == "[DONE]":
                return None
                
            data = json.loads(data_str)
            choice = data["choices"][0]
            content = choice["delta"].get("content") or ""
            think_content = choice["delta"].get("reasoning_content", "")
            is_final = choice.get("finish_reason") is not None

            # 将思考内容也作为普通内容返回，但标记为is_thinking
            if think_content:
                return StreamChunk(content=think_content, is_thinking=True, is_final=is_final)
            else:
                return StreamChunk(content=content, is_final=is_final)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"解析AI平台流式块失败: {line}", exc_info=True)
            return None
