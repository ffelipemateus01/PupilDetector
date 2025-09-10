from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class CameraContext:
    index: int
    name: str
    available: Optional[bool] = None