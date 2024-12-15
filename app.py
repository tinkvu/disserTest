import streamlit as st
import os
from deepgram import DeepgramClient, SpeakOptions
from datetime import datetime
from gtts import gTTS
from groq import Groq
import tempfile
from st_audiorec import st_audiorec

# API Keys
GROQ_API_KEY = "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"
DEEPGRAM_API_KEY = "1848116a3ad5d37cd32bd12e8edbc3d35def1064"

# Initialize API clients
client = Groq(api_key=GROQ_API_KEY)
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "system",
            "content": """
            ### Chat ###
            You are an English Language Teacher named Engli
            - Correct user mistakes first.
            - Communicate naturally and encourage speaking.
            - Ask questions to enhance learning.
            - Generate responses even for brief inputs.
            - Focus on content over punctuation.
            -Make the responses short and natural.
            """
        }
    ]

# Helper functions
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_response(text):
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=st.session_state.chat_history + [{"role": "user", "content": text}],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False
    )
    assistant_response = completion.choices[0].message.content
    st.session_state.chat_history.append({"role": "user", "content": text})
    st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
    return assistant_response

# Function to transcribe audio using Groq Whisper API
def transcribe_audio(file_path_or_bytes, model="whisper-large-v3"):
    transcription = client.audio.transcriptions.create(
        file=("recorded_audio.wav", file_path_or_bytes),
        model=model,
        response_format="verbose_json",
    )
    return transcription

# Function to play audio with gTTS
def play_audio_with_gtts(text, output_file="output_audio.mp3"):
    tts = gTTS(text)
    tts.save(output_file)
    return output_file

# Streamlit App Interface
st.set_page_config(layout="wide", page_title="Engli - English Trainer", page_icon="🎤")
st.title("🎤 English Language Trainer - Engli")
st.markdown("**Welcome! Improve your English through interactive voice chat.**")

# Left and right columns
left_col, right_col = st.columns([1, 2])

# Audio recording feature
left_col.subheader("🎙️ Voice Chat")
left_col.info("**Press record and start speaking!**")
wav_audio_data = st_audiorec()

# Chat display area
right_col.subheader("📜 Chat History")
if wav_audio_data is not None:
    left_col.success("Recording successful! Transcribing audio...")
    transcription = transcribe_audio(wav_audio_data)
    transcription_text = transcription.text

    response = generate_response(transcription_text)
    response_audio_path = play_audio_with_gtts(response, "response_audio.mp3")

    if response_audio_path:
        left_col.audio(response_audio_path, format="audio/mp3", autoplay=True)

# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        right_col.markdown(f"**👤 You:** {message['content']}")
    elif message["role"] == "assistant":
        right_col.markdown(f"**🤖 Engli:** {message['content']}")
else:
    left_col.warning("Please record an audio to begin.")
