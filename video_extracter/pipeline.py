# video_extracter/pipeline.py

import os
import uuid
import logging
import re
import sys # <-- NEW
from fastapi import APIRouter, HTTPException, Depends # <-- MODIFIED
from pydantic import BaseModel, HttpUrl

# --- NEW: Path and Auth Imports ---
# This block adds the project's root directory to the Python path
# so we can import 'auth', 'db', and 'models' from the parent folder.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import auth
import models
from db import get_db
# --- End of New Imports ---

import yt_dlp
import whisper

# --- Setup ---
# OLD: app = FastAPI() (DELETE THIS)
router = APIRouter() # <-- NEW: Create a router instead
logging.basicConfig(level=logging.INFO)
log = logging.info

# NEW: Define a directory to store transcripts
TRANSCRIPT_DIR = "transcripts"
os.makedirs(TRANSCRIPT_DIR, exist_ok=True) 

# OLD: app.add_middleware(...) (DELETE THE ENTIRE CORS BLOCK)
# The main.py app will handle CORS for all routes.

# --- Pydantic Models ---
class VideoRequest(BaseModel):
    url: HttpUrl

class TranscriptResponse(BaseModel):
    transcript: str
    source: str 
    user_email: str # <-- NEW: Let's return which user made the request

# --- Helper Functions ---
# (Helper functions get_safe_filename, save_transcript_to_file,
# fetch_existing_transcript, and generate_asr_transcript remain THE SAME)

# (Paste all your helper functions here exactly as they were)
def get_safe_filename(url: str) -> str:
    """Creates a safe filename from a URL."""
    try:
        if "youtube.com" in url or "youtu.be" in url:
            video_id = re.search(r'(?<=v=)[\w-]+|(?<=youtu.be/)[\w-]+', url).group(0)
            return f"{video_id}.txt"
    except Exception:
        pass 
    return f"transcript_{uuid.uuid4().hex}.txt"

url_storage = {} # You should improve this, but it works for now

def save_transcript_to_file(filename: str, transcript: str, source: str):
    """Saves the transcript to a text file in the TRANSCRIPT_DIR."""
    filepath = os.path.join(TRANSCRIPT_DIR, filename)
    header = f"Source: {source}\n"
    header += f"Original URL: {url_storage.get(filename, 'Unknown')}\n" 
    header += ("-" * 30) + "\n\n"
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(header + transcript)
        log(f"Successfully saved transcript to: {filepath}")
    except Exception as e:
        log(f"Error saving transcript to file: {e}")

def fetch_existing_transcript(video_url: str) -> str | None:
    # ... (code unchanged)
    log(f"Attempting to find existing transcript for: {video_url}")
    ydl_opts = {
        'skip_download': True,      
        'writesubtitles': False,     
        'writeautomaticsub': True,   
        'subtitleslangs': ['en'],    
        'outtmpl': '-',          
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            if info.get('automatic_captions', {}).get('en'):
                log("Found automatic 'en' captions.")
                transcript_parts = []
                def capture_output(d):
                    if d['status'] == 'finished' and d.get('info_dict', {}).get('ext') == 'vtt':
                        with open(d['filename'], 'r', encoding='utf-8') as f:
                            transcript_parts.append(f.read())
                
                temp_file = f"temp_subs_{uuid.uuid4().hex}"
                vtt_opts = {
                    'skip_download': True,
                    'writeautomaticsub': True,
                    'subtitlesformat': 'vtt',
                    'subtitleslangs': ['en'],
                    'outtmpl': temp_file,
                    'quiet': True,
                    'progress_hooks': [capture_output]
                }
                
                with yt_dlp.YoutubeDL(vtt_opts) as vtt_ydl:
                    vtt_ydl.download([video_url])

                if transcript_parts:
                    log("Successfully extracted VTT content.")
                    if os.path.exists(f"{temp_file}.en.vtt"):
                        os.remove(f"{temp_file}.en.vtt")
                    
                    lines = transcript_parts[0].split('\n')
                    clean_lines = [line for line in lines if "-->" not in line and "WEBVTT" not in line and line.strip()]
                    final_transcript = []
                    last_line = ""
                    for line in clean_lines:
                        if line != last_line:
                            final_transcript.append(line)
                            last_line = line
                    
                    return "\n".join(final_transcript)
            
            log("No automatic 'en' captions found.")
            return None
            
    except Exception as e:
        log(f"Error fetching existing transcript: {e}")
        return None

def generate_asr_transcript(video_url: str) -> str:
    # ... (code unchanged)
    log(f"No existing transcript. Starting ASR process for: {video_url}")
    
    try:
        model = whisper.load_model("base")
        log("Whisper 'base' model loaded.")
    except Exception as e:
        log(f"Failed to load Whisper model: {e}")
        raise HTTPException(status_code=500, detail="ASR model failed to load.")

    temp_audio_file = f"temp_audio_{uuid.uuid4().hex}.m4a"
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': temp_audio_file,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        log(f"Audio downloaded: {temp_audio_file}")
    except Exception as e:
        log(f"Failed to download audio: {e}")
        raise HTTPException(status_code=500, detail="Failed to download video audio.")

    try:
        result = model.transcribe(temp_audio_file)
        transcript = result["text"]
        log("Transcription complete.")
        return transcript
    except Exception as e:
        log(f"Failed to transcribe audio: {e}")
        raise HTTPException(status_code=500, detail="ASR model failed to process audio.")
    finally:
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)
            log(f"Cleaned up {temp_audio_file}")


# --- API Endpoint ---

# OLD: @app.post("/transcribe")
@router.post("/transcribe") # <-- NEW: Use the router
async def transcribe_video(
    request: VideoRequest,
    # --- NEW: Add this dependency to protect the endpoint ---
    current_user: models.User = Depends(auth.get_current_user)
) -> TranscriptResponse:
    """
    The main API endpoint for the pipeline. Now requires authentication.
    """
    url = str(request.url)
    # NEW: Log which user is making the request
    log(f"Received request for URL: {url} from user: {current_user.email}")

    filename = get_safe_filename(url)
    url_storage[filename] = url
    
    transcript = None
    source = None
    
    transcript = fetch_existing_transcript(url)
    if transcript:
        log("Returning existing transcript.")
        source = "existing_transcript"
    else:
        log("Falling back to ASR generation.")
        try:
            transcript = generate_asr_transcript(url)
            log("Returning ASR transcript.")
            source = "asr"
        except HTTPException as e:
            raise e
        except Exception as e:
            log(f"Unhandled exception during ASR: {e}")
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

    if transcript:
        save_transcript_to_file(filename, transcript, source)
        if filename in url_storage:
            del url_storage[filename]

    return TranscriptResponse(
        transcript=transcript,
        source=source,
        user_email=current_user.email # <-- NEW
    )

@router.get("/")
def read_root():
    return {"message": "Video Transcription API is running. POST to /transcribe"}
