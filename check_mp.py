import mediapipe as mp

print(mp.__file__)          # откуда импортируется mediapipe
print(hasattr(mp, "solutions"))
print(dir(mp)[:20])