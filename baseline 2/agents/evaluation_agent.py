"""
Evaluation Agent
전략 카드 평가 및 수정 권고
"""
from datetime import datetime
from loguru import logger

from contracts import EvaluationReport, CardCheck, RecommendedAction


def evaluation_agent_node(state):
    """
    평가 에이전트
    - 전략 카드 검증
    - 제약 조건 부합 확인
    - 근거 품질 체크
    - 수정 권고 생성
    """
    logger.info("Evaluation Agent: 시작")
    
    strategy_cards = state.get("strategy_cards", [])
    
    if not strategy_cards:
        logger.warning("평가할 전략 카드 없음")
        return {
            "logs": ["[WARNING] 전략 카드 없음"]
        }
    
    eval_report = _evaluate_strategy_cards(state)
    
    logger.info(f"Evaluation Agent: 완료 (심각도: {eval_report.severity})")
    
    return {
        "eval_report": eval_report.dict(),
        "logs": [f"[{datetime.now()}] evaluation_agent: 평가 완료 (심각도: {eval_report.severity})"]
    }


def _evaluate_strategy_cards(state) -> EvaluationReport:
    """
    전략 카드 평가
    """
    checks = []
    strategy_cards = state.get("strategy_cards", [])
    
    for idx, card in enumerate(strategy_cards):
        check = _evaluate_single_card(idx, card, state)
        checks.append(check)
    
    # 전체 심각도 판단
    severity = _determine_severity(checks)
    
    # 권장 액션
    actions = _generate_recommended_actions(checks)
    
    # 요약
    total = len(checks)
    ok_count = sum(1 for c in checks if c.constraint_fit and c.evidence_match)
    summary = f"카드 {total}건 중 {ok_count}건 적합, {total - ok_count}건 수정 권고"
    
    return EvaluationReport(
        summary=summary,
        severity=severity,
        checks=checks,
        recommended_actions=actions
    )


def _evaluate_single_card(idx: int, card: dict, state) -> CardCheck:
    """
    개별 카드 평가
    """
    risk_notes = []
    fix_suggestion = None
    
    constraints = state.get("constraints", {})
    context_json = state.get("context_json", {})
    
    # 1. 제약 조건 검증
    constraint_fit = _check_constraints(card, constraints, risk_notes)
    
    # 2. 근거 매칭 검증
    evidence_match = _check_evidence(card, context_json, risk_notes)
    
    # 3. 수정 제안 생성
    if not constraint_fit or risk_notes:
        fix_suggestion = _generate_fix_suggestion(card, risk_notes)
    
    return CardCheck(
        card_idx=idx,
        constraint_fit=constraint_fit,
        evidence_match=evidence_match,
        risk_notes=risk_notes,
        fix_suggestion=fix_suggestion
    )


def _check_constraints(card: dict, constraints: dict, risk_notes: list) -> bool:
    """제약 조건 검증"""
    budget_krw = constraints.get("budget_krw", 0)
    card_budget = card.get("budget", {}).get("cap", 0)
    
    # 예산 초과 체크
    if card_budget > budget_krw:
        overage_pct = ((card_budget - budget_krw) / budget_krw) * 100
        risk_notes.append(f"예산 초과 {overage_pct:.0f}%")
        return False
    
    # 채널 제약 체크
    preferred_channels = constraints.get("preferred_channels", [])
    card_channels = card.get("channel_hints", [])
    
    if preferred_channels and not any(ch in preferred_channels for ch in card_channels):
        risk_notes.append(f"선호 채널 불일치")
        return False
    
    return True


def _check_evidence(card: dict, context_json: dict, risk_notes: list) -> bool:
    """근거 매칭 검증"""
    if not context_json:
        risk_notes.append("컨텍스트 데이터 없음")
        return False
    
    # 참조 검증
    references = card.get("references", [])
    if not references:
        risk_notes.append("근거 참조 없음")
        return False
    
    # 근거 칩 검증
    evidence_chips = card.get("evidence_chips", [])
    if len(evidence_chips) < 2:
        risk_notes.append("근거 칩 부족 (최소 2개 권장)")
        return False
    
    return True


def _generate_fix_suggestion(card: dict, risk_notes: list) -> str:
    """수정 제안 생성"""
    suggestions = []
    
    for note in risk_notes:
        if "예산 초과" in note:
            suggestions.append("채널 축소 또는 기간 단축")
        elif "채널 불일치" in note:
            suggestions.append("선호 채널로 변경")
        elif "근거 칩 부족" in note:
            suggestions.append("컨텍스트 데이터 기반 근거 추가")
    
    return ", ".join(suggestions) if suggestions else "세부 검토 필요"


def _determine_severity(checks: list[CardCheck]) -> str:
    """전체 심각도 판단"""
    total = len(checks)
    issues = sum(1 for c in checks if not c.constraint_fit or c.risk_notes)
    
    if issues == 0:
        return "low"
    elif issues / total < 0.5:
        return "medium"
    else:
        return "high"


def _generate_recommended_actions(checks: list[CardCheck]) -> list[RecommendedAction]:
    """권장 액션 생성"""
    actions = []
    
    for check in checks:
        if check.fix_suggestion:
            actions.append(RecommendedAction(
                action=f"card[{check.card_idx}] 수정 적용",
                impact=check.fix_suggestion
            ))
    
    # 공통 액션
    actions.append(RecommendedAction(
        action="2주간 A/B 로그 수집",
        impact="사후 검증 가능"
    ))
    
    return actions