"""
Strategy Supervisor Agent
최상위 의사결정 및 오케스트레이션
"""
from datetime import datetime
from loguru import logger

from contracts import StrategyCard, InputsUsed, Timeline, Budget, KPITargets, KPITarget, Tracking


def strategy_supervisor_node(state):
    """
    전략 슈퍼바이저 초기화
    - 의도 파악
    - 하위 에이전트 실행 준비
    """
    logger.info("Strategy Supervisor: 시작")
    
    # Intent 분석 (실제로는 LLM 또는 규칙 기반 분석)
    user_query = state.get("user_query", "")
    if "비교" in user_query or "순위" in user_query:
        intent = "comparison"
    else:
        intent = "strategy"
    
    logger.info(f"Intent detected: {intent}")
    
    return {
        "intent": intent,
        "logs": [
            f"[{datetime.now()}] strategy_supervisor: 의도 분석 시작",
            f"[{datetime.now()}] intent: {intent}"
        ]
    }


def merge_supervisor_node(state):
    """
    병렬 수집 완료 후 데이터 통합 및 전략 카드 생성
    """
    logger.info("Merge Supervisor: 데이터 통합 시작")
    
    logs = [f"[{datetime.now()}] merge_supervisor: 3개 에이전트 결과 통합"]
    
    # Context, Situation, Resource 검증
    if not state.get("context_json"):
        logger.warning("Context JSON 누락")
        logs.append("[WARNING] context_json 누락")
    
    if not state.get("situation_json"):
        logger.info("Situation JSON 없음 (정상 케이스)")
    
    if not state.get("resource_json"):
        logger.warning("Resource JSON 누락")
        logs.append("[WARNING] resource_json 누락")
    
    # 전략 카드 생성 (실제로는 LLM 기반 생성)
    strategy_card = _generate_strategy_card(state)
    
    logs.append(f"[{datetime.now()}] 전략 카드 생성 완료: {strategy_card.title}")
    
    logger.info(f"전략 카드 생성 완료: 1개")
    
    return {
        "strategy_cards": [strategy_card.dict()],
        "logs": logs
    }


def _generate_strategy_card(state) -> StrategyCard:
    """
    전략 카드 생성 로직 (예시)
    실제로는 LLM + 프롬프트 엔지니어링
    """
    context = state.get("context_json", {})
    situation = state.get("situation_json", {})
    resource = state.get("resource_json", {})
    constraints = state.get("constraints", {})
    
    # 기본 전략 생성
    card = StrategyCard(
        id=f"STR-{datetime.now().strftime('%Y%m%d')}-001",
        card_type="base_strategy",
        title="평일 런치 타겟 번들 프로모션",
        hypothesis="런치 비중이 낮고 주말에 편중된 매출 구조를 평일로 분산하여 전체 매출 증대",
        why=[
            f"주말 편중: {context.get('metrics', {}).get('derived', {}).get('weekend_share', 0.0):.0%}",
            f"런치 비중: {context.get('metrics', {}).get('derived', {}).get('lunch_share', 0.0):.0%}"
        ],
        inputs_used=InputsUsed(
            context_version="ctx.v1",
            situation_signal_ids=situation.get("signals", []) if situation.get("has_valid_signal") else [],
            resource_refs=resource.get("resource_refs", [])
        ),
        target_segment="직장인, 20-40대",
        channel_hints=constraints.get("preferred_channels", ["kakao", "instagram"]),
        offer="11-14시 세트 메뉴 3종, 15% 할인",
        timeline=Timeline(
            start=datetime.now().strftime("%Y-%m-%d"),
            end="2025-11-30"
        ),
        budget=Budget(
            cap=constraints.get("budget_krw", 50000),
            unit="KRW"
        ),
        constraints_applied=constraints,
        kpi_targets=KPITargets(
            primary=KPITarget(
                metric="trans",
                target="+8%/2w"
            ),
            secondary=[
                KPITarget(metric="lunch_sales", target="+15%/2w")
            ]
        ),
        assets_needed=[
            "image:lunch_set_banner",
            "copy:lunch_promo_caption"
        ],
        risks=[
            "직원 대응 역량 부족 시 고객 불만 발생 가능",
            "재료 수급 이슈 발생 시 프로모션 중단 리스크"
        ],
        evidence_chips=[
            f"업종평균대비: {context.get('metrics', {}).get('derived', {}).get('same_industry_sales_ratio', 0.0):.2f}",
            f"경쟁강도: {context.get('metrics', {}).get('derived', {}).get('comp_intensity', 0.0):.2f}"
        ],
        tracking=Tracking(
            metric_keys=["lunch_sales", "trans", "repeat_rate"]
        ),
        assumptions=[
            "직원 1명 1시간/일 확보 가능",
            "세트 메뉴 원가율 65% 가정"
        ],
        references=[
            {"type": "db", "table": "store_metrics_daily"},
            {"type": "ctx", "field": "metrics.derived.lunch_share"}
        ],
        contract_version="strategy.v1"
    )
    
    return card