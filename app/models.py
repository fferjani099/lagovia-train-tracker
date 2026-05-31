from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Station:
    id: str | None
    name: str
    standard_name: str | None = None


@dataclass(frozen=True)
class RawDeparture:
    train_number: str
    destination: str
    scheduled_departure_time: datetime
    delay_seconds: int

