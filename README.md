# Rehabilitation Exercise Analysis System

**Podręczna Fizjoterapia/Pomocnik Fizjoterapeuty** - Aplikacja pomagająca pacjentom w poprawnym wykonywaniu ćwiczeń i w kontakcie z fizjoterapeutą.

**Handy Physiotherapy/Physiotherapist's Assistant** - An application helping patients in performing exercises correctly and in contact with a physiotherapist.

A computer vision-based application for real-time exercise form analysis and rehabilitation progress tracking using pose estimation technology.

## 🎯 Project Overview

This system uses Google's MoveNet pose estimation model to analyze exercise form in real-time, specifically designed for rehabilitation and physical therapy applications. The application can detect exercise repetitions, assess movement quality, and track patient progress over time.

Aplikacja ma za zadanie umożliwić każdemu kto posiada komputer/laptop oraz kamerę na wykonywanie ćwiczeń w domu. Aplikacja będzie posiadać bazę ćwiczeń, które będą dostosowane do potrzeb pacjenta. Fizjoterapeuta będzie mógł kontrolować wyniki pacjenta korzystając z raportów dostarczanych po każdych ćwiczeniach. Pacjent będzie mógł się również bezpośrednio kontaktować się z fizjoterapeutą w razie jakichkolwiek pytań.

## ✨ Key Features

### Current Features
- ✅ Real-time pose estimation using MoveNet
- ✅ Live keypoint visualization and skeleton overlay
- ✅ Pose sequence buffering for temporal analysis
- ✅ Data collection system for training ML models
- ✅ Session data export in JSON format

### Planned Features (See [Roadmap](#roadmap))
- 🔄 Exercise repetition detection and counting
- 🔄 Exercise type classification (squats, lunges, arm raises)
- 🔄 Form quality assessment and scoring
- 🔄 Patient progress tracking over time
- 🔄 Safety monitoring and movement limitation warnings
- 🔄 Clinical reporting and data export

## 🏥 Target Use Cases

- **Rehabilitation Centers**: Objective movement assessment and progress tracking
- **Physical Therapy**: Exercise form correction and compliance monitoring  
- **Home Recovery**: Supervised remote rehabilitation sessions
- **Research**: Data collection for movement analysis studies

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Webcam or camera device
- Windows 10+ (currently optimized for Windows)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/rehabilitation-exercise-analysis.git
   cd rehabilitation-exercise-analysis
   ```

2. **Set up Python environment**
   ```bash
   cd desktop_app
   pip install pipenv
   pipenv install
   pipenv shell
   ```

3. **Download models**
   - Download MoveNet models and place in `desktop_app/backend/models/`
   - `lightning.tflite` (faster, less accurate)
   - `thunder.tflite` (slower, more accurate)

4. **Run the application**
   ```bash
   cd backend
   python core.py
   ```

## 🏗️ Architecture

```
Masters-Degree-Project/
├── desktop_app/                # Main application
│   ├── backend/
│   │   ├── core.py            # Main MoveNet wrapper and pose estimation
│   │   ├── models/            # TensorFlow Lite models
│   │   │   ├── lightning.tflite
│   │   │   └── thunder.tflite
│   │   └── __init__.py
│   ├── frontend/              # Future GUI components
│   ├── Pipfile               # Python dependencies
│   └── Pipfile.lock
├── fast_api/                  # Future API backend
└── docker/                   # Docker configuration
```

## 🔧 Core Components

### MoveNet Class
Main pose estimation engine that:
- Loads and runs TensorFlow Lite models
- Processes video frames in real-time
- Maintains pose sequence buffers
- Handles data collection and export

### Key Functions
- `predict(frame)`: Run pose estimation on a single frame
- `draw_keypoints()`: Visualize detected body keypoints
- `draw_connections()`: Draw skeleton connections
- `render_window()`: Main application loop with camera input

## 📊 Data Format

### Keypoint Structure
The system detects 17 body keypoints:
```python
landmarks = {
    0: "nose", 1: "left_eye", 2: "right_eye",
    3: "left_ear", 4: "right_ear",
    5: "left_shoulder", 6: "right_shoulder",
    7: "left_elbow", 8: "right_elbow", 
    9: "left_wrist", 10: "right_wrist",
    11: "left_hip", 12: "right_hip",
    13: "left_knee", 14: "right_knee",
    15: "left_ankle", 16: "right_ankle"
}
```

### Session Data Export
```json
{
  "metadata": {
    "exercise": "squat",
    "quality": "good", 
    "participant_id": "patient_001",
    "rep_number": 1,
    "total_frames": 120
  },
  "poses": [
    {
      "timestamp": "2025-07-14T10:30:00",
      "keypoints": [[y1, x1, confidence1], ...],
      "frame_shape": [480, 640, 3]
    }
  ]
}
```

## 🗺️ Development Roadmap

### Phase 1: Core Foundation (Weeks 1-4)
- [ ] **Milestone 1.1**: Repetition Detection System
  - Exercise repetition start/end detection
  - Repetition counting functionality  
  - RepetitionDetector class implementation

- [ ] **Milestone 1.2**: Exercise Classification
  - Exercise type detection (squats, lunges, etc.)
  - Exercise state tracking (up/down phases)

### Phase 2: Rehabilitation Features (Weeks 5-10)
- [ ] **Milestone 2.1**: Form Quality Assessment
  - Joint angle calculations
  - Form scoring algorithms
  - Range of motion measurements

- [ ] **Milestone 2.2**: Progress Tracking
  - Patient session management
  - Progress metrics over time
  - Exercise prescription tracking

### Phase 3: Clinical Integration (Weeks 11-14)
- [ ] **Milestone 3.1**: Safety Features
  - Movement limitation warnings
  - Emergency stop mechanisms
  - Pain/discomfort detection prompts

- [ ] **Milestone 3.2**: Reporting & Export
  - Progress report generation
  - Clinical data export
  - Healthcare system integration

## 🐳 Docker Setup (Future API)

For the FastAPI backend:
```bash
cd fast_api
docker compose -f ./docker/docker-compose.yml -p entrustment-app --env-file ./backend/.env up --build
```

## 🤝 Contributing

This is currently a research/thesis project. Contributions and feedback are welcome!

### Development Setup
1. Fork the repository
2. Create a feature branch from main
3. Follow the existing code style
4. Add tests for new functionality
5. Submit a pull request

### Issue Labels
- `phase-1`, `phase-2`, `phase-3`: Development phases
- `repetition-detection`: Repetition counting features
- `classification`: Exercise type classification
- `form-analysis`: Movement quality assessment
- `rehabilitation`: Healthcare-specific features
- `safety`: Safety and monitoring
- `reporting`: Data export and reporting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google's MoveNet team for the pose estimation models
- TensorFlow team for the machine learning framework
- OpenCV community for computer vision tools

---

**⚠️ Disclaimer**: This software is for research and educational purposes. It is not intended to replace professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers for medical decisions.