# AI-Based Video Review

This project provides an API endpoint to analyze video presentations, extracting metrics like Words Per Minute (WPM), filler word count, and dominant emotion.

## Prerequisites

*   **Python 3.9+**
*   **pip** (Python package installer)
*   **FFmpeg**: Required for audio extraction. Download and install it from [https://ffmpeg.org/](https://ffmpeg.org/), ensuring it's added to your system's PATH.
*   **(Optional) Docker**: For containerized deployment.

## Manual Setup & Execution

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/DamarKusumo/be-video-analyzer
    cd AI-Based-Video-Review
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    # On Windows
    .\.venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the FastAPI application using Uvicorn:**
    Navigate to the project's root directory (`AI-Based-Video-Review`) in your terminal and run:
    ```bash
    uvicorn project.app.main:app --reload
    ```
    The application will be available at `http://127.0.0.1:8000`.

## Configuration (CORS)

This application uses CORS (Cross-Origin Resource Sharing) middleware to allow requests from web frontends hosted on different origins (domains).

1.  Create a file named `.env` in the root directory of the project (alongside `requirements.txt` and `Dockerfile`).
2.  Add the following line to the `.env` file, replacing the example URLs with the actual origins of your frontend application(s):
    ```
    # Example: ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
    ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
    ```
    *   Multiple origins should be separated by commas without spaces.
3.  **Important:** Ensure `.env` is added to your `.gitignore` file to prevent committing sensitive or environment-specific configurations.

## Docker Setup & Execution

1.  **Build the Docker image:**
    Make sure Docker Desktop or Docker Engine is running. Navigate to the project's root directory in your terminal and run:
    ```bash
    docker build -t video-review-app .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -p 8000:8000 --name video-app-container video-review-app
    ```
    The application will be available at `http://localhost:8000` (or `http://<your-docker-ip>:8000`).

## API Documentation

### Analyze Video

*   **Endpoint:** `/analyze`
*   **Method:** `POST`
*   **Description:** Uploads a video file (.mp4 format recommended) for analysis.
*   **Request:** `multipart/form-data`
    *   `file`: The video file to be analyzed.

*   **Example Request (using cURL):**
    ```bash
    curl -X POST -F "file=@/path/to/your/video.mp4" http://127.0.0.1:8000/analyze
    ```

*   **Success Response (200 OK):** `application/json`
    Returns a JSON object containing the analysis results.
    ```json
    {
      "speed_wpm": 156.23,
      "filler_words": 0,
      "dominant_emotion": "neutral",
      "recommendations": [
        "Gunakan lebih banyak ekspresi wajah positif."
      ]
    }
    ```
    *   `speed_wpm` (float): Calculated words per minute.
    *   `filler_words` (int): Count of detected filler words.
    *   `dominant_emotion` (str): The most frequently detected emotion.
    *   `recommendations` (list[str]): Suggestions for improvement based on the analysis.

*   **Error Responses:**
    *   `422 Unprocessable Entity`: If the file is missing or not in the expected format.
    *   `500 Internal Server Error`: If an error occurs during processing (e.g., FFmpeg issue, model loading failure).
