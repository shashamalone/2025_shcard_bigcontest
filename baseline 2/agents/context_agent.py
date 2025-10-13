from langchain_google_genai import ChatGoogleGenerativeAI
from tools.analyst_tool import analyze_store_metrics


def context_agent_node(state: dict) -> dict:
    """점포/상권 컨텍스트 생성 에이전트"""
    
    # 1. 점포 메트릭 분석
    metrics_result = analyze_store_metrics(state["user_query"])
    
    # 2. 구조화된 컨텍스트 생성
    structured_context = {
        "meta": {
            "store_id": "STORE_001",
            "business_type": "카페",
            "location": "강남구"
        },
        "metrics": {
            "weekend_ratio": 65,
            "avg_transaction": 12000,
            "revisit_rate": 28,
            "peak_hour": "14-16시"
        },
        "market": {
            "competition_level": "높음",
            "nearby_stores": 8,
            "foot_traffic": "중상"
        },
        "risks": [
            {"type": "재방문율", "severity": "중", "desc": "업계 평균(35%) 대비 낮음"}
        ]
    }
    
    # 자신이 수정한 필드만 반환
    return {
        "context_json": structured_context,
        "logs": ["[context_agent] 컨텍스트 생성 완료"]
    }