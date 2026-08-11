import cv2
import os
import logging
import csv
import numpy as np
from core.face_manager import FaceManager

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
INFO_FILE = os.path.join(DATASET_DIR, "info.csv")

class BatchRegistrar:
    def __init__(self):
        self.face_manager = FaceManager()
        self.student_info = self._load_info_csv()

    def _load_info_csv(self):
        info = {}
        if os.path.exists(INFO_FILE):
            try:
                with open(INFO_FILE, mode="r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        name = row.get("Name", "").strip()
                        if name:
                            info[name] = {
                                "department": row.get("Department", "Unknown").strip(),
                                "semester": row.get("Semester", "Unknown").strip(),
                                "roll_no": row.get("RollNo", "Unknown").strip()
                            }
                logging.info(f"Loaded additional info for {len(info)} students from CSV.")
            except Exception as e:
                logging.error(f"Error reading {INFO_FILE}: {e}")
        else:
            logging.warning(f"No {INFO_FILE} found. Will use default 'Unknown' for department/semester.")
        return info

    def process_dataset(self):
        if not os.path.exists(DATASET_DIR):
            logging.error(f"Dataset directory not found at {DATASET_DIR}")
            return

        student_folders = [f for f in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, f))]
        
        if not student_folders:
            logging.warning("Dataset folder is empty. Please add folders inside 'dataset/' with student names.")
            return

        new_records = 0

        for student_name in student_folders:
            folder_path = os.path.join(DATASET_DIR, student_name)
            image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

            if not image_files:
                logging.warning(f"No images found for student '{student_name}'. Skipping.")
                continue

            embeddings_list = []
            
            for img_name in image_files:
                img_path = os.path.join(folder_path, img_name)
                img = cv2.imread(img_path)
                
                if img is None:
                    logging.warning(f"Could not read image {img_path}. Skipping.")
                    continue
                    
                faces = self.face_manager.get_faces(img)
                face = self.face_manager.get_prominent_face(faces)
                
                if face:
                    embeddings_list.append(face.embedding)
                else:
                    logging.warning(f"No face detected in {img_path}. Skipping.")

            if embeddings_list:
                # Average the embeddings for robust recognition
                avg_embedding = np.mean(embeddings_list, axis=0)
                
                # Normalize the averaged embedding
                avg_embedding = avg_embedding / np.linalg.norm(avg_embedding)
                
                dept = self.student_info.get(student_name, {}).get("department", "Unknown")
                sem = self.student_info.get(student_name, {}).get("semester", "Unknown")
                roll = self.student_info.get(student_name, {}).get("roll_no", "Unknown")
                
                self.face_manager.add_student(student_name, avg_embedding, dept, sem, roll)
                new_records += 1
                logging.info(f"Successfully processed {len(embeddings_list)} images for '{student_name}'.")

        if new_records > 0:
            print(f"\n[SUCCESS] Batch registration complete! Added/Updated {new_records} students.")
        else:
            print("\n[INFO] No new students were registered.")

if __name__ == "__main__":
    registrar = BatchRegistrar()
    registrar.process_dataset()
