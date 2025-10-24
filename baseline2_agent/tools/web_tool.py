"""
Web Search Tool
Tavily API 래퍼
"""
import os
from typing import List, Dict
from loguru import logger

try:
    from tavily import TavilyClient
except ImportError:
    logger.warning("tavily-python 미설치")
    TavilyClient = None


class WebSearchTool:
    """
    Tavily 기반 웹 검색 도구
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        
        if self.api_key and TavilyClient:
            self.client = TavilyClient(api_key=self.api_key)
            logger.info("Tavily 클라이언트 초기화 완료")
        else:
            logger.warning("TAVILY_API_KEY 없음 또는 라이브러리 미설치")
            self.client = None
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        include_domains: List[str] = None,
        exclude_domains: List[str] = None
    ) -> List[Dict]:
        """
        웹 검색
        
        Args:
            query: 검색 쿼리
            max_results: 최대 결과 수
            search_depth: "basic" | "advanced"
            include_domains: 포함할 도메인
            exclude_domains: 제외할 도메인
        
        Returns:
            [{"title": "...", "url": "...", "content": "...", "score": 0.95}, ...]
        """
        if not self.client:
            logger.warning("Tavily 클라이언트 없음")
            return []
        
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_domains=include_domains,
                exclude_domains=exclude_domains
            )
            
            results = []
            for result in response.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0.0)
                })
            
            logger.info(f"검색 완료: {query} → {len(results)}개 결과")
            return results
            
        except Exception as e:
            logger.error(f"검색 실패: {e}")
            return []
    
    def search_events(
        self,
        location: str,
        date_range: str = None,
        max_results: int = 3
    ) -> List[Dict]:
        """
        행사 정보 검색
        
        Args:
            location: 지역명 (예: "성수동", "서울")
            date_range: 날짜 범위 (예: "이번 주", "11월")
            max_results: 최대 결과 수
        
        Returns:
            행사 정보 리스트
        """
        query = f"{location} 행사 이벤트 축제"
        if date_range:
            query += f" {date_range}"
        
        results = self.search(
            query=query,
            max_results=max_results,
            search_depth="basic"
        )
        
        # 행사 정보 파싱 (실제로는 더 정교한 파싱 필요)
        events = []
        for r in results:
            events.append({
                "title": r["title"],
                "location": location,
                "url": r["url"],
                "description": r["content"][:200],
                "source": "web"
            })
        
        return events


class WeatherTool:
    """
    날씨 정보 도구 (예시)
    실제로는 기상청 API 연동
    """
    
    def __init__(self):
        logger.info("WeatherTool 초기화")
    
    def get_forecast(
        self,
        location: str,
        days: int = 7
    ) -> Dict:
        """
        날씨 예보 조회
        
        Args:
            location: 지역명
            days: 예보 일수
        
        Returns:
            날씨 예보 데이터
        """
        # 더미 데이터 (실제로는 API 호출)
        logger.info(f"날씨 조회: {location}, {days}일")
        
        return {
            "location": location,
            "forecast": [
                {
                    "date": "2025-11-10",
                    "temp_max": 15,
                    "temp_min": 8,
                    "pop": 0.7,
                    "rain_mm": 18.0,
                    "description": "흐리고 비"
                }
            ]
        }


# 싱글톤 인스턴스
_web_tool_instance = None
_weather_tool_instance = None


def get_web_tool() -> WebSearchTool:
    """웹 검색 도구 인스턴스"""
    global _web_tool_instance
    if _web_tool_instance is None:
        _web_tool_instance = WebSearchTool()
    return _web_tool_instance


def get_weather_tool() -> WeatherTool:
    """날씨 도구 인스턴스"""
    global _weather_tool_instance
    if _weather_tool_instance is None:
        _weather_tool_instance = WeatherTool()
    return _weather_tool_instance
