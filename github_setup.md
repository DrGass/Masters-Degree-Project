# GitHub Project Setup

## Issues to Create

### Phase 1: Core Foundation

#### Milestone 1.1: Repetition Detection System
- [ ] **Issue 1**: Implement basic squat repetition detection
  - Description: Create algorithm to detect squat up/down phases using hip and knee keypoints
  - Labels: enhancement, phase-1, repetition-detection
  - Assignee: You
  - Milestone: Repetition Detection

- [ ] **Issue 2**: Add repetition counting functionality
  - Description: Count completed repetitions and display in UI
  - Labels: enhancement, phase-1, repetition-detection
  - Milestone: Repetition Detection

- [ ] **Issue 3**: Create RepetitionDetector class
  - Description: Separate repetition logic into dedicated class
  - Labels: refactor, phase-1, repetition-detection
  - Milestone: Repetition Detection

#### Milestone 1.2: Exercise Classification
- [ ] **Issue 4**: Implement exercise type detection
  - Description: Classify between squats, lunges, arm raises
  - Labels: enhancement, phase-1, classification
  - Milestone: Exercise Classification

- [ ] **Issue 5**: Add exercise state tracking
  - Description: Track current phase of exercise (up/down/neutral)
  - Labels: enhancement, phase-1, classification
  - Milestone: Exercise Classification

### Phase 2: Rehabilitation Features

#### Milestone 2.1: Form Quality Assessment
- [ ] **Issue 6**: Implement joint angle calculations
  - Description: Calculate knee, hip, shoulder angles for form analysis
  - Labels: enhancement, phase-2, form-analysis
  - Milestone: Form Quality

- [ ] **Issue 7**: Create form scoring system
  - Description: Score exercise form based on angle ranges and movement patterns
  - Labels: enhancement, phase-2, form-analysis
  - Milestone: Form Quality

- [ ] **Issue 8**: Add range of motion measurements
  - Description: Track and measure ROM for rehabilitation progress
  - Labels: enhancement, phase-2, rehabilitation
  - Milestone: Form Quality

#### Milestone 2.2: Progress Tracking
- [ ] **Issue 9**: Implement patient session management
  - Description: Create system to track patient sessions over time
  - Labels: enhancement, phase-2, data-management
  - Milestone: Progress Tracking

- [ ] **Issue 10**: Add progress metrics calculation
  - Description: Calculate improvement metrics and trends
  - Labels: enhancement, phase-2, analytics
  - Milestone: Progress Tracking

### Phase 3: Clinical Integration

#### Milestone 3.1: Safety Features
- [ ] **Issue 11**: Implement movement limitation warnings
  - Description: Alert when movements exceed safe ranges
  - Labels: enhancement, phase-3, safety
  - Milestone: Safety Features

- [ ] **Issue 12**: Add emergency stop mechanism
  - Description: Quick way to stop exercise if issues detected
  - Labels: enhancement, phase-3, safety
  - Milestone: Safety Features

#### Milestone 3.2: Reporting & Export
- [ ] **Issue 13**: Generate progress reports
  - Description: Create PDF/HTML reports for therapists
  - Labels: enhancement, phase-3, reporting
  - Milestone: Reporting

- [ ] **Issue 14**: Export data for clinical review
  - Description: Export session data in clinical formats
  - Labels: enhancement, phase-3, reporting
  - Milestone: Reporting

## GitHub CLI Commands to Create Issues

```bash
# Install GitHub CLI first: https://cli.github.com/

# Create issues (run from your repo directory)
gh issue create --title "Implement basic squat repetition detection" --body "Create algorithm to detect squat up/down phases using hip and knee keypoints" --label "enhancement,phase-1,repetition-detection"

gh issue create --title "Add repetition counting functionality" --body "Count completed repetitions and display in UI" --label "enhancement,phase-1,repetition-detection"

gh issue create --title "Create RepetitionDetector class" --body "Separate repetition logic into dedicated class" --label "refactor,phase-1,repetition-detection"

# Continue for all issues...
```

## Project Board Setup

1. Go to your GitHub repo
2. Click "Projects" tab
3. Create new project
4. Choose "Board" template
5. Add columns:
   - Backlog
   - Phase 1 - In Progress
   - Phase 2 - Ready
   - Phase 3 - Future
   - Done

## Labels to Create

- `phase-1` (blue)
- `phase-2` (yellow) 
- `phase-3` (red)
- `repetition-detection` (green)
- `classification` (purple)
- `form-analysis` (orange)
- `rehabilitation` (pink)
- `safety` (dark red)
- `reporting` (light blue)
