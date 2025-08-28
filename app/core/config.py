from pathlib import Path
import logging
from typing import Literal, get_args

from pydantic import model_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# from app.utils.crypto_sm4 import decrypt




# class MilvusSettings(BaseSettings):
#     user: str = Field(..., description="Milvus用名")
#     pwd: str = Field(..., description="Milvus密钥")
#     port: str = Field(..., description="Milvus端口号")
#     host: str = Field(..., description="Milvus主机地址")
#     db_name: str = Field(..., description="Milvus数据库")
#     collection: str = Field(..., description="Milvus集合")
#     collection_summary: str = Field(..., description="Milvus总结集合")
#     collection_tasks: str = Field(..., description="Milvus任务下达集合")
#     collection_matters: str = Field(..., description="Milvus审计事项集合")
#     limit: int = Field(10, description="Milvus检索限制")
#
#
# class MysqlSettings(BaseSettings):
#     host: str = Field(..., description="MySQL主机地址")
#     port: str = Field(..., description="MySQL端口号")
#     user: str = Field(..., description="MySQL用户名")
#     passwd: str = Field(..., description="MySQL密钥")
#     database: str = Field(..., description="MySQL数据库")
#     charset: str = Field("utf8mb4", description="MySQL字符集")
#     ssl_disable: bool = Field(True, description="MySQL是否禁用SSL")
#
#
# class UrlSettings(BaseSettings):
#     get_attachment: str = Field(..., description="对话附件下载")
#     get_technology_task_file: str = Field(..., description="科技项目文档下载")
#     update_knowledgebase_file_state: str = Field(..., description="知识库文件状态回调")
#     update_task_assignment_file_state: str = Field(..., description="任务下达文件状态回调")
#     update_model_dataset_state: str = Field(..., description="模型数据集更新状态回调")
#     post_created_graph: str = Field(..., description="上传生成的图表")
#
#
# class VectorModelServiceSettings(BaseSettings):
#     enable: bool = Field(False, description="是否连接到已部署的向量化服务")
#     url: str = Field(..., description="服务地址")
#     sleep_time: float = Field(0.2, description="调用太频繁会导致服务异常")


class LLMSettings(BaseSettings):
    instruct_url: str = Field(..., description="指令模型URL")
    thinking_url: str = Field(..., description="思考模型URL")
    instruct_model: str = Field(..., description="指令模型")
    thinking_model: str = Field(..., description="思考模型")
    instruct_tokenizer_dir: str = Field(..., description="指令模型Tokenizer目录")
    thinking_tokenizer_dir: str = Field(..., description="思考模型Tokenizer目录")
    max_input_tokens: int = Field(7600, description="最大输入token数")
    default_top_p: float = Field(0.75, description="默认top_p")
    context_tokens: int = Field(8000, description="上下文token数")
    context_tokens_long: int = Field(8000, description="上下文token数(长)")

    qwen3_model: str = Field(..., description="Qwen3模型")
    qwen3_url: str = Field(..., description="Qwen3模型URL")
    qwen3_key: str = Field(..., description="Qwen3模型Key")


# class PathSettings(BaseSettings):
#     # in
#     hot_stop_word_dict: str = Field(..., description="热门知识 - 停用词词典")
#     hot_user_dict: str = Field(..., description="热门知识 - 用户自定义分词词典")
#     # out
#     log_dir: Path = Field(Path("logs/"), description="日志目录")
#     # temp
#     audit_assignment_dir: Path = Field(..., json_schema_extra={"path_rule": "create_dir"}, description="审计任务目录")
#     docx_img_temp_dir: Path = Field(..., json_schema_extra={"path_rule": "create_dir"}, description="docx图片临时目录")
#     docx_table_temp: Path = Field(..., json_schema_extra={"path_rule": "create_file"}, description="docx表格临时文件")
#     docx_structure_temp: Path = Field(..., json_schema_extra={"path_rule": "create_file"}, description="docx结构临时文件")
#     upload_file_temp_dir: Path = Field(..., json_schema_extra={"path_rule": "create_dir"}, description="上传文件临时存储目录")
#     pdf2img_dir: Path = Field(..., json_schema_extra={"path_rule": "create_dir"}, description="PDF转图片目录")
#     # localdb
#     dialogs_dir: str = Field(..., description="对话记录文件存储目录")
#     session_files_map: str = Field(..., description="会话临时文件映射")
#     mat_required: str = Field(..., description="任务所需材料对照表")
#     all_mission_info: str = Field(..., description="所有初始化工作台任务的信息")
#     all_model_info: str = Field(..., description="所有初始化工作台模型的信息")
#     hot_knowledge_map: str = Field(..., description="热门知识 - 映射表")
#     # ref
#     libreoffice: Path = Field(..., json_schema_extra={"path_rule": "must_exist_dir"})
#     model_paddleocr_rec: Path
#     model_paddleocr_det: Path
#     model_paddleocr_cls: Path
#     model_embedding: Path
#     model_reranker: Path
#     model_tokenizer: Path
#
#
# class ConstantSettings(BaseSettings):
#     history_count_max: int = Field(2, description="历史记录条数")
#     history_time_max: int = Field(86400, description="历史记录限时 24 * 60 * 60")
#     recent_dial_max: int = Field(10, description="最近对话条数")
#     task_assignment_namespace: str = Field(..., description="任务下达命名空间")
#     hot_knowledge_loop_hours: int = Field(168, description="热门知识更新周期，单位小时")
#     summary_leaf_chunk_size: int = Field(5000, description="待摘要文本长度")
#     summary_size: int = Field(200, description="生成摘要长度")
#     environment: EnvironmentEnum = Field(..., description="环境")


class AppSettings(BaseSettings):
    """
    应用配置模型。
    按以下优先级加载配置：
    1. 环境变量
    2. 此处指定 .env 文件中定义的值
    3. 此处代码中定义的默认值
    """
    model_config = SettingsConfigDict(
        env_prefix="APP_",  # 为所有环境变量设置一个统一的前缀
        env_nested_delimiter="__",  # 使用双下划线作为嵌套分隔符
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # 嵌套配置
    # milvus: MilvusSettings
    # mysql: MysqlSettings
    llm: LLMSettings
    # url: UrlSettings
    # path: PathSettings
    # constant: ConstantSettings
    # vector_model_service: VectorModelServiceSettings

    # sm4_cbc: str = ""
    # sm4_offset: str = ""


settings = AppSettings()
