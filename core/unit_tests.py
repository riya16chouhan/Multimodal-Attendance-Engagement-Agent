import unittest
import numpy as np
from face_detector import FaceDetectorTracker
from noise_speech_analyzer import NoiseAndSpeechAnalyzer
from engagement_scorer import EngagementScorer

class TestMultimodalAgentComponents(unittest.TestCase):
    
    def test_face_tracker_initialization(self):
        tracker = FaceDetectorTracker()
        self.assertEqual(len(tracker.tracked_objects), 0)
        self.assertEqual(tracker.max_disappeared, 30)

    def test_speech_detector_threshold(self):
        analyzer = NoiseAndSpeechAnalyzer(rms_threshold=0.015)
        # Test low energy (background noise)
        quiet_chunk = np.zeros(16000)
        result_quiet = analyzer.detect_speech_activity(quiet_chunk)
        self.assertFalse(result_quiet["is_speech"])

        # Test high energy (speech)
        loud_chunk = np.ones(16000) * 0.1
        result_loud = analyzer.detect_speech_activity(loud_chunk)
        self.assertTrue(result_loud["is_speech"])

    def test_engagement_scorer(self):
        scorer = EngagementScorer(face_weight=0.4, speech_weight=0.6)
        metrics = {"avg_faces": 1.0, "speech_ratio": 1.0}
        score_data = scorer.calculate_score(metrics, expected_participants=1.0)
        self.assertEqual(score_data["engagement_score"], 1.0)
        self.assertEqual(score_data["engagement_tier"], "High Engagement")

if __name__ == "__main__":
    unittest.main()