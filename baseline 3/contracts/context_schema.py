"""
Context Schema
점포/상권 컨텍스트 데이터 표준 스키마
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class Store(BaseModel):
    """점포 기본 정보"""
    id: str = Field(..., description="점포 ID")
    name: str = Field(..., description="점포명")
    industry_code: str = Field(..., description="업종 코드")
    market_id: str = Field(..., description="상권 ID")


class Period(BaseModel):
    """분석 기간"""
    start: str = Field(..., description="시작일 (YYYY-MM-DD)")
    end: str = Field(..., description="종료일 (YYYY-MM-DD)")


class KPI(BaseModel):
    """핵심 KPI"""
    sales_sum: float = Field(0.0, description="총 매출")
    visits_sum: int = Field(0, description="총 방문 수")
    aov: float = Field(0.0, description="객단가")
    repeat_rate: float = Field(0.0, description="재방문율")


class DerivedMetrics(BaseModel):
    """파생 지표"""
    same_industry_sales_ratio: float = Field(0.0, description="업종평균대비 매출비")
    sales_volatility_4w: float = Field(0.0, description="매출 변동성(4주)")
    lunch_share: float = Field(0.0, description="런치 비중")
    weekend_share: float = Field(0.0, description="주말 비중")
    afternoon_share: float = Field(0.0, description="오후 비중")
    comp_intensity: float = Field(0.0, description="경쟁 강도")
    market_churn_rate_4w: float = Field(0.0, description="상권 churn율(4주)")
    foot_traffic_proxy: float = Field(0.0, description="유동인구 지수")
    aov_gap_pct: float = Field(0.0, description="객단가 편차(%)")


class TimeSeries(BaseModel):
    """시계열 데이터"""
    daily_sales: list[float] = Field(default_factory=list, description="일별 매출")
    daily_visits: list[int] = Field(default_factory=list, description="일별 방문")


class Metrics(BaseModel):
    """지표 전체"""
    kpi: KPI = Field(default_factory=KPI)
    derived: DerivedMetrics = Field(default_factory=DerivedMetrics)
    timeseries: TimeSeries = Field(default_factory=TimeSeries)


class FootTrafficProxy(BaseModel):
    """유동인구 상세"""
    index: float = Field(0.0, description="유동 지수")
    trend_4w: Literal["up", "flat", "down"] = Field("flat", description="4주 추세")
    zscore: float = Field(0.0, description="Z-score")


class Market(BaseModel):
    """상권 정보"""
    market_id: str = Field(..., description="상권 ID")
    same_industry_store_cnt: int = Field(0, description="동일 업종 점포 수")
    total_store_cnt: int = Field(0, description="전체 점포 수")
    new_open_cnt_4w: int = Field(0, description="4주 신규 개점 수")
    close_cnt_4w: int = Field(0, description="4주 폐점 수")
    avg_sales_industry: float = Field(0.0, description="업종 평균 매출")
    foot_traffic_proxy: FootTrafficProxy = Field(default_factory=FootTrafficProxy)
    rent_level: float = Field(0.0, description="임대료 수준 (0~1)")
    vacancy_rate: float = Field(0.0, description="공실률")


class Risk(BaseModel):
    """위험 평가"""
    score: float = Field(0.0, ge=0.0, le=1.0, description="위험 점수 (0~1)")
    typology: Optional[str] = Field(None, description="위험 유형")
    reasons: list[str] = Field(default_factory=list, description="위험 요인")
    evidence_chips: list[str] = Field(default_factory=list, description="근거 칩")


class SessionConstraints(BaseModel):
    """세션 제약 조건"""
    budget_krw: int = Field(0, description="예산 (원)")
    budget_tier: Literal["low", "med", "high"] = Field("low", description="예산 등급")
    preferred_channels: list[str] = Field(default_factory=list, description="선호 채널")
    forbidden_channels: list[str] = Field(default_factory=list, description="금지 채널")
    brand_tone: str = Field("friendly", description="브랜드 톤")


class Provenance(BaseModel):
    """데이터 출처"""
    as_of: str = Field(..., description="기준일 (YYYY-MM-DD)")
    sources: list[str] = Field(default_factory=list, description="데이터 소스")
    version: str = Field("ctx.v1", description="스키마 버전")


class ContextJSON(BaseModel):
    """Context 전체 스키마"""
    store: Store
    period: Period
    metrics: Metrics = Field(default_factory=Metrics)
    market: Market
    risk: Risk = Field(default_factory=Risk)
    session_constraints: SessionConstraints = Field(default_factory=SessionConstraints)
    provenance: Provenance