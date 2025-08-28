from pydantic import BaseModel, Field
from typing import Literal, Optional


class ChatMessage(BaseModel):
    """标准的聊天消息格式"""
    role: Literal["system", "user", "assistant"]
    content: str

class LLMResponse(BaseModel):
    """标准的LLM响应模型，包含思考和回答"""
    think: Optional[str] = None
    answer: str

class StreamChunk(BaseModel):
    """标准化的流式响应块"""
    content: str
    is_thinking: bool = False
    is_final: bool = False

class AuditStreamChunk(BaseModel):
    """为审计项目前端定制的流式响应块"""
    stream_message_id: int = Field(..., alias="streamMessageId")
    stream_message: str = Field(..., alias="streamMessage")
    is_think: Literal["0", "1"] = Field(..., alias="isThink")
    end_stream: bool = Field(False, alias="endStream")