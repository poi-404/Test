from enum import Enum

class LLMProviderEnum(str, Enum):
    """定义所有可用的LLM服务提供商"""
    DEVNET = "devnet"
    AI_PLATFORM = "ai_platform"
    EPRI = "epri"

class LLMUseCaseEnum(str, Enum):
    """定义LLM的应用场景"""
    GENERAL = "general_purpose"  # 通用任务
    LONG_TEXT = "long_text"      # 长文本任务