import streamlit as st
import cv2
import time
from face_detector import FaceDetectorTracker
from attendance_service import AttendanceService
from audio_signal_extractor import AudioSignalExtractor
from noise_speech_analyzer import NoiseAndSpeechAnalyzer
from multimodal_agent import MultimodalAgent
from signal_fusion import SignalFusionEngine
from engagement_scorer import EngagementScorer
from teacher_profiles import RecommendationsEngine, TeacherProfileService

st.set_page_config(page_title="Multimodal Attendance & Engagement Agent", layout="wide")

st.title("🎓 Multimodal Attendance & Engagement Agent Dashboard")
st.sidebar.header("Session Configuration")

# Instructor & Mode Selection
teacher_name = st.sidebar.text_input("Teacher Name", "Prof. Riya Chouhan")
instruction_mode = st.sidebar.selectbox("Instruction Mode", ["Human Instructor", "Autonomous AI Instructor (MannMitra)"])
duration_threshold = st.sidebar.slider("Presence Duration Threshold (s)", 5, 60, 15)

run_session = st.sidebar.checkbox("Start Live Session", value=False)
frame_placeholder = st.empty()
metrics_placeholder = st.empty()

def run_streamlit_agent():
    cap = cv2.VideoCapture(0)
    tracker = FaceDetectorTracker()
    attendance = AttendanceService(presence_threshold_seconds=duration_threshold)
    audio_extractor = AudioSignalExtractor(sample_rate=16000, chunk_duration=1.0)
    speech_analyzer = NoiseAndSpeechAnalyzer(rms_threshold=0.015)
    
    multimodal_agent = MultimodalAgent()
    fusion_engine = SignalFusionEngine(window_size_seconds=5.0)
    engagement_scorer = EngagementScorer()
    recommendations_engine = RecommendationsEngine()

    audio_extractor.start_stream()
    current_vad_status = "Background Noise / Silence"
    current_rms = 0.0
    is_speech = False

    try:
        while run_session and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.warning("Failed to capture video frame.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = tracker.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            tracked_faces = tracker.update(faces)
            attendance.process_frame(tracked_faces)

            if not audio_extractor.audio_queue.empty():
                chunk = audio_extractor.audio_queue.get()
                vad_result = speech_analyzer.detect_speech_activity(chunk)
                current_vad_status = vad_result["status"]
                current_rms = vad_result["rms_energy"]
                is_speech = vad_result["is_speech"]

            fusion_engine.add_signal_sample(len(tracked_faces), current_rms, is_speech)
            fused_metrics = fusion_engine.get_fused_metrics()
            agent_insight = multimodal_agent.evaluate_classroom_state(tracked_faces, current_vad_status)
            score_data = engagement_scorer.calculate_score(fused_metrics, expected_participants=1.0)

            # Draw visual bounding boxes
            for object_id, data in tracked_faces.items():
                (x, y, w, h) = data["bbox"]
                record = attendance.session_records.get(object_id)
                is_present = record and record["marked_present"]
                color = (0, 255, 0) if is_present else (0, 165, 255)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, f"ID: {object_id}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Convert frame for Streamlit display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)

            with metrics_placeholder.container():
                cols = st.columns(3)
                cols[0].metric("Classroom State", agent_insight["classroom_state"])
                cols[1].metric("Engagement Score", score_data["engagement_score"], score_data["engagement_tier"])
                cols[2].metric("Active Participants", len(tracked_faces))

            time.sleep(0.03)
    finally:
        audio_extractor.stop_stream()
        cap.release()

if run_session:
    run_streamlit_agent()
else:
    st.info("Check 'Start Live Session' in the sidebar to initiate the agent interface.")