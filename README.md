# Bulk Email Sender

This project consists of a FastAPI backend and an Angular frontend.

## Getting Started

### Prerequisites
- Python 3.x
- Node.js & npm

### Using VS Code (Recommended)
1. Open the root folder in VS Code.
2. Go to the **Run and Debug** view (Cmd+Shift+D).
3. Select **"Full Stack (Backend + Frontend)"** and press F5.
   - This will start the FastAPI backend on `http://localhost:8000`
   - This will start the Angular frontend on `http://localhost:4200`

### Using the Terminal
To start both services simultaneously:
```bash
./run.sh
```

### Manual Start

#### Backend
```bash
cd backend
./venv/bin/python app/main.py
```

#### Frontend
```bash
cd frontend
npm start
```
