# Arziki AI Business Assistant

Arziki is an intelligent, AI-powered backend service designed to provide business analytics, demand forecasting, and conversational insights. Built with FastAPI and powered by Google's Gemini models, it offers a robust platform for businesses to interact with their data through a conversational interface, transcribe audio notes, and generate predictive reports.

## ✨ Features

*   **Secure Authentication**: JWT-based authentication with user registration, login, and secure password handling (hashing and recovery).
*   **Conversational AI Chat**: Engage in a conversation with an AI assistant that maintains user-specific chat history.
*   **Audio Transcription**: Upload audio files (e.g., meeting notes, voice memos) to be transcribed and analyzed by the AI.
*   **Predictive Analytics**: Submit business data (e.g., product sales, inventory) to receive demand predictions (`High`, `Medium`, `Low`) with detailed reasoning.
*   **Automated PDF Reporting**: Automatically generate professional PDF reports from analytics data. The AI first creates an HTML report, which is then converted to a PDF.
*   **Cloud Storage Integration**: All generated reports and user-uploaded files are securely stored in Google Cloud Storage.
*   **Email Notifications**: Integrated email service for account verification and password recovery.
*   **Scalable Architecture**: Built with a modular structure using FastAPI routers and services, making it easy to extend and maintain.

## 🛠️ Technology Stack

*   **Backend**: FastAPI
*   **AI & Machine Learning**:
    *   Google Generative AI (Gemini) for chat, analysis, and report generation.
    *   Google Cloud Speech-to-Text for audio transcription.
*   **Database**: SQLAlchemy (compatible with PostgreSQL, SQLite, etc.)
*   **Authentication**: JWT & OAuth2 with `passlib` for password hashing.
*   **Data Validation**: Pydantic
*   **File Storage**: Google Cloud Storage
*   **PDF Generation**: ReportLab & BeautifulSoup
*   **Email**: FastAPI-Mail with Zoho SMTP.
*   **Caching**: Redis for token blacklisting.
*   **Web Server**: Uvicorn

## 📂 Project Structure

The project follows a modular structure, organized for scalability and maintainability.

```
arziki/
├── .venv/
├── src/
│   ├── app/
│   │   ├── db/
│   │   │   ├── dependencies.py
│   │   │   └── models.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   └── chat.py
│   │   ├── schemas/
│   │   │   ├── chat.py
│   │   │   └── user.py
│   │   ├── services/
│   │   │   ├── auth.py
│   │   │   └── chat.py
│   │   └── utils/
│   │       ├── mail_config.py
│   │       ├── pdf_config.py
│   │       └── redis_config.py
│   ├── ai/
│   │   └── main_agent.py
│   ├── core/
│   │   └── config.py
│   ├── .env
│   └── main.py
├── README.md
└── requirements.txt
```

##  Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

*   Python 3.8+
*   A running Redis instance.
*   Google Cloud Platform (GCP) project with credentials for Cloud Storage and Generative AI.
*   Zoho Mail account (or other SMTP provider) for sending emails.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd arziki
```

### 2. Create and Activate a Virtual Environment

```bash
# For Windows
python -m venv .venv
.venv\Scripts\activate

# For macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Create a `requirements.txt` file with the following content:

```
fastapi
uvicorn[standard]
sqlalchemy
pydantic
python-dotenv
passlib[argon2]
python-jose[cryptography]
fastapi-mail
google-cloud-storage
google-generativeai
google-cloud-speech
reportlab
beautifulsoup4
redis
httpx
```

Then, install the packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory (`src/`) and populate it with your credentials. Use `.env.example` as a template.

```env
# .env
DATABASE_URL="sqlite:///./test.db"
SECRET_KEY="your_super_secret_key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Cloud
CLOUD_BUCKET_NAME="your-gcs-bucket-name"
GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/gcp-credentials.json"

# Email (Zoho)
ZOHO_MAIL="your-email@zoho.com"
ZOHO_PASSWORD="your-app-password"
ZOHO_SMTP_PORT=587
ZOHO_SMTP_HOST="smtp.zoho.com"
```

### 5. Run the Application

Navigate to the `src` directory and start the server.

```bash
cd src
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. You can access the interactive API documentation at `http://127.0.0.1:8000/docs`.