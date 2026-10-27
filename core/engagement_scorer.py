class EngagementScorer:
    def __init__(self, face_weight=0.4, speech_weight=0.6):
        self.face_weight = face_weight
        self.speech_weight = speech_weight

    def calculate_score(self, fused_metrics, expected_participants=1.0):
        """
        Computes normalized engagement score combining facial presence 
        and active speech participation ratio.
        """
        face_ratio = min(fused_metrics["avg_faces"] / expected_participants, 1.0)
        speech_ratio = fused_metrics["speech_ratio"]

        # Weighted composite score formula
        engagement_score = (face_ratio * self.face_weight) + (speech_ratio * self.speech_weight)
        
        # Determine descriptive engagement tier
        if engagement_score >= 0.75:
            tier = "High Engagement"
        elif engagement_score >= 0.40:
            tier = "Moderate Engagement"
        else:
            tier = "Low Engagement"

        return {
            "engagement_score": round(float(engagement_score), 2),
            "engagement_tier": tier
        }

if __name__ == "__main__":
    scorer = EngagementScorer()
    metrics = {"avg_faces": 1.0, "avg_rms": 0.025, "speech_ratio": 0.8}
    print(scorer.calculate_score(metrics, expected_participants=1.0))