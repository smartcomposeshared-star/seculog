from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class LoginEvent:
    username: str
    ip_address: str
    success: bool
    timestamp: datetime
    country: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


@dataclass
class Alert:
    login_event: LoginEvent
    rule_type: str
    severity: str
    details: str
    timestamp: datetime
