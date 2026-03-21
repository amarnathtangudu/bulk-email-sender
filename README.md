# Bulk Email Sender

Bulk Email Sender is a full-stack application designed to help users efficiently manage, personalize, and dispatch bulk emails. It is specifically built for creators, influencers, and businesses that need to send customized outreach emails (e.g., to hotels, brands, and cafes) at scale without losing a personal touch.

## 🚀 Features

- **Dynamic Placeholders**: Easily inject personalized data such as `{{name}}`, `{{location}}`, or `{{dates}}` into your email templates to automate personalization.
- **AI-Powered Templates**: Not sure what to say? Use the integrated **Google Gemini AI** features to generate, improve, or rewrite professional, warm, and compelling collaboration emails.
- **CSV Data Import/Export**: Add recipients directly via the UI or by uploading existing CSV lists. You can also generate and download CSV templates specifically tied to your current email template's placeholders.
- **Real-Time Preview**: Get a live visual preview of both the subject line and body of your emails before sending them.
- **Native SMTP Dispatch**: Cleanly integrates with your existing Gmail SMTP credentials to deliver outreach directly from your inbox alongside a live status tracker.

## 🏗 Architecture

The project consists of an **Angular** frontend and a **FastAPI** backend:
- **/backend**: A modular Python FastAPI app serving the API, rendering templates with Jinja2, and communicating with Google's Gemini models.
- **/frontend**: A standalone modern Angular single-page application handling user interactions, API integrations, and state management.

## 🏁 Getting Started

To get the application up and running locally, please refer to the specific documentation for the backend and frontend modules:

- 👉 **[Backend Setup & Running Instructions](./backend/README.md)**
- 👉 **[Frontend Setup & Running Instructions](./frontend/README.md)**

## 📋 Prerequisites

To work on both aspects of this project, make sure you have installed:
- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js (v18+) & npm](https://nodejs.org/)
- A Google Gemini API Key if you aim to use the AI generator functionality.
