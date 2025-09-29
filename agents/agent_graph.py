from langgraph.graph import StateGraph, END
from .llm_config import get_llm
from .prompts import USER_PROMPT
from tools.mcp_tool import search_merchant
from tools.rag_tool import rag_search
from typing import TypedDict


# 상태 정의
class AgentState(TypedDict):
    input: str
    output: str

def create_agent_graph():
    llm = get_llm()
    graph = StateGraph(AgentState)
    
    def fetch_merchant(state):
        merchant = search_merchant.run(state["input"])
        return {"merchant_data": merchant, "input": state["input"]}

    def fetch_rag(state):
        rag_docs = rag_search.run(state["input"])
        return {"rag_docs": rag_docs, **state}

    def analyze(state):
        merchant_data = state.get("merchant_data", "가맹점 데이터 없음")
        rag_docs = state.get("rag_docs", [])
        
        context = f"가맹점 데이터: {merchant_data}\nRAG 검색 결과: {rag_docs}"
        prompt = USER_PROMPT.format(user_input=f"{context}\n\n사용자 질문: {state['input']}")
        response = llm.invoke(prompt)
        
        # 응답 내용 안전하게 꺼내기
        try:
            output_text = response.text()  # ✅ 여기서 꺼내야 함
        except Exception:
            output_text = getattr(response, "content", None) or getattr(response, "text", None)
        if not output_text:
            output_text = "⚠️ 분석 결과를 생성하지 못했습니다. 입력값과 모델 설정을 확인해주세요."

        return {"output": output_text}

    # 그래프 구성 -  fetch_merchant → fetch_rag → analyze 순으로 실행
    graph.add_node("fetch_merchant", fetch_merchant)
    graph.add_node("fetch_rag", fetch_rag)
    graph.add_node("analyze", analyze)

    graph.set_entry_point("fetch_merchant")
    graph.add_edge("fetch_merchant", "fetch_rag")
    graph.add_edge("fetch_rag", "analyze")
    graph.add_edge("analyze", END)

    return graph.compile()
