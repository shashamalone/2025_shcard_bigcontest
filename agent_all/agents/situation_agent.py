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

try:
    from tools.tavily_events import get_tool as get_events_tool
    from tools.weather_signals import detect_weather_signals
    HAS_SITUATION_TOOLS = True
except ImportError:
    print("⚠️  상황 도구(tavily_events, weather_signals) 없음")
    HAS_SITUATION_TOOLS = False

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

# LangChain StructuredTool 준비
if HAS_SITUATION_TOOLS:
    TAVILY_EVENTS_TOOL = get_events_tool(market_locator=default_market_locator)
else:
    TAVILY_EVENTS_TOOL = None

def _call_events(market_id: str, start: str, end: str, user_query: Optional[str]) -> Dict[str, Any]:
    """Tavily 이벤트 호출"""
    if not HAS_SITUATION_TOOLS or not TAVILY_EVENTS_TOOL:
        return {
            "has_valid_signal": False,
            "summary": "도구 미설치",
            "signals": [],
            "citations": [],
            "assumptions": []
        }

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
    if not HAS_SITUATION_TOOLS:
        return {
            "has_valid_signal": False,
            "summary": "도구 미설치",
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
    user_query: Optional[str] = None
) -> Dict[str, Any]:
    """
    상황 정보 수집 (병렬)

    Args:
        market_id: 상권 ID (e.g., "M45", "강남")
        period_start: 시작일 (YYYY-MM-DD)
        period_end: 종료일 (YYYY-MM-DD)
        user_query: 사용자 쿼리 (선택)

    Returns:
        {
            "has_valid_signal": bool,
            "summary": str,
            "signals": List[Dict],
            "citations": List[str],
            "assumptions": List[str]
        }
    """

    if not (market_id and period_start and period_end):
        return {
            "has_valid_signal": False,
            "summary": "입력 누락: market_id/start/end 필요",
            "signals": [],
            "citations": [],
            "assumptions": []
        }

    store = {"market_id": market_id}
    period = {"start": period_start, "end": period_end}

    # 병렬 실행
    events, wx = None, None

    with ThreadPoolExecutor(max_workers=2) as ex:
        futures = {
            ex.submit(_call_events, market_id, period_start, period_end, user_query): "events",
            ex.submit(_call_weather, user_query, store, period): "weather",
        }

        for fut in as_completed(futures):
            tag = futures[fut]
            try:
                res = fut.result()
            except Exception as e:
                res = {
                    "has_valid_signal": False,
                    "summary": f"{tag} 수집 실패({e})",
                    "signals": [],
                    "citations": [],
                    "assumptions": []
                }

            if tag == "events":
                events = res
            else:
                wx = res

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
