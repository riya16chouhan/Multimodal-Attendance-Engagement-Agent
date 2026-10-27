class MultimodalAgent:
    def __init__(self, engagement_threshold=0.5):
        self.engagement_threshold = engagement_threshold

    def evaluate_classroom_state(self, tracked_faces, audio_vad_status):
        """
        Combines vision data (number of active faces) and audio data (VAD status)
        to determine the overall classroom dynamic.
        """
        active_face_count = len(tracked_faces)
        is_speech_active = (audio_vad_status == "Speech Detected")

        # Rule-based multimodal reasoning
        if active_face_count == 0:
            state = "Empty Room / No Participants"
            recommendation = "Wait for participants to join or check camera feed."
        elif is_speech_active and active_face_count > 0:
            state = "Active Lecture / Discussion"
            recommendation = "Maintain current pacing; speaker is engaged."
        elif not is_speech_active and active_face_count > 0:
            state = "Quiet Study / Passive Listening"
            recommendation = "Consider prompting interactive questions to boost engagement."
        else:
            state = "Uncertain State"
            recommendation = "Monitor signals."

        return {
            "active_faces": active_face_count,
            "audio_status": audio_vad_status,
            "classroom_state": state,
            "recommendation": recommendation
        }

if __name__ == "__main__":
    agent = MultimodalAgent()
    print(agent.evaluate_classroom_state({0: {"bbox": (0,0,10,10)}}, "Speech Detected"))