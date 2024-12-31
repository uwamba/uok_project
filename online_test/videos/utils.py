import mss
import time
import os
import cv2
import dlib
from .models import MonitoringLog

def capture_screen(user, test, interval=5):
    """Capture screen activity."""
    with mss.mss() as sct:
        while True:
            screenshot_path = f'uploads/{int(time.time())}.png'
            sct.shot(output=screenshot_path)
            MonitoringLog.objects.create(
                user=user,
                test=test,
                activity_type="screen",
                data="Screenshot captured",
                screenshot=screenshot_path
            )
            time.sleep(interval)


def monitor_webcam(user, exam):
    detector = dlib.get_frontal_face_detector()
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        if len(faces) == 0:
            activity = "No face detected"
        elif len(faces) > 1:
            activity = "Multiple faces detected"
        else:
            activity = "Face detected"

        # Log activity (replace this with your MonitoringLog logic)
        print(activity)

        # Save the frame as an image file for debugging
        cv2.imwrite(f'media/frames/{int(time.time())}.jpg', frame)

        # Skip displaying the frame in headless environments
        if "DISPLAY" in os.environ:  # Check if a graphical environment is available
            cv2.imshow("Webcam", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()