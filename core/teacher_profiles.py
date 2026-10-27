class TeacherProfileService:
    def __init__(self):
        # Supports dual instruction modes: Human Teacher and AI Teacher
        self.profiles = {
            "human_teacher": {
                "name": "Prof. Riya Chouhan",
                "mode": "Human Instructor",
                "effectiveness_score": 87.5,
                "trend": "+12%",
                "class_history": [
                    {"name": "CS101 (Today)", "engagement": 85},
                    {"name": "CS101 (Yesterday)", "engagement": 78},
                    {"name": "Math Workshop", "engagement": 92}
                ],
                "strengths": [
                    "High engagement sessions (85%+)",
                    "Interactive Q&A facilitation"
                ],
                "recommendations": [
                    "Incorporate interactive polling questions during mid-session intervals to sustain peak participation.",
                    "Review audio noise thresholds during group discussions to maintain clear instruction delivery."
                ]
            },
            "ai_teacher": {
                "name": "Agentic AI Tutor (MannMitra)",
                "mode": "Autonomous AI Instructor",
                "effectiveness_score": 91.0,
                "trend": "+18%",
                "class_history": [
                    {"name": "AI Session 01", "engagement": 90},
                    {"name": "AI Session 02", "engagement": 93}
                ],
                "strengths": [
                    "Real-time personalized feedback",
                    "Continuous 24/7 responsiveness"
                ],
                "recommendations": [
                    "Adjust response pacing for complex concepts to ensure comprehension.",
                    "Prompt students proactively when attention scores drop below thresholds."
                ]
            }
        }

    def get_profile(self, teacher_type: str = "human_teacher"):
        return self.profiles.get(teacher_type, self.profiles["human_teacher"])

class RecommendationsEngine:
    def generate_realtime_recommendations(self, session_status: dict):
        recs = []
        people = session_status.get("people", [])
        
        if people:
            avg_attention = sum(p.get("attention", 50) for p in people) / len(people)
            if avg_attention < 40:
                recs.append({
                    "type": "alert",
                    "message": "Classroom attention is dropping. Consider a quick interactive polling question."
                })

            for p in people:
                if p.get("attention", 50) < 40:
                    recs.append({
                        "type": "warning",
                        "message": f"Participant ID {p.get('id')} appears distracted."
                    })

        if not recs:
            recs.append({
                "type": "info",
                "message": "Engagement levels are stable. Proceed with current teaching pacing."
            })

        return recs

if __name__ == "__main__":
    service = TeacherProfileService()
    print("--- Human Teacher Profile ---")
    print(service.get_profile("human_teacher"))
    print("\n--- AI Teacher Profile ---")
    print(service.get_profile("ai_teacher"))