import cv2
import numpy as np

class FaceDetectorTracker:
    def __init__(self, max_disappeared=30):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.next_object_id = 0
        self.tracked_objects = {}  # {id: {"centroid": (x, y), "bbox": (x, y, w, h), "disappeared": 0}}
        self.max_disappeared = max_disappeared

    def register(self, centroid, bbox):
        self.tracked_objects[self.next_object_id] = {
            "centroid": centroid,
            "bbox": bbox,
            "disappeared": 0
        }
        self.next_object_id += 1

    def deregister(self, object_id):
        del self.tracked_objects[object_id]

    def update(self, rects):
        if len(rects) == 0:
            for object_id in list(self.tracked_objects.keys()):
                self.tracked_objects[object_id]["disappeared"] += 1
                if self.tracked_objects[object_id]["disappeared"] > self.max_disappeared:
                    self.deregister(object_id)
            return self.tracked_objects

        input_centroids = np.zeros((len(rects), 2), dtype="int")
        for (i, (x, y, w, h)) in enumerate(rects):
            input_centroids[i] = (int(x + w / 2.0), int(y + h / 2.0))

        if len(self.tracked_objects) == 0:
            for i in range(len(rects)):
                self.register(input_centroids[i], rects[i])
        else:
            object_ids = list(self.tracked_objects.keys())
            object_centroids = [obj["centroid"] for obj in self.tracked_objects.values()]

            D = np.linalg.norm(np.array(object_centroids)[:, np.newaxis] - input_centroids[np.newaxis, :], axis=2)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows, used_cols = set(), set()
            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                object_id = object_ids[row]
                self.tracked_objects[object_id]["centroid"] = input_centroids[col]
                self.tracked_objects[object_id]["bbox"] = rects[col]
                self.tracked_objects[object_id]["disappeared"] = 0
                used_rows.add(row)
                used_cols.add(col)

            unused_rows = set(range(0, D.shape[0])).difference(used_rows)
            unused_cols = set(range(0, D.shape[1])).difference(used_cols)

            for row in unused_rows:
                object_id = object_ids[row]
                self.tracked_objects[object_id]["disappeared"] += 1
                if self.tracked_objects[object_id]["disappeared"] > self.max_disappeared:
                    self.deregister(object_id)

            for col in unused_cols:
                self.register(input_centroids[col], rects[col])

        return self.tracked_objects