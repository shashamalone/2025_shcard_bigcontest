from langchain_google_genai import ChatGoogleGenerativeAI
from tools.web_tool import get_weather_info, get_local_events


def situation_agent_node(state: dict) -> dict:
    """날씨/이벤트 기반 상황 인식 에이전트"""
    
    # 1. 날씨 정보 수집
    weather_data = get_weather_info("서울 강남구")
    
    # 2. 지역 이벤트 수집
    events_data = get_local_events("강남구")
    
    # 3. 상황 분석
    situation_json = {
        "weather": {
            "condition": weather_data.get("condition", "맑음"),
            "temp": weather_data.get("temp", 15),
            "signal": False,
            "reason": "특이사항 없음"
        },
        "events": {
            "upcoming": events_data.get("events", []),
            "marketing_opportunity": events_data.get("opportunity", False)
        },
        "temporal": {
            "season": "봄",
            "day_type": "평일",
            "special_period": None
        },
        "recommendations": []
    }
    
    # 날씨 기반 추천
    if weather_data.get("condition") == "비":
        situation_json["weather"]["signal"] = True
        situation_json["weather"]["reason"] = "비 오는 날 프로모션 기회"
        situation_json["recommendations"].append({
            "trigger": "rainy_day",
            "action": "우산 지참 고객 할인",
            "urgency": "high"
        })
    
    # 자신이 수정한 필드만 반환
    return {
        "situation_json": situation_json,
        "logs": [f"[situation_agent] 추천 {len(situation_json['recommendations'])}건 생성"]
    }