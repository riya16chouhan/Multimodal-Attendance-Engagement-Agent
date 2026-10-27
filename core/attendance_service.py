import time
from datetime import datetime

class AttendanceService:
    def __init__(self, presence_threshold_seconds=15):
        self.presence_threshold_seconds = presence_threshold_seconds
        self.session_records = {}  # {id: {"first_seen", "last_seen", "accumulated_time", "marked_present"}}

    def process_frame(self, tracked_objects):
        current_time = time.time()
        active_ids = set(tracked_objects.keys())

        for object_id in active_ids:
            if object_id not in self.session_records:
                self.session_records[object_id] = {
                    "first_seen": current_time,
                    "last_seen": current_time,
                    "accumulated_time": 0.0,
                    "marked_present": False
                }
            else:
                record = self.session_records[object_id]
                delta = current_time - record["last_seen"]
                if delta < 5.0:  # Allow brief drops/occlusions up to 5s
                    record["accumulated_time"] += delta
                record["last_seen"] = current_time

                if not record["marked_present"] and record["accumulated_time"] >= self.presence_threshold_seconds:
                    record["marked_present"] = True
                    print(f"[ATTENDANCE] Participant {object_id} marked PRESENT at {datetime.now().strftime('%H:%M:%S')}")

    def generate_report(self):
        print("\n--- Final Attendance Report ---")
        for obj_id, record in self.session_records.items():
            status = "PRESENT" if record["marked_present"] else "ABSENT"
            print(f"Participant ID: {obj_id} | Status: {status} | Time: {round(record['accumulated_time'], 2)}s")