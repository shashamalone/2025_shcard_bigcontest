import os
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults


# Tavily 검색 초기화
tavily_search = TavilySearchResults(
    max_results=5,
    include_answer=True
) if os.getenv("TAVILY_API_KEY") else None


@tool
def get_weather_info(location: str) -> dict:
    """날씨 정보 조회 도구
    
    Args:
        location: 지역명
        
    Returns:
        날씨 정보 딕셔너리
    """
    # 실제 구현 시 기상청 API 연동
    return {
        "location": location,
        "condition": "맑음",
        "temp": 15,
        "humidity": 60,
        "precipitation": 0,
        "forecast_3days": [
            {"day": "today", "condition": "맑음", "temp_high": 18, "temp_low": 10},
            {"day": "tomorrow", "condition": "흐림", "temp_high": 16, "temp_low": 9},
            {"day": "day_after", "condition": "비", "temp_high": 14, "temp_low": 8}
        ]
    }


@tool
def get_local_events(location: str) -> dict:
    """지역 이벤트 정보 조회 도구
    
    Args:
        location: 지역명
        
    Returns:
        이벤트 정보 딕셔너리
    """
    # 실제 구현 시 공공데이터 API 연동
    return {
        "location": location,
        "events": [
            {
                "name": "강남 페스티벌",
                "date": "2025-10-15",
                "type": "문화행사",
                "expected_visitors": 5000
            }
        ],
        "opportunity": True,
        "recommendation": "행사 기간 특별 메뉴 출시 권장"
    }


@tool
def search_marketing_trends(query: str) -> str:
    """마케팅 트렌드 검색 도구 (Tavily 활용)
    
    Args:
        query: 검색 쿼리
        
    Returns:
        검색 결과 문자열
    """
    if not tavily_search:
        return "Tavily API 키가 설정되지 않았습니다."
    
    try:
        results = tavily_search.invoke({"query": query})
        
        if not results:
            return "검색 결과가 없습니다."
        
        output = []
        for i, result in enumerate(results[:3], 1):
            content = result.get("content", "내용 없음")
            url = result.get("url", "")
            output.append(f"[{i}] {content[:150]}...\n출처: {url}")
        
        return "\n\n".join(output)
    
    except Exception as e:
        return f"검색 오류: {str(e)}"


web_tools = [
    get_weather_info,
    get_local_events,
    search_marketing_trends
]