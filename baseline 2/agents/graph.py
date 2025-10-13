from langgraph.graph import StateGraph, END

from agents.state import AgentState
from agents.strategy_supervisor import strategy_supervisor_node, merge_supervisor_node
from agents.context_agent import context_agent_node
from agents.situation_agent import situation_agent_node
from agents.resource_agent import resource_agent_node
from agents.evaluation_agent import evaluation_agent_node


def build_graph():
    """마케팅 멀티에이전트 그래프 생성
    
    흐름:
    strategy_supervisor → {context, situation, resource}(병렬)
    → merge_supervisor → evaluation_agent → END
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
    
    # 병렬 분기
    g.add_edge("strategy_supervisor", "context_agent")
    g.add_edge("strategy_supervisor", "situation_agent")
    g.add_edge("strategy_supervisor", "resource_agent")
    
    # 병렬 수렴
    g.add_edge("context_agent", "merge_supervisor")
    g.add_edge("situation_agent", "merge_supervisor")
    g.add_edge("resource_agent", "merge_supervisor")
    
    # 평가 및 종료
    g.add_edge("merge_supervisor", "evaluation_agent")
    g.add_edge("evaluation_agent", END)
    
    return g.compile()


def run_marketing_agent(user_query: str, constraints: dict = None) -> AgentState:
    """마케팅 에이전트 실행"""
    graph = build_graph()
    
    initial_state = AgentState(
        user_query=user_query,
        constraints=constraints or {}
    )
    
    final_state = graph.invoke(initial_state)
    return final_state