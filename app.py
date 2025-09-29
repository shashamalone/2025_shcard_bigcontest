# streamlit_app.py
import streamlit as st
from agents.agent_graph import create_agent_graph

st.set_page_config(page_title="소상공인 마케팅 상담사", layout="wide")
st.title("🧩 소상공인 마케팅 전략 상담사")

graph = create_agent_graph()

user_input = st.text_input("가맹점명을 입력하세요", placeholder="예: 동네카페1")
if st.button("전략 추천"):
    if not user_input.strip():
        st.warning("가맹점명을 입력해주세요.")
    else:
        result = graph.invoke({"input": user_input})
        st.success("📊 분석 결과")
        st.write(result["output"])
