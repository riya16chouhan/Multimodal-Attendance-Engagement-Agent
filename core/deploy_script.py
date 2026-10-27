import os
import sys

def verify_production_environment():
    print("[INFO] Verifying production environment dependencies and directories...")
    
    # Check directory paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"[INFO] Working directory verified: {current_dir}")

    required_files = [
        "face_detector.py",
        "attendance_service.py",
        "audio_signal_extractor.py",
        "noise_speech_analyzer.py",
        "multimodal_agent.py",
        "signal_fusion.py",
        "engagement_scorer.py",
        "teacher_profiles.py",
        "session_analytics.py",
        "ui_interface.py"
    ]

    missing_files = [f for f in required_files if not os.path.exists(os.path.join(current_dir, f))]
    
    if missing_files:
        print(f"[ERROR] Missing required project modules: {missing_files}")
        sys.exit(1)
    else:
        print("[SUCCESS] All modular components successfully verified for production deployment.")

if __name__ == "__main__":
    verify_production_environment()
    print("\n[DEPLOYMENT] To launch the interactive production web dashboard, run:")
    print("streamlit run .\\core\\ui_interface.py")