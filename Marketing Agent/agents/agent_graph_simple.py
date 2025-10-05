import os
from typing import TypedDict, Annotated, List
import operator
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tools.analyst_tool import analyst_tools
from tools.content_writer_tool import content_writer_tools
from tools.designer_tool import designer_tools


# 상태 정의
class MarketingState(TypedDict):
    messages: Annotated[List[str], operator.add]
    business_info: str
    analysis_result: str
    content_draft: str
    design_concept: str
    final_strategy: str
    needs_rework: bool
    iteration_count: int


# Agent 생성 함수
def create_agent_executor(agent_name: str, system_prompt: str, tools: list):
    """공통 Agent Executor 생성 함수"""
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_openai_functions_agent(model, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


# 각 노드 함수 정의
def content_writer_node(state: MarketingState):
    """콘텐츠 작가 노드"""
    system_prompt = """당신은 전문 마케팅 콘텐츠 작가입니다.
    비즈니스 정보를 바탕으로 매력적인 마케팅 메시지를 작성합니다.
    타겟 고객에게 공감을 얻을 수 있는 카피를 만드세요."""
    
    executor = create_agent_executor("ContentWriter", system_prompt, content_writer_tools)
    
    input_text = f"""
    비즈니스 정보: {state['business_info']}
    
    다음 작업을 수행하세요:
    1. 메인 마케팅 카피 작성
    2. 소셜 미디어 콘텐츠 제안 (instagram 기준)
    """
    
    result = executor.invoke({"input": input_text})
    
    return {
        "messages": [f"[콘텐츠 작가] {result['output']}"],
        "content_draft": result['output']
    }


def graphic_designer_node(state: MarketingState):
    """그래픽 디자이너 노드"""
    system_prompt = """당신은 브랜드 아이덴티티를 이해하는 그래픽 디자이너입니다.
    콘텐츠에 맞는 비주얼 컨셉을 제안합니다.
    현대적이고 매력적인 디자인 가이드를 제공하세요."""
    
    executor = create_agent_executor("GraphicDesigner", system_prompt, designer_tools)
    
    input_text = f"""
    비즈니스 정보: {state['business_info']}
    콘텐츠 초안: {state['content_draft']}
    
    다음 작업을 수행하세요:
    1. 브랜드 스타일에 맞는 디자인 컨셉 제안
    2. Instagram에 최적화된 디자인 가이드 제공
    """
    
    result = executor.invoke({"input": input_text})
    
    return {
        "messages": [f"[그래픽 디자이너] {result['output']}"],
        "design_concept": result['output']
    }


def data_analyst_node(state: MarketingState):
    """데이터 분석가 노드"""
    system_prompt = """당신은 마케팅 데이터 분석 전문가입니다.
    시장 트렌드와 성공 사례를 분석하여 실행 가능한 인사이트를 제공합니다.
    RAG와 웹 검색을 활용하여 최신 정보를 수집하세요."""
    
    executor = create_agent_executor("DataAnalyst", system_prompt, analyst_tools)
    
    input_text = f"""
    비즈니스 정보: {state['business_info']}
    
    다음 작업을 수행하세요:
    1. 시장 데이터 분석
    2. 관련 성공 사례 검색 (RAG 활용)
    3. 최신 마케팅 트렌드 조사 (웹 검색)
    """
    
    result = executor.invoke({"input": input_text})
    
    return {
        "messages": [f"[데이터 분석가] {result['output']}"],
        "analysis_result": result['output']
    }


def brand_manager_node(state: MarketingState):
    """브랜드 매니저 노드 - 최종 검토 및 승인"""
    iteration_count = state.get('iteration_count', 0)
    
    # 간단한 검토 로직
    content_quality = len(state.get('content_draft', '')) > 100
    design_quality = len(state.get('design_concept', '')) > 100
    analysis_quality = len(state.get('analysis_result', '')) > 100
    
    all_good = content_quality and design_quality and analysis_quality
    
    if all_good or iteration_count >= 2:
        # 최종 전략 종합
        final_strategy = f"""
        === 최종 마케팅 전략 ===
        
        📊 시장 분석:
        {state.get('analysis_result', 'N/A')}
        
        ✍️ 콘텐츠 전략:
        {state.get('content_draft', 'N/A')}
        
        🎨 디자인 컨셉:
        {state.get('design_concept', 'N/A')}
        
        === 실행 계획 ===
        1. 소셜 미디어 캠페인 시작 (1주차)
        2. 콘텐츠 제작 및 게시 (2주차)
        3. 성과 측정 및 최적화 (3-4주차)
        
        예상 예산: 소규모 (월 50-100만원)
        예상 기간: 4주
        """
        
        return {
            "messages": [f"[브랜드 매니저] 최종 승인 완료!"],
            "final_strategy": final_strategy,
            "needs_rework": False,
            "iteration_count": iteration_count + 1
        }
    else:
        return {
            "messages": [f"[브랜드 매니저] 수정이 필요합니다. (반복 {iteration_count + 1})"],
            "needs_rework": True,
            "iteration_count": iteration_count + 1
        }


# 라우팅 함수
def should_continue(state: MarketingState):
    """브랜드 매니저 이후 진행 방향 결정"""
    if state.get('needs_rework', False) and state.get('iteration_count', 0) < 2:
        return "content_writer"
    else:
        return END


# 워크플로우 그래프 생성
def create_marketing_workflow():
    """마케팅 MultiAgent 워크플로우 생성"""
    workflow = StateGraph(MarketingState)
    
    # 노드 추가
    workflow.add_node("content_writer", content_writer_node)
    workflow.add_node("graphic_designer", graphic_designer_node)
    workflow.add_node("data_analyst", data_analyst_node)
    workflow.add_node("brand_manager", brand_manager_node)
    
    # 엣지 정의
    workflow.set_entry_point("content_writer")
    workflow.add_edge("content_writer", "graphic_designer")
    workflow.add_edge("graphic_designer", "data_analyst")
    workflow.add_edge("data_analyst", "brand_manager")
    
    # 조건부 엣지
    workflow.add_conditional_edges(
        "brand_manager",
        should_continue,
        {
            "content_writer": "content_writer",
            END: END
        }
    )
    
    # 메모리 추가
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app


# 실행 함수
def run_marketing_agent(business_info: str):
    """마케팅 에이전트 실행"""
    app = create_marketing_workflow()
    
    initial_state = {
        "messages": [],
        "business_info": business_info,
        "analysis_result": "",
        "content_draft": "",
        "design_concept": "",
        "final_strategy": "",
        "needs_rework": False,
        "iteration_count": 0
    }
    
    config = {"configurable": {"thread_id": "1"}}
    
    final_state = None
    for state in app.stream(initial_state, config):
        final_state = state
        print(f"\n=== 현재 상태 ===")
        print(state)
    
    return final_state
