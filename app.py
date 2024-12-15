import streamlit as st
import os
from deepgram import DeepgramClient, SpeakOptions
from datetime import datetime
from pydub import AudioSegment
from gtts import gTTS
from groq import Groq
import tempfile
import subprocess

# API Keys
GROQ_API_KEY = "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"
DEEPGRAM_API_KEY = "1848116a3ad5d37cd32bd12e8edbc3d35def1064"

# Initialize API clients
client = Groq(api_key=GROQ_API_KEY)
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

# Initial chat history
chat_history = [
    {
        "role": "system",
        "content": """
        ### Chat ###
        You are an English Language Teacher named Engli
        - List any mistakes the user makes and correct them first.
        - Your job is to keep communicating with the user and make them speak.
        - Don't use any emojis, and the responses should be in English.
        - Ask the user questions and help them improve their English.
        - Never stop the conversation. You should generate a response.
        - The responses should mimic a natural human conversational style.
        - If the user message is too short or null, ask them to say it again.
        - Ignore symbol mistakes like missing question marks or commas, since this is a voice chat.
        """
    }
]

# Helper functions
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_response(text):
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=chat_history + [{"role": "user", "content": text}],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False
    )

    assistant_response = completion.choices[0].message.content
    chat_history.append({"role": "assistant", "content": assistant_response})
    return assistant_response

def deepgram_tts(text, output_path):
    options = SpeakOptions(model="aura-asteria-en")
    response = deepgram.speak.v("1").save(output_path, text, options)
    return output_path

# Streamlit App Interface
st.title("English Language Trainer - Engli")

uploaded_file = st.file_uploader("Upload your audio file", type=["mp3", "wav"])

if uploaded_file:
    st.success(f"Uploaded file: {uploaded_file.name}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        audio_file = temp_file.name
        if not uploaded_file.name.endswith(".wav"):
            try:
                sound = AudioSegment.from_file(uploaded_file)
                sound.export(audio_file, format="wav")
            except FileNotFoundError:
                st.error("'ffprobe' is required but not found. Please install ffmpeg.")
                st.stop()
        else:
            audio_file = uploaded_file.name

    st.audio(audio_file, format="audio/wav")

    # Simulate transcription (mock for now)
    transcription_text = "This is a sample transcription of the audio file."
    st.write(f"**Transcription:** {transcription_text}")

    response = generate_response(transcription_text)
    st.write(f"**Response:** {response}")

    response_audio_path = deepgram_tts(response, "response_audio.mp3")
    st.audio(response_audio_path, format="audio/mp3")
else:
    st.info("Please upload an audio file to begin.")
