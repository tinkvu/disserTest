import streamlit as st
import os
from deepgram import DeepgramClient, SpeakOptions
from datetime import datetime
from gtts import gTTS
from groq import Groq
import tempfile
from st_audiorec import st_audiorec

# Streamlit App Interface
st.set_page_config(layout="wide", page_title="Engli - English Trainer", page_icon="🎤")

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Initialize API clients
client = Groq(api_key=GROQ_API_KEY)
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_details" not in st.session_state:
    st.session_state.user_details = {}

# Collect user details
with st.sidebar.form("user_details_form"):
    st.header("User Information")
    st.session_state.user_details["name"] = st.text_input("Your Name:", placeholder="John Doe")
    st.session_state.user_details["profession"] = st.text_input("Your Profession:", placeholder="Software Engineer")
    st.session_state.user_details["nationality"] = st.text_input("Your Nationality:", placeholder="American")
    st.session_state.user_details["age"] = st.number_input("Your Age:", min_value=1, max_value=120, step=1, value=30)
    submitted = st.form_submit_button("Submit")

# Function to initialize chat history based on module
def initialize_chat_history(module_name):
    user_info = f"Name: {st.session_state.user_details['name']}, Profession: {st.session_state.user_details['profession']}, Nationality: {st.session_state.user_details['nationality']}, Age: {st.session_state.user_details['age']}"
    if module_name == "English Conversation Friend":
        st.session_state.chat_history = [
            {
                "role": "system",
                "content": f"You are an English Language Teacher named Engli. Keep conversations friendly and correct mistakes if any. Your aim is to be the user's English-speaking companion to improve communication skills. Use short, natural responses and add pauses with ellipses (‘…’). {user_info}"
            }
        ]
    elif module_name == "Corporate English":
        st.session_state.chat_history = [
            {
                "role": "system",
                "content": f"You are a Corporate English Coach. Ask the user's profession and provide relevant business communication tips. Use concise and professional language. {user_info}"
            }
        ]
    elif module_name == "Irish Slangs":
        st.session_state.chat_history = [
            {
                "role": "system",
                "content": f"You are a lively old Irish person. Use Irish slang naturally and explain it when necessary. Keep the chat engaging and fun. {user_info}"
            }
        ]
    elif module_name == "Pronunciation Checker":
        st.session_state.chat_history = [
            {
                "role": "system",
                "content": "You help the user check word pronunciation. Ask for text input and pronounce it clearly."
            }
        ]

# Reset conversation
if st.sidebar.button("Reset Conversation"):
    initialize_chat_history(st.session_state.current_module)

# Tutorial Section
def display_tutorial():
    st.header("📚 Welcome to Engli - English Trainer")
    st.markdown(
        """### About the Modules:
        - **English Conversation Friend:** Engage in natural conversations while receiving gentle corrections and language improvement tips.
        - **Corporate English:** Learn professional English tailored to your career. Improve workplace communication skills.
        - **Irish Slangs:** Experience a fun, interactive chat using authentic Irish slang, with clear explanations.
        - **Pronunciation Checker:** Enter words or phrases to hear their correct pronunciation instantly.
        
        ### Project Vision:
        Engli is designed to enhance your English learning experience through personalized and interactive modules. Each module serves a unique purpose, making learning practical, fun, and engaging.
        
        **Get Started Today!**
        """
    )

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

# Module selection
module = st.sidebar.selectbox(
    "Select a Module", ["Tutorial", "English Conversation Friend", "Corporate English", "Irish Slangs", "Pronunciation Checker"]
)

# Update the app title based on the selected module
st.title(f"🎤 {module}")

if module == "Tutorial":
    display_tutorial()
else:
    if "current_module" not in st.session_state or st.session_state.current_module != module:
        initialize_chat_history(module)
        st.session_state.current_module = module

    # Left and right columns
    left_col, right_col = st.columns([1, 2])

    # Pronunciation Checker Module
    if module == "Pronunciation Checker":
        left_col.subheader("🔊 Pronunciation Checker")
        text_to_pronounce = left_col.text_input("Enter text for pronunciation:", placeholder="Dún Laoghaire")
        if text_to_pronounce:
            audio_file = pronounce_text(text_to_pronounce)
            if audio_file:
                left_col.audio(audio_file, format="audio/mp3", autoplay=True)

    # Audio recording feature
    if module != "Pronunciation Checker":
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
    if module != "Pronunciation Checker":
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                right_col.markdown(f"**👤 You:** {message['content']}")
            elif message["role"] == "assistant":
                right_col.markdown(f"**🤖 Engli:** {message['content']}")
        else:
            left_col.warning("Please record an audio to begin.")
