import logging

import torch
import sentence_transformers

from app.core.config import settings

logger = logging.getLogger(__name__)
EMBEDDING_MODEL = settings.path.model_embedding  # 嵌入模型名称


class EmbeddingModel:
    """
    封装 sentence_transformers 的嵌入模型。
    """
    def __init__(self):
        device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        logger.info(f"正在加载嵌入模型 {EMBEDDING_MODEL} 到设备 {device}...")
        self.client = sentence_transformers.SentenceTransformer(
            EMBEDDING_MODEL, device=device
        )
        logger.info("嵌入模型加载完成。")

    def embed_document(self, texts: list[str]) -> list[list[float]]:
        """
        生成文档文本的嵌入向量。
        """
        try:
            embeddings = self.client.encode(texts).tolist()
            return embeddings
        except Exception as e:
            logger.error(f"生成嵌入向量时发生错误: {e}", exc_info=True)
            return []

    def embed_query(self, text: str) -> list[float]:
        """
        生成单个查询文本的嵌入向量。
        """
        try:
            embedding = self.client.encode(text).tolist()
            return embedding
        except Exception as e:
            logger.error(f"生成查询嵌入向量时发生错误: {e}", exc_info=True)
            return []
