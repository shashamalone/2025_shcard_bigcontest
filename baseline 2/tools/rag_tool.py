import os
from langchain.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone


# Pinecone 초기화
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "marketing-kb")

embeddings = None
vectorstore = None
retriever = None

if PINECONE_API_KEY:
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        embeddings = HuggingFaceEmbeddings(
            model_name="jhgan/ko-sroberta-multitask"
        )
        
        vectorstore = PineconeVectorStore.from_existing_index(
            index_name=PINECONE_INDEX_NAME,
            embedding=embeddings
        )
        
        retriever = vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )
    except Exception as e:
        print(f"Pinecone 초기화 실패: {e}")


@tool
def search_success_cases(query: str) -> str:
    """마케팅 성공 사례 검색 (RAG)
    
    Args:
        query: 검색 쿼리
        
    Returns:
        검색된 사례 문자열
    """
    if not retriever:
        return "Pinecone Vector DB가 설정되지 않았습니다."
    
    try:
        docs = retriever.get_relevant_documents(query)
        
        if not docs:
            return "관련 사례를 찾을 수 없습니다."
        
        results = []
        for i, doc in enumerate(docs[:3], 1):
            content = doc.page_content[:200]
            metadata = doc.metadata
            results.append(f"사례 {i}:\n{content}...\n출처: {metadata.get('source', 'unknown')}")
        
        return "\n\n".join(results)
    
    except Exception as e:
        return f"RAG 검색 오류: {str(e)}"


@tool
def search_marketing_tools(query: str) -> str:
    """마케팅 도구 및 리소스 검색 (RAG)
    
    Args:
        query: 검색 쿼리
        
    Returns:
        검색된 도구 정보 문자열
    """
    if not retriever:
        return "Pinecone Vector DB가 설정되지 않았습니다."
    
    try:
        docs = retriever.get_relevant_documents(query)
        
        if not docs:
            return "관련 도구를 찾을 수 없습니다."
        
        results = []
        for i, doc in enumerate(docs[:3], 1):
            content = doc.page_content[:150]
            results.append(f"도구 {i}: {content}...")
        
        return "\n\n".join(results)
    
    except Exception as e:
        return f"도구 검색 오류: {str(e)}"


@tool
def search_constraints_examples(constraint_type: str) -> str:
    """제약조건별 마케팅 사례 검색
    
    Args:
        constraint_type: 제약 유형 (예: low_budget, no_experience)
        
    Returns:
        제약조건 관련 사례 문자열
    """
    if not retriever:
        return "Pinecone Vector DB가 설정되지 않았습니다."
    
    query_map = {
        "low_budget": "저예산 마케팅 성공 사례",
        "no_experience": "초보자도 가능한 마케팅",
        "time_limited": "짧은 시간 고효율 마케팅"
    }
    
    query = query_map.get(constraint_type, constraint_type)
    
    try:
        docs = retriever.get_relevant_documents(query)
        
        if not docs:
            return f"{constraint_type} 관련 사례를 찾을 수 없습니다."
        
        results = []
        for i, doc in enumerate(docs[:2], 1):
            results.append(f"예시 {i}:\n{doc.page_content[:200]}...")
        
        return "\n\n".join(results)
    
    except Exception as e:
        return f"사례 검색 오류: {str(e)}"


rag_tools = [
    search_success_cases,
    search_marketing_tools,
    search_constraints_examples
]