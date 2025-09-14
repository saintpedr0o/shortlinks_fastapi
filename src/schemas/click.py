from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class BaseClick(BaseModel):
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None


class ClickOut(BaseClick):
    id: int
    link_id: int
    clicked_at: datetime

    model_config = {"from_attributes": True}


class StatsOut(BaseModel):
    total_clicks: int = 0
    today_clicks: int = 0
    unique_ips: int = 0
    unique_referrers: int = 0
    top_referrers: Dict[str, int] = Field(default_factory=dict)
    browsers: Dict[str, int] = Field(default_factory=dict)


class ClicksByPeriodItem(BaseModel):
    period: str
    count: int


class PeriodClicksResponse(BaseModel):
    clicks_by_period: List[ClicksByPeriodItem]
