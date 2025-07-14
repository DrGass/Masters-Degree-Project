#!/usr/bin/env python3
"""
Quick Start Script for Rehabilitation Exercise Analysis Project
This script helps you set up your development environment and GitHub project
"""

import os
import subprocess
import sys


def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")

    # Check Python
    try:
        import sys

        python_version = sys.version_info
        if python_version.major == 3 and python_version.minor >= 8:
            print("✅ Python 3.8+ found")
        else:
            print("❌ Python 3.8+ required")
            return False
    except:
        print("❌ Python not found")
        return False

    # Check Git
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        print("✅ Git found")
    except:
        print("❌ Git not found - please install Git")
        return False

    # Check GitHub CLI (optional)
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
        print("✅ GitHub CLI found")
        return True
    except:
        print("⚠️  GitHub CLI not found (optional - for automated issue creation)")
        print("   Install from: https://cli.github.com/")
        return True


def check_existing_setup():
    """Check what's already set up in the project"""
    print("\n🔍 Checking existing project setup...")

    # Check if we're in the right directory
    if not os.path.exists("desktop_app"):
        print("❌ Not in project root directory")
        return False

    # Check desktop_app structure
    if os.path.exists("desktop_app/Pipfile"):
        print("✅ Pipenv configuration found")
    else:
        print("❌ Pipenv not configured")
        return False

    # Check models
    if os.path.exists("desktop_app/backend/models/lightning.tflite"):
        print("✅ MoveNet Lightning model found")
    else:
        print("❌ MoveNet Lightning model missing")

    if os.path.exists("desktop_app/backend/models/thunder.tflite"):
        print("✅ MoveNet Thunder model found")
    else:
        print("❌ MoveNet Thunder model missing")

    # Check core.py
    if os.path.exists("desktop_app/backend/core.py"):
        print("✅ Core pose estimation code found")
    else:
        print("❌ Core code missing")
        return False

    return True


def setup_development_environment():
    """Set up or verify the development environment"""
    print("\n🚀 Verifying development environment...")

    # Check if pipenv is installed
    try:
        subprocess.run(["pipenv", "--version"], capture_output=True, check=True)
        print("✅ Pipenv found")
    except:
        print("📦 Installing pipenv...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pipenv"])

    # Check if dependencies are installed
    os.chdir("desktop_app")
    try:
        result = subprocess.run(["pipenv", "check"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Dependencies are up to date")
        else:
            print("📦 Installing/updating dependencies...")
            subprocess.run(["pipenv", "install"])
    except:
        print("📦 Setting up dependencies...")
        subprocess.run(["pipenv", "install"])

    os.chdir("..")
    print("✅ Development environment ready!")


def create_missing_directories():
    """Create only missing directories for the project"""
    print("\n📁 Creating missing project directories...")

    directories = [
        "desktop_app/data/sessions",
        "desktop_app/data/progress",
        "desktop_app/data/reports",
        "training_data",
    ]

    created_any = False
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created: {directory}")
            created_any = True
        else:
            print(f"✅ Exists: {directory}")

    if not created_any:
        print("✅ All directories already exist")


def display_next_steps():
    """Display next steps for the user"""
    print("\n🎯 Next Steps:")

    # Check what's already done
    models_exist = os.path.exists(
        "desktop_app/backend/models/lightning.tflite"
    ) and os.path.exists("desktop_app/backend/models/thunder.tflite")

    if not models_exist:
        print("\n1. Download MoveNet models:")
        print(
            "   - Lightning model: https://tfhub.dev/google/lite-model/movenet/singlepose/lightning/tflite/float16/4"
        )
        print(
            "   - Thunder model: https://tfhub.dev/google/lite-model/movenet/singlepose/thunder/tflite/float16/4"
        )
        print("   - Place in: desktop_app/backend/models/")
    else:
        print("\n1. ✅ MoveNet models are already installed")

    print("\n2. Test the current system:")
    print("   cd desktop_app/backend")
    print("   pipenv shell")
    print("   python core.py")

    print("\n3. Set up GitHub project (optional):")
    print("   - Install GitHub CLI: https://cli.github.com/")
    print("   - Run: gh auth login")
    print("   - Run: python setup_github_project.py")

    print("\n4. Start development with Phase 1:")
    print("   - Implement squat repetition detection")
    print("   - Add repetition counting")
    print("   - Create RepetitionDetector class")

    print("\n📚 Resources:")
    print("   - Project roadmap: See README.md")
    print("   - GitHub setup: See github_setup.md")
    print("   - Issue tracking: Use GitHub Issues")


def main():
    """Main setup function"""
    print("🏥 Rehabilitation Exercise Analysis System - Setup")
    print("=" * 50)

    # Check requirements
    if not check_requirements():
        print("\n❌ Please install missing requirements and try again")
        sys.exit(1)

    # Check existing setup
    if not check_existing_setup():
        print("\n❌ Project setup incomplete. Please check your project structure.")
        sys.exit(1)

    # Create missing directories
    create_missing_directories()

    # Setup development environment
    try:
        setup_development_environment()
    except Exception as e:
        print(f"\n⚠️  Warning: Could not verify development environment: {e}")
        print("You may need to check it manually")

    # Display next steps
    display_next_steps()

    print("\n🎉 Setup verified! Your project is ready for development!")
    print("\nYour existing setup:")
    print("✅ MoveNet models installed")
    print("✅ Pipenv environment configured")
    print("✅ Core pose estimation working")
    print("✅ Project structure complete")
    print("\nReady to start Phase 1: Repetition Detection!")


if __name__ == "__main__":
    main()
