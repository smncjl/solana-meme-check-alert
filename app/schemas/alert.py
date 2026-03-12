from datetime import datetime

from pydantic import BaseModel


class AlertOut(BaseModel):
    token_address: str
    channel: str
    alert_type: str
    status: str
    sent_at: datetime
    payload: dict
