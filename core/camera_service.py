import cv2
import time
from face_detector import FaceDetectorTracker
from attendance_service import AttendanceService
from audio_signal_extractor import AudioSignalExtractor
from noise_speech_analyzer import NoiseAndSpeechAnalyzer
from multimodal_agent import MultimodalAgent
from signal_fusion import SignalFusionEngine
from engagement_scorer import EngagementScorer

# Epic 5 Imports
from teacher_profiles import RecommendationsEngine, TeacherProfileService
from session_analytics import SessionAnalyticsGenerator

def main(video_source=0):
    # Prompt user for teacher/instructor name at startup (Activity 5.1/5.2)
    teacher_name = input("Please enter the teacher's name for this session: ").strip()
    if not teacher_name:
        teacher_name = "Prof. Riya Chouhan"  # Fallback default

    print(f"\n[INFO] Session initialized with Instructor: {teacher_name}")

    cap = cv2.VideoCapture(video_source)
    tracker = FaceDetectorTracker()
    attendance = AttendanceService(presence_threshold_seconds=15)

    audio_extractor = AudioSignalExtractor(sample_rate=16000, chunk_duration=1.0)
    speech_analyzer = NoiseAndSpeechAnalyzer(rms_threshold=0.015)

    # AI & Analytics Modules
    multimodal_agent = MultimodalAgent()
    fusion_engine = SignalFusionEngine(window_size_seconds=5.0)
    engagement_scorer = EngagementScorer()
    
    # Epic 5 Engines
    teacher_profile_service = TeacherProfileService()
    recommendations_engine = RecommendationsEngine()
    analytics_gen = SessionAnalyticsGenerator()

    # Fetch instructor profile details
    teacher_profile = teacher_profile_service.get_profile("human_teacher")
    teacher_profile["name"] = teacher_name  # Update with user's inputted name

    print(f"Starting Multimodal Attendance & Engagement Agent for {teacher_profile['name']}...")
    audio_extractor.start_stream()

    fused_metrics = {"speech_ratio": 0.0}
    score_data = {"engagement_score": 0.0, "engagement_tier": "Initializing"}

    try:
        current_vad_status = "Background Noise / Silence"
        current_rms = 0.0
        is_speech = False

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
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

            # 1. Signal Fusion & Scoring
            fusion_engine.add_signal_sample(len(tracked_faces), current_rms, is_speech)
            fused_metrics = fusion_engine.get_fused_metrics()
            agent_insight = multimodal_agent.evaluate_classroom_state(tracked_faces, current_vad_status)
            score_data = engagement_scorer.calculate_score(fused_metrics, expected_participants=1.0)

            # 2. Real-time Teacher Recommendations (Activity 5.1)
            dummy_status = {"people": [{"id": oid, "attention": 60} for oid in tracked_faces.keys()]}
            recs = recommendations_engine.generate_realtime_recommendations(dummy_status)

            # Render Overlay Information on Video Feed
            cv2.putText(frame, f"Instructor: {teacher_profile['name']}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame, f"State: {agent_insight['classroom_state']}", (20, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            cv2.putText(frame, f"Score: {score_data['engagement_score']} ({score_data['engagement_tier']})", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

            # Display active recommendation alert on frame if any
            if recs:
                cv2.putText(frame, f"Tip: {recs[0]['message']}", (20, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

            for object_id, data in tracked_faces.items():
                (x, y, w, h) = data["bbox"]
                record = attendance.session_records.get(object_id)
                is_present = record and record["marked_present"]
                
                label = f"ID: {object_id} ({'Present' if is_present else 'Tracking...'})"
                color = (0, 255, 0) if is_present else (0, 165, 255)

                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

            cv2.imshow("Multimodal Attendance & Engagement Agent", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        audio_extractor.stop_stream()
        cap.release()
        cv2.destroyAllWindows()
        
        # 3. Generate and Save Student Session Analytics Report (Activity 5.2)
        final_report = analytics_gen.generate_report(
            session_id=f"SESSION_{int(time.time())}",
            instructor_type=teacher_profile["mode"],
            attendance_records=attendance.session_records,
            fused_metrics=fused_metrics,
            engagement_score_data=score_data
        )
        # Inject the custom teacher name into the final JSON output
        final_report["instructor_name"] = teacher_name
        
        analytics_gen.save_report_to_json(final_report, "session_analytics_report.json")
        attendance.generate_report()

if __name__ == "__main__":
    main()