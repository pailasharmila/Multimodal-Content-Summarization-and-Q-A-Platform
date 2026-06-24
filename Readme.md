# 🧠 AI Second Brain

A full-stack, multi-modal personal knowledge assistant that lets you **capture**, **transcribe**, **summarize**, and **query** content from both web articles and YouTube videos — all protected behind JWT-based user authentication.

---

## 📌 Project Overview

AI Second Brain is a locally-run AI application with two core modules:

| Module | What it does |
|---|---|
| **TextBrain** | Capture any web article → auto-summarize it → ask questions about it via RAG |
| **VideoBrain** | Paste a YouTube URL → auto-transcribe it (captions or Whisper ASR) → process for Q&A |

All features are user-authenticated, meaning every user gets their own secure session.

---

## 🏗️ Architecture

```
AI-Second-Brain/
│
├── main.py                        # FastAPI app entry point (auth + text routes)
├── auth.py                        # JWT auth logic (login, register, token)
├── models.py                      # SQLAlchemy User model
├── db.py                          # Database engine + session setup
│
├── ai_engine/
│   └── core.py                    # TextBrain: scrape → summarize → RAG (ChromaDB + LlamaIndex)
│
├── video_extracter/
│   ├── pipeline.py                # VideoBrain: YouTube → transcript → FastAPI router
│   ├── core.py                    # Video RAG pipeline (ChromaDB + LlamaIndex)
│   ├── preprocess.py              # Cleans raw VTT captions / ASR output
│   ├── video.html                 # VideoBrain frontend
│   └── transcripts/               # Saved transcript .txt files
│
├── text_brain_frontend/
│   └── index.html                 # TextBrain frontend
│
├── login.html                     # Shared login/register page
├── .env                           # Environment variables (not committed)
└── rough.txt                      # Developer notes
```

---

## ⚙️ Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — REST API framework
- [SQLAlchemy](https://www.sqlalchemy.org/) + SQLite — User database
- [python-jose](https://python-jose.readthedocs.io/) — JWT token handling
- [passlib (bcrypt)](https://passlib.readthedocs.io/) — Password hashing
- [LlamaIndex](https://www.llamaindex.ai/) — RAG (Retrieval-Augmented Generation) pipeline
- [ChromaDB](https://www.trychroma.com/) — Local vector database for embeddings
- [Ollama (gemma:2b)](https://ollama.com/) — Local LLM for summarization and Q&A
- [HuggingFace Embeddings](https://huggingface.co/) — `BAAI/bge-small-en-v1.5` for text embeddings
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — YouTube caption/audio extraction
- [OpenAI Whisper](https://github.com/openai/whisper) — ASR fallback for video transcription
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) — Web scraping

**Frontend**
- Vanilla HTML, CSS, JavaScript
- [Tailwind CSS](https://tailwindcss.com/) (VideoBrain UI)

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running locally with `gemma:2b` pulled
- [ffmpeg](https://ffmpeg.org/) installed (required by Whisper)
- Node.js (optional, only if extending the frontend)

### 2. Clone & Set Up Virtual Environment

```powershell
git clone <your-repo-url>
cd AI-Second-Brain

# Create virtual environment
python -m venv brain

# Activate (Windows — allow temporarily)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\brain\Scripts\Activate.ps1

# Activate (Mac/Linux)
source brain/bin/activate
```

### 3. Install Dependencies

```bash
pip install fastapi uvicorn sqlalchemy python-jose[cryptography] passlib[bcrypt] \
            python-dotenv requests beautifulsoup4 llama-index chromadb \
            llama-index-embeddings-huggingface llama-index-vector-stores-chroma \
            llama-index-llms-ollama yt-dlp openai-whisper
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:{some thing like below}

```env
DATABASE_URL=postgresql://postgres:password@localhost/second_brain
#DATABASE_URL=sqlite:///./second_brain.db
JWT_SECRET=738b69071d615a8dd0138c84c18f6532cd6b8006d6f3b16ca768a8fhkeic
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
#Add cors in .env during the production so that it won't break
ALLOWED_ORIGINS=http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:5501,http://localhost:5501
```

> ⚠️ Never commit your `.env` file. Add it to `.gitignore`.

### 5. Run the Backend

```bash
uvicorn main:app --reload
```

The API will be live at `http://127.0.0.1:8000`.
Interactive docs available at `http://127.0.0.1:8000/docs`.

### 6. Open the Frontend

Open `login.html` with **Live Server** (VS Code extension) or any local HTTP server on port 5500.

```
http://127.0.0.1:5500/login.html
```

---

## 🔐 Authentication Flow

1. **Register** a new account via the Register form → stored securely with bcrypt-hashed password.
2. **Login** → server issues a JWT access token.
3. Token is saved in `localStorage` on the client.
4. Every protected API request sends `Authorization: Bearer <token>` in the header.
5. On token expiry (default 30 min), the user is redirected to login.

### API Endpoints

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `POST` | `/register` | ❌ | Create new user account |
| `POST` | `/token` | ❌ | Login and receive JWT token |
| `GET` | `/users/me` | ✅ | Get current user info |
| `POST` | `/capture` | ✅ | Scrape and index a web article |
| `POST` | `/query` | ✅ | Ask a question (RAG over articles) |
| `POST` | `/summary` | ✅ | Retrieve stored summary for a URL |
| `POST` | `/video/transcribe` | ✅ | Transcribe a YouTube video |

---

## 🧩 Module Deep Dives

### TextBrain (`ai_engine/core.py`)

1. Takes a URL → scrapes text with BeautifulSoup
2. Sends text to local Ollama LLM → generates a summary
3. Summary is embedded and stored in ChromaDB with a unique ID (`summary_<url>`)
4. Full text is chunked and indexed in ChromaDB via LlamaIndex for RAG queries

### VideoBrain (`video_extracter/pipeline.py`)

1. Takes a YouTube URL
2. Tries to fetch **existing auto-generated captions** via `yt-dlp`
3. If no captions found → downloads audio → runs **Whisper ASR** to generate transcript
4. Raw transcript is saved as a `.txt` file in `video_extracter/transcripts/`
5. Returns transcript + source type + user email in response

### Transcript Preprocessing (`video_extracter/preprocess.py`)

Cleans raw VTT caption data:
- Strips HTML timestamp tags like `<00:00:08.280><c>`
- Removes `[Music]`, `[Laughter]` artifacts
- De-duplicates repeated caption lines

---

## 🗺️ Roadmap (Upcoming Features)

- [ ] Per-user isolated ChromaDB collections (currently shared)
- [ ] Save summaries to user accounts (persistent, per-user storage)
- [ ] Video transcript Q&A via RAG pipeline
- [ ] PDF / document upload support
- [ ] Logout button and token refresh
- [ ] Deployment (Docker + cloud hosting)

---

## 🐛 Known Limitations

- The ChromaDB vector store is **shared across all users** — user data isolation is not yet implemented.
- The `url_storage` dict in `pipeline.py` is in-memory only and resets on server restart.
- Whisper transcription can be slow on CPU for long videos.
- The frontend requires a Live Server or similar; opening HTML files directly (`file://`) may cause CORS issues.

---

## 🧑‍💻 Developer Notes

```bash
# Deactivate virtual environment when done
deactivate

# Run backend with auto-reload during development
uvicorn main:app --reload

# Check API docs interactively
# http://127.0.0.1:8000/docs
```

---

## 📄 License

This project is for personal learning and development purposes.

sharmila__paila_

---

*Built with curiosity, FastAPI, and a local LLM. 🚀*
