# tools/weather_signals.py 
from __future__ import annotations
import requests
from typing import Dict, Any, Tuple, Optional, Callable

MARKET_ALIAS = {"M45": (37.5446, 127.0559, "성수동")}
RAIN_MM = 10.0
POP_HOURS = 6
HEAT_1D, HEAT_2D = 33.0, 31.0
COLD_1D, COLD_2D = -12.0, -10.0

def _locate(mid: str, locator: Optional[Callable[[str], Tuple[float,float,str]]]):
    if locator: return locator(mid)
    if mid in MARKET_ALIAS: return MARKET_ALIAS[mid]
    raise ValueError(f"market_id '{mid}' 위치 미정")

def _om(lat: float, lon: float, start: str, end: str) -> Dict[str, Any]:
    r = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": lat, "longitude": lon, "timezone": "Asia/Seoul",
        "hourly": "precipitation_probability,precipitation,temperature_2m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "start_date": start, "end_date": end
    }, timeout=30)
    r.raise_for_status()
    return r.json()

def detect_weather_signals(input_json: Dict[str, Any],
                           market_locator: Optional[Callable[[str], Tuple[float,float,str]]] = None) -> Dict[str, Any]:
    store, period = input_json.get("store", {}), input_json.get("period", {})
    mid, start, end = store.get("market_id"), period.get("start"), period.get("end")
    if not (mid and start and end):
        return {"has_valid_signal": False, "summary": "입력 누락", "signals": [], "citations": [], "assumptions": [], "contract_version": "situation.v1"}

    lat, lon, area = _locate(mid, market_locator)
    data = _om(lat, lon, start, end)
    hourly, daily = data.get("hourly", {}), data.get("daily", {})

    pop = [p for p in (hourly.get("precipitation_probability") or []) if p is not None]
    rain = [x for x in (hourly.get("precipitation") or []) if x is not None]
    pop_mean = round(sum(pop)/len(pop), 2) if pop else None
    pop_max  = max(pop) if pop else None
    rain_sum = round(sum(rain), 2) if rain else 0.0
    pop60h   = sum(1 for p in pop if p >= 60)

    tmax = daily.get("temperature_2m_max") or []
    tmin = daily.get("temperature_2m_min") or []
    tmax_overall = max(tmax) if tmax else None
    tmin_overall = min(tmin) if tmin else None

    heat = (tmax_overall is not None) and (tmax_overall >= HEAT_1D or sum(1 for v in tmax if v >= HEAT_2D) >= 2)
    cold = (tmin_overall is not None) and (tmin_overall <= COLD_1D or sum(1 for v in tmin if v <= COLD_2D) >= 2)
    rain_sig = (rain_sum >= RAIN_MM) or (pop60h >= POP_HOURS)

    signals = []
    if rain_sig:
        desc = "우천 신호("
        if pop_mean is not None: desc += f"평균POP {pop_mean}%, "
        if pop_max  is not None: desc += f"최대POP {pop_max}%, "
        desc += f"강수합 {rain_sum}mm)"
        signals.append({
            "signal_id": f"WX-{start.replace('-','')}",
            "signal_type": "weather",
            "description": desc,
            "details": {"pop_mean": pop_mean, "pop_max": pop_max, "rain_mm": rain_sum, "area_name": area, "period": {"start": start, "end": end}},
            "relevance": 0.70, "valid": True, "reason": "강수합 또는 POP≥60% 시간 누적 충족"
        })
    if heat:
        signals.append({
            "signal_id": f"WXH-{start.replace('-','')}",
            "signal_type": "weather",
            "description": f"폭염 신호(Tmax={tmax_overall}°C)",
            "details": {"tmax_overall": tmax_overall, "area_name": area, "period": {"start": start, "end": end}},
            "relevance": 0.55, "valid": True, "reason": "최고기온 임계 충족"
        })
    if cold:
        signals.append({
            "signal_id": f"WXC-{start.replace('-','')}",
            "signal_type": "weather",
            "description": f"한파 신호(Tmin={tmin_overall}°C)",
            "details": {"tmin_overall": tmin_overall, "area_name": area, "period": {"start": start, "end": end}},
            "relevance": 0.55, "valid": True, "reason": "최저기온 임계 충족"
        })

    kinds = []
    if any(s["signal_id"].startswith("WX-") for s in signals):  kinds.append("우천")
    if any(s["signal_id"].startswith("WXH-") for s in signals): kinds.append("폭염")
    if any(s["signal_id"].startswith("WXC-") for s in signals): kinds.append("한파")
    summary = f"{area} {start}~{end}: " + ("/".join(kinds) if kinds else "특이 신호 없음")

    return {
        "has_valid_signal": bool(signals),
        "summary": summary,
        "signals": signals,
        "citations": ["Open-Meteo API"],
        "assumptions": ["POP≥60% 시간 누적 또는 강수합≥10mm이면 우천 영향 가정", "폭염/한파 임계는 상단 상수 사용"],
        "contract_version": "situation.v1",
    }