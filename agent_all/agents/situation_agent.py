# agents/situation_agent.py
"""
상황 정보 수집 Agent
- Tavily Events (주변 행사 정보)
- Weather Signals (날씨 정보)
병렬로 호출하여 Situation JSON 생성
"""

from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
from pathlib import Path

# tools 임포트
sys.path.append(str(Path(__file__).parent.parent))

# 개별 import로 변경
HAS_EVENTS_TOOL = False
HAS_WEATHER_TOOL = False

try:
    from tools.tavily_events import get_tool as get_events_tool
    HAS_EVENTS_TOOL = True
except ImportError as e:
    print(f"⚠️  Tavily Events 도구 미설치: {e}")
    get_events_tool = None

try:
    from tools.weather_signals import detect_weather_signals
    HAS_WEATHER_TOOL = True
except ImportError as e:
    print(f"⚠️  Weather Signals 도구 미설치: {e}")
    detect_weather_signals = None

HAS_SITUATION_TOOLS = HAS_EVENTS_TOOL or HAS_WEATHER_TOOL

def default_market_locator(mid: str):
    """✅ 실제 데이터 기반 상권 위치 매핑 (40+ 상권)"""
    try:
        from agents.market_coordinates import get_coordinates
        return get_coordinates(mid)
    except ImportError:
        # 폴백: 기본 좌표
        basic_map = {
            "강남": (37.4979, 127.0276, "강남"),
            "홍대": (37.5563, 126.9237, "홍대"),
            "성수동": (37.5446, 127.0559, "성수동"),
        }
        if mid in basic_map:
            return basic_map[mid]
        # 서울시청 기본값
        return (37.5665, 126.9780, mid)

def _call_events(market_id: str, start: str, end: str, user_query: Optional[str]) -> Dict[str, Any]:
    """Tavily 이벤트 호출"""
    if not HAS_EVENTS_TOOL or not get_events_tool:
        return {
            "has_valid_signal": False,
            "summary": "이벤트 도구 미설치",
            "signals": [],
            "citations": [],
            "assumptions": []
        }

    # TAVILY_EVENTS_TOOL 동적 생성
    TAVILY_EVENTS_TOOL = get_events_tool(market_locator=default_market_locator)

    try:
        return TAVILY_EVENTS_TOOL.invoke({
            "market_id": market_id,
            "start": start,
            "end": end,
            "user_query": user_query,
        })
    except Exception as e:
        return {
            "has_valid_signal": False,
            "summary": f"이벤트 수집 실패: {e}",
            "signals": [],
            "citations": [],
            "assumptions": []
        }

def _call_weather(user_query: Optional[str], store: Dict[str, Any], period: Dict[str, str]) -> Dict[str, Any]:
    """Open-Meteo 날씨 호출"""
    if not HAS_WEATHER_TOOL or not detect_weather_signals:
        return {
            "has_valid_signal": False,
            "summary": "날씨 도구 미설치",
            "signals": [],
            "citations": [],
            "assumptions": []
        }

    try:
        return detect_weather_signals({
            "user_query": user_query,
            "store": store,
            "period": period,
        }, market_locator=default_market_locator)
    except Exception as e:
        return {
            "has_valid_signal": False,
            "summary": f"날씨 수집 실패: {e}",
            "signals": [],
            "citations": [],
            "assumptions": []
        }

def collect_situation_info(
    market_id: str,
    period_start: str,
    period_end: str,
    user_query: Optional[str] = None,
    collect_mode: str = "weather_only"  # "weather_only", "event_only" (both 제거)
) -> Dict[str, Any]:
    """
    상황 정보 수집 (사용자 선택 모드 기반)

    Args:
        market_id: 상권 ID (e.g., "M45", "강남")
        period_start: 시작일 (YYYY-MM-DD)
        period_end: 종료일 (YYYY-MM-DD)
        user_query: 사용자 쿼리 (선택)
        collect_mode: "weather_only" 또는 "event_only" (사용자가 Streamlit에서 선택)

    Returns:
        {
            "has_valid_signal": bool,
            "summary": str,
            "signals": List[Dict],
            "citations": List[str],
            "assumptions": List[str],
            "event_count": int,
            "weather_count": int
        }
    """

    if not (market_id and period_start and period_end):
        return {
            "has_valid_signal": False,
            "summary": "입력 누락: market_id/start/end 필요",
            "signals": [],
            "citations": [],
            "assumptions": [],
            "event_count": 0,
            "weather_count": 0
        }

    # 유효한 모드 검증
    if collect_mode not in ["weather_only", "event_only"]:
        print(f"   ⚠️ 잘못된 collect_mode: {collect_mode}, 기본값 weather_only 사용")
        collect_mode = "weather_only"

    # 선택된 모드 로그
    mode_emoji = "🌤️" if collect_mode == "weather_only" else "📅"
    mode_name = "날씨 전용" if collect_mode == "weather_only" else "행사 전용"
    print(f"   {mode_emoji} 수집 모드: {mode_name}")

    store = {"market_id": market_id}
    period = {"start": period_start, "end": period_end}

    # 단일 모드 실행 (병렬 불필요)
    events = None
    wx = None

    if collect_mode == "event_only":
        try:
            events = _call_events(market_id, period_start, period_end, user_query)
        except Exception as e:
            events = {
                "has_valid_signal": False,
                "summary": f"이벤트 수집 실패({e})",
                "signals": [],
                "citations": [],
                "assumptions": []
            }

    elif collect_mode == "weather_only":
        try:
            wx = _call_weather(user_query, store, period)
        except Exception as e:
            wx = {
                "has_valid_signal": False,
                "summary": f"날씨 수집 실패({e})",
                "signals": [],
                "citations": [],
                "assumptions": []
            }

    # 안전 가드
    events = events or {"signals": [], "citations": [], "assumptions": [], "summary": None}
    wx = wx or {"signals": [], "citations": [], "assumptions": [], "summary": None}

    # 병합
    ev_sig = events.get("signals") or []
    wx_sig = wx.get("signals") or []
    signals = ev_sig + wx_sig
    has_valid = bool(signals)

    parts = []
    if events.get("summary"):
        parts.append(f"📅 이벤트: {events['summary']}")
    if wx.get("summary"):
        parts.append(f"🌤️ 날씨: {wx['summary']}")
    summary = " | ".join(parts) if parts else "신호 없음"

    merged = {
        "has_valid_signal": has_valid,
        "summary": summary,
        "signals": signals,
        "citations": (events.get("citations") or []) + (wx.get("citations") or []),
        "assumptions": (events.get("assumptions") or []) + (wx.get("assumptions") or []),
        "event_count": len(ev_sig),
        "weather_count": len(wx_sig),
    }

    return merged
