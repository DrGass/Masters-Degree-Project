import tensorflow as tf
import numpy as np
import cv2
import matplotlib.pyplot as plt
import pprint
import json
from datetime import datetime
from collections import deque


class MoveNet:
    def __init__(self, model_path):
        self.interpreter = tf.lite.Interpreter(model_path)
        self.interpreter.allocate_tensors()
        self.amount = 256 if "thunder" in model_path else 192

        # Add pose sequence buffer for AI analysis
        self.pose_buffer = deque(maxlen=30)  # Store last 30 frames
        self.data_collection_mode = False
        self.current_session_data = []

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
        self.landmarks = {
            0: "nose",
            1: "left_eye",
            2: "right_eye",
            3: "left_ear",
            4: "right_ear",
            5: "left_shoulder",
            6: "right_shoulder",
            7: "left_elbow",
            8: "right_elbow",
            9: "left_wrist",
            10: "right_wrist",
            11: "left_hip",
            12: "right_hip",
            13: "left_knee",
            14: "right_knee",
            15: "left_ankle",
            16: "right_ankle",
        }

    def predict(self, frame):
        # Image reshaping - use self.amount for dynamic sizing
        img = frame.copy()
        img = tf.image.resize_with_pad(
            tf.expand_dims(img, axis=0), self.amount, self.amount
        )
        input_image = tf.cast(img, dtype=tf.float32)

        # Setup input and output
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

        # Make predictions
        self.interpreter.set_tensor(input_details[0]["index"], np.array(input_image))
        self.interpreter.invoke()
        keypoints_with_scores = self.interpreter.get_tensor(output_details[0]["index"])

        # Store in buffer for sequence analysis
        self._update_pose_buffer(keypoints_with_scores)

        # Store for data collection if enabled
        if self.data_collection_mode:
            self._store_session_data(keypoints_with_scores, frame.shape)

        return keypoints_with_scores

    def _update_pose_buffer(self, keypoints):
        """Store keypoints in buffer for sequence analysis"""
        # Extract and normalize keypoints
        shaped_keypoints = np.squeeze(keypoints)
        if shaped_keypoints.shape[0] == 17:  # Ensure we have all keypoints
            self.pose_buffer.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "keypoints": shaped_keypoints.tolist(),
                }
            )

    def _store_session_data(self, keypoints, frame_shape):
        """Store data for training collection"""
        if hasattr(self, "current_exercise") and hasattr(self, "current_quality"):
            session_entry = {
                "timestamp": datetime.now().isoformat(),
                "keypoints": np.squeeze(keypoints).tolist(),
                "frame_shape": frame_shape,
                "exercise": self.current_exercise,
                "quality": self.current_quality,
            }
            self.current_session_data.append(session_entry)

    def get_pose_sequence(self):
        """Get current pose sequence for AI analysis"""
        if len(self.pose_buffer) == self.pose_buffer.maxlen:
            return list(self.pose_buffer)
        return None

    def enable_data_collection(self, exercise_type, form_quality):
        """Enable data collection mode"""
        self.data_collection_mode = True
        self.current_exercise = exercise_type
        self.current_quality = form_quality
        self.current_session_data = []

    def save_session_data(self, participant_id, rep_number):
        """Save collected session data"""
        if not self.current_session_data:
            return False

        filename = f"session_{self.current_exercise}_{self.current_quality}_{participant_id}_{rep_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        session_data = {
            "metadata": {
                "exercise": self.current_exercise,
                "quality": self.current_quality,
                "participant_id": participant_id,
                "rep_number": rep_number,
                "total_frames": len(self.current_session_data),
            },
            "poses": self.current_session_data,
        }

        with open(f"training_data/{filename}", "w") as f:
            json.dump(session_data, f)

        self.current_session_data = []
        return True


def draw_keypoints(frame, keypoints, confidence_threshold):
    y, x, c = frame.shape
    shaped = np.squeeze(np.multiply(keypoints, [y, x, 1]))

    count = 0
    for kp in shaped:
        ky, kx, kp_conf = kp
        print(ky, kx, kp_conf)
        if kp_conf > confidence_threshold:
            cv2.circle(frame, (int(kx), int(ky)), 4, (0, 255, 0), -1)
            cv2.putText(
                frame,
                str(count),
                (int(kx), int(ky)),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
            )
            count += 1

    return frame


def draw_connections(frame, keypoints, edges, confidence_threshold):
    y, x, c = frame.shape
    shaped = np.squeeze(np.multiply(keypoints, [y, x, 1]))

    for edge, color in edges.items():
        p1, p2 = edge
        y1, x1, c1 = shaped[p1]
        y2, x2, c2 = shaped[p2]

        if (c1 > confidence_threshold) & (c2 > confidence_threshold):
            cv2.line(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
    return frame


# Add to the render_window function:


def render_window():
    cap = cv2.VideoCapture(0)

    # Initialize models
    model_path = "models/lightning.tflite"
    movenet_model = MoveNet(model_path)

    # Initialize exercise analyzer (optional - only if model exists)
    try:
        from exercise_analyzer import ExerciseFormAnalyzer

        form_analyzer = ExerciseFormAnalyzer("models/exercise_form_model.h5")
        analysis_enabled = True
    except:
        form_analyzer = None
        analysis_enabled = False
        print("Exercise form analyzer not available")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h_diff = (frame.shape[1] - frame.shape[0]) // 2
        frame = cv2.copyMakeBorder(
            frame, h_diff, h_diff, 0, 0, cv2.BORDER_CONSTANT, None, value=0
        )

        # Get predictions
        keypoints_with_scores = movenet_model.predict(frame)

        # Analyze form if possible
        form_result = None
        if analysis_enabled and form_analyzer:
            pose_sequence = movenet_model.get_pose_sequence()
            if pose_sequence:
                form_result = form_analyzer.analyze_form(pose_sequence)

        # Render keypoints
        draw_keypoints(frame, keypoints_with_scores, 0.4)

        # Display analysis results
        y_offset = 30
        if form_result and "predicted_class" in form_result:
            class_text = f"Form: {form_result['predicted_class']} ({form_result['confidence']:.2f})"
            color = (
                (0, 255, 0)
                if form_result["predicted_class"] == "good"
                else (
                    (0, 165, 255)
                    if form_result["predicted_class"] == "warning"
                    else (0, 0, 255)
                )
            )
            cv2.putText(
                frame,
                class_text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
            )
            y_offset += 30

            feedback_text = form_result["feedback"]
            cv2.putText(
                frame,
                feedback_text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )

        # Display buffer status
        buffer_status = f"Buffer: {len(movenet_model.pose_buffer)}/{movenet_model.pose_buffer.maxlen}"
        cv2.putText(
            frame,
            buffer_status,
            (10, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )

        cv2.imshow("MoveNet Lightning", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    render_window()


if __name__ == "__main__":
    main()
