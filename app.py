import streamlit as st
import os
from deepgram import DeepgramClient, SpeakOptions
from datetime import datetime
from gtts import gTTS
from groq import Groq
import tempfile
import subprocess
from st_audiorec import st_audiorec

# API Keys
GROQ_API_KEY = "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"
DEEPGRAM_API_KEY = "1848116a3ad5d37cd32bd12e8edbc3d35def1064"

# Initialize API clients
client = Groq(api_key=GROQ_API_KEY)
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
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
st.set_page_config(layout="wide")
st.title("English Language Trainer - Engli")

# Left and right columns
left_col, right_col = st.columns(2)

# Audio recording feature
left_col.subheader("Voice Chat")
left_col.write("Record your audio below:")
wav_audio_data = st_audiorec()

# Chat display area
right_col.subheader("Transcriptions and Responses")
if wav_audio_data is not None:
    st.write("Transcribing audio...")
    
    transcription = transcribe_audio(wav_audio_data)

    # Access transcription text and language attributes
    transcription_text = transcription.text
    # transcription_language = transcription.language

    st.subheader("Transcription Results:")
    st.text(transcription_text)
    # with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
    #     temp_audio.write(wav_audio_data)
    #     audio_file = temp_audio.name

    # left_col.audio(audio_file, format="audio/wav")

    # transcription_text = transcribe_audio(audio_file)
    right_col.write(f"**Transcription:** {transcription_text}")

    response = generate_response(transcription_text)
    right_col.write(f"**Response:** {response}")

    response_audio_path = play_audio_with_gtts(response, "response_audio.mp3")
    if response_audio_path:
        left_col.audio(response_audio_path, format="audio/mp3")
# Display complete chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        right_col.markdown(f"**You:** {message['content']}")
    elif message["role"] == "assistant":
        right_col.markdown(f"**Engli:** {message['content']}")
else:
    left_col.info("Please record an audio to begin.")

