"""
RAG Tool
Pinecone Vector DB 래퍼
"""
import os
from typing import List, Dict
from loguru import logger

try:
    from pinecone import Pinecone, ServerlessSpec
    from sentence_transformers import SentenceTransformer
except ImportError:
    logger.warning("Pinecone 또는 sentence_transformers 미설치")


class RAGTool:
    """
    Pinecone 기반 RAG 도구
    """
    
    def __init__(
        self,
        api_key: str = None,
        environment: str = None,
        index_name: str = "marketing-context",
        embedding_model: str = "jhgan/ko-sroberta-multitask"
    ):
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.environment = environment or os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
        self.index_name = index_name
        
        # Embedding 모델
        logger.info(f"Embedding 모델 로드: {embedding_model}")
        self.embedder = SentenceTransformer(embedding_model)
        
        # Pinecone 초기화
        if self.api_key:
            self.pc = Pinecone(api_key=self.api_key)
            self._initialize_index()
        else:
            logger.warning("PINECONE_API_KEY 없음 - RAG 비활성화")
            self.pc = None
    
    def _initialize_index(self):
        """인덱스 초기화"""
        try:
            # 인덱스 존재 확인
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"인덱스 생성: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=768,  # ko-sroberta-multitask dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=self.environment
                    )
                )
            
            self.index = self.pc.Index(self.index_name)
            logger.info(f"인덱스 연결 성공: {self.index_name}")
            
        except Exception as e:
            logger.error(f"인덱스 초기화 실패: {e}")
            self.index = None
    
    def embed(self, text: str) -> List[float]:
        """텍스트 임베딩"""
        return self.embedder.encode(text).tolist()
    
    def upsert(self, documents: List[Dict]):
        """
        문서 업로드
        
        Args:
            documents: [{"id": "doc1", "text": "...", "metadata": {...}}, ...]
        """
        if not self.index:
            logger.warning("인덱스 없음")
            return
        
        vectors = []
        for doc in documents:
            vector = self.embed(doc["text"])
            vectors.append({
                "id": doc["id"],
                "values": vector,
                "metadata": {
                    **doc.get("metadata", {}),
                    "text": doc["text"]
                }
            })
        
        self.index.upsert(vectors=vectors)
        logger.info(f"{len(vectors)}개 문서 업로드 완료")
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter: Dict = None
    ) -> List[Dict]:
        """
        유사도 검색
        
        Args:
            query: 검색 쿼리
            top_k: 반환 개수
            filter: 메타데이터 필터
        
        Returns:
            [{"id": "...", "score": 0.95, "text": "...", "metadata": {...}}, ...]
        """
        if not self.index:
            logger.warning("인덱스 없음")
            return []
        
        query_vector = self.embed(query)
        
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            filter=filter
        )
        
        docs = []
        for match in results.matches:
            docs.append({
                "id": match.id,
                "score": match.score,
                "text": match.metadata.get("text", ""),
                "metadata": {k: v for k, v in match.metadata.items() if k != "text"}
            })
        
        logger.info(f"검색 완료: {len(docs)}개 결과")
        return docs
    
    def delete(self, ids: List[str] = None, delete_all: bool = False):
        """문서 삭제"""
        if not self.index:
            return
        
        if delete_all:
            self.index.delete(delete_all=True)
            logger.info("전체 문서 삭제")
        elif ids:
            self.index.delete(ids=ids)
            logger.info(f"{len(ids)}개 문서 삭제")


# 싱글톤 인스턴스
_rag_tool_instance = None


def get_rag_tool() -> RAGTool:
    """RAG 도구 인스턴스 반환"""
    global _rag_tool_instance
    if _rag_tool_instance is None:
        _rag_tool_instance = RAGTool()
    return _rag_tool_instance
