import cv2
import mediapipe as mp
import numpy as np
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils
dress = cv2.imread("dress.png", cv2.IMREAD_UNCHANGED)
def overlay_transparent(background, overlay, x, y, width=None, height=None):
    if width and height:
        overlay = cv2.resize(overlay, (width, height))
    h, w, _ = overlay.shape
    for i in range(h):
        for j in range(w):
            if y + i >= background.shape[0] or x + j >= background.shape[1]:
                continue
            alpha = overlay[i, j, 3] / 255.0
            background[y + i, x + j] = (1 - alpha) * background[y + i, x + j] + alpha * overlay[i, j, :3]
    return background
cap = cv2.VideoCapture(0)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
        dress_width = int(abs(right_shoulder.x - left_shoulder.x) * frame.shape[1] * 1.5)
        dress_height = int(abs(right_hip.y - left_shoulder.y) * frame.shape[0] * 1.2)
        x = int(left_shoulder.x * frame.shape[1] - dress_width // 4)
        y = int(left_shoulder.y * frame.shape[0])
        frame = overlay_transparent(frame, dress, x, y, width=dress_width, height=dress_height)
    cv2.imshow("Virtual Dress Fitting", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()