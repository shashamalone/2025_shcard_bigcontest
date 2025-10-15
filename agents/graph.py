# agents/graph.py
# 상태 정의
from typing import TypedDict, Optional, Dict, Any, List

class AgentState(TypedDict, total=False):
    user_query: Optional[str]
    store: Dict[str, Any]     # {"id": "...", "market_id": "M45", "industry_code": "CAFE", ...}
    period: Dict[str, str]    # {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}

    # 상황 수집 결과 (situation_agent_node 가 채움)
    situation: Dict[str, Any]     # 최종 병합된 Situation JSON
    log: List[str]                # 선택: 진행 로그

# 그래프 연결
from __future__ import annotations
from typing import TypedDict, Optional, Dict, Any, List
from langgraph.graph import StateGraph, END

from agents.situation_agent import situation_agent_node
# from agents.context_agent import context_node
# from agents.strategy_supervisor import strategy_node
# from agents.evaluation_agent import evaluation_node

class AgentState(TypedDict, total=False):
    user_query: Optional[str]
    store: Dict[str, Any]
    period: Dict[str, str]
    situation: Dict[str, Any]
    log: List[str]

def build_graph():
    g = StateGraph(AgentState)

    # 기존 노드들
    # g.add_node("intent", intent_node)
    # g.add_node("context", context_node)
    g.add_node("situation", situation_agent_node)  # ★ 내부 병렬 호출
    # g.add_node("strategy", strategy_node)
    # g.add_node("evaluation", evaluation_node)

    # 플로우(예시): context → situation → strategy → evaluation
    # g.set_entry_point("intent")
    # g.add_edge("intent", "context")
    # g.add_edge("context", "situation")
    # g.add_edge("situation", "strategy")
    # g.add_edge("strategy", "evaluation")
    # g.add_edge("evaluation", END)

    # 최소 실행만 원하면 situation만 연결
    g.set_entry_point("situation")
    g.add_edge("situation", END)

    return g.compile()

if __name__ == "__main__":
    app = build_graph()
    init_state: AgentState = {
        "user_query": "성수동 팝업/행사 + 이번 주 비 영향 있을까?",
        "store": {"id": "S123", "market_id": "M45", "industry_code": "CAFE"},
        "period": {"start": "2025-11-10", "end": "2025-11-16"},
    }
    final = app.invoke(init_state)
    print(final["situation"]["summary"])
    print(len(final["situation"]["signals"]))

```