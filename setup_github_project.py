#!/usr/bin/env python3
"""
GitHub Project Setup Automation
Run this script to automatically create GitHub issues from the roadmap
"""

import subprocess
import json


# GitHub CLI commands to set up the project
def create_labels():
    """Create GitHub labels for the project"""
    labels = [
        {
            "name": "phase-1",
            "color": "0052cc",
            "description": "Phase 1: Core Foundation",
        },
        {
            "name": "phase-2",
            "color": "fbca04",
            "description": "Phase 2: Rehabilitation Features",
        },
        {
            "name": "phase-3",
            "color": "d93f0b",
            "description": "Phase 3: Clinical Integration",
        },
        {
            "name": "repetition-detection",
            "color": "0e8a16",
            "description": "Repetition detection features",
        },
        {
            "name": "classification",
            "color": "5319e7",
            "description": "Exercise classification",
        },
        {
            "name": "form-analysis",
            "color": "f9d0c4",
            "description": "Form quality analysis",
        },
        {
            "name": "rehabilitation",
            "color": "e11d21",
            "description": "Rehabilitation specific features",
        },
        {
            "name": "safety",
            "color": "b60205",
            "description": "Safety and monitoring features",
        },
        {
            "name": "reporting",
            "color": "c5def5",
            "description": "Data export and reporting",
        },
    ]

    for label in labels:
        cmd = f'gh label create "{label["name"]}" --color {label["color"]} --description "{label["description"]}"'
        print(f"Creating label: {label['name']}")
        subprocess.run(cmd, shell=True, capture_output=True)


def create_milestones():
    """Create GitHub milestones"""
    milestones = [
        {
            "title": "Repetition Detection",
            "description": "Implement basic exercise repetition detection",
        },
        {
            "title": "Exercise Classification",
            "description": "Add exercise type classification",
        },
        {
            "title": "Form Quality Assessment",
            "description": "Implement form quality scoring",
        },
        {"title": "Progress Tracking", "description": "Add patient progress tracking"},
        {"title": "Safety Features", "description": "Implement safety monitoring"},
        {
            "title": "Reporting & Export",
            "description": "Add clinical reporting features",
        },
    ]

    for milestone in milestones:
        cmd = f'gh api repos/:owner/:repo/milestones -f title="{milestone["title"]}" -f description="{milestone["description"]}"'
        print(f"Creating milestone: {milestone['title']}")
        subprocess.run(cmd, shell=True, capture_output=True)


def create_issues():
    """Create GitHub issues from roadmap"""
    issues = [
        {
            "title": "Implement basic squat repetition detection",
            "body": """## Description
Create algorithm to detect squat up/down phases using hip and knee keypoints.

## Acceptance Criteria
- [ ] Detect when squat starts (person begins descending)
- [ ] Detect bottom of squat position
- [ ] Detect when squat ends (person returns to standing)
- [ ] Handle edge cases (partial squats, holds, etc.)

## Technical Requirements
- Use hip (11,12) and knee (13,14) keypoints
- Implement state machine for squat phases
- Add confidence thresholds for detection

## Time Estimate
3-5 days""",
            "labels": ["enhancement", "phase-1", "repetition-detection"],
        },
        {
            "title": "Add repetition counting functionality",
            "body": """## Description
Count completed repetitions and display in UI.

## Acceptance Criteria
- [ ] Accurate rep counting for squats
- [ ] Display current rep count on screen
- [ ] Reset counter functionality
- [ ] Store rep count in session data

## Time Estimate
2-3 days""",
            "labels": ["enhancement", "phase-1", "repetition-detection"],
        },
        {
            "title": "Create RepetitionDetector class",
            "body": """## Description
Refactor repetition detection logic into a dedicated class for better organization.

## Acceptance Criteria
- [ ] Create RepetitionDetector class
- [ ] Move detection logic from MoveNet class
- [ ] Support multiple exercise types
- [ ] Maintain backward compatibility

## Time Estimate
2 days""",
            "labels": ["refactor", "phase-1", "repetition-detection"],
        },
        # Add more issues as needed...
    ]

    for issue in issues:
        labels_str = ",".join(issue["labels"])
        cmd = f'gh issue create --title "{issue["title"]}" --body "{issue["body"]}" --label "{labels_str}"'
        print(f"Creating issue: {issue['title']}")
        subprocess.run(cmd, shell=True, capture_output=True)


def setup_project_board():
    """Instructions for setting up project board"""
    print(
        """
=== PROJECT BOARD SETUP ===
1. Go to your GitHub repo
2. Click 'Projects' tab
3. Click 'New project'
4. Choose 'Board' template
5. Add these columns:
   - Backlog
   - Phase 1 - In Progress  
   - Phase 2 - Ready
   - Phase 3 - Future
   - Done

6. Drag issues to appropriate columns
    """
    )


if __name__ == "__main__":
    print("Setting up GitHub project automation...")
    print("\nNote: Make sure you have GitHub CLI installed and authenticated")
    print("Run: gh auth login")

    response = input("\nDo you want to create labels? (y/n): ")
    if response.lower() == "y":
        create_labels()

    response = input("Do you want to create milestones? (y/n): ")
    if response.lower() == "y":
        create_milestones()

    response = input("Do you want to create initial issues? (y/n): ")
    if response.lower() == "y":
        create_issues()

    setup_project_board()
    print("\nGitHub project setup complete!")
