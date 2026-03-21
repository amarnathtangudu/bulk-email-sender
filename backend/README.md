# Bulk Email Sender - Backend

This backend application powers the Bulk Email Sender, providing APIs for email generation (via Gemini), template rendering, CSV generation, and bulk email dispatch via SMTP.

## Requirements

Ensure you have Python 3.10+ installed.
You can find the dependencies in `requirements.txt`

## Installation

1. Navigate to the `backend` directory.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables by copying or updating `.env`:
   ```bash
   # Add your Gemini API Key if you want to override the default encoded one
   GEMINI_API_KEY=your_key_here
   ```

## Running the Application

You can start the FastAPI server using Python:

```bash
python app/main.py
```
Or use Uvicorn directly:
```bash
uvicorn app.main:app --reload
```

The API will be accessible at `http://localhost:8000`.
Swagger documentation is available at `http://localhost:8000/docs`.

## Project Structure
- `app/main.py`: Application entrypoint.
- `app/config.py`: Environment and configuration settings.
- `app/models.py`: Pydantic models for request/response validation.
- `app/services.py`: Business logic (SMTP, Jinja2 templating, Gemini AI).
- `app/controllers.py`: FastAPI route definitions.
