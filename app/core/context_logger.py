import uuid
import logging
from contextvars import ContextVar
from typing import Optional

# 定义全局上下文变量。在不同的异步任务（如不同的API请求）中拥有不同的值。
REQUEST_ID_VAR: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
SESSION_ID_VAR: ContextVar[Optional[str]] = ContextVar("session_id", default=None)

class ContextualFilter(logging.Filter):
    """
    日志过滤器，将上下文变量中的ID注入到日志记录中。
    """
    def filter(self, record: logging.LogRecord) -> bool:
        # 从上下文变量中获取ID，并将其作为新的属性附加到record对象上
        record.request_id = REQUEST_ID_VAR.get()
        record.session_id = SESSION_ID_VAR.get()
        return True


class CtxLogger:
    """一个上下文管理器，用于在特定代码块内设置日志上下文。"""
    def __init__(self, session_id: Optional[str] = None, request_id: Optional[str] = None):
        if request_id is None:
            # 如果没有提供request_id，自动生成一个
            request_id = str(uuid.uuid4())

        self.session_id = session_id
        self.request_id = request_id
        self._session_token = None
        self._request_token = None

    def __enter__(self):
        # 进入上下文时，设置上下文变量并保存token
        self._session_token = SESSION_ID_VAR.set(self.session_id)
        self._request_token = REQUEST_ID_VAR.set(self.request_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 退出上下文时，重置上下文变量到之前的值
        if self._session_token:
            SESSION_ID_VAR.reset(self._session_token)
        if self._request_token:
            REQUEST_ID_VAR.reset(self._request_token)
