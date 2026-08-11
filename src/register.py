import cv2
import logging
from core.face_manager import FaceManager

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class StudentRegistrar:
    def __init__(self):
        self.face_manager = FaceManager()

    def register_student(self):
        print("\n--- Student Registration ---")
        name = input("Enter Student Name: ").strip()
        if not name:
            logging.warning("Name cannot be empty. Aborting.")
            return

        department = input("Enter Department (e.g. CS/IT/BBA): ").strip()
        semester = input("Enter Semester (e.g. 1-8): ").strip()
        roll_no = input("Enter Roll No (e.g. CS-101): ").strip()

        logging.info("Starting camera... Please look at the camera.")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logging.error("Failed to open camera.")
            return

        print("\n[INSTRUCTIONS]: Press 's' to capture your face and register. Press 'q' to cancel.")
        
        embedding_captured = False

        while True:
            ret, frame = cap.read()
            if not ret:
                logging.error("Failed to grab frame from camera.")
                break

            # Overlay instructions
            cv2.putText(frame, "Press 's' to capture", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'q' to cancel", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow("Register Student", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('s'):
                faces = self.face_manager.get_faces(frame)
                face = self.face_manager.get_prominent_face(faces)
                
                if face:
                    self.face_manager.add_student(name, face.embedding, department, semester, roll_no)
                    embedding_captured = True
                    logging.info("Face captured and embedding generated successfully!")
                    break
                else:
                    logging.warning("No face detected. Please ensure your face is clearly visible and try again.")
            
            elif key == ord('q'):
                logging.info("Registration cancelled by user.")
                break

        cap.release()
        cv2.destroyAllWindows()

        if embedding_captured:
            print(f"\n[SUCCESS] Student '{name}' registered successfully!\n")
        else:
            print("\n[FAILED] Registration process did not complete.\n")

if __name__ == "__main__":
    registrar = StudentRegistrar()
    registrar.register_student()
