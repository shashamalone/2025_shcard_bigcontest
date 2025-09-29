# agents/prompts.py
from langchain.prompts import ChatPromptTemplate

SYSTEM_PROMPT = """당신은 소상공인 마케팅 전략 AI 상담사입니다.
데이터 근거에 기반해 상권/가맹점 맞춤 전략을 제안하세요.
출력은 항상 동일한 근거 → 전략 → 실행가이드 → 검증순으로."""

USER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", "{user_input}")
])