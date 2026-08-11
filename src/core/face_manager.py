
import numpy as np
import pickle
import os
import logging
from insightface.app import FaceAnalysis

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EMBEDDINGS_FILE = os.path.join(BASE_DIR, "data", "embeddings.pkl")

class FaceManager:
    def __init__(self):
        self.app = self._initialize_model()
        self.student_data = self.load_student_data()

    def _initialize_model(self):
        logging.info("Initializing Face Analysis model...")
        app = FaceAnalysis(name='buffalo_l')
        app.prepare(ctx_id=0, det_size=(640, 640))
        return app

    def load_student_data(self):
        if not os.path.exists(EMBEDDINGS_FILE):
            logging.warning("No embeddings found. Please register students first.")
            return {}
        try:
            with open(EMBEDDINGS_FILE, "rb") as f:
                data = pickle.load(f)
                logging.info(f"Loaded {len(data)} student records.")
                return data
        except Exception as e:
            logging.error(f"Failed to load student data: {e}")
            return {}

    def save_student_data(self):
        try:
            with open(EMBEDDINGS_FILE, "wb") as f:
                pickle.dump(self.student_data, f)
            logging.info("Student data successfully saved to disk.")
        except Exception as e:
            logging.error(f"Failed to save student data: {e}")

    def get_faces(self, frame):
        """Returns detected faces from the frame."""
        return self.app.get(frame)

    def get_prominent_face(self, faces):
        """Returns the most prominent face from a list of faces."""
        if not faces:
            return None
        return sorted(faces, key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]), reverse=True)[0]

    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def find_best_match(self, embedding, threshold=0.5):
        """Finds the best matching student for a given embedding."""
        best_name = "Unknown"
        best_similarity = 0.0
        department = ""
        semester = ""
        roll_no = ""

        for student_name, data in self.student_data.items():
            similarity = self.cosine_similarity(embedding, data["embedding"])
            if similarity > best_similarity and similarity > threshold:
                best_similarity = similarity
                best_name = student_name
                department = data.get("department", "")
                semester = data.get("semester", "")
                roll_no = data.get("roll_no", "")

        return best_name, best_similarity, department, semester, roll_no

    def add_student(self, name, embedding, department, semester, roll_no=""):
        self.student_data[name] = {
            "embedding": embedding,
            "department": department,
            "semester": semester,
            "roll_no": roll_no
        }
        self.save_student_data()
