import cv2

class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    def start(self):
        self.cap = cv2.VideoCapture(0)

    def get_frame(self):
        success, frame = self.cap.read()
        if not success:
            return None
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        _, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def release(self):
        self.cap.release()