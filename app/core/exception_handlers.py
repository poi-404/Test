import logging
import json

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: Exception):
    """
    捕获并处理Pydantic的请求体验证错误。

    - 记录详细的错误信息，包括请求URL、客户端IP、请求体和具体的校验失败原因。
    """
    if isinstance(exc, RequestValidationError):
        detail_errors = exc.errors()
    else:
        # 为其他可能的异常提供一个备用方案
        detail_errors = [{"msg": "Internal Server Error", "loc": [], "type": "server_error"}]

    # 尝试获取原始请求体
    try:
        raw_body = await request.json()
    except json.JSONDecodeError:
        # 如果请求体不是有效的JSON，则按原始字节读取
        raw_body = await request.body()
        if isinstance(raw_body, bytes):
            raw_body = raw_body.decode('utf-8', errors='ignore') # 尝试解码为字符串

    # 格式化详细的错误日志
    log_message = (
        f"请求校验失败 (422 Unprocessable Entity)\n"
        f"      URL: {request.url}\n"
        f"      客户端: {request.client.host}:{request.client.port}\n"
        f"      未通过的参数/请求体: {raw_body}\n"
        f"      校验错误详情: {detail_errors}"
    )

    logger.warning(log_message)  # 使用 warning 级别，因为它是一个客户端错误，但需要我们关注

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": detail_errors},
    )
