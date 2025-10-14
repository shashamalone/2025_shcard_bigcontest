"""
Store Resolver Agent
FastMCP 기반 가맹점 검색 및 중복 해소
최상위 노드로 동작하여 사용자 쿼리에서 가맹점을 추출하고 정규화합니다.
"""
from datetime import datetime
from loguru import logger
from typing import List, Dict, Any

from tools.store_search_tool import (
    mcp_search_stores,
    mcp_get_store_detail,
    mcp_deduplicate_stores
)


def store_resolver_node(state):
    """
    Store Resolver Agent

    역할:
    1. 사용자 쿼리에서 가맹점 관련 키워드 추출
    2. FastMCP를 통한 가맹점 검색
    3. 중복 가맹점 해소
    4. 정규화된 가맹점 정보를 state에 저장

    Args:
        state: AgentState

    Returns:
        업데이트된 state (resolved_stores, store_ids 추가)
    """
    logger.info("Store Resolver Agent: 시작")

    user_query = state.get("user_query", "")
    logs = [f"[{datetime.now()}] store_resolver: 가맹점 검색 시작"]

    # 1. 쿼리에서 가맹점 검색어 추출 (간단한 구현)
    # 실제로는 LLM으로 Named Entity Recognition
    search_query = _extract_store_query(user_query)
    logger.info(f"Extracted store query: {search_query}")
    logs.append(f"[{datetime.now()}] 검색어 추출: '{search_query}'")

    # 2. FastMCP 검색
    if search_query:
        try:
            search_results = mcp_search_stores.invoke({
                "query": search_query,
                "top_k": 10
            })
            logger.info(f"MCP search returned {len(search_results)} results")
            logs.append(f"[{datetime.now()}] MCP 검색 완료: {len(search_results)}개 발견")
        except Exception as e:
            logger.error(f"MCP search failed: {e}")
            search_results = []
            logs.append(f"[{datetime.now()}] [ERROR] MCP 검색 실패: {e}")
    else:
        search_results = []
        logs.append(f"[{datetime.now()}] 검색어 없음, 검색 건너뜀")

    # 3. 중복 해소
    if search_results:
        store_ids = [s["가맹점구분번호"] for s in search_results]

        try:
            unique_store_ids = mcp_deduplicate_stores.invoke({
                "store_ids": store_ids
            })
            logger.info(f"Deduplication: {len(store_ids)} → {len(unique_store_ids)}")
            logs.append(f"[{datetime.now()}] 중복 제거: {len(store_ids)} → {len(unique_store_ids)}")
        except Exception as e:
            logger.error(f"Deduplication failed: {e}")
            unique_store_ids = store_ids
            logs.append(f"[{datetime.now()}] [WARNING] 중복 제거 실패, 원본 사용")

        # 4. 최종 가맹점 리스트 구성
        resolved_stores = []
        for store_id in unique_store_ids:
            # 기존 search_results에서 찾기
            store_info = next((s for s in search_results if s["가맹점구분번호"] == store_id), None)
            if store_info:
                resolved_stores.append(store_info)

        logger.info(f"Resolved {len(resolved_stores)} stores")
        logs.append(f"[{datetime.now()}] 최종 가맹점: {len(resolved_stores)}개")

        # 5. 대표 가맹점 선택 (첫 번째 항목)
        primary_store_id = unique_store_ids[0] if unique_store_ids else None

        return {
            "resolved_stores": resolved_stores,
            "store_ids": unique_store_ids,
            "primary_store_id": primary_store_id,
            "store_search_query": search_query,
            "logs": logs
        }
    else:
        # 가맹점 없음
        logger.warning("No stores found")
        logs.append(f"[{datetime.now()}] [WARNING] 가맹점을 찾을 수 없음")

        return {
            "resolved_stores": [],
            "store_ids": [],
            "primary_store_id": None,
            "store_search_query": search_query,
            "logs": logs
        }


def _extract_store_query(user_query: str) -> str:
    """
    사용자 쿼리에서 가맹점 검색 키워드 추출

    간단한 규칙 기반 구현.
    실제로는 LLM 기반 NER 또는 프롬프트 엔지니어링 사용

    Args:
        user_query: 사용자 입력

    Returns:
        검색 키워드
    """
    # 예시: "강남 카페베네에서 프로모션 추천해줘"
    # → "강남 카페베네"

    # 간단한 구현: 쿼리 전체를 검색어로 사용
    # TODO: LLM 기반 NER로 개선

    keywords = []

    # 지역명 추출
    locations = ["강남", "역삼", "신사", "서울", "부산", "대구"]
    for loc in locations:
        if loc in user_query:
            keywords.append(loc)

    # 업종 추출
    categories = ["카페", "음식점", "레스토랑", "베이커리", "편의점"]
    for cat in categories:
        if cat in user_query:
            keywords.append(cat)

    # 상호명 추출 (간단한 규칙)
    if "카페베네" in user_query:
        keywords.append("카페베네")
    elif "스타벅스" in user_query:
        keywords.append("스타벅스")

    # 조합
    if keywords:
        search_query = " ".join(keywords)
    else:
        # 키워드 없으면 원본 쿼리 일부 사용
        search_query = user_query[:50]

    return search_query.strip()


def verify_store_node(state):
    """
    Store 검증 노드 (옵션)

    resolved_stores가 비어있거나 모호한 경우 사용자에게 확인 요청

    Args:
        state: AgentState

    Returns:
        업데이트된 state
    """
    logger.info("Store Verifier: 시작")

    resolved_stores = state.get("resolved_stores", [])
    logs = [f"[{datetime.now()}] store_verifier: 검증 시작"]

    if not resolved_stores:
        logger.warning("No stores to verify")
        logs.append(f"[{datetime.now()}] [WARNING] 검증할 가맹점 없음")
        return {
            "store_verification_status": "failed",
            "logs": logs
        }

    # 단일 가맹점: 즉시 확정
    if len(resolved_stores) == 1:
        logger.info("Single store found, auto-confirm")
        logs.append(f"[{datetime.now()}] 단일 가맹점, 자동 확정: {resolved_stores[0]['상호명']}")
        return {
            "store_verification_status": "confirmed",
            "logs": logs
        }

    # 다중 가맹점: 첫 번째를 primary로 설정
    logger.info(f"Multiple stores ({len(resolved_stores)}), using first as primary")
    logs.append(f"[{datetime.now()}] 다중 가맹점({len(resolved_stores)}개), 첫 번째 사용")

    return {
        "store_verification_status": "multiple_found",
        "logs": logs
    }
