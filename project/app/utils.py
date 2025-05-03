import subprocess
import re
import cv2
import mediapipe as mp
from collections import Counter

def extract_audio(video_path: str) -> str:
    audio_path = video_path.replace(".mp4", ".wav")
    try:
        result = subprocess.run(
            ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path, "-y"],
            capture_output=True,  
            text=True,           
            check=True           
        )
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg failed with error:\n{e.stderr}")
        raise RuntimeError(f"FFmpeg failed: {e.stderr}") from e
    except FileNotFoundError:
        print("FFmpeg command not found. Make sure it's installed and in your PATH.")
        raise RuntimeError("FFmpeg not found. Please install it and add to PATH.")

    return audio_path

def count_filler_words(transcript: str) -> int:
    filler_words = ["uh", "um", "like", "you know", "eh", "kayak", "apa ya"]
    pattern = "|".join(rf"\b{word}\b" for word in filler_words)
    return len(re.findall(pattern, transcript, flags=re.IGNORECASE))

def detect_emotion_from_video(video_path: str, face_mesh_model) -> str:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return "neutral" # Or raise an exception

    emotions = []
    try:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break

            # Process the image and find face landmarks
            # To improve performance, optionally resize the image.
            image.flags.writeable = False
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_mesh_model.process(image_rgb)
            image.flags.writeable = True

            # Basic emotion detection based on lip distance (example)
            if results.multi_face_landmarks:
                # Simplified: Using the first detected face
                landmarks = results.multi_face_landmarks[0].landmark
                # Example landmarks for lips (adjust indices as needed)
                top_lip_y = landmarks[13].y
                bottom_lip_y = landmarks[14].y
                distance = abs(top_lip_y - bottom_lip_y)

                # Very basic thresholding example (needs refinement)
                if distance > 0.04: # Arbitrary threshold for 'happy' (open mouth)
                    emotions.append("happy")
                else:
                    emotions.append("neutral")
    finally:
        cap.release()

    # Return the most common emotion
    return Counter(emotions).most_common(1)[0][0] if emotions else "neutral"
