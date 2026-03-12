from pydantic import BaseModel


class SummaryStatsResponse(BaseModel):
    tokens_tracked: int
    evaluations_total: int
    alerts_total: int
    latest_decision_counts: dict[str, int]
