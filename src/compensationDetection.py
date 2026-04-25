import cv2
import mediapipe as mp
import numpy as np


class compensationDetection:
    def __init__(self, camera_index=0):
        # MediaPipe setup
        self.mp_holistic = mp.solutions.holistic
        self.mp_drawing = mp.solutions.drawing_utils

        self.cap = cv2.VideoCapture(camera_index)
        self.holistic = self.mp_holistic.Holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Control flags
        self.running = False
        self.compensation_detected = False  

    
    def calculate_angle(self, a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        ba = a - b
        bc = c - b

        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        return np.degrees(np.arccos(cosine_angle))

    def get_landmark_coords(self, landmarks, index, w, h):
        lm = landmarks.landmark[index]
        return int(lm.x * w), int(lm.y * h)

    def draw_feedback(self, image, point, angle, label):
        TARGET = 90
        MARGIN = 40

        deviation = abs(angle - TARGET)
        in_range = deviation <= MARGIN

        color = (0, 255, 0) if in_range else (0, 0, 255)
        status = "OK" if in_range else "ALERT!"

        cv2.putText(image, f"{label}: {angle:.1f}", (point[0] - 40, point[1] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(image, status, (point[0] - 40, point[1] + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
        cv2.circle(image, point, 8, color, -1)

        return in_range

    
    def detect_compensation(self, left_angle, right_angle):
        """
        Define your compensation condition here.
        Example: if any elbow is out of range.
        """
        TARGET = 90
        MARGIN = 40

        left_ok = abs(left_angle - TARGET) <= MARGIN
        right_ok = abs(right_angle - TARGET) <= MARGIN

        if not left_ok or not right_ok:
            self.compensation_detected = True
        else:
            self.compensation_detected = False


    def start(self):
        self.running = True

        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            h, w, _ = frame.shape

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.holistic.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Draw pose
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, self.mp_holistic.POSE_CONNECTIONS
                )

                lm = results.pose_landmarks

                # LEFT
                ls = self.get_landmark_coords(lm, 11, w, h)
                le = self.get_landmark_coords(lm, 13, w, h)
                lw = self.get_landmark_coords(lm, 15, w, h)

                left_angle = self.calculate_angle(ls, le, lw)
                self.draw_feedback(image, le, left_angle, "L-Elbow")

                # RIGHT
                rs = self.get_landmark_coords(lm, 12, w, h)
                re = self.get_landmark_coords(lm, 14, w, h)
                rw = self.get_landmark_coords(lm, 16, w, h)

                right_angle = self.calculate_angle(rs, re, rw)
                self.draw_feedback(image, re, right_angle, "R-Elbow")

                self.detect_compensation(left_angle, right_angle)

                if self.compensation_detected:
                    cv2.putText(image, "COMPENSATION DETECTED!",
                                (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 0, 255), 3)

            cv2.imshow("Compensation Detection", image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                self.stop()

        self.cleanup()

    def stop(self):
        self.running = False

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.holistic.close()

    def update_feed(self):
        if self.cap.isOpened():
            self.cap.grab()

    def check_for_compensation(self):
        if not self.cap.isOpened():
                return False

        ret, frame = self.cap.retrieve()
        if not ret:
            return False

        h, w, _ = frame.shape
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.holistic.process(image)

        self.compensation_detected = False

        if results.pose_landmarks:
            lm = results.pose_landmarks

            # LEFT
            ls = self.get_landmark_coords(lm, 11, w, h)
            le = self.get_landmark_coords(lm, 13, w, h)
            lw = self.get_landmark_coords(lm, 15, w, h)
            left_angle = self.calculate_angle(ls, le, lw)

            # RIGHT
            rs = self.get_landmark_coords(lm, 12, w, h)
            re = self.get_landmark_coords(lm, 14, w, h)
            rw = self.get_landmark_coords(lm, 16, w, h)
            right_angle = self.calculate_angle(rs, re, rw)

            self.detect_compensation(left_angle, right_angle)

        return self.compensation_detected

    def cleanup(self):
        self.cap.release()
        self.holistic.close()


if __name__ == "__main__":
    detector = compensationDetection()
    detector.start()

    # After closing window
    print("Compensation detected:", detector.compensation_detected)        