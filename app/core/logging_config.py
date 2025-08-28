import sys
import logging
from logging.config import dictConfig

from app.core.config import settings
from app.core.context_logger import ContextualFilter


LOG_FILE_PATH = settings.path.log_dir / "ai-audit.log"
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False, # 不禁用现有的logger

    # --- 定义日志格式 ---
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s - [%(session_id)-12s] [%(request_id)s] - %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": None,
            "defaults": {"request_id": "N/A", "session_id": "N/A"}
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(asctime)s - [%(session_id)-12s] [%(request_id)s] - %(client_addr)s - "%(request_line)s" %(status_code)s',
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": None,
            "defaults": {"request_id": "N/A", "session_id": "N/A"}
        },
    },

    # --- 定义处理器 (输出到哪里) ---
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": sys.stdout,
            "filters": ["contextual_filter"]
        },
        "rotating_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "default",
            "filename": LOG_FILE_PATH,
            "when": "D",           # 每天轮换
            "interval": 1,         # 间隔1天
            "backupCount": 14,     # 保留14份日志
            "encoding": "utf-8",
            "filters": ["contextual_filter"]

        },
        "access_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "access",
            "filename": settings.path.log_dir / "access.log",
            "when": "D",
            "interval": 1,
            "backupCount": 14,
            "encoding": "utf-8",
        },
    },
    "filters": {
        "contextual_filter": {
            "()": ContextualFilter
        }
    },
    # --- 定义 Logger (谁来记录日志) ---
    "loggers": {
        # 根 Logger: 捕获所有未被明确指定的日志
        "": {
            "handlers": ["console", "rotating_file"],
            "level": "INFO",
        },
        # Uvicorn 错误日志 (将继承根 logger 的 handlers)
        "uvicorn.error": {
            "level": "INFO",
        },
        # Gunicorn 错误日志 (将继承根 logger 的 handlers)
        "gunicorn.error": {
            "level": "INFO",
        },
        # Uvicorn 和 Gunicorn 访问日志 (使用独立的 handler 和 formatter)
        "uvicorn.access": {
            "handlers": ["console", "access_file"],
            "level": "INFO",
            "propagate": False, # 不将访问日志向上传播到根 logger
        },
        "gunicorn.access": {
            "handlers": ["console", "access_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

def configure_logging():
    """
    应用日志配置字典。
    在应用启动时调用一次即可。
    """
    dictConfig(LOGGING_CONFIG)
    logging.getLogger().info("统一日志系统配置完成。")
