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
    st.session_state.chat_history = []

# Function to initialize chat history based on module
def initialize_chat_history(module_name):
    if module_name == "English Conversation Friend":
        st.session_state.chat_history = [
            {
                "role": "system",
                "content": "You are an English Language Teacher named Engli. Keep conversations friendly, correct mistakes, and provide translations."
            }
        ]
    elif module_name == "Corporate English":
        st.session_state.chat_history = [
            {
                "role": "system",
                "content": "You are a Corporate English Coach. Ask the user's profession and provide corporate language tips."
            }
        ]
    elif module_name == "Irish Slangs":
        st.session_state.chat_history = [
            {
                "role": "system",
                "content": "You are an old Irish person. Use Irish slangs and explain them where needed."
            }
        ]
    elif module_name == "Any Language to English":
        st.session_state.chat_history = [
            {
                "role": "system",
                "content": "You translate text from any language to English and pronounce it clearly."
            }
        ]

# Function to pronounce text using gTTS
def pronounce_text(text):
    try:
        tts = gTTS(text)
        tts.save("pronunciation.mp3")
        return "pronunciation.mp3"
    except Exception as e:
        st.error(f"Pronunciation generation failed: {e}")
        return None

# Helper functions
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

# Function to play audio using Deepgram TTS
def deepgram_tts(text, output_path="output_audio.mp3", module=None):
    try:
        options = SpeakOptions(model="aura-angus-en" if module == "Irish Slangs" else "aura-asteria-en")
        audio_folder = os.path.join("static", "audio")
        if not os.path.exists(audio_folder):
            os.makedirs(audio_folder)
        filename = os.path.join(audio_folder, output_path)
        deepgram.speak.v("1").save(filename, {"text": text}, options)
        return filename
    except Exception as e:
        st.error(f"TTS generation failed: {e}")
        return None

# Streamlit App Interface
st.set_page_config(layout="wide", page_title="Engli - English Trainer", page_icon="🎤")
st.title("🎤 English Language Trainer - Engli")

# Module selection
module = st.sidebar.selectbox(
    "Select a Module", ["English Conversation Friend", "Corporate English", "Irish Slangs", "Any Language to English"]
)
initialize_chat_history(module)

# Left and right columns
left_col, right_col = st.columns([1, 2])

# Pronunciation feature
if module == "Any Language to English":
    left_col.subheader("🔊 Pronunciation Helper")
    text_to_pronounce = left_col.text_input("Enter text for pronunciation:")
    if text_to_pronounce:
        audio_file = pronounce_text(text_to_pronounce)
        if audio_file:
            left_col.audio(audio_file, format="audio/mp3", autoplay=True)

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
    response_audio_path = deepgram_tts(response, "response_audio.mp3", module)

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
