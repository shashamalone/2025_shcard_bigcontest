# agents/llm_config.py
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm():
    """Google Generative AI 기반 LLM 불러오기"""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
        max_output_tokens=512
    )
