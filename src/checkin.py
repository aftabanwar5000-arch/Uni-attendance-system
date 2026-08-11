import cv2
import logging
from datetime import datetime
from core.face_manager import FaceManager
from core.db_manager import DBManager

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class CheckInSystem:
    def __init__(self, cooldown_seconds=5, similarity_threshold=0.5):
        self.cooldown_seconds = cooldown_seconds
        self.similarity_threshold = similarity_threshold
        
        # State tracking
        self.student_status = {}
        self.last_action_time = {}
        
        self.face_manager = FaceManager()
        DBManager.setup_database()  # Ensure database is initialized

    def run(self):
        logging.info("Starting camera...")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logging.error("Failed to open camera.")
            return

        print("\n--- University Check-In System ---")
        print("Press 'q' to Quit\n")

        while True:
            ret, frame = cap.read()
            if not ret:
                logging.error("Failed to grab frame.")
                break

            faces = self.face_manager.get_faces(frame)

            for face in faces:
                bbox = face.bbox.astype(int)
                embedding = face.embedding

                name, _, department, semester, roll_no = self.face_manager.find_best_match(embedding, self.similarity_threshold)

                if name != "Unknown":
                    current_time = datetime.now()
                    
                    # Logic for Check-in / Check-out
                    if name not in self.student_status:
                        self.student_status[name] = "Inside"
                        self.last_action_time[name] = current_time
                        
                        status_str = "CHECK-IN"
                        logging.info(f"{name} {status_str} at {current_time.strftime('%H:%M:%S')}")
                        DBManager.log_attendance(name, status_str, current_time, department, semester, roll_no)

                    else:
                        time_diff = (current_time - self.last_action_time[name]).total_seconds()
                        
                        if time_diff > self.cooldown_seconds:
                            if self.student_status[name] == "Inside":
                                self.student_status[name] = "Outside"
                                status_str = "CHECK-OUT"
                            else:
                                self.student_status[name] = "Inside"
                                status_str = "CHECK-IN"

                            logging.info(f"{name} {status_str} at {current_time.strftime('%H:%M:%S')}")
                            DBManager.log_attendance(name, status_str, current_time, department, semester, roll_no)
                            self.last_action_time[name] = current_time

                # Draw bounding box and name
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
                
                label = f"{name}"
                if name != "Unknown":
                    status = self.student_status.get(name, "Unknown")
                    label += f" ({status})"
                    
                (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(frame, (bbox[0], bbox[1] - 25), (bbox[0] + w, bbox[1]), color, -1)
                cv2.putText(frame, label, (bbox[0], bbox[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            cv2.putText(frame, "Press 'q' to quit", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imshow("University Check-In System", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("Exiting Check-In System...")
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    system = CheckInSystem(cooldown_seconds=5)
    system.run()
