import cv2
import logging
from core.face_manager import FaceManager

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class FaceRecognizer:
    def __init__(self, similarity_threshold=0.5):
        self.similarity_threshold = similarity_threshold
        self.face_manager = FaceManager()

    def run(self):
        logging.info("Starting camera...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            logging.error("Failed to open camera.")
            return

        print("\n--- Face Recognition Tester ---")
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

                name, best_similarity, _, _ = self.face_manager.find_best_match(embedding, self.similarity_threshold)

                # Draw bounding box and name
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
                
                label = f"{name} ({best_similarity:.2f})" if name != "Unknown" else "Unknown"
                
                # Add background for text to make it readable
                (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(frame, (bbox[0], bbox[1] - 25), (bbox[0] + w, bbox[1]), color, -1)
                cv2.putText(frame, label, (bbox[0], bbox[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # Display instructions
            cv2.putText(frame, "Press 'q' to quit", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imshow("Face Recognition", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("Exiting Face Recognition...")
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    recognizer = FaceRecognizer()
    recognizer.run()
