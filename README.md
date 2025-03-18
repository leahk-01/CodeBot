# Setting Up the Project

Follow the steps below to set up the project environment and run both the backend and frontend.

## 1. Create and Activate a Virtual Environment

### Open your terminal (Command Prompt or PowerShell) and run:
#### On Windows:
     python -m venv venv
     venv\Scripts\activate

#### On macOS/Linux:
     python3 -m venv venv
     source venv/bin/activate


## 2. Install Dependencies

    pip install -r requirements.txt

## 3. Running the Application

### Start the Backend (FastAPI Server)

    uvicorn src.main:app --reload

### Start the Frontend (Flet UI)

    python src/ui.py