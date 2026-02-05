# Agentic Research Assistant

An AI-powered research assistant capable of intelligent routing, document summarization, and data extraction. Built with a modern tech stack featuring **FastAPI**, **LangChain**, **ChromaDB**, and **React**.

## 🚀 Features

- **Intelligent Routing**: Automatically decides the best agent to handle your query (Summarization, Extraction, Comparison, etc.).
- **RAG (Retrieval-Augmented Generation)**: Ingests and queries documents using ChromaDB for grounded answers.
- **Multi-Agent Architecture**: thorough separation of concerns between Router, Summarizer, and Extractor agents.
- **Modern Stack**:
  - **Backend**: Python 3.10+, FastAPI, Pydantic, OpenAI/Groq API.
  - **Frontend**: React (TypeScript), Vite.

## 🛠️ Prerequisites

- **Python** 3.10 or higher
- **Node.js** 18 or higher
- **Groq API Key** (or compatible OpenAI Application Key)

## 📦 Installation & Setup

### 1. Backend Setup

Navigate to the backend directory and set up the Python environment.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

**Environment Configuration:**

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and add your API credentials:
   ```env
   GROQ_API_KEY=your_gsk_...
   ```

### 2. Frontend Setup

Navigate to the frontend directory and install dependencies.

```bash
cd frontend
npm install
```

## 🏃‍♂️ Running the Application

### Start the Backend Server

```bash
# In the backend directory (ensure venv is active)
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.
API Documentation: `http://localhost:8000/docs`

### Start the Frontend Client

```bash
# In the frontend directory
npm run dev
```
The application will run at `http://localhost:5173`.

## 📂 Project Structure

```
.
├── backend/            # FastAPI backend
│   ├── app/            # Source code (agents, API, db)
│   ├── chroma_db/      # Vector database storage
│   └── requirements.txt
├── frontend/           # React frontend (Vite)
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
