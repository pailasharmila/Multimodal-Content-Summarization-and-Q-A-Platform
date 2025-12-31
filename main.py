# main.py
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

# --- AI Engine Imports ---
from ai_engine.core import process_url, ask_question, get_summary

# --- Auth and DB Imports ---
import auth
import models
from db import SessionLocal, engine, get_db

# --- NEW: Import the video router ---
from video_extracter.pipeline import router as video_router


# --- Create DB Tables ---
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- CORS Middleware ---
# (Your existing CORS middleware is perfect and will
#  also apply to the new video routes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500", 
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        # You may need to add the port your video.html is served on
        # if it's different, e.g., "http://127.0.0.1:5501"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Schemas (Request/Response Models) ---
class URLRequest(BaseModel):
    url: str

class QuestionRequest(BaseModel):
    question: str

# --- Authentication Endpoints ---
# (Your /token, /register, and /users/me endpoints remain THE SAME)

@app.post("/token", response_model=auth.Token)
async def login_for_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    # ... (code unchanged)
    user = auth.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register", response_model=auth.User, status_code=status.HTTP_201_CREATED)
async def register_user(user: auth.UserCreate, db: Session = Depends(get_db)):
    # ... (code unchanged)
    db_user = auth.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return auth.create_user(db=db, user=user)


@app.get("/users/me", response_model=auth.User)
async def read_users_me(current_user: auth.User = Depends(auth.get_current_user)):
    # ... (code unchanged)
    return current_user

# --- Original Endpoints (Now Protected) ---
# (Your /capture, /query, and /summary endpoints remain THE SAME)

@app.get("/")
async def hello():
    return "Hello second_brain (now with auth!)"

@app.post("/capture")
async def capture_url(
    request: URLRequest, 
    current_user: auth.User = Depends(auth.get_current_user)
):
    # ... (code unchanged)
    success = process_url(request.url) 
    if not success:
        raise HTTPException(status_code=400, detail="Failed to process the URL.")
    
    return {
        "status": "success", 
        "message": f"Article captured for user {current_user.email}"
    }

@app.post("/query")
async def query_knowledge(
    request: QuestionRequest, 
    current_user: auth.User = Depends(auth.get_current_user)
):
    # ... (code unchanged)
    answer = ask_question(request.question) 
    return {"answer": answer, "user": current_user.email}

@app.post("/summary")
async def get_url_summary(
    request: URLRequest,
    current_user: auth.User = Depends(auth.get_current_user)
):
    # ... (code unchanged)
    summary = get_summary(request.url)
    if summary == "No summary found for this URL." or summary == "Error finding summary.":
        raise HTTPException(status_code=404, detail=summary)
    
    return {"summary": summary, "user": current_user.email}


# --- NEW: Include the video router ---
# This line "links" your video pipeline to the main app.
# All routes from pipeline.py will now be available under the /video prefix.
# e.g., /transcribe becomes /video/transcribe
app.include_router(
    video_router, 
    prefix="/video", 
    tags=["Video Brain"] # This adds a nice "Video Brain" section to your /docs
)