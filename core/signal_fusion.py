import time

class SignalFusionEngine:
    def __init__(self, window_size_seconds=5.0):
        self.window_size_seconds = window_size_seconds
        self.fusion_buffer = []

    def add_signal_sample(self, face_count, rms_energy, is_speech):
        current_time = time.time()
        self.fusion_buffer.append({
            "timestamp": current_time,
            "face_count": face_count,
            "rms_energy": rms_energy,
            "is_speech": is_speech
        })
        self._prune_old_samples(current_time)

    def _prune_old_samples(self, current_time):
        self.fusion_buffer = [
            sample for sample in self.fusion_buffer 
            if current_time - sample["timestamp"] <= self.window_size_seconds
        ]

    def get_fused_metrics(self):
        if not self.fusion_buffer:
            return {"avg_faces": 0.0, "avg_rms": 0.0, "speech_ratio": 0.0}

        total_samples = len(self.fusion_buffer)
        avg_faces = sum(s["face_count"] for s in self.fusion_buffer) / total_samples
        avg_rms = sum(s["rms_energy"] for s in self.fusion_buffer) / total_samples
        speech_count = sum(1 for s in self.fusion_buffer if s["is_speech"])
        speech_ratio = speech_count / total_samples

        return {
            "avg_faces": round(avg_faces, 2),
            "avg_rms": round(avg_rms, 4),
            "speech_ratio": round(speech_ratio, 2)
        }

if __name__ == "__main__":
    fusion = SignalFusionEngine()
    fusion.add_signal_sample(face_count=2, rms_energy=0.02, is_speech=True)
    print(fusion.get_fused_metrics())