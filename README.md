# AI-fitness-trainer
AI-based fitness trainer using OpenCV and MediaPipe Public
# 🏋️ AI Fitness Trainer

Real-time arm curl counter using computer vision.

## 🚀 Features
- Real-time pose detection (MediaPipe)
- Arm curl angle calculation
- Repetition counter
- Visual feedback (green flash + GOOD REP)
- Clean UI with OpenCV

## 🧠 How it works
The system calculates the elbow angle using shoulder, elbow and wrist landmarks.
When the arm moves from extended (>150°) to flexed (<70°), a repetition is counted.

## 🛠 Technologies
- Python
- OpenCV
- MediaPipe
- NumPy

## ▶️ Run locally

```bash
pip install -r requirements.txt
python pose_estimation.py
