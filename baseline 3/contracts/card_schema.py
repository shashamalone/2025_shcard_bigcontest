"""
Strategy Card & Evaluation Schema
전략 카드 및 평가 리포트 표준 스키마
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field


# ========== Strategy Card ==========

class InputsUsed(BaseModel):
    """사용된 입력"""
    context_version: str = Field("ctx.v1", description="컨텍스트 버전")
    situation_signal_ids: list[str] = Field(default_factory=list, description="상황 신호 ID")
    resource_refs: list[str] = Field(default_factory=list, description="리소스 참조")


class Timeline(BaseModel):
    """실행 기간"""
    start: str = Field(..., description="시작일 (YYYY-MM-DD)")
    end: str = Field(..., description="종료일 (YYYY-MM-DD)")


class Budget(BaseModel):
    """예산"""
    cap: int = Field(0, description="예산 상한 (원)")
    unit: str = Field("KRW", description="통화 단위")


class ConstraintsApplied(BaseModel):
    """적용된 제약"""
    budget_tier: Literal["low", "med", "high"] = Field("low")
    preferred_channels: list[str] = Field(default_factory=list)
    forbidden_channels: list[str] = Field(default_factory=list)


class KPITarget(BaseModel):
    """KPI 목표"""
    metric: str = Field(..., description="지표명 (trans, sales, repeat_rate 등)")
    target: str = Field(..., description="목표치 (+8%/2w 등)")


class KPITargets(BaseModel):
    """KPI 목표들"""
    primary: KPITarget
    secondary: list[KPITarget] = Field(default_factory=list)


class Tracking(BaseModel):
    """추적 지표"""
    metric_keys: list[str] = Field(default_factory=list, description="추적할 지표 키")


class Reference(BaseModel):
    """참조"""
    type: Literal["db", "ctx", "situation", "resource", "doc"] = Field(..., description="참조 유형")
    table: Optional[str] = Field(None, description="테이블명 (DB 참조)")
    field: Optional[str] = Field(None, description="필드명 (CTX 참조)")
    id: Optional[str] = Field(None, description="문서 ID")


class StrategyCard(BaseModel):
    """전략 카드"""
    id: str = Field(..., description="카드 ID (STR-YYYYMMDD-###)")
    card_type: Literal["base_strategy", "situation_response", "resource_package"] = Field(
        "base_strategy", description="카드 유형"
    )
    
    title: str = Field(..., description="전략 제목")
    hypothesis: str = Field(..., description="전략 가설")
    why: list[str] = Field(default_factory=list, description="근거 칩")
    
    inputs_used: InputsUsed = Field(default_factory=InputsUsed)
    
    target_segment: str = Field(..., description="타겟 세그먼트")
    channel_hints: list[str] = Field(default_factory=list, description="추천 채널")
    offer: str = Field(..., description="제안 내용")
    
    timeline: Timeline
    budget: Budget = Field(default_factory=Budget)
    constraints_applied: ConstraintsApplied = Field(default_factory=ConstraintsApplied)
    
    kpi_targets: KPITargets
    
    assets_needed: list[str] = Field(default_factory=list, description="필요 자산")
    risks: list[str] = Field(default_factory=list, description="위험 요소")
    evidence_chips: list[str] = Field(default_factory=list, description="근거 칩")
    tracking: Tracking = Field(default_factory=Tracking)
    
    assumptions: list[str] = Field(default_factory=list, description="가정 사항")
    references: list[Reference] = Field(default_factory=list, description="참조")
    contract_version: str = Field("strategy.v1", description="계약 버전")


# ========== Situation Schema ==========

class SignalDetails(BaseModel):
    """신호 상세"""
    pop: Optional[float] = Field(None, description="강수확률")
    rain_mm: Optional[float] = Field(None, description="강수량 (mm)")
    distance_km: Optional[float] = Field(None, description="거리 (km)")
    expected_visitors: Optional[int] = Field(None, description="예상 방문객")


class Signal(BaseModel):
    """상황 신호"""
    signal_id: str = Field(..., description="신호 ID")
    signal_type: Literal["weather", "event"] = Field(..., description="신호 유형")
    description: str = Field(..., description="설명")
    details: SignalDetails = Field(default_factory=SignalDetails)
    relevance: float = Field(0.0, ge=0.0, le=1.0, description="관련성 (0~1)")
    valid: bool = Field(True, description="유효 여부")
    reason: str = Field("", description="판단 근거")


class SituationJSON(BaseModel):
    """상황 JSON"""
    has_valid_signal: bool = Field(False, description="유효 신호 존재 여부")
    summary: str = Field("", description="상황 요약")
    signals: list[Signal] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list, description="출처")
    assumptions: list[str] = Field(default_factory=list, description="가정")
    contract_version: str = Field("situation.v1", description="계약 버전")


# ========== Resource Schema ==========

class PackageBudget(BaseModel):
    """패키지 예산"""
    cap: int = Field(0, description="상한")
    unit: str = Field("KRW", description="단위")
    tier: Literal["low", "med", "high"] = Field("low", description="등급")


class Package(BaseModel):
    """리소스 패키지"""
    id: str = Field(..., description="패키지 ID")
    version: str = Field("v1", description="버전")
    channel: str = Field(..., description="채널")
    budget: PackageBudget = Field(default_factory=PackageBudget)
    fit_score: float = Field(0.0, ge=0.0, le=1.0, description="적합도 (0~1)")


class ChecklistItem(BaseModel):
    """체크리스트 항목"""
    step: str = Field(..., description="단계")
    owner: str = Field(..., description="담당자")
    eta_min: int = Field(0, description="예상 소요 시간 (분)")


class EstimatedCosts(BaseModel):
    """예상 비용"""
    media_spend: int = Field(0, description="매체 비용")
    production_spend: int = Field(0, description="제작 비용")


class Execution(BaseModel):
    """실행 계획"""
    checklist: list[ChecklistItem] = Field(default_factory=list)
    assets_needed: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    templates: list[dict] = Field(default_factory=list)
    estimated_costs: EstimatedCosts = Field(default_factory=EstimatedCosts)


class KPIAlignment(BaseModel):
    """KPI 정렬"""
    primary: dict = Field(default_factory=dict)
    tracking: dict = Field(default_factory=dict)


class ResourceCard(BaseModel):
    """리소스 카드"""
    card_type: str = Field("resource_package")
    derived_from_card_id: Optional[str] = Field(None)
    offer_id: str = Field(...)
    
    title: str = Field(...)
    summary: str = Field(...)
    
    package: Package
    execution: Execution = Field(default_factory=Execution)
    kpi_alignment: KPIAlignment = Field(default_factory=KPIAlignment)
    
    constraints_applied: dict = Field(default_factory=dict)
    risks: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    references: list[dict] = Field(default_factory=list)
    citations: list[dict] = Field(default_factory=list)
    
    constraints_matched: bool = Field(True)
    contract_version: str = Field("resource.v1")


class ResourceJSON(BaseModel):
    """리소스 JSON"""
    resource_card: ResourceCard
    resource_refs: list[str] = Field(default_factory=list)


# ========== Evaluation Schema ==========

class CardCheck(BaseModel):
    """카드 검증"""
    card_idx: int = Field(..., description="카드 인덱스")
    constraint_fit: bool = Field(..., description="제약 부합 여부")
    evidence_match: bool = Field(..., description="근거 매칭 여부")
    risk_notes: list[str] = Field(default_factory=list, description="위험 노트")
    fix_suggestion: Optional[str] = Field(None, description="수정 제안")


class RecommendedAction(BaseModel):
    """권장 액션"""
    action: str = Field(..., description="액션")
    impact: str = Field(..., description="영향")


class EvaluationReport(BaseModel):
    """평가 리포트"""
    summary: str = Field(..., description="요약")
    severity: Literal["low", "medium", "high"] = Field("low", description="심각도")
    checks: list[CardCheck] = Field(default_factory=list)
    recommended_actions: list[RecommendedAction] = Field(default_factory=list)


# ========== Batch Evaluation ==========

class Scores(BaseModel):
    """점수"""
    constraint_fit: float = Field(0.0, ge=0.0, le=1.0)
    evidence_quality: float = Field(0.0, ge=0.0, le=1.0)
    feasibility: float = Field(0.0, ge=0.0, le=1.0)
    impact: float = Field(0.0, ge=0.0, le=1.0)


class RiskAssessment(BaseModel):
    """위험 평가"""
    overall_risk_level: Literal["low", "medium", "high"] = Field("low")
    total_risk_score: float = Field(0.0, ge=0.0, le=1.0)
    items: list[str] = Field(default_factory=list)


class DetailedFeedback(BaseModel):
    """상세 피드백"""
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    best_practices: list[str] = Field(default_factory=list)


class BatchEvaluationItem(BaseModel):
    """배치 평가 항목"""
    card_idx: int
    card_title: str
    overall_score: float = Field(0.0, ge=0.0, le=1.0)
    recommendation: Literal["approve", "changes_requested", "reject"] = Field("approve")
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    scores: Scores = Field(default_factory=Scores)
    risk_assessment: RiskAssessment = Field(default_factory=RiskAssessment)
    detailed_feedback: DetailedFeedback = Field(default_factory=DetailedFeedback)


class BatchEvaluationResult(BaseModel):
    """배치 평가 결과"""
    summary: str = Field(...)
    overall_quality: float = Field(0.0, ge=0.0, le=1.0)
    approved_count: int = Field(0)
    needs_changes_count: int = Field(0)
    rejected_count: int = Field(0)
    timestamp: str = Field(...)
    items: list[BatchEvaluationItem] = Field(default_factory=list)