import cv2
from contexts.pupil_ctx import PupilContext
from datetime import datetime, timezone

class PupilTracker():
    def __init__(self):
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    def detect(self, gray_frame) -> PupilContext:
        try:
            blurred = cv2.GaussianBlur(gray_frame, (5, 5), 0) #(5, 5)
            _, binary = cv2.threshold(blurred, 10, 255, cv2.THRESH_BINARY_INV)
            binary = cv2.erode(binary, None, iterations=1)
            binary = cv2.dilate(binary, None, iterations=1)
            #binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, self.kernel)
            cv2.imshow('binary', binary)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                return None
            largest_contour = max(contours, key=cv2.contourArea)
            (position_x, position_y), radius = cv2.minEnclosingCircle(largest_contour)
            return PupilContext(x=position_x, y=position_y, radius=radius, timestamp=datetime.now(timezone.utc))
        except cv2.error as e:
            return None
        except Exception as e:
            print(f"Erro inesperado na detecção de pupila: {e}")
            return None