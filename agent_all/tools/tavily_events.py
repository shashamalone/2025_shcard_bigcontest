# tools/tavily_events.py 
from __future__ import annotations
import os, re, logging, datetime as dt
from typing import Dict, Any, List, Tuple, Optional, Callable
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

# ── ENV & Tool ──────────────────────────────────────────────────────────────
load_dotenv()
assert os.getenv("TAVILY_API_KEY"), "TAVILY_API_KEY가 .env에 없습니다!"
# (선택) 다른 곳에서 쓸 수 있으므로 강제 미검증
# os.getenv("KCISA_SERVICE_KEY")

# ── 로거(에러/경고 가독성) ─────────────────────────────────────────────────
LOGGER = logging.getLogger("tavily_events")
if not LOGGER.handlers:
    # 환경변수 TAVILY_EVENTS_LOG=DEBUG/INFO/WARNING 로 조절 가능 (기본 WARNING)
    logging.basicConfig(level=os.getenv("TAVILY_EVENTS_LOG", "WARNING").upper(), format="%(levelname)s: %(message)s")

_tavily = TavilySearchResults(max_results=5, include_answer=True, include_raw_content=False)

# ── 최소 지역 별칭(없으면 market_locator로 대체) ─────────────────────────────
MARKET_ALIAS: Dict[str, Tuple[float, float, str]] = {
    "M45": (37.5446, 127.0559, "성수동"),
}

def _area_name(market_id: str, market_locator: Optional[Callable[[str], Tuple[float,float,str]]]) -> str:
    if market_locator:
        return market_locator(market_id)[2]
    if market_id in MARKET_ALIAS:
        return MARKET_ALIAS[market_id][2]
    raise ValueError(f"[events] market_id '{market_id}' 지역명 매핑 실패")

def _queries(area: str, start: str, end: str, user_query: Optional[str]) -> List[str]:
    s, e = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    month = f"{s.year} {s.month}월"; week = f"{s:%Y-%m-%d}~{e:%Y-%m-%d}"
    base = [
        f"{area} 팝업스토어 {month}",
        f"{area} 행사 {month}",
        f"{area} 이벤트 {week}",
        f"{area} 전시 공연 일정 {month}",
    ]
    return ([f"{area} {user_query}"] if user_query else []) + base

def _visitors(text: str) -> Optional[int]:
    if not text: return None
    m = re.search(r"(\d+)\s*만\s*명", text)   # 5만명
    if m: return int(m.group(1)) * 10000
    m = re.search(r"(\d+)\s*천\s*명", text)   # 8천명
    if m: return int(m.group(1)) * 1000
    m = re.search(r"(\d{3,})\s*명", text)     # 8000명
    if m: return int(m.group(1))
    return None

# ── NEW: 기간(월) 관련 가중치(간단 가점) ─────────────────────────────────────
def _month_bias(text: str, y: int, m: int) -> float:
    """제목/스니펫에 'YYYY'와 'M월'이 동시 등장하면 +0.1 가점."""
    if not text:
        return 0.0
    try:
        return 0.1 if (str(y) in text and f"{m}월" in text) else 0.0
    except Exception:
        return 0.0

# ── Core: 입력(JSON 계약) → Situation JSON(event signals) ──────────────────
def search_event_signals(
    input_json: Dict[str, Any],
    market_locator: Optional[Callable[[str], Tuple[float, float, str]]] = None,
    tavily: Optional[TavilySearchResults] = None,
) -> Dict[str, Any]:
    store, period = input_json.get("store", {}), input_json.get("period", {})
    mid, start, end = store.get("market_id"), period.get("start"), period.get("end")
    if not (mid and start and end):
        LOGGER.error("[tavily_events] 입력 누락: market_id/start/end 필요")
        return {
            "has_valid_signal": False,
            "summary": "입력 누락",
            "signals": [],
            "citations": [],
            "assumptions": [],
            "contract_version": "situation.v1",
        }

    area = _area_name(mid, market_locator)
    qs = _queries(area, start, end, input_json.get("user_query"))
    tool = tavily or _tavily

    # 월 가점 계산을 위해 시작/끝 파싱
    s_date, e_date = dt.date.fromisoformat(start), dt.date.fromisoformat(end)

    signals, citations, seen = [], [], set()
    for q in qs:
        try:
            res = tool.invoke(q)
        except Exception as e:
            LOGGER.warning("[tavily_events] Tavily 쿼리 실패: '%s' (%s)", q, e)
            continue
        if not isinstance(res, list):
            LOGGER.warning("[tavily_events] 예기치 않은 반환형: %s (query=%s)", type(res).__name__, q)
            continue

        for it in res:
            title, url, snip = it.get("title") or "지역 이벤트", it.get("url"), it.get("answer") or ""
            key = (title, url)
            if key in seen:
                continue
            seen.add(key)
            if url and url not in citations:
                citations.append(url)

            exp = _visitors(title + " " + snip)
            rel = (
                0.5
                + (0.2 if re.search(r"(팝업|행사|이벤트|전시|마켓|야시장|페스티벌|콘서트)", title) else 0.0)
                + (0.15 if exp and exp >= 5000 else 0.0)
                # ── NEW: 요청 월/연도와 일치하면 소폭 가점
                + _month_bias((title or "") + " " + snip, s_date.year, s_date.month)
            )
            rel = min(rel, 0.95)

            signals.append({
                "signal_id": f"EV-{start.replace('-','')}-{len(signals)+1}",
                "signal_type": "event",
                "description": title,
                "details": {
                    "area_name": area,
                    "expected_visitors": exp,
                    "distance_km": None,  # 지오코딩 붙일 때 채우기
                    "url": url,
                    "period_hint": {"start": start, "end": end},
                    "snippet": snip,
                },
                "relevance": rel,
                "valid": True,
                "reason": "지역/기간 키워드 매칭 및 스니펫 근거",
            })

    summary = f"{area} {start}~{end}: " + (f"{len(signals)}건의 이벤트 단서" if signals else "이벤트 단서 없음")
    return {
        "has_valid_signal": bool(signals),
        "summary": summary,
        "signals": signals,
        "citations": citations[:8],
        "assumptions": ["타이틀/스니펫 기반 1차 정규화. 확정 일정·좌표는 후속 연동에서 확정."],
        "contract_version": "situation.v1",
    }

# ── LangChain Tool 래퍼 ─────────────────────────────────────────────────────
class EventArgs(BaseModel):
    """에이전트에서 간단 호출용 파라미터(필수 최소셋)."""
    market_id: str = Field(..., description="상권 ID (예: M45)")
    start: str = Field(..., description="기간 시작 YYYY-MM-DD")
    end: str = Field(..., description="기간 종료 YYYY-MM-DD")
    user_query: Optional[str] = Field(None, description="사용자 질의(선택, 예: '팝업 스토어 2025 10월')")

def get_tool(
    market_locator: Optional[Callable[[str], Tuple[float, float, str]]] = None,
    tavily: Optional[TavilySearchResults] = None,
) -> StructuredTool:
    """
    에이전트에 등록할 Tool 객체 반환.
    사용 예: tools = [ get_tool(market_locator=db_lookup) ]
    """
    def _call(market_id: str, start: str, end: str, user_query: Optional[str] = None):
        input_json = {
            "user_query": user_query,
            "store": {"id": None, "market_id": market_id, "industry_code": None},
            "period": {"start": start, "end": end},
        }
        return search_event_signals(input_json, market_locator=market_locator, tavily=tavily)

    return StructuredTool.from_function(
        func=_call,
        name="tavily_events_search",
        description="Tavily로 지역(상권ID)·기간에 맞는 행사/팝업/전시 단서를 수집해 Situation JSON(event signals)을 반환",
        args_schema=EventArgs,
        return_direct=False,
    )

__all__ = ["search_event_signals", "get_tool", "EventArgs"]
