"""
Situation Agent
외부 상황 인식 (날씨, 행사 등)
"""
from datetime import datetime
from loguru import logger

from contracts import SituationJSON, Signal, SignalDetails


def situation_agent_node(state):
    """
    상황 에이전트
    - 날씨 데이터 조회
    - 행사 정보 검색
    - 신호 유효성 판단
    """
    logger.info("Situation Agent: 시작")
    state.logs.append(f"[{datetime.now()}] situation_agent: 상황 분석 시작")
    
    # 의도 분석: 상황 관련 키워드 탐지
    if not _need_situation_analysis(state.user_query):
        logger.info("상황 분석 불필요")
        state.situation_json = SituationJSON(
            has_valid_signal=False,
            summary="상황 신호 없음",
            signals=[],
            contract_version="situation.v1"
        ).dict()
        state.logs.append(f"[{datetime.now()}] situation_agent: 스킵 (관련 키워드 없음)")
        return state
    
    # 상황 분석 실행
    situation_json = _analyze_situation(state)
    
    state.situation_json = situation_json.dict()
    state.logs.append(f"[{datetime.now()}] situation_agent: 완료 (신호: {len(situation_json.signals)}개)")
    
    logger.info(f"Situation Agent: 완료 (신호: {len(situation_json.signals)}개)")
    
    return state


def _need_situation_analysis(user_query: str) -> bool:
    """상황 분석 필요 여부 판단"""
    keywords = ["날씨", "비", "행사", "이벤트", "축제", "공휴일"]
    return any(kw in user_query for kw in keywords)


def _analyze_situation(state) -> SituationJSON:
    """
    상황 분석 실행
    - 날씨 API 호출
    - 행사 웹 검색
    """
    signals = []
    
    # 1. 날씨 신호 (예시)
    weather_signal = _check_weather(state)
    if weather_signal:
        signals.append(weather_signal)
    
    # 2. 행사 신호 (예시)
    event_signal = _check_events(state)
    if event_signal:
        signals.append(event_signal)
    
    # 요약 생성
    summary = _generate_summary(signals)
    
    return SituationJSON(
        has_valid_signal=len(signals) > 0,
        summary=summary,
        signals=signals,
        citations=["기상청 API (예시)", "지역 행사 캘린더 (예시)"],
        assumptions=["우천 시 내점↓ / 배달↑ 가정"],
        contract_version="situation.v1"
    )


def _check_weather(state) -> Signal | None:
    """
    날씨 데이터 조회
    실제로는 기상청 API 호출
    """
    # 더미 데이터
    pop = 0.7  # 강수확률 70%
    rain_mm = 18.0
    
    if pop >= 0.6:
        return Signal(
            signal_id=f"WX-{datetime.now().strftime('%Y%m%d')}",
            signal_type="weather",
            description=f"강수확률 {pop*100:.0f}%, 예보 강수량 {rain_mm}mm",
            details=SignalDetails(pop=pop, rain_mm=rain_mm),
            relevance=0.82,
            valid=True,
            reason="POP≥60% 충족"
        )
    
    return None


def _check_events(state) -> Signal | None:
    """
    행사 정보 검색
    실제로는 Tavily API 또는 행사 캘린더 API 호출
    """
    # 더미 데이터
    # 실제로는 웹 검색 필요
    
    return Signal(
        signal_id=f"EV-{datetime.now().strftime('%Y%m%d')}",
        signal_type="event",
        description="한강 야시장 (예상 8천명)",
        details=SignalDetails(distance_km=1.2, expected_visitors=8000),
        relevance=0.75,
        valid=True,
        reason="도보 15분 이내 대규모 행사"
    )


def _generate_summary(signals: list[Signal]) -> str:
    """신호 요약 생성"""
    if not signals:
        return "특이 상황 없음"
    
    weather_signals = [s for s in signals if s.signal_type == "weather"]
    event_signals = [s for s in signals if s.signal_type == "event"]
    
    parts = []
    if weather_signals:
        parts.append(f"우천(POP≥60%)")
    if event_signals:
        parts.append(f"대규모 행사")
    
    return " + ".join(parts) + " → 유동 흐름 변화 예상"