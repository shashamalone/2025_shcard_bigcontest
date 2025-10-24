"""
Intent Detection Schema
사용자 의도 분류 및 파라미터 추출 정의
"""
from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field


class IntentType(str, Enum):
    """의도 유형"""
    STRATEGY = "strategy"
    COMPARISON = "comparison"
    UNKNOWN = "unknown"


class FilterParams(BaseModel):
    """전역 필터 파라미터"""
    store_id: Optional[str] = Field(None, description="점포 ID")
    area_id: Optional[str] = Field(None, description="상권 ID")
    start_date: Optional[str] = Field(None, description="시작일 (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="종료일 (YYYY-MM-DD)")
    budget_krw: Optional[int] = Field(None, description="예산 (원)")
    primary_channel: Optional[str] = Field(None, description="주 채널")


class StrategyQueryParams(BaseModel):
    """전략 쿼리 파라미터"""
    target_kpi: Optional[str] = Field(None, description="목표 KPI (trans, sales, retention)")
    focus_area: list[str] = Field(default_factory=list, description="집중 영역 (평일, 런치 등)")
    risk_tolerance: Literal["low", "medium", "high"] = Field("medium", description="위험 선호도")


class ComparisonQueryParams(BaseModel):
    """비교 쿼리 파라미터"""
    compare_scope: Literal["nearby", "industry", "custom"] = Field("nearby", description="비교 범위")
    distance_km: Optional[float] = Field(None, description="반경 (km)")
    percentile: list[int] = Field(default_factory=lambda: [25, 50, 75], description="백분위")


class Intent(BaseModel):
    """사용자 의도 스키마"""
    intent_type: IntentType = Field(IntentType.STRATEGY, description="의도 유형")
    user_query: str = Field(..., description="원본 사용자 질의")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="확신도 (0~1)")
    
    filter_params: FilterParams = Field(default_factory=FilterParams, description="필터 파라미터")
    strategy_query_params: Optional[StrategyQueryParams] = Field(None, description="전략 파라미터")
    comparison_query_params: Optional[ComparisonQueryParams] = Field(None, description="비교 파라미터")


# Intent Detection Rules
INTENT_KEYWORDS = {
    "strategy": [
        "전략", "프로모션", "쿠폰", "광고", "유입", "재방문", 
        "객단가", "런치", "평일", "캠페인", "마케팅"
    ],
    "comparison": [
        "비교", "인근", "동종", "백분위", "상위", "순위"
    ]
}

# Confidence Threshold
MIN_CONFIDENCE = 0.55
