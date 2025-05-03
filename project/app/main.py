import os
from pathlib import Path
import time
import uuid
import shutil
import asyncio
import whisper
import mediapipe as mp
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .processor import process_video
from .models import AnalysisResult

# Load environment variables from .env file
load_dotenv()

# ---- Model Loading and Lifespan Management ----

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models during startup
    print("Loading models...")
    # Use a smaller/faster Whisper model
    app.state.whisper_model = whisper.load_model("tiny.en")
    app.state.face_mesh_model = mp.solutions.face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=False)
    print("Models loaded successfully.")
    yield
    # Clean up models and resources during shutdown
    print("Closing models...")
    if hasattr(app.state, 'face_mesh_model') and app.state.face_mesh_model:
        app.state.face_mesh_model.close()
    # Whisper model might not have an explicit close method
    print("Models closed.")

app = FastAPI(lifespan=lifespan)

# ---- CORS Middleware Setup ----

allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "") # Default to empty string if not set
origins = [origin.strip() for origin in allowed_origins_str.split(',') if origin.strip()]

# Add a fallback if origins list is empty after reading env var
if not origins:
    print("WARN: ALLOWED_ORIGINS environment variable not set or empty. Allowing default origins for local dev: http://localhost:8000, http://127.0.0.1:8000")
    origins = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        # Add other default origins if needed, e.g., your common frontend dev port
        # "http://localhost:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all standard methods
    allow_headers=["*"], # Allows all headers
)

# ---- File Paths and Directory Setup ----

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()
UPLOADS_DIR = SCRIPT_DIR / ".." / ".." / "uploads"
# Create uploads directory if it doesn't exist
os.makedirs(UPLOADS_DIR, exist_ok=True)

# ---- API Endpoint ----

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_video(request: Request, file: UploadFile = File(...)):
    # Generate a unique filename to avoid collisions and simplify cleanup
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4().hex[:8])
    # Sanitize filename (optional, but good practice)
    original_stem = Path(file.filename).stem.replace(' ', '_')
    unique_filename = f"{timestamp}_{unique_id}_{original_stem}{Path(file.filename).suffix}"
    filepath = UPLOADS_DIR / unique_filename

    # Save the uploaded file temporarily
    try:
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")
    finally:
        await file.close()

    # Process video in a separate thread to avoid blocking the event loop
    try:
        # Retrieve pre-loaded models from app state
        whisper_model = request.app.state.whisper_model
        face_mesh_model = request.app.state.face_mesh_model

        # --- Start timing ---
        start_time = time.monotonic()
        print(f"Starting processing for: {filepath}")

        # Run the blocking function in a thread pool
        analysis_result = await asyncio.to_thread(
            process_video, str(filepath), whisper_model, face_mesh_model
        )

        # --- End timing and log duration ---
        end_time = time.monotonic()
        duration = end_time - start_time
        print(f"Finished processing {filepath} in {duration:.2f} seconds")

        return analysis_result
    except Exception as e:
        # Log the exception details here if needed
        print(f"Error processing video {filepath}: {e}")
        # Re-raise a more generic error or a specific one
        raise HTTPException(status_code=500, detail=f"Error during video analysis: {e}")
    finally:
        # Clean up the temporary uploaded video file
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"Successfully removed temporary file: {filepath}")
            except OSError as e:
                # Log this error, as it might indicate a problem
                print(f"Error removing temporary file {filepath}: {e}")
