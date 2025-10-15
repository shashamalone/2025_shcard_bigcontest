# agents/situation_agent.py
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tools.tavily_events import get_tool as get_events_tool
from tools.weather_signals import detect_weather_signals

def default_market_locator(mid: str):
    # DB/지오코더 있으면 교체
    return (37.5446, 127.0559, "성수동")

# LangChain StructuredTool 준비(모듈 로드시 1회)
TAVILY_EVENTS_TOOL = get_events_tool(market_locator=default_market_locator)

def _call_events(market_id: str, start: str, end: str, user_query: Optional[str]) -> Dict[str, Any]:
    """Tavily 이벤트 호출 (예외는 상위에서 처리)"""
    return TAVILY_EVENTS_TOOL.invoke({
        "market_id": market_id,
        "start": start,
        "end": end,
        "user_query": user_query,
    })

def _call_weather(user_query: Optional[str], store: Dict[str, Any], period: Dict[str, str]) -> Dict[str, Any]:
    """Open-Meteo 날씨 호출 (예외는 상위에서 처리)"""
    return detect_weather_signals({
        "user_query": user_query,
        "store": store,
        "period": period,
    })

def situation_agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """단일 노드 내에서 이벤트/날씨를 병렬 호출하고 Situation JSON으로 병합."""
    user_query = state.get("user_query")
    store = state.get("store") or {}
    period = state.get("period") or {}

    mid, start, end = store.get("market_id"), period.get("start"), period.get("end")
    if not (mid and start and end):
        merged = {
            "has_valid_signal": False,
            "summary": "입력 누락: market_id/start/end 필요",
            "signals": [],
            "citations": [],
            "assumptions": [],
            "contract_version": "situation.v1",
        }
        return {"situation": merged, "log": (state.get("log") or []) + ["[situation] 입력 누락"]}

    # --- 병렬 실행 영역 ---
    events, wx = None, None
    logs = state.get("log") or []

    with ThreadPoolExecutor(max_workers=2) as ex:
        futures = {
            ex.submit(_call_events, mid, start, end, user_query): "events",
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
                    "assumptions": [],
                    "contract_version": "situation.v1",
                }
                logs.append(f"[situation] {tag} error: {e}")

            if tag == "events":
                events = res
            else:
                wx = res

    # 안전 가드
    events = events or {"signals": [], "citations": [], "assumptions": [], "summary": None}
    wx     = wx     or {"signals": [], "citations": [], "assumptions": [], "summary": None}

    # --- 병합 ---
    ev_sig = events.get("signals") or []
    wx_sig = wx.get("signals") or []
    signals = ev_sig + wx_sig
    has_valid = bool(signals)

    parts = []
    if events.get("summary"): parts.append(events["summary"])
    if wx.get("summary"): parts.append(wx["summary"])
    summary = " / ".join(parts) if parts else "신호 없음"

    merged = {
        "has_valid_signal": has_valid,
        "summary": summary,
        "signals": signals,
        "citations": (events.get("citations") or []) + (wx.get("citations") or []),
        "assumptions": (events.get("assumptions") or []) + (wx.get("assumptions") or []),
        "contract_version": "situation.v1",
    }

    logs.append(f"[situation] events={len(ev_sig)} weather={len(wx_sig)} (parallel)")
    return {"situation": merged, "log": logs}