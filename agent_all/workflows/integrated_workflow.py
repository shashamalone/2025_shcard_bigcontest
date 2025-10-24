# workflows/integrated_workflow.py
"""
통합 워크플로우
- Situation Agent → Content Agent 연동
- Langgraph StateGraph 기반 구현
"""
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from agents.situation_agent import situation_agent_node, OptimizedStrategyState
from agents.content_agent import content_agent_node


def create_situation_content_workflow() -> StateGraph:
    """
    Situation + Content Agent 워크플로우 생성
    
    흐름:
    1. Situation Agent: 이벤트/날씨 수집
    2. (조건부) Content Agent: 콘텐츠 가이드 생성
    """
    workflow = StateGraph(OptimizedStrategyState)
    
    # 노드 추가
    workflow.add_node("situation_agent", situation_agent_node)
    workflow.add_node("content_agent", content_agent_node)
    
    # 조건부 라우팅
    def route_after_situation(state: Dict[str, Any]) -> Literal["content_agent", "END"]:
        """
        Situation 수집 후 조건 판단:
        - 전략팀 산출물이 있고, Promotion에 채널 언급 있으면 → content_agent
        - 아니면 종료
        """
        strategy_4p = state.get("strategy_4p", {})
        promotion = strategy_4p.get("promotion", "")
        
        # 채널 키워드 체크
        channel_keywords = ["인스타", "블로그", "페이스북", "유튜브", "틱톡", "SNS"]
        has_channel = any(kw in promotion for kw in channel_keywords)
        
        if has_channel and promotion:
            return "content_agent"
        else:
            return END
    
    # 엣지 연결
    workflow.set_entry_point("situation_agent")
    workflow.add_conditional_edges(
        "situation_agent",
        route_after_situation,
        {
            "content_agent": "content_agent",
            END: END
        }
    )
    workflow.add_edge("content_agent", END)
    
    return workflow.compile()


# === 실행 헬퍼 ===
def run_workflow(
    store_name: str,
    market_id: str,
    period_start: str,
    period_end: str,
    strategy_4p: Dict[str, str],
    **kwargs
) -> Dict[str, Any]:
    """
    워크플로우 실행 헬퍼
    
    Args:
        store_name: 가맹점명
        market_id: 상권 ID
        period_start: 기간 시작 (YYYY-MM-DD)
        period_end: 기간 종료 (YYYY-MM-DD)
        strategy_4p: 전략팀 4P 결과
        **kwargs: 추가 state 항목
    
    Returns:
        최종 state
    """
    from langchain_core.messages import HumanMessage
    
    initial_state = {
        "messages": [HumanMessage(content=f"{store_name} 상황 분석 및 콘텐츠 가이드 요청")],
        "target_store_name": store_name,
        "target_market_id": market_id,
        "period_start": period_start,
        "period_end": period_end,
        "strategy_4p": strategy_4p,
        "log": [],
        **kwargs  # targeting_positioning, market_customer_analysis 등
    }
    
    workflow = create_situation_content_workflow()
    final_state = workflow.invoke(initial_state)
    
    return final_state


# === 테스트 ===
if __name__ == "__main__":
    print("=== Situation + Content Workflow 테스트 ===\n")
    
    result = run_workflow(
        store_name="성수 브런치 카페",
        market_id="M45",
        period_start="2025-11-01",
        period_end="2025-11-07",
        strategy_4p={
            "product": "건강 브런치 세트",
            "price": "중가 (12,000~15,000원)",
            "place": "매장 중심, 배달 보조",
            "promotion": "인스타그램 릴스 + 네이버 블로그로 2030 직장인 타겟"
        },
        targeting_positioning="직장인 밀집 지역, 평일 런치 수요 집중",
        market_customer_analysis="20-30대 여성 고객 비중 높음",
        industry="카페"
    )
    
    print("\n[Situation 결과]")
    situation = result.get("situation", {})
    print(f"  - 유효 신호: {situation.get('has_valid_signal')}")
    print(f"  - 요약: {situation.get('summary')}")
    print(f"  - 신호 수: {len(situation.get('signals', []))}")
    
    if "content_guide" in result:
        print("\n[Content Guide 결과]")
        guide = result["content_guide"]
        print(f"  - 타겟: {guide.get('target_audience')}")
        print(f"  - 톤앤매너: {guide.get('brand_tone')}")
        print(f"  - 채널 수: {len(guide.get('channels', []))}")
        
        for ch in guide.get("channels", [])[:2]:  # 처음 2개만 출력
            print(f"\n  [{ch['channel_name']}]")
            print(f"    - 형식: {ch['post_format']}")
            print(f"    - 빈도: {ch['posting_frequency']}")
            print(f"    - 해시태그: {', '.join(ch['hashtags'][:5])}...")
    
    print("\n[로그]")
    for log in result.get("log", []):
        print(f"  {log}")
