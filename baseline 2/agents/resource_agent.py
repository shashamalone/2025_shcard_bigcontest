from langchain_google_genai import ChatGoogleGenerativeAI
from tools.rag_tool import search_marketing_tools


def resource_agent_node(state: dict) -> dict:
    """예산/채널/도구 매칭 에이전트"""
    
    # 1. 제약조건에서 예산 추출
    budget = state["constraints"].get("budget_krw", 50000)
    
    # 2. 예산 밴드 분류
    if budget < 50000:
        budget_band = "0-50k"
    elif budget < 100000:
        budget_band = "50-100k"
    else:
        budget_band = "100k+"
    
    # 3. RAG로 적합한 마케팅 도구 검색
    tools_result = search_marketing_tools(f"예산 {budget}원 소상공인 마케팅")
    
    # 4. 리소스 구조화
    resource_json = {
        "budget_band": budget_band,
        "available_budget": budget,
        "primary_channel": "instagram",
        "channel_mix": [
            {"name": "instagram", "fit_score": 0.9, "cost": "무료~10만원/월"},
            {"name": "naver_blog", "fit_score": 0.85, "cost": "무료"},
            {"name": "kakao_channel", "fit_score": 0.8, "cost": "무료"}
        ],
        "tools": [
            {"name": "Canva", "purpose": "디자인", "cost": "무료"},
            {"name": "Buffer", "purpose": "스케줄링", "cost": "월 5달러"},
            {"name": "Google Analytics", "purpose": "분석", "cost": "무료"}
        ],
        "time_investment": {
            "weekly_hours": 5,
            "breakdown": {
                "content_creation": 2,
                "posting": 1,
                "engagement": 2
            }
        },
        "skill_requirements": [
            {"skill": "기본 SNS 사용", "level": "초급"},
            {"skill": "사진 촬영", "level": "중급"}
        ]
    }
    
    # 자신이 수정한 필드만 반환
    return {
        "resource_json": resource_json,
        "logs": [f"[resource_agent] 예산 밴드: {budget_band}, 주요 채널: instagram"]
    }