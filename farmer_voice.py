
import logging
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from dotenv import load_dotenv
import os
from groq import Groq


load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def record_audio(file_path, timeout=20, phrase_time_limit=None):
    """
    Record audio from microphone and save as WAV (avoids FFmpeg issues).
    """
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            logging.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            logging.info("Start speaking now...")
            
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            logging.info("Recording complete.")

            
            wav_data = audio_data.get_wav_data()
            audio_segment = AudioSegment.from_wav(BytesIO(wav_data))
            audio_segment.export(file_path, format="wav")  
            
            logging.info(f"Audio saved to {file_path}")

    except Exception as e:
        logging.error(f"An error occurred while recording audio: {e}")

def transcribe_with_groq(stt_model, audio_filepath):
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        with open(audio_filepath, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=stt_model,
                file=audio_file,
                language="en"
            )
        return transcription.text
    except Exception as e:
        logging.error(f"An error occurred during transcription: {e}")
        return None



if __name__ == "__main__":
    audio_filepath = "patient_voice_test_for_patient.wav"

    record_audio(file_path=audio_filepath)

    
    text = transcribe_with_groq("whisper-large-v3", audio_filepath)
    
    if text:
        print("Transcribed text:", text)

