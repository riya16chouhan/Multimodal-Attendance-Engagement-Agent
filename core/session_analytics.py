import json
from datetime import datetime

class SessionAnalyticsGenerator:
    def __init__(self):
        pass

    def generate_report(self, session_id: str, instructor_type: str, attendance_records: dict, fused_metrics: dict, engagement_score_data: dict):
        """
        Compiles multimodal session data into a structured JSON analytics summary,
        specifying whether a Human Teacher or AI Teacher led the session.
        """
        total_participants = len(attendance_records)
        present_count = sum(1 for r in attendance_records.values() if r.get("marked_present", False))
        absent_count = total_participants - present_count

        report = {
            "session_id": session_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "instruction_mode": instructor_type,  # Differentiates between Human or AI Teacher
            "summary_metrics": {
                "total_registered": total_participants,
                "present_count": present_count,
                "absent_count": absent_count,
                "attendance_rate": round((present_count / total_participants * 100) if total_participants > 0 else 0.0, 2),
                "average_engagement_score": engagement_score_data.get("engagement_score", 0.0),
                "engagement_tier": engagement_score_data.get("engagement_tier", "Unknown"),
                "active_speech_ratio": fused_metrics.get("speech_ratio", 0.0)
            },
            "participant_details": attendance_records
        }

        return report

    def save_report_to_json(self, report: dict, filename: str = "session_analytics_report.json"):
        with open(filename, "w") as f:
            json.dump(report, f, indent=4)
        print(f"[INFO] Dual-mode session analytics report successfully saved to {filename}")

if __name__ == "__main__":
    generator = SessionAnalyticsGenerator()
    sample_attendance = {0: {"marked_present": True, "accumulated_time": 45.0}}
    sample_metrics = {"speech_ratio": 0.70}
    sample_score = {"engagement_score": 0.85, "engagement_tier": "High Engagement"}
    
    # Example generating report for the AI Teacher mode
    report = generator.generate_report("CS101_AI_SESSION", "AI Teacher (MannMitra)", sample_attendance, sample_metrics, sample_score)
    generator.save_report_to_json(report, "ai_teacher_session_report.json")