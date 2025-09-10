from contexts.camera_ctx import CameraContext
from contexts.pupil_ctx import PupilContext
from exceptions import CameraHandlerError
from tracker import PupilTracker
from configurations import CameraConfiguration
import cv2
import time
import threading

class CameraHandler():
    def __init__(self):
        self._video_capture = None
        self._camera = None
        self._configuration = None
        self._recording = False
        self._tracker = PupilTracker()
        self._scale_factor = 0.5
        self._running = False

    def open(self, camera: CameraContext):
        self._camera = camera
        self._configuration = CameraConfiguration()
        cap = cv2.VideoCapture(camera.index)
        fourcc = cv2.VideoWriter.fourcc(*'MJPG')
        cap.set(cv2.CAP_PROP_FOURCC, fourcc)
        cap.set(cv2.CAP_PROP_FPS, self._configuration.fps)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._configuration.resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._configuration.resolution[1])
        #print(f'{cap.get(cv2.CAP_PROP_FPS)} FPS')
        #print(f'{cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}')
        is_reading = False
        if cap.isOpened():
            is_reading, _ = cap.read()
        if not is_reading:
            raise CameraHandlerError('Houve um problema ao tentar abrir a camera selecionada.')
        self._video_capture = cap
        self._running = True
        threading.Thread(target=self.run, daemon=False).start()
    
    def run(self):
        frame_interval = 1.0 / self._configuration.fps
        try:
            while self._running:
                start_time = time.perf_counter()
                if self._video_capture.isOpened():
                    ret, frame = self._video_capture.read()
                    if ret:
                        small_frame = cv2.resize(src=frame, dsize=(0, 0),fx=self._scale_factor, fy=self._scale_factor)
                        gray_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
                        pupil = self._tracker.detect(gray_frame)
                        
                        gray_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)
                        if pupil:
                            gray_frame = self.draw_pupil(gray_frame, pupil)
                        cv2.imshow('gray', gray_frame)
                elapsed_time = time.perf_counter() - start_time
                sleep_time = frame_interval - elapsed_time
                if sleep_time > 0:
                    time.sleep(sleep_time)
                cv2.waitKey(1)
        except Exception as e:
            raise CameraHandlerError(f'Houve um problema ao tentar ler um novo frame. {e}')
        
    def draw_pupil(self, frame, pupil: PupilContext):
        pt1 = (int(pupil.x - pupil.radius / 2.0), int(pupil.y))
        pt2 = (int(pupil.x + pupil.radius / 2.0), int(pupil.y))
        cv2.line(frame, pt1, pt2, (220, 180, 100), 1)
        pt1 = (int(pupil.x), int(pupil.y - pupil.radius / 2.0))
        pt2 = (int(pupil.x), int(pupil.y + pupil.radius / 2.0))
        cv2.line(frame, pt1, pt2, (220, 180, 100), 1)
        return frame

    def close(self):
        print(self._video_capture)
        if self._video_capture:
            self._video_capture.release()
            #cv2.destroyWindow(self._camera.name)
            self._running = False
            self._video_capture = None
            self._camera = None   

if __name__ == "__main__":
    from contexts.camera_ctx import CameraContext

    cam_ctx = CameraContext(name="cam0", index=0)

    handler = CameraHandler()
    handler.open(cam_ctx)  # apenas abre a câmera