import os
import sys
import time

import cv2
import mediapipe as mp
import numpy as np
from pygame import mixer


class WaterDrinkingDetector:
    def __init__(self, water_tracker_app=None, detection_interval=3, sound_file="assets/beep.mp3", show_window=True):
        mixer.init()

        if hasattr(sys, '_MEIPASS'):
            self.assets_path = os.path.join(sys._MEIPASS, "assets")
        else:
            self.assets_path = os.path.join(os.getcwd(), 'assets')

        self.ping_sound = os.path.join(self.assets_path, 'beep.mp3')
        mixer.music.load(self.ping_sound)

        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_face_mesh = mp.solutions.face_mesh

        self.hands = self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.pose = self.mp_pose.Pose()
        self.face_mesh = self.mp_face_mesh.FaceMesh()

        self.cap = cv2.VideoCapture(0)

        self.last_notification_time = 0
        self.detection_interval = detection_interval
        self.show_window = show_window
        self.running = False

        self.water_tracker_app = water_tracker_app

    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape

        hand_results = self.hands.process(rgb_frame)
        pose_results = self.pose.process(rgb_frame)
        face_results = self.face_mesh.process(rgb_frame)

        mouth_x, mouth_y = None, None
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                mouth_x = int(face_landmarks.landmark[13].x * w)
                mouth_y = int(face_landmarks.landmark[13].y * h)
                cv2.circle(frame, (mouth_x, mouth_y), 5, (0, 255, 0), -1)

        if hand_results.multi_hand_landmarks and mouth_x is not None:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                index_finger_x = int(hand_landmarks.landmark[8].x * w)
                index_finger_y = int(hand_landmarks.landmark[8].y * h)
                cv2.circle(frame, (index_finger_x, index_finger_y), 5, (255, 0, 0), -1)

                distance = np.linalg.norm([mouth_x - index_finger_x, mouth_y - index_finger_y])
                if distance < 50:  # Próg wykrywania picia
                    if time.time() - self.last_notification_time > self.detection_interval:
                        mixer.music.play()
                        self.last_notification_time = time.time()
                        if self.water_tracker_app is not None:
                            self.water_tracker_app.add_water(sip=True)
                    cv2.putText(frame, "Pijesz wode!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return frame

    def start_detection(self):
        """Uruchamia detekcję picia wody."""
        self.running = True
        while self.cap.isOpened() and self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = self.process_frame(frame)

            if self.show_window:
                cv2.imshow("Wykrywanie picia wody", frame)

            # Używając klawisza 'q', możemy zakończyć program
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
    water_detector = WaterDrinkingDetector(detection_interval=10, sound_file="assets/beep.mp3", show_window=True)
    water_detector.start_detection()
