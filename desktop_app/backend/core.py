import tensorflow as tf
import numpy as np
import cv2

interpreter = tf.lite.Interpreter(model_path="lightningh_model_3.tflite")
interpreter.allocate_tensors()

cap = cv2.VideoCapture(0)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    cap.release()
    cv2.destroyAllWindows()
