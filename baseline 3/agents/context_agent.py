"""
Context Agent
점포/상권 컨텍스트 생성
"""
from datetime import datetime
from loguru import logger

from contracts import ContextJSON, Store, Period, Market, Risk, SessionConstraints, Provenance


def context_agent_node(state):
    """
    컨텍스트 에이전트
    - 점포/상권 데이터 수집
    - 파생 지표 계산
    - 위험 평가
    """
    logger.info("Context Agent: 시작")
    state.logs.append(f"[{datetime.now()}] context_agent: 컨텍스트 생성 시작")
    
    # 실제로는 DB 쿼리 + 계산
    context_json = _build_context_json(state)
    
    state.context_json = context_json.dict()
    state.logs.append(f"[{datetime.now()}] context_agent: 완료 (버전: {context_json.provenance.version})")
    
    logger.info("Context Agent: 완료")
    
    return state


def _build_context_json(state) -> ContextJSON:
    """
    컨텍스트 JSON 생성 (예시)
    실제로는 DB에서 데이터 로드 + 계산
    """
    # 더미 데이터 (실제로는 DB 쿼리)
    from contracts.context_schema import (
        KPI, DerivedMetrics, TimeSeries, Metrics,
        FootTrafficProxy
    )
    
    context = ContextJSON(
        store=Store(
            id=state.constraints.get("store_id", "S123"),
            name="테스트 카페",
            industry_code="CAFE",
            market_id="M45"
        ),
        period=Period(
            start=state.constraints.get("start_date", "2025-09-01"),
            end=state.constraints.get("end_date", "2025-09-30")
        ),
        metrics=Metrics(
            kpi=KPI(
                sales_sum=12500000,
                visits_sum=3200,
                aov=39000,
                repeat_rate=0.27
            ),
            derived=DerivedMetrics(
                same_industry_sales_ratio=0.82,
                sales_volatility_4w=0.31,
                lunch_share=0.18,
                weekend_share=0.62,
                afternoon_share=0.22,
                comp_intensity=0.74,
                market_churn_rate_4w=0.012,
                foot_traffic_proxy=0.64,
                aov_gap_pct=-0.12
            ),
            timeseries=TimeSeries(
                daily_sales=[],
                daily_visits=[]
            )
        ),
        market=Market(
            market_id="M45",
            same_industry_store_cnt=47,
            total_store_cnt=312,
            new_open_cnt_4w=5,
            close_cnt_4w=2,
            avg_sales_industry=15200000,
            foot_traffic_proxy=FootTrafficProxy(
                index=0.64,
                trend_4w="down",
                zscore=-1.2
            ),
            rent_level=0.55,
            vacancy_rate=0.07
        ),
        risk=Risk(
            score=0.67,
            typology="over_comp",
            reasons=["comp_intensity↑", "same_industry_sales_ratio=0.82"],
            evidence_chips=[
                "경쟁강도 0.74 (상위 20%)",
                "업종평균대비 매출 0.82",
                "런치비중 18%"
            ]
        ),
        session_constraints=SessionConstraints(
            budget_krw=state.constraints.get("budget_krw", 50000),
            budget_tier=state.constraints.get("budget_tier", "low"),
            preferred_channels=state.constraints.get("preferred_channels", ["kakao", "instagram"]),
            forbidden_channels=[],
            brand_tone="friendly"
        ),
        provenance=Provenance(
            as_of=datetime.now().strftime("%Y-%m-%d"),
            sources=["store_metrics_daily", "market_features_daily"],
            version="ctx.v1"
        )
    )
    
    return context


def _calculate_risk_score(metrics: dict) -> float:
    """
    위험 점수 계산
    
    가중치:
    - 경쟁 강도: 30%
    - 상권 활력: 20%
    - 상대 성과: 20%
    - 고객 충성: 15%
    - 운영 편중: 10%
    - 비용 요인: 5%
    """
    weights = {
        "comp_intensity": 0.30,
        "market_churn_rate_4w": 0.20,
        "same_industry_sales_ratio": 0.20,
        "repeat_rate": 0.15,
        "weekend_share": 0.10,
        "rent_level": 0.05
    }
    
    # 실제 계산 로직
    # ...
    
    return 0.67  # 예시