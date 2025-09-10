from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class PupilContext:
    x: float
    y: float
    radius: float
    timestamp: datetime