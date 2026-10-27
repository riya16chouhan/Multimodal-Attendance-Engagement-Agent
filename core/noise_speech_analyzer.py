import numpy as np

class NoiseAndSpeechAnalyzer:
    def __init__(self, sample_rate=16000, rms_threshold=0.015):
        self.sample_rate = sample_rate
        self.rms_threshold = rms_threshold

    def detect_speech_activity(self, audio_chunk):
        rms = np.sqrt(np.mean(audio_chunk**2))
        is_speech = rms >= self.rms_threshold
        return {
            "is_speech": bool(is_speech),
            "rms_energy": float(rms),
            "status": "Speech Detected" if is_speech else "Background Noise / Silence"
        }

    def process_audio_buffer(self, audio_buffer):
        analysis_results = []
        speech_frame_count = 0

        print("\n--- Running Noise & Speech Activity Analysis ---")
        for entry in audio_buffer:
            chunk = entry["waveform"]
            vad_result = self.detect_speech_activity(chunk)
            
            analysis_record = {
                "timestamp": entry["timestamp"],
                **vad_result
            }
            analysis_results.append(analysis_record)
            
            if vad_result["is_speech"]:
                speech_frame_count += 1
            
            print(f"Time: {round(entry['timestamp'], 2)}s | Status: {vad_result['status']} | RMS: {round(entry['rms_energy'], 4)}")

        total_frames = len(audio_buffer)
        speech_percentage = (speech_frame_count / total_frames * 100) if total_frames > 0 else 0.0
        print(f"\n[SUMMARY] Total Frames: {total_frames} | Speech Frames: {speech_frame_count} | Active Speech Ratio: {round(speech_percentage, 2)}%")
        
        return analysis_results