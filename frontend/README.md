# Bulk Email Sender - Frontend

This is the Angular frontend for the Bulk Email Sender. It allows users to:
- Add and manage recipients
- Use placeholders (like `{{name}}`) in subjects and email bodies
- Preview personalized emails dynamically
- Request AI-generated outreach templates using Google Gemini
- Send bulk emails seamlessly via SMTP

## Requirements

Ensure you have **Node.js** (v18 or newer recommended) and **npm** installed on your system.

## Installation

1. Navigate to the `frontend` directory in your terminal:
   ```bash
   cd frontend
   ```

2. Install all necessary dependencies by running:
   ```bash
   npm install
   ```

## Running the Application

To start the local development server, run:
```bash
npm start
# or 
ng serve
```

Once the server is running, open your browser and navigate to `http://localhost:4200/`. The application will automatically reload whenever you modify any of the source files.

## Project Structure

- `src/app/app.component.ts`: The main user interface component containing the template and layout structure.
- `src/app/services/api.service.ts`: Extracted service layer to handle all HTTP communication with the FastAPI backend.
- `src/app/models/`: Any custom typings required by the Angular application.

## Tooling

This project was generated using [Angular CLI](https://github.com/angular/angular-cli) version 21.1.5. You can use standard `ng` commands to scaffold or build.
