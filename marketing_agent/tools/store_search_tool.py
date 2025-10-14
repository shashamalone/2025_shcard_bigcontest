"""
Store Search Tool
FastMCP 기반 가맹점 검색 및 중복 해소
"""
from langchain.tools import tool
from typing import List, Dict, Any
from loguru import logger


# FastMCP 클라이언트 연결
# 실제 환경에서는 FastMCP 설정 파일 로드
try:
    from mcp import FastMCP
    # mcp_client = FastMCP.connect(config_path="mcp_config.json")
    MCP_AVAILABLE = False  # TODO: 실제 MCP 연결 시 True로 변경
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("FastMCP not available, using mock data")


def search_stores_from_mcp(query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """FastMCP를 통한 가맹점 검색

    Args:
        query: 검색 쿼리 (자연어 또는 구조화된 질의)
        filters: 추가 필터 (업종, 지역 등)

    Returns:
        가맹점 리스트
    """
    if MCP_AVAILABLE:
        # 실제 FastMCP 호출
        # results = mcp_client.call_tool(
        #     tool_name="search_stores",
        #     arguments={"query": query, "filters": filters}
        # )
        # return results
        pass
    else:
        # Mock 데이터
        mock_data = [
            {
                "가맹점구분번호": "STORE_001_01",
                "상호명": "카페베네 강남점",
                "주소": "서울 강남구 테헤란로 123",
                "업종": "카페",
                "월평균매출": 15000000,
                "재방문율": 28,
                "신규고객비율": 42,
                "경쟁강도": 0.78
            },
            {
                "가맹점구분번호": "STORE_001_02",
                "상호명": "카페베네 역삼점",
                "주소": "서울 강남구 역삼동 456",
                "업종": "카페",
                "월평균매출": 12000000,
                "재방문율": 32,
                "신규고객비율": 38,
                "경쟁강도": 0.65
            },
            {
                "가맹점구분번호": "STORE_002_01",
                "상호명": "카페베네 신사점",
                "주소": "서울 강남구 신사동 789",
                "업종": "카페",
                "월평균매출": 18000000,
                "재방문율": 35,
                "신규고객비율": 40,
                "경쟁강도": 0.82
            },
            {
                "가맹점구분번호": "STORE_003_01",
                "상호명": "스타벅스 강남점",
                "주소": "서울 강남구 강남대로 111",
                "업종": "카페",
                "월평균매출": 25000000,
                "재방문율": 45,
                "신규고객비율": 35,
                "경쟁강도": 0.95
            }
        ]
        return mock_data


@tool
def mcp_search_stores(query: str, top_k: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """FastMCP를 통한 가맹점 검색

    FastMCP 서버의 검색 기능을 직접 활용합니다.
    MCP 서버는 자체적으로 semantic search, fuzzy matching 등을 수행합니다.

    Args:
        query: 자연어 검색 쿼리 (예: "강남 카페", "역삼동 음식점")
        top_k: 반환할 최대 결과 수
        filters: 추가 필터 조건 (업종, 지역 등)

    Returns:
        검색 결과 가맹점 리스트

    Example:
        >>> mcp_search_stores("강남 카페", top_k=3)
        [
            {
                "가맹점구분번호": "STORE_001_01",
                "상호명": "카페베네 강남점",
                ...
            }
        ]
    """
    logger.info(f"MCP Store search: query='{query}', top_k={top_k}, filters={filters}")

    results = search_stores_from_mcp(query, filters)

    # Top-K 제한
    results = results[:top_k]

    logger.info(f"Found {len(results)} stores via MCP")
    return results


@tool
def mcp_get_store_detail(store_id: str) -> Dict[str, Any]:
    """FastMCP를 통한 가맹점 상세 조회

    Args:
        store_id: 가맹점구분번호

    Returns:
        가맹점 상세 정보

    Example:
        >>> mcp_get_store_detail("STORE_001_01")
        {
            "가맹점구분번호": "STORE_001_01",
            "상호명": "카페베네 강남점",
            ...
        }
    """
    logger.info(f"MCP Store detail lookup: {store_id}")

    if MCP_AVAILABLE:
        # 실제 FastMCP 호출
        # result = mcp_client.call_tool(
        #     tool_name="get_store_by_id",
        #     arguments={"store_id": store_id}
        # )
        # return result
        pass
    else:
        # Mock 구현
        all_stores = search_stores_from_mcp("")
        for store in all_stores:
            if store["가맹점구분번호"] == store_id:
                logger.info(f"Store found: {store['상호명']}")
                return store

        logger.warning(f"Store not found: {store_id}")
        return {"error": f"가맹점을 찾을 수 없습니다: {store_id}"}


@tool
def mcp_deduplicate_stores(store_ids: List[str]) -> List[str]:
    """FastMCP를 통한 가맹점 중복 해소

    FastMCP 서버가 제공하는 중복 탐지 및 해소 기능을 활용합니다.
    MCP 서버는 자체 로직으로 동일 가맹점을 판별합니다.

    Args:
        store_ids: 가맹점구분번호 리스트

    Returns:
        중복 제거된 가맹점구분번호 리스트

    Example:
        >>> mcp_deduplicate_stores(["STORE_001_01", "STORE_001_02", "STORE_001_01"])
        ["STORE_001_01", "STORE_001_02"]
    """
    logger.info(f"MCP Deduplication: {len(store_ids)} stores")

    if MCP_AVAILABLE:
        # 실제 FastMCP 호출
        # result = mcp_client.call_tool(
        #     tool_name="deduplicate_stores",
        #     arguments={"store_ids": store_ids}
        # )
        # return result
        pass
    else:
        # Mock 구현: 단순 중복 제거
        unique_ids = list(dict.fromkeys(store_ids))
        logger.info(f"Deduplication result: {len(store_ids)} → {len(unique_ids)}")
        return unique_ids


# LangChain tools 리스트
store_search_tools = [
    mcp_search_stores,
    mcp_get_store_detail,
    mcp_deduplicate_stores
]
