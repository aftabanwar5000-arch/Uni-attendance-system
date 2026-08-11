# University Face Recognition Attendance System

A professional, modular face recognition attendance system built with Python, OpenCV, and InsightFace.

## Folder Structure

- `data/`: Contains all persistent storage (`university.db` and `embeddings.pkl`).
- `dataset/`: Contains images for batch registration (folder per student).
- `src/`: Contains all the source code for the application.
  - `main.py`: The web dashboard built with Flask.
  - `checkin.py`: The live camera attendance system.
  - `register.py`: The interactive student registration script.
  - `recognize.py`: The script for testing recognition logic.
  - `batch_register.py`: Script to process bulk images from `dataset/`.
  - `core/`: Core shared logic for database and facial recognition.
  - `templates/`: HTML templates for the dashboard.

## Setup Instructions

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Register Students**:
   - Manually: Run `python src/register.py`
   - Bulk: Place student image folders in `dataset/` and run `python src/batch_register.py`
3. **Start Check-in System**:
   ```bash
   python src/checkin.py
   ```
4. **View Dashboard**:
   ```bash
   python src/main.py
   ```
   Open `http://localhost:5001/` in your browser. Default login is `admin` / `1234`.
