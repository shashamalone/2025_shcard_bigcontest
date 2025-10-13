from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


def strategy_supervisor_node(state: dict) -> dict:
    """전략 슈퍼바이저 - 의도 분석"""
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.3
    )
    
    # 간단한 의도 분류
    if "현황" in state["user_query"] or "분석" in state["user_query"]:
        intent = "overview"
    else:
        intent = "strategy"
    
    return {
        "intent": intent,
        "logs": [f"[strategy_supervisor] 의도: {intent}"]
    }


def merge_supervisor_node(state: dict) -> dict:
    """병렬 에이전트 결과 통합 및 전략 카드 생성"""
    
    if not all([state.get("context_json"), state.get("situation_json"), state.get("resource_json")]):
        return {
            "logs": ["[merge_supervisor] 경고: 일부 에이전트 결과 누락"]
        }
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.7
    )
    
    # 전략 카드 생성
    strategy_cards = [{
        "card_type": "strategy",
        "title": "평일 점심 타임 할인 프로모션",
        "why": [
            f"주말 매출 비중 {state['context_json'].get('metrics', {}).get('weekend_ratio', 60)}%",
            "평일 유동인구 활용 필요"
        ],
        "what": [
            "11-14시 세트메뉴 20% 할인",
            "SNS 사전 예고"
        ],
        "how": [
            {"step": "1. Instagram 스토리 게시", "owner": "사장님", "eta_min": 15},
            {"step": "2. POS 쿠폰 설정", "owner": "사장님", "eta_min": 10},
            {"step": "3. 매장 입구 안내문", "owner": "직원", "eta_min": 5}
        ],
        "constraints_applied": state["constraints"],
        "expected_effect": {
            "kpi": "평일 거래 건수",
            "lift_hypothesis": "+5~8% (2주 기준)"
        },
        "references": [
            {"type": "context", "source": "store_metrics"}
        ]
    }]
    
    return {
        "strategy_cards": strategy_cards,
        "logs": [f"[merge_supervisor] 전략 카드 {len(strategy_cards)}개 생성"]
    }