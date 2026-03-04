import mediapipe as mp

print("mediapipe file:", mp.__file__)
print("has solutions:", hasattr(mp, "solutions"))
print("attrs:", [a for a in dir(mp) if "solutions" in a])