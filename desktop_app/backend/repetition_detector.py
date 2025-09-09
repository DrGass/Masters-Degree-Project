import numpy as np
import math
from collections import deque
from datetime import datetime


class SquatDetector:
    def __init__(self):
        self.state = "standing"  # standing, descending, bottom, ascending
        self.rep_count = 0
        self.current_rep_frames = []
        self.completed_reps = []

        # Thresholds for squat detection - more lenient for partial visibility
        self.hip_knee_angle_threshold = 120  # degrees
        self.min_descent_frames = (
            8  # minimum frames for descent phase (further reduced)
        )
        self.min_ascent_frames = 8  # minimum frames for ascent phase (further reduced)

        # State tracking
        self.state_frame_count = 0
        self.last_hip_knee_angle = None
        self.descent_start_frame = None

        # Angle smoothing for stability during movement
        self.angle_history = deque(maxlen=5)  # Keep last 5 angles for smoothing
        self.frames_without_detection = 0
        self.max_frames_without_detection = 15  # Allow 15 frames of missing data

        # State persistence - prevent flickering between states
        self.state_confidence = 0
        self.min_state_confidence = 2  # Need 2 consistent readings to change state
        self.pending_state = None

    def calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points"""
        try:
            # Convert to numpy arrays
            p1 = np.array(point1)
            p2 = np.array(point2)  # vertex
            p3 = np.array(point3)

            # Calculate vectors
            v1 = p1 - p2
            v2 = p3 - p2

            # Calculate angle using dot product
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            cos_angle = np.clip(cos_angle, -1.0, 1.0)  # Handle numerical errors
            angle = math.degrees(math.acos(cos_angle))

            return angle
        except:
            return None

    def get_smoothed_angle(self, keypoints):
        """Get hip-knee angle with temporal smoothing to handle unstable keypoints"""
        try:
            # Ensure we have enough keypoints
            if len(keypoints) < 10:
                return None

            best_angle = None
            best_confidence = 0

            # Try both sides and pick the one with higher confidence
            sides = [
                (12, 14, 16, "right"),  # right_hip, right_knee, right_ankle
                (11, 13, 15, "left"),  # left_hip, left_knee, left_ankle
            ]

            for hip_idx, knee_idx, ankle_idx, side_name in sides:
                # Check if all three points have reasonable confidence
                hip_conf = keypoints[hip_idx][2]
                knee_conf = keypoints[knee_idx][2]
                ankle_conf = keypoints[ankle_idx][2]

                # Use even more lenient threshold and consider combined confidence
                min_confidence = 0.1
                avg_confidence = (hip_conf + knee_conf + ankle_conf) / 3

                if (
                    hip_conf > min_confidence
                    and knee_conf > min_confidence
                    and ankle_conf > min_confidence
                ):
                    hip = keypoints[hip_idx][:2]
                    knee = keypoints[knee_idx][:2]
                    ankle = keypoints[ankle_idx][:2]

                    angle = self.calculate_angle(hip, knee, ankle)
                    if angle is not None and avg_confidence > best_confidence:
                        best_angle = angle
                        best_confidence = avg_confidence

            if best_angle is not None:
                # Add to history for smoothing
                self.angle_history.append(best_angle)
                self.frames_without_detection = 0

                # Return smoothed angle (median of recent measurements)
                if len(self.angle_history) >= 3:
                    sorted_angles = sorted(list(self.angle_history))
                    return sorted_angles[len(sorted_angles) // 2]  # median
                else:
                    return best_angle
            else:
                self.frames_without_detection += 1

                # If we've lost tracking but have recent history, use last known angle
                if (
                    self.frames_without_detection <= self.max_frames_without_detection
                    and len(self.angle_history) > 0
                ):
                    return list(self.angle_history)[-1]  # Return last known angle

            return None

        except Exception as e:
            self.frames_without_detection += 1
            return None

    def update_state_with_confidence(self, new_state):
        """Update state only after consistent readings to prevent flickering"""
        if new_state == self.state:
            self.state_confidence = min(self.state_confidence + 1, 10)
            self.pending_state = None
        elif new_state == self.pending_state:
            self.state_confidence += 1
            if self.state_confidence >= self.min_state_confidence:
                self.state = new_state
                self.state_confidence = 0
                self.pending_state = None
        else:
            self.pending_state = new_state
            self.state_confidence = 0

    def _extract_detailed_keypoints(self, keypoints):
        """Extract detailed keypoint information for training"""
        if len(keypoints) < 17:
            return None

        detailed_keypoints = {}
        landmark_names = [
            "nose",
            "left_eye",
            "right_eye",
            "left_ear",
            "right_ear",
            "left_shoulder",
            "right_shoulder",
            "left_elbow",
            "right_elbow",
            "left_wrist",
            "right_wrist",
            "left_hip",
            "right_hip",
            "left_knee",
            "right_knee",
            "left_ankle",
            "right_ankle",
        ]

        for i, name in enumerate(landmark_names):
            if i < len(keypoints):
                detailed_keypoints[name] = {
                    "x": float(keypoints[i][0]),
                    "y": float(keypoints[i][1]),
                    "confidence": float(keypoints[i][2]),
                }

        return detailed_keypoints

    def _extract_confidence_scores(self, keypoints):
        """Extract confidence scores for all keypoints"""
        if len(keypoints) < 17:
            return None

        return [float(kp[2]) for kp in keypoints]

    def _calculate_biomechanics(self, keypoints):
        """Calculate biomechanical measurements for training"""
        try:
            if len(keypoints) < 17:
                return None

            biomechanics = {}

            # Key angles for squat analysis
            # Right side angles
            if all(keypoints[i][2] > 0.1 for i in [12, 14, 16]):  # hip, knee, ankle
                right_knee_angle = self.calculate_angle(
                    keypoints[12][:2], keypoints[14][:2], keypoints[16][:2]
                )
                biomechanics["right_knee_angle"] = right_knee_angle

            # Left side angles
            if all(keypoints[i][2] > 0.1 for i in [11, 13, 15]):  # hip, knee, ankle
                left_knee_angle = self.calculate_angle(
                    keypoints[11][:2], keypoints[13][:2], keypoints[15][:2]
                )
                biomechanics["left_knee_angle"] = left_knee_angle

            # Hip angle (trunk lean)
            if all(keypoints[i][2] > 0.1 for i in [5, 11, 13]):  # shoulder, hip, knee
                right_hip_angle = self.calculate_angle(
                    keypoints[5][:2], keypoints[11][:2], keypoints[13][:2]
                )
                biomechanics["trunk_lean_angle"] = right_hip_angle

            # Ankle angle
            if all(keypoints[i][2] > 0.1 for i in [14, 16]):  # knee, ankle
                # Calculate ankle dorsiflexion (approximate)
                ankle_y_diff = keypoints[16][1] - keypoints[14][1]
                biomechanics["ankle_dorsiflexion"] = float(ankle_y_diff)

            # Hip width (stance width)
            if all(keypoints[i][2] > 0.1 for i in [11, 12]):  # left_hip, right_hip
                hip_width = abs(keypoints[12][0] - keypoints[11][0])
                biomechanics["hip_width"] = float(hip_width)

            # Knee tracking (knee valgus/varus)
            if all(keypoints[i][2] > 0.1 for i in [11, 13, 15]):  # hip, knee, ankle
                knee_deviation = keypoints[13][0] - (
                    (keypoints[11][0] + keypoints[15][0]) / 2
                )
                biomechanics["left_knee_deviation"] = float(knee_deviation)

            if all(keypoints[i][2] > 0.1 for i in [12, 14, 16]):  # hip, knee, ankle
                knee_deviation = keypoints[14][0] - (
                    (keypoints[12][0] + keypoints[16][0]) / 2
                )
                biomechanics["right_knee_deviation"] = float(knee_deviation)

            return biomechanics

        except Exception as e:
            return None

    def detect_squat_phase(self, keypoints):
        """Detect current phase of squat movement with comprehensive data collection"""
        current_angle = self.get_smoothed_angle(keypoints)

        if current_angle is None:
            # If we've lost tracking for too long, reset to standing
            if self.frames_without_detection > self.max_frames_without_detection:
                if self.state != "standing":
                    print(f"⚠️ Lost tracking, resetting to standing")
                    self.state = "standing"
                    self.state_frame_count = 0
            return self.state, False

        rep_completed = False

        # Store comprehensive frame data for training
        frame_data = {
            "timestamp": datetime.now().isoformat(),
            "frame_number": len(self.current_rep_frames),
            "state": self.state,
            "hip_knee_angle": current_angle,
            "frames_without_detection": self.frames_without_detection,
            "keypoints_raw": (
                keypoints.tolist() if hasattr(keypoints, "tolist") else keypoints
            ),
            "keypoints_detailed": self._extract_detailed_keypoints(keypoints),
            "biomechanics": self._calculate_biomechanics(keypoints),
            "confidence_scores": self._extract_confidence_scores(keypoints),
        }

        # Determine what state we should be in based on angle
        suggested_state = self.state

        if self.state == "standing":
            if current_angle < self.hip_knee_angle_threshold - 5:  # Add hysteresis
                suggested_state = "descending"

        elif self.state == "descending":
            # Look for reversal in angle trend
            if (
                self.last_hip_knee_angle is not None
                and current_angle > self.last_hip_knee_angle + 3
            ):  # Reduced threshold
                if self.state_frame_count >= self.min_descent_frames:
                    suggested_state = "ascending"
                else:
                    # Too short descent, reset
                    suggested_state = "standing"
                    self.current_rep_frames = []

        elif self.state == "ascending":
            if current_angle >= self.hip_knee_angle_threshold + 5:  # Add hysteresis
                if self.state_frame_count >= self.min_ascent_frames:
                    # Complete repetition detected!
                    suggested_state = "standing"
                    self.rep_count += 1
                    rep_completed = True

                    # Store completed repetition with comprehensive data
                    rep_data = {
                        "rep_number": self.rep_count,
                        "start_timestamp": (
                            self.current_rep_frames[0]["timestamp"]
                            if self.current_rep_frames
                            else None
                        ),
                        "end_timestamp": frame_data["timestamp"],
                        "total_frames": len(self.current_rep_frames)
                        + 1,  # +1 for current frame
                        "duration_seconds": (len(self.current_rep_frames) + 1) / 24.0,
                        "frames": self.current_rep_frames
                        + [frame_data],  # Include current frame
                        "biomechanical_summary": self._summarize_rep_biomechanics(
                            self.current_rep_frames + [frame_data]
                        ),
                    }
                    self.completed_reps.append(rep_data)
                    self.current_rep_frames = []
                    self.state_frame_count = 0

        # Update state with confidence checking
        if suggested_state != self.state:
            self.update_state_with_confidence(suggested_state)

        # Reset state frame count when transitioning
        if suggested_state != self.state:
            if suggested_state == "descending":
                self.descent_start_frame = len(self.current_rep_frames)
                self.state_frame_count = 0
            elif suggested_state == "ascending":
                self.state_frame_count = 0
            elif suggested_state == "standing" and not rep_completed:
                self.state_frame_count = 0

        # Add current frame to rep data (only if not completed - completed reps already have it)
        if not rep_completed:
            self.current_rep_frames.append(frame_data)

        self.last_hip_knee_angle = current_angle
        self.state_frame_count += 1

        return self.state, rep_completed

    def _summarize_rep_biomechanics(self, frames):
        """Summarize biomechanical data across the entire repetition"""
        if not frames:
            return None

        try:
            # Extract angles throughout the movement
            angles = [
                f["hip_knee_angle"] for f in frames if f["hip_knee_angle"] is not None
            ]

            summary = {
                "max_depth_angle": min(angles) if angles else None,
                "angle_range": max(angles) - min(angles) if angles else None,
                "total_frames": len(frames),
                "stable_tracking_frames": sum(
                    1 for f in frames if f["frames_without_detection"] == 0
                ),
                "average_confidence": None,
            }

            # Calculate average confidence across all keypoints and frames
            all_confidences = []
            for frame in frames:
                if frame.get("confidence_scores"):
                    all_confidences.extend(frame["confidence_scores"])

            if all_confidences:
                summary["average_confidence"] = sum(all_confidences) / len(
                    all_confidences
                )

            return summary

        except Exception as e:
            return None

    def get_rep_stats(self):
        """Get statistics about completed repetitions"""
        stats = {
            "total_reps": self.rep_count,
            "current_state": self.state,
            "current_rep_frames": len(self.current_rep_frames),
            "tracking_stability": max(
                0,
                1.0
                - (self.frames_without_detection / self.max_frames_without_detection),
            ),
        }

        if self.completed_reps:
            durations = [rep["duration_seconds"] for rep in self.completed_reps]
            stats.update(
                {
                    "average_duration": sum(durations) / len(durations),
                    "last_rep_duration": durations[-1] if durations else 0,
                }
            )
        else:
            stats.update({"average_duration": 0, "last_rep_duration": 0})

        return stats

    def reset_counter(self):
        """Reset the repetition counter"""
        self.rep_count = 0
        self.completed_reps = []
        self.current_rep_frames = []
        self.state = "standing"
        self.state_frame_count = 0
        self.angle_history.clear()
        self.frames_without_detection = 0
        self.state_confidence = 0
        self.pending_state = None
