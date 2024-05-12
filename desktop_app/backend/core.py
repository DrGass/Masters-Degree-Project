import tensorflow as tf
import numpy as np
import cv2
import matplotlib.pyplot as plt


class MoveNet:
    def __init__(self, model_path):
        self.interpreter = tf.lite.Interpreter(model_path)
        self.interpreter.allocate_tensors()
        self.amount = 256 if "thunder" in model_path else 192
        self.edges = {
            (0, 1): "m",
            (0, 2): "c",
            (1, 3): "m",
            (2, 4): "c",
            (0, 5): "m",
            (0, 6): "c",
            (5, 7): "m",
            (7, 9): "m",
            (6, 8): "c",
            (8, 10): "c",
            (5, 6): "y",
            (5, 11): "m",
            (6, 12): "c",
            (11, 12): "y",
            (11, 13): "m",
            (13, 15): "m",
            (12, 14): "c",
            (14, 16): "c",
        }

    def predict(self, frame):
        # Image reshaping
        img = frame.copy()
        img = tf.image.resize_with_pad(
            np.expand_dims(img, axis=0), self.amount, self.amount
        )
        input_image = tf.cast(img, dtype=tf.float32)

        # Setup input and output
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

        # Make predictions
        self.interpreter.set_tensor(input_details[0]["index"], np.array(input_image))
        self.interpreter.invoke()
        keypoints_with_scores = self.interpreter.get_tensor(output_details[0]["index"])

        return keypoints_with_scores


def draw_keypoints(frame, keypoint, confidence):
    y, x, c = frame.shape
    shaped = np.squeeze(np.multiply(keypoint, [y, x, 1]))

    for kp in shaped:
        ky, kx, kp_conf = kp
        if kp_conf > confidence:
            cv2.circle(frame, (int(kx), int(ky)), 4, (0, 255, 0), -1)
    return frame


def draw_connections(frame, keypoints_with_scores, edges, confidence=0.4):
    y, x, c = frame.shape
    shaped = np.squeeze(np.multiply(keypoints_with_scores, [y, x, 1]))

    for edge, color in edges.items():
        p1, p2 = edge
        y1, x1, c1 = shaped[p1]
        y2, x2, c2 = shaped[p2]

        if (c1 > confidence) & (c2 > confidence):
            cv2.line(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
    return frame


def render_window():

    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        model_path = "thunder_model_3.tflite"
        # model_path = "lightning_model_3.tflite"
        MoveNet_model = MoveNet(model_path)
        keypoints_with_scores = MoveNet_model.predict(frame)

        # Render keypoints
        draw_keypoints(frame, keypoints_with_scores, 0.4)
        draw_connections(frame, keypoints_with_scores, MoveNet_model.edges, 0.4)

        cv2.imshow("MoveNet Lightning", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    render_window()


if __name__ == "__main__":
    main()
