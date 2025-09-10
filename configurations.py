from dataclasses import dataclass

@dataclass(frozen=True)
class CameraConfiguration:
    fps: float = 120.0
    resolution: tuple[int, int] = (640, 480)