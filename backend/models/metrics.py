from pydantic import BaseModel
from typing import List

class DashboardMetrics(BaseModel):
    total_open_denials: int
    total_at_risk: float
    total_denied_amount: float = 0.0
    urgent_appeals: int
    high_probability_count: int
    recovered_this_month: float
    recovery_rate_this_month: int
    total_recovered_ytd: float
    total_claims_recovered: int

class PayerMetrics(BaseModel):
    payer_name: str
    total_denials: int
    appeals_submitted: int
    appeals_won: int
    success_rate: int
    recovered_amount: float

class CategoryMetrics(BaseModel):
    category: str
    total_denials: int
    appeals_submitted: int
    appeals_won: int
    success_rate: int
    recovered_amount: float

class TrendMetrics(BaseModel):
    month: str
    recovered_amount: float
    submitted_appeals: int
    won_appeals: int
    success_rate: int
