"""
Contracts Module
모든 JSON 스키마 및 계약 정의
"""
from .intents import (
    Intent,
    IntentType,
    FilterParams,
    StrategyQueryParams,
    ComparisonQueryParams,
    INTENT_KEYWORDS,
    MIN_CONFIDENCE
)
from .context_schema import (
    ContextJSON,
    Store,
    Period,
    Metrics,
    Market,
    Risk,
    SessionConstraints,
    KPI,
    DerivedMetrics,
    TimeSeries,
    FootTrafficProxy,
    Provenance
)
from .card_schema import (
    StrategyCard,
    SituationJSON,
    ResourceJSON,
    EvaluationReport,
    BatchEvaluationResult,
    InputsUsed,
    Timeline,
    Budget,
    KPITargets,
    KPITarget,
    Tracking,
    ConstraintsApplied,
    Reference,
    Signal,
    SignalDetails,
    ResourceCard,
    Package,
    PackageBudget,
    Execution,
    ChecklistItem,
    EstimatedCosts,
    KPIAlignment,
    CardCheck,
    RecommendedAction,
    Scores,
    RiskAssessment,
    DetailedFeedback,
    BatchEvaluationItem
)

__all__ = [
    # Intents
    "Intent",
    "IntentType",
    "FilterParams",
    "StrategyQueryParams",
    "ComparisonQueryParams",
    "INTENT_KEYWORDS",
    "MIN_CONFIDENCE",
    
    # Context Schema
    "ContextJSON",
    "Store",
    "Period",
    "Metrics",
    "Market",
    "Risk",
    "SessionConstraints",
    "KPI",
    "DerivedMetrics",
    "TimeSeries",
    "FootTrafficProxy",
    "Provenance",
    
    # Card Schema - Strategy
    "StrategyCard",
    "InputsUsed",
    "Timeline",
    "Budget",
    "KPITargets",
    "KPITarget",
    "Tracking",
    "ConstraintsApplied",
    "Reference",
    
    # Card Schema - Situation
    "SituationJSON",
    "Signal",
    "SignalDetails",
    
    # Card Schema - Resource
    "ResourceJSON",
    "ResourceCard",
    "Package",
    "PackageBudget",
    "Execution",
    "ChecklistItem",
    "EstimatedCosts",
    "KPIAlignment",
    
    # Card Schema - Evaluation
    "EvaluationReport",
    "CardCheck",
    "RecommendedAction",
    "BatchEvaluationResult",
    "Scores",
    "RiskAssessment",
    "DetailedFeedback",
    "BatchEvaluationItem"
]