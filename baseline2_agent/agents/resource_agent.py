"""
Resource Agent
예산/채널/툴 매칭
"""
from datetime import datetime
from loguru import logger

from contracts import ResourceJSON, ResourceCard, Package, PackageBudget, Execution, ChecklistItem, EstimatedCosts


def resource_agent_node(state):
    """
    리소스 에이전트
    - 예산 등급 판단
    - 채널 매칭
    - 실행 체크리스트 생성
    """
    logger.info("Resource Agent: 시작")
    
    resource_json = _build_resource_json(state)
    
    logger.info("Resource Agent: 완료")
    
    return {
        "resource_json": resource_json.dict(),
        "logs": [f"[{datetime.now()}] resource_agent: 리소스 매칭 완료"]
    }


def _build_resource_json(state) -> ResourceJSON:
    """
    리소스 JSON 생성
    - 예산에 맞는 패키지 선택
    - 실행 가능한 체크리스트 구성
    """
    constraints = state.get("constraints", {})
    budget_krw = constraints.get("budget_krw", 50000)
    budget_tier = _determine_budget_tier(budget_krw)
    preferred_channels = constraints.get("preferred_channels", ["kakao"])
    primary_channel = preferred_channels[0] if preferred_channels else "kakao"
    
    # 패키지 매칭
    package = Package(
        id=f"CAT-{primary_channel.upper()}-{budget_tier.upper()}-01",
        version="v1",
        channel=primary_channel,
        budget=PackageBudget(
            cap=budget_krw,
            unit="KRW",
            tier=budget_tier
        ),
        fit_score=0.86
    )
    
    # 실행 체크리스트
    execution = _generate_execution_plan(primary_channel, budget_tier)
    
    # 리소스 카드 생성
    resource_card = ResourceCard(
        card_type="resource_package",
        derived_from_card_id=None,
        offer_id=f"OFF-{datetime.now().strftime('%Y%m%d%H%M')}",
        title=f"{primary_channel.capitalize()} 저예산 패키지",
        summary=f"예산 {budget_krw:,}원으로 실행 가능한 {primary_channel} 캠페인",
        package=package,
        execution=execution,
        kpi_alignment={
            "primary": {"metric": "reach", "target": "+12%/2w"},
            "tracking": {"metric_keys": ["reach", "impressions", "ctr"]}
        },
        constraints_applied={
            "budget_tier": budget_tier,
            "preferred_channels": preferred_channels,
            "forbidden_channels": []
        },
        risks=[
            "영상 제작 리소스 부족 시 일정 지연 가능",
            "소재 반복 시 효율 하락"
        ],
        assumptions=[
            "직원 1명 1시간/일 확보",
            "주 3회 업로드 가능"
        ],
        references=[
            {"type": "doc", "id": f"playbooks/{primary_channel.upper()}-lowbudget-01"}
        ],
        citations=[
            {"type": "best_practice", "source": "Meta Business Help"}
        ],
        constraints_matched=True,
        contract_version="resource.v1"
    )
    
    return ResourceJSON(
        resource_card=resource_card,
        resource_refs=[package.id]
    )


def _determine_budget_tier(budget_krw: int) -> str:
    """예산 등급 판단"""
    if budget_krw < 100000:
        return "low"
    elif budget_krw < 500000:
        return "med"
    else:
        return "high"


def _generate_execution_plan(channel: str, tier: str) -> Execution:
    """
    채널/등급별 실행 계획 생성
    """
    if channel == "instagram" and tier == "low":
        checklist = [
            ChecklistItem(step="릴스 촬영 (30s)", owner="staff", eta_min=40),
            ChecklistItem(step="해시태그 10개 적용", owner="owner", eta_min=10),
            ChecklistItem(step="스토리 2회 리포스트", owner="owner", eta_min=5)
        ]
        assets = [
            "video:reels_30s_vertical",
            "copy:promo_caption_short",
            "hashtag:set_10"
        ]
        dependencies = [
            "IG 비즈니스 계정 연결",
            "브랜드 가이드라인 확인"
        ]
        templates = [
            {"id": "playbooks/IG-lowbudget-01", "title": "저예산 릴스 실행 가이드"}
        ]
        costs = EstimatedCosts(media_spend=20000, production_spend=0)
        
    elif channel == "kakao" and tier == "low":
        checklist = [
            ChecklistItem(step="카톡 채널 쿠폰 발급", owner="owner", eta_min=15),
            ChecklistItem(step="알림톡 템플릿 작성", owner="owner", eta_min=20),
            ChecklistItem(step="타겟 세그먼트 설정", owner="owner", eta_min=10)
        ]
        assets = [
            "copy:coupon_message",
            "image:coupon_banner"
        ]
        dependencies = [
            "카카오톡 채널 개설",
            "알림톡 승인"
        ]
        templates = [
            {"id": "playbooks/KAKAO-lowbudget-01", "title": "카톡 쿠폰 발급 가이드"}
        ]
        costs = EstimatedCosts(media_spend=30000, production_spend=0)
        
    else:
        # 기본 플랜
        checklist = [
            ChecklistItem(step="캠페인 소재 준비", owner="staff", eta_min=30)
        ]
        assets = []
        dependencies = []
        templates = []
        costs = EstimatedCosts(media_spend=0, production_spend=0)
    
    return Execution(
        checklist=checklist,
        assets_needed=assets,
        dependencies=dependencies,
        templates=templates,
        estimated_costs=costs
    )