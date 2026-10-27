import numpy as np
import librosa
import sounddevice as sd
import queue
import time

class AudioSignalExtractor:
    def __init__(self, sample_rate=16000, chunk_duration=1.0):
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.audio_buffer = []

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            print(f"[AUDIO WARNING] {status}", flush=True)
        mono_chunk = np.mean(indata, axis=1) if len(indata.shape) > 1 else indata
        self.audio_queue.put(mono_chunk.copy())

    def start_stream(self):
        self.is_recording = True
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self.audio_callback,
            blocksize=self.chunk_size
        )
        self.stream.start()
        print("[INFO] Audio signal extraction stream started...")

    def stop_stream(self):
        self.is_recording = False
        self.stream.stop()
        self.stream.close()
        print("[INFO] Audio signal extraction stream stopped.")

    def process_live_stream(self, duration_seconds=10):
        self.start_stream()
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration_seconds:
                if not self.audio_queue.empty():
                    chunk = self.audio_queue.get()
                    rms = np.sqrt(np.mean(chunk**2))
                    timestamp = time.time()
                    
                    self.audio_buffer.append({
                        "timestamp": timestamp,
                        "waveform": chunk,
                        "rms_energy": float(rms)
                    })
                    print(f"[AUDIO] Timestamp: {round(timestamp, 2)} | RMS Energy: {round(rms, 4)}")
        finally:
            self.stop_stream()
        
        return self.audio_buffer