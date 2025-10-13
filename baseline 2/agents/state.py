from typing import Literal, Annotated
from pydantic import BaseModel, Field
from operator import add


class AgentState(BaseModel):
    """멀티에이전트 시스템의 중앙 상태"""
    user_query: str = ""
    intent: Literal["strategy", "overview"] = "strategy"
    constraints: dict = Field(default_factory=dict)
    
    # 각 에이전트 결과
    context_json: dict | None = None
    situation_json: dict | None = None
    resource_json: dict | None = None
    
    # 최종 산출물
    strategy_cards: list[dict] = Field(default_factory=list)
    eval_report: dict | None = None
    
    # 로그 (병렬 추가 가능)
    logs: Annotated[list[str], add] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True