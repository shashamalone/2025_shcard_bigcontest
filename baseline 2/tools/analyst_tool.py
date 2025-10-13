from langchain.tools import tool


@tool
def analyze_store_metrics(query: str) -> dict:
    """점포 메트릭 분석 도구
    
    Args:
        query: 분석 요청 쿼리
        
    Returns:
        점포 지표 딕셔너리
    """
    # 실제 구현 시 DB 연결 또는 파일 읽기
    return {
        "revenue": {
            "daily_avg": 500000,
            "weekend_ratio": 0.65,
            "trend": "stable"
        },
        "customer": {
            "daily_visits": 42,
            "revisit_rate": 0.28,
            "avg_transaction": 12000
        },
        "operations": {
            "peak_hours": ["14-16", "19-21"],
            "low_hours": ["10-11", "15-17"]
        }
    }


@tool
def query_sales_data(sql_template: str, params: dict) -> list:
    """SQL 쿼리 실행 도구
    
    Args:
        sql_template: SQL 쿼리 템플릿
        params: 파라미터 딕셔너리
        
    Returns:
        쿼리 결과 리스트
    """
    # 안전 가드: 화이트리스트 검증
    allowed_tables = ["store_metrics_daily", "transactions", "customer_visits"]
    
    # 실제 구현 시 DB 연결
    return [
        {"date": "2025-01-01", "revenue": 450000, "visits": 38},
        {"date": "2025-01-02", "revenue": 520000, "visits": 45}
    ]


@tool
def visualize_data(data: list, chart_type: str) -> str:
    """데이터 시각화 도구
    
    Args:
        data: 시각화할 데이터
        chart_type: 차트 유형 (line/bar/pie)
        
    Returns:
        차트 설정 JSON 문자열
    """
    import json
    
    chart_config = {
        "type": chart_type,
        "data": data,
        "options": {
            "responsive": True,
            "title": "매출 추이"
        }
    }
    
    return json.dumps(chart_config, ensure_ascii=False)


analyst_tools = [
    analyze_store_metrics,
    query_sales_data,
    visualize_data
]