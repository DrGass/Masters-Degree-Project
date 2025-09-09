import tensorflow as tf
import numpy as np
import cv2
import matplotlib.pyplot as plt
import pprint
import json
import os
from datetime import datetime
from collections import deque
from repetition_detector import SquatDetector


class MoveNet:
    def __init__(self, model_path):
        self.interpreter = tf.lite.Interpreter(model_path)
        self.interpreter.allocate_tensors()
        self.amount = 192  # Movenet Lightning input size
        self.current_repetition = []  # Current rep being recorded
        self.completed_repetitions = []  # Complete reps for analysis
        self.min_rep_frames = 48  # Minimum frames for a valid rep (2 seconds at 24fps)
        self.max_rep_frames = 180  # Maximum frames for a valid rep (6 seconds at 30fps)
        self.pose_buffer = deque(maxlen=450)  # Store last 450 frames
        self.data_collection_mode = True
        self.current_session_data = []

        # Exercise detection capabilities
        self.available_exercises = {
            "squat": SquatDetector,
            # Future exercises will be added here
        }

        self.current_exercise = None
        self.exercise_detector = None
        self.exercise_mode = False

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
        img = frame.copy()
        img = tf.image.resize_with_pad(
            tf.expand_dims(img, axis=0), self.amount, self.amount
        )
        input_image = tf.cast(img, dtype=tf.float32)

        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

        # Make predictions
        self.interpreter.set_tensor(input_details[0]["index"], np.array(input_image))
        self.interpreter.invoke()
        keypoints_with_scores = self.interpreter.get_tensor(output_details[0]["index"])

        # Store in buffer for sequence analysis
        self._update_pose_buffer(keypoints_with_scores)

        # Add repetition detection if in exercise mode
        if self.exercise_mode and self.exercise_detector and self.current_exercise:
            shaped_keypoints = np.squeeze(keypoints_with_scores)
            # Run detection regardless of number of keypoints detected
            state, rep_completed = self.exercise_detector.detect_squat_phase(
                shaped_keypoints
            )

            if rep_completed:
                print(
                    f"✅ {self.current_exercise.title()} #{self.exercise_detector.rep_count} completed!"
                )

        # Store for data collection if enabled
        if self.data_collection_mode:
            self._store_session_data(keypoints_with_scores, frame.shape)

        return keypoints_with_scores

    def set_exercise_mode(self, exercise_type):
        """Set the current exercise type and initialize detector"""
        if exercise_type in self.available_exercises:
            self.current_exercise = exercise_type
            detector_class = self.available_exercises[exercise_type]
            self.exercise_detector = detector_class()
            self.exercise_mode = True
            print(f"✅ Exercise mode set to: {exercise_type}")
            return True
        else:
            print(f"❌ Exercise '{exercise_type}' not available")
            return False

    def disable_exercise_mode(self):
        """Disable exercise detection mode"""
        self.exercise_mode = False
        self.current_exercise = None
        self.exercise_detector = None
        print("Exercise mode disabled")

    def get_exercise_stats(self):
        """Get current exercise statistics"""
        if self.exercise_mode and self.exercise_detector:
            stats = self.exercise_detector.get_rep_stats()
            stats["exercise_type"] = self.current_exercise
            return stats
        return None

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

        # Ensure data directory exists
        data_dir = "../data/sessions"
        os.makedirs(data_dir, exist_ok=True)

        filename = f"session_{self.current_exercise}_{self.current_quality}_{participant_id}_{rep_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(data_dir, filename)

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

        with open(filepath, "w") as f:
            json.dump(session_data, f)

        self.current_session_data = []
        return True

    def save_exercise_session(self, participant_id=None):
        """Save completed exercise session with repetition data"""
        if not self.exercise_mode or not self.exercise_detector:
            return False

        stats = self.get_exercise_stats()
        if not stats or stats["total_reps"] == 0:
            return False

        # Ensure data directory exists
        data_dir = "../data/sessions"
        os.makedirs(data_dir, exist_ok=True)

        participant_str = f"_{participant_id}" if participant_id else ""
        filename = f"exercise_session_{self.current_exercise}{participant_str}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(data_dir, filename)

        session_data = {
            "metadata": {
                "exercise_type": self.current_exercise,
                "participant_id": participant_id,
                "session_date": datetime.now().isoformat(),
                "total_repetitions": stats["total_reps"],
                "average_duration": stats["average_duration"],
                "session_duration_seconds": len(self.pose_buffer) / 24.0,  # Approximate
            },
            "repetitions": self.exercise_detector.completed_reps,
            "summary": stats,
        }

        with open(filepath, "w") as f:
            json.dump(session_data, f, indent=2)

        print(f"💾 Session saved: {filepath}")
        return True

    # ...existing methods...


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


def render_window():
    cap = cv2.VideoCapture(0)

    # Set camera resolution for better quality display
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Initialize models
    model_path = "models/lightning.tflite"
    movenet_model = MoveNet(model_path)

    # Enable squat detection by default for testing
    movenet_model.set_exercise_mode("squat")

    import time

    prev_time = time.time()
    fps = 0
    fps_history = []
    target_fps = 24
    frame_duration = 1.0 / target_fps

    while cap.isOpened():
        loop_start = time.time()
        ret, frame = cap.read()
        if not ret:
            break

        # Store original frame for display
        display_frame = frame.copy()

        # Resize frame for processing (square aspect ratio for MoveNet)
        h, w = frame.shape[:2]
        h_pad = w_pad = 0  # Initialize padding values

        if h != w:
            # Make frame square by padding
            max_dim = max(h, w)
            h_pad = (max_dim - h) // 2
            w_pad = (max_dim - w) // 2
            frame = cv2.copyMakeBorder(
                frame, h_pad, h_pad, w_pad, w_pad, cv2.BORDER_CONSTANT
            )

        # Get predictions (MoveNet processes at 192x192 internally)
        keypoints_with_scores = movenet_model.predict(frame)

        # Scale keypoints back to display frame size
        display_h, display_w = display_frame.shape[:2]
        frame_h, frame_w = frame.shape[:2]

        # Adjust keypoints for display frame
        scaled_keypoints = keypoints_with_scores.copy()
        shaped_keypoints = np.squeeze(scaled_keypoints)

        # Scale coordinates from padded frame to original display frame
        for i in range(len(shaped_keypoints)):
            # Convert from normalized coordinates to padded frame coordinates
            y_padded = shaped_keypoints[i][0] * frame_h
            x_padded = shaped_keypoints[i][1] * frame_w

            # Remove padding offset
            y_original = y_padded - h_pad
            x_original = x_padded - w_pad

            # Normalize to display frame
            shaped_keypoints[i][0] = y_original / display_h
            shaped_keypoints[i][1] = x_original / display_w

        # Render keypoints on display frame
        draw_keypoints(display_frame, np.expand_dims(shaped_keypoints, axis=0), 0.4)
        draw_connections(
            display_frame,
            np.expand_dims(shaped_keypoints, axis=0),
            movenet_model.edges,
            0.4,
        )

        # Display exercise statistics on display frame
        stats = movenet_model.get_exercise_stats()
        if stats:
            y_offset = 30

            # Exercise type
            exercise_text = f"Exercise: {stats['exercise_type'].title()}"
            cv2.putText(
                display_frame,
                exercise_text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 0),
                2,
            )
            y_offset += 40

            # Repetition counter
            rep_text = f"Reps: {stats['total_reps']}"
            cv2.putText(
                display_frame,
                rep_text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                3,
            )
            y_offset += 40

            # Current state
            state_text = f"State: {stats['current_state']}"
            state_colors = {
                "standing": (255, 255, 255),
                "descending": (0, 255, 255),
                "ascending": (255, 165, 0),
                "bottom": (255, 0, 255),
            }
            color = state_colors.get(stats["current_state"], (255, 255, 255))
            cv2.putText(
                display_frame,
                state_text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
            )
            y_offset += 35

            # Tracking stability indicator
            stability = stats.get("tracking_stability", 0)
            stability_text = f"Tracking: {stability*100:.0f}%"
            stability_color = (
                (0, 255, 0)
                if stability > 0.7
                else (0, 165, 255) if stability > 0.4 else (0, 0, 255)
            )
            cv2.putText(
                display_frame,
                stability_text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                stability_color,
                2,
            )
            y_offset += 30

            # Average duration
            if stats["total_reps"] > 0:
                duration_text = f"Avg: {stats['average_duration']:.1f}s"
                cv2.putText(
                    display_frame,
                    duration_text,
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

        # Display buffer status
        buffer_status = f"Buffer: {len(movenet_model.pose_buffer)}/{movenet_model.pose_buffer.maxlen}"
        cv2.putText(
            display_frame,
            buffer_status,
            (10, display_frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )

        # Calculate and display FPS
        curr_time = time.time()
        fps = 1.0 / (curr_time - prev_time)
        prev_time = curr_time
        fps_history.append(fps)
        if len(fps_history) > 30:
            fps_history.pop(0)
        avg_fps = sum(fps_history) / len(fps_history)
        cv2.putText(
            display_frame,
            f"FPS: {avg_fps:.1f}",
            (display_frame.shape[1] - 120, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
        )

        # Resize display frame for larger window (optional)
        display_height = 800  # Larger display size
        aspect_ratio = display_frame.shape[1] / display_frame.shape[0]
        display_width = int(display_height * aspect_ratio)
        display_frame_large = cv2.resize(display_frame, (display_width, display_height))

        cv2.imshow("Rehabilitation Exercise Tracker", display_frame_large)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            # Save session before quitting
            if movenet_model.exercise_mode and movenet_model.exercise_detector:
                movenet_model.save_exercise_session()
            break
        elif key == ord("r"):
            # Reset repetition counter
            if movenet_model.exercise_detector:
                movenet_model.exercise_detector.reset_counter()
                print("🔄 Repetition counter reset")
        elif key == ord("s"):
            # Manual save session
            if movenet_model.exercise_mode and movenet_model.exercise_detector:
                movenet_model.save_exercise_session()
                print("💾 Session manually saved")

        # Limit frame rate to 24 FPS for stable performance and consistent
        elapsed = time.time() - loop_start
        if elapsed < frame_duration:
            time.sleep(frame_duration - elapsed)

    cap.release()
    cv2.destroyAllWindows()


def main():
    render_window()


if __name__ == "__main__":
    main()
