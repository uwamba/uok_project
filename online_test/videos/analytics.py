import cv2
import mss
import numpy as np
import dlib

# Initialize camera and screen capture
cap = cv2.VideoCapture(0)  # Camera capture
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

with mss.mss() as sct:
    monitor = sct.monitors[1]  # Screen capture

    while True:
        # Capture camera frame
        ret, camera_frame = cap.read()
        if not ret:
            break

        # Capture screen frame
        screenshot = sct.grab(monitor)
        screen_frame = np.array(screenshot)
        screen_frame = cv2.cvtColor(screen_frame, cv2.COLOR_BGR2RGB)

        # Process the camera frame for face detection
        gray = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            landmarks = predictor(gray, face)
            for n in range(0, 68):
                x, y = landmarks.part(n).x, landmarks.part(n).y
                cv2.circle(camera_frame, (x, y), 1, (0, 255, 0), -1)

        # Display both camera and screen frames
        cv2.imshow("Camera Feed", camera_frame)
        cv2.imshow("Screen Capture", screen_frame)

        # Break if the user presses 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
