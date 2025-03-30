import os
import sys
import time

import cv2
import torch
from pygame import mixer


class WaterDrinkingDetector:
    def __init__(self, water_tracker_app=None, detection_interval=3, show_window=True):
        mixer.init()

        if hasattr(sys, '_MEIPASS'):
            self.assets_path = os.path.join(sys._MEIPASS, "assets")
        else:
            self.assets_path = os.path.join(os.getcwd(), 'assets')

        self.ping_sound = os.path.join(self.assets_path, 'beep.mp3')
        mixer.music.load(self.ping_sound)

        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

        self.class_names = self.model.names

        self.cap = cv2.VideoCapture(0)
        self.last_notification_time = 0
        self.detection_interval = detection_interval
        self.show_window = show_window
        self.running = False
        self.water_tracker_app = water_tracker_app

    def process_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.model(frame_rgb)

        for result in results.xywh[0]:
            x_center, y_center, width, height, conf, cls = result
            cls = int(cls)

            class_name = self.class_names[cls]
            # if class_name in {"cup", "wine glass", "bottle"}:
            #     print(f"[{datetime.now().time()}]", class_name, conf)
            if self.show_window and conf > 0.55:
                self.draw_rectangle(class_name, cls, frame, height, width, x_center, y_center)

            if class_name in {"cup", "wine glass", "bottle"} and conf > 0.55:
                if time.time() - self.last_notification_time > self.detection_interval:
                    mixer.music.play()
                    self.last_notification_time = time.time()
                    if self.water_tracker_app:
                        self.water_tracker_app.add_water(sip=True)

        return frame

    def draw_rectangle(self, class_name, cls, frame, height, width, x_center, y_center):
        x_center = x_center.item()
        y_center = y_center.item()
        width = width.item()
        height = height.item()
        h, w, _ = frame.shape
        x1 = int(x_center - width / 2)
        y1 = int(y_center - height / 2)
        x2 = int(x_center + width / 2)
        y2 = int(y_center + height / 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f'{class_name} (ID: {cls})', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0),
                    2)

    def start_detection(self):
        """Uruchamia detekcję picia wody."""
        self.running = True
        while self.cap.isOpened() and self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            small_frame = cv2.resize(frame, (0, 0), fx=0.75, fy=0.75)

            frame = self.process_frame(small_frame)

            if self.show_window:
                cv2.imshow("Wykrywanie picia wody", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def stop_detection(self):
        """Zatrzymuje detekcję picia wody."""
        self.running = False
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    water_detector = WaterDrinkingDetector(detection_interval=10, show_window=True)
    water_detector.start_detection()
