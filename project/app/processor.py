import whisper 
import librosa
import cv2
import mediapipe as mp 
import numpy as np
import os
from .utils import extract_audio, detect_emotion_from_video, count_filler_words

def process_video(video_path: str, whisper_model, face_mesh_model):
    audio_path = None
    try:
        audio_path = extract_audio(video_path)

        result = whisper_model.transcribe(audio_path)
        transcript = result["text"]
        duration = result.get("segments", [{"end": 0}])[-1].get("end", 0)
        
        word_count = len(transcript.split())
        wpm = (word_count / (duration / 60)) if duration > 0 else 0

        filler_count = count_filler_words(transcript)

        dominant_emotion = detect_emotion_from_video(video_path, face_mesh_model)

        recommendations = []
        if dominant_emotion != 'neutral': 
            recommendations.append(f"Cobalah untuk menunjukkan lebih banyak emosi {dominant_emotion} jika sesuai.")
        else:
             recommendations.append("Gunakan lebih banyak ekspresi wajah positif.")
        if wpm < 120:
             recommendations.append("Cobalah berbicara sedikit lebih cepat.")
        elif wpm > 180:
             recommendations.append("Cobalah berbicara sedikit lebih lambat.")
        if filler_count > (word_count * 0.05): 
            recommendations.append("Kurangi penggunaan kata-kata pengisi.")

        return {
            "speed_wpm": round(wpm, 2),
            "filler_words": filler_count,
            "dominant_emotion": dominant_emotion,
            "recommendations": recommendations
        }
    finally:
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
                print(f"Successfully removed temporary audio file: {audio_path}")
            except OSError as e:
                print(f"Error removing temporary audio file {audio_path}: {e}")
