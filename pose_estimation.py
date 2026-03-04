import cv2
import mediapipe as mp
import numpy as np
import time
import pyttsx3
import threading

engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1)

last_speak_time = 0

def speak(text):
    global last_speak_time
    current_time = time.time()

    # Разрешаем говорить только раз в 1 секунду
    if current_time - last_speak_time > 1:
        engine.say(text)
        engine.runAndWait()
        last_speak_time = current_time
# -----------------------
# Настройки
# -----------------------
WEIGHT = 10  # вес гантели (кг)

# -----------------------
# MediaPipe
# -----------------------
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=0,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# -----------------------
# Камера
# -----------------------
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 640)
cap.set(4, 480)

# -----------------------
# Переменные
# -----------------------
rep_flash_time = 0
left_counter = 0
right_counter = 0

left_stage = None
right_stage = None

prev_left_angle = 0
prev_right_angle = 0

start_time = time.time()
prev_time = 0

# -----------------------
# Функция угла
# -----------------------
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])

    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360-angle

    return angle

# -----------------------
# Основной цикл
# -----------------------
speak ("System ready")
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    if time.time() - rep_flash_time < 0.3:
        overlay = frame.copy()
        cv2.rectangle(overlay, (0,0), (640,480), (0,255,0), -1)
        alpha = 0.2
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
    if time.time() - rep_flash_time < 0.5:
        cv2.putText(frame, "REP!",
                    (250,250),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2,
                    (0,255,0),
                    4,
                    cv2.LINE_AA)
    cv2.putText(frame, f"Reps: {left_counter}",
                    (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.5,
                    (255,255,255),
                    3,
                    cv2.LINE_AA)
                    
                
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = pose.process(image)
    image.flags.writeable = True
    frame = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    try:
        landmarks = results.pose_landmarks.landmark

        # -------- ЛЕВАЯ РУКА --------
        left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

        left_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
        left_angle = (left_angle + prev_left_angle) / 2
        prev_left_angle = left_angle
        if left_angle > 150:
            left_stage = "down"
        if left_angle < 70 and left_stage == "down":
            left_stage = "up"
            left_counter += 1
            rep_flash_time = time.time()
            print("LEFT REP DETECTED")
            print("Speak Function Called")
            speak("Left rep")

        # -------- ПРАВАЯ РУКА --------
        right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                       landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                       landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

        right_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
        right_angle = (right_angle + prev_right_angle) / 2
        prev_right_angle = right_angle

        if right_angle > 160:
            right_stage = "down"
        if right_angle < 40 and right_stage == "down":
            right_stage = "up"
            right_counter += 1

        # -------- BAD FORM --------
        bad_form = False
        if left_shoulder[1] < left_elbow[1] - 0.05:
            bad_form = True
        if right_shoulder[1] < right_elbow[1] - 0.05:
            bad_form = True

        if bad_form:
            cv2.putText(frame, "BAD FORM!",
                        (200,80),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.2,
                        (0,0,255),
                        3)

    except:
        pass

    # -------- VOLUME --------
    total_reps = left_counter + right_counter
    volume = total_reps * WEIGHT

    # -------- TIMER --------
    elapsed = int(time.time() - start_time)

    # -------- FPS --------
    current_time = time.time()
    fps = 1 / (current_time - prev_time) if prev_time != 0 else 0
    prev_time = current_time

    # -------- UI --------
    cv2.rectangle(frame, (0,0), (260,140), (40,40,40), -1)

    cv2.putText(frame, f"Left: {left_counter}",
                (10,30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255,255,255),
                2)

    cv2.putText(frame, f"Right: {right_counter}",
                (10,60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255,255,255),
                2)

    cv2.putText(frame, f"Volume: {volume} kg",
                (10,90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0,255,0),
                2)

    cv2.putText(frame, f"Time: {elapsed}s",
                (10,120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255,255,255),
                2)

    cv2.putText(frame, f"FPS: {int(fps)}",
                (480,30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0,255,0),
                2)

    mp_drawing.draw_landmarks(
        frame,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS
    )

    cv2.imshow("AI Smart Biceps Trainer", frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# =========================
# НАСТРОЙКИ
# =========================
WEIGHT_LEFT = 10
WEIGHT_RIGHT = 10

# =========================
# ГОЛОС (без лагов)
# =========================
engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1)


def speak(text):
            engine.say(text)
            engine.runAndWait()
   
# =========================
# MEDIAPIPE
# =========================
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=0,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# =========================
# КАМЕРА
# =========================
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 640)
cap.set(4, 480)

# =========================
# ПЕРЕМЕННЫЕ
# =========================
left_counter = 0
right_counter = 0

left_stage = None
right_stage = None

prev_left_angle = 0
prev_right_angle = 0

volume = 0

start_time = time.time()
prev_time = 0
last_warning_time = 0

last_left_rep_time = 0
last_right_rep_time = 0

# =========================
# ФУНКЦИЯ УГЛА
# =========================
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
              np.arctan2(a[1]-b[1], a[0]-b[0])

    angle = np.abs(radians*180.0/np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle

# =========================
# ОСНОВНОЙ ЦИКЛ
# =========================
while cap.isOpened():

    ret, frame = cap.read()
    if not ret:
        break

    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = pose.process(image)
    image.flags.writeable = True
    frame = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    try:
        landmarks = results.pose_landmarks.landmark

        # -------- ЛЕВАЯ РУКА --------
        left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

        left_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
        left_angle = (left_angle + prev_left_angle) / 2
        prev_left_angle = left_angle

        if left_angle > 160:
            left_stage = "down"

        if left_angle < 40 and left_stage == "down":
            if time.time() - last_left_rep_time > 0.8:
                left_stage = "up"
                left_counter += 1
                volume += WEIGHT_LEFT
                last_left_rep_time = time.time()
                print("LEFT REP DETECTED")
                speak("Left rep")

        # -------- ПРАВАЯ РУКА --------
        right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                       landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                       landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

        right_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
        right_angle = (right_angle + prev_right_angle) / 2
        prev_right_angle = right_angle

        if right_angle > 160:
            right_stage = "down"

        if right_angle < 40 and right_stage == "down":
            if time.time() - last_right_rep_time > 0.8:
                right_stage = "up"
                right_counter += 1
                volume += WEIGHT_RIGHT
                last_right_rep_time = time.time()
                speak("Right rep")

        # -------- BAD FORM --------
        bad_form = False

        if left_shoulder[1] < left_elbow[1] - 0.05:
            bad_form = True
        if right_shoulder[1] < right_elbow[1] - 0.05:
            bad_form = True

        if bad_form:
            cv2.putText(frame, "BAD FORM!",
                        (200,80),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.2,
                        (0,0,255),
                        3)

            if time.time() - last_warning_time > 3:
                speak("Fix your form")
                last_warning_time = time.time()

    except:
        pass

    # -------- ТАЙМЕР --------
    elapsed = int(time.time() - start_time)

    # -------- FPS --------
    current_time = time.time()
    fps = 1 / (current_time - prev_time) if prev_time != 0 else 0
    prev_time = current_time

    # -------- UI --------
    cv2.rectangle(frame, (0,0), (300,160), (40,40,40), -1)

    cv2.putText(frame, f"Left: {left_counter}",
                (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    cv2.putText(frame, f"Right: {right_counter}",
                (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    cv2.putText(frame, f"Volume: {volume} kg",
                (10,90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    cv2.putText(frame, f"Time: {elapsed}s",
                (10,120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    cv2.putText(frame, f"FPS: {int(fps)}",
                (500,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    mp_drawing.draw_landmarks(frame,
                              results.pose_landmarks,
                              mp_pose.POSE_CONNECTIONS)

    cv2.imshow("AI Smart Biceps Trainer PRO", frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()