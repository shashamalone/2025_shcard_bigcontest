import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain.tools import tool


# .env 파일에서 API 키 불러오기
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY","API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")  # 환경값은 콘솔에서 확인

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY 환경 변수가 설정되지 않았습니다.")
# Pinecone 초기화 (새 SDK 방식)
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "my-index")


# 임베딩 모델 (한국어 최적화)
try:
    embeddings = HuggingFaceEmbeddings(model_name="jhgan/ko-sroberta-multitask")
    
    # Pinecone 벡터스토어
    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=PINECONE_INDEX_NAME,
        embedding=embeddings
    )
    
    # Retriever 설정
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 3,  # 상위 3개 결과
        }
    )
except Exception as e:
    print(f"Pinecone 초기화 실패: {e}")
    retriever = None


# Tavily 검색 도구
tavily_search = TavilySearchResults(
    max_results=6,
    include_answer=True,
    include_raw_content=True,
    include_domains=["github.io", "wikidocs.net"],
)


@tool
def search_success_cases_rag(query: str) -> str:
    """Pinecone 벡터 DB에서 성공 사례를 검색합니다."""
    if retriever is None:
        return "Pinecone 벡터 DB가 설정되지 않았습니다."
    
    try:
        docs = retriever.get_relevant_documents(query)
        results = []
        for i, doc in enumerate(docs, 1):
            results.append(f"사례 {i}: {doc.page_content[:300]}...")
        return "\n\n".join(results) if results else "관련 사례를 찾을 수 없습니다."
    except Exception as e:
        return f"RAG 검색 오류: {str(e)}"


@tool
def search_web_for_trends(query: str) -> str:
    """Tavily를 사용하여 최신 마케팅 트렌드와 성공 사례를 웹에서 검색합니다."""
    try:
        results = tavily_search.invoke({"query": query})
        
        if not results:
            return "검색 결과가 없습니다."
        
        output = []
        for i, result in enumerate(results[:3], 1):
            content = result.get("content", "내용 없음")
            url = result.get("url", "URL 없음")
            output.append(f"결과 {i}:\n내용: {content[:200]}...\nURL: {url}")
        
        return "\n\n".join(output)
    except Exception as e:
        return f"웹 검색 오류: {str(e)}"


@tool
def analyze_market_data(business_type: str, target_audience: str) -> str:
    """비즈니스 유형과 타겟 고객을 분석하여 시장 데이터를 제공합니다."""
    analysis = f"""
    === 시장 분석 결과 ===
    
    비즈니스 유형: {business_type}
    타겟 고객: {target_audience}
    
    주요 분석:
    1. 시장 규모: 중소규모 ({business_type} 업종 기준)
    2. 경쟁 강도: 중간 수준
    3. 성장 가능성: 긍정적
    4. 추천 채널: 소셜 미디어, 로컬 SEO, 커뮤니티 마케팅
    
    타겟 고객 인사이트:
    - 주요 관심사: 가성비, 신뢰성, 편의성
    - 선호 플랫폼: 인스타그램, 네이버, 카카오톡
    - 구매 패턴: 온라인 리서치 후 오프라인 구매 또는 온라인 직접 구매
    """
    return analysis


# 모든 도구를 리스트로 제공
analyst_tools = [
    search_success_cases_rag,
    search_web_for_trends,
    analyze_market_data,
]
