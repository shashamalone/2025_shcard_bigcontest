"""
LangGraph Assembly
Multi-Agent 시스템 그래프 구성
"""
from typing import Literal, TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator

from .strategy_supervisor import strategy_supervisor_node, merge_supervisor_node
from .context_agent import context_agent_node
from .situation_agent import situation_agent_node
from .resource_agent import resource_agent_node
from .evaluation_agent import evaluation_agent_node


class AgentState(TypedDict):
    """중앙 상태 관리 - TypedDict 사용"""
    user_query: str
    intent: str
    constraints: dict
    
    # 데이터 수집 결과
    context_json: dict | None
    situation_json: dict | None
    resource_json: dict | None
    
    # 전략 생성 결과
    strategy_cards: list[dict]
    
    # 평가 결과
    eval_report: dict | None
    batch_eval_result: dict | None
    
    # 로그 - 병렬 처리를 위해 Annotated 사용
    logs: Annotated[list[str], operator.add]


def build_graph():
    """
    LangGraph 조립
    
    흐름:
    1. strategy_supervisor (엔트리)
    2. context_agent, situation_agent, resource_agent (병렬)
    3. merge_supervisor (데이터 통합 및 전략 생성)
    4. evaluation_agent (전략 평가)
    5. END
    """
    g = StateGraph(AgentState)
    
    # 노드 등록
    g.add_node("strategy_supervisor", strategy_supervisor_node)
    g.add_node("context_agent", context_agent_node)
    g.add_node("situation_agent", situation_agent_node)
    g.add_node("resource_agent", resource_agent_node)
    g.add_node("merge_supervisor", merge_supervisor_node)
    g.add_node("evaluation_agent", evaluation_agent_node)
    
    # 엔트리 포인트
    g.set_entry_point("strategy_supervisor")
    
    # 병렬 실행: 3개 에이전트 동시 실행
    g.add_edge("strategy_supervisor", "context_agent")
    g.add_edge("strategy_supervisor", "situation_agent")
    g.add_edge("strategy_supervisor", "resource_agent")
    
    # 병렬 완료 후 merge로 수렴
    g.add_edge("context_agent", "merge_supervisor")
    g.add_edge("situation_agent", "merge_supervisor")
    g.add_edge("resource_agent", "merge_supervisor")
    
    # 평가 및 종료
    g.add_edge("merge_supervisor", "evaluation_agent")
    g.add_edge("evaluation_agent", END)
    
    return g.compile()


# 그래프 인스턴스 생성
marketing_graph = build_graph()