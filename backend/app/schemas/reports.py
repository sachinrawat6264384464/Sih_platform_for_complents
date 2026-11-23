from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class BureauWorkload(BaseModel):
    bureau_code: str
    bureau_name: str
    total_complaints: int
    count: Optional[int] = 0
    pending: int
    under_process: int
    disposed: int
    escalated: int


class RegionalWorkload(BaseModel):
    region_code: str
    region_name: str
    city: str
    total_institutions: int
    total_complaints: int
    count: Optional[int] = 0
    pending: int


class MonthlyTrend(BaseModel):
    month: str
    received: int
    disposed: int


class DashboardMetricsOut(BaseModel):
    total_institutions: int
    total_complaints: int
    pending_complaints: int
    under_process_complaints: int
    disposed_complaints: int
    transferred_complaints: int
    escalated_complaints: int
    overdue_complaints: int
    potential_overlapping_cases: int
    confirmed_linked_cases: int
    sla_compliance_rate: float
    integration_health_score: float
    bureau_workload: List[BureauWorkload]
    regional_workload: List[RegionalWorkload]
    region_workload: Optional[List[RegionalWorkload]] = None
    monthly_trends: List[MonthlyTrend]
    integration_health: Optional[List[Dict[str, Any]]] = None
    complaint_ageing: Optional[Dict[str, int]] = None
