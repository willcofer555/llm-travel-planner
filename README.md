# Travel Discovery API Backend

FastAPI backend for the travel location discovery application.

## Setup

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   
   # Activate virtual environment:
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Required API Keys:**
   - OpenAI API Key: Get from https://platform.openai.com/
   - Google Maps API Key: Get from Google Cloud Console

5. **Run the server:**
   ```bash
   python main.py
   ```

   Server will start at `http://localhost:8000`

## API Endpoints

- `POST /api/chat` - Main chat endpoint for travel recommendations
- `GET /health` - Health check endpoint
- `GET /docs` - FastAPI automatic documentation

## Features

- AI-powered travel recommendations using OpenAI GPT-3.5-turbo
- Google Maps integration for geocoding and place details
- Rate limiting (10 requests per minute)
- CORS configuration for frontend integration
- Comprehensive error handling and logging