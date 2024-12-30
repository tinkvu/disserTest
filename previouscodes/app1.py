import streamlit as st
import os
from deepgram import DeepgramClient, SpeakOptions
from gtts import gTTS
from groq import Groq
from st_audiorec import st_audiorec

# Minimalist Black and White Design
st.set_page_config(layout="wide", page_title="Engli - English Trainer", page_icon="📖")

# API Keys (Use environment variables)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Initialize API clients
client = Groq(api_key=GROQ_API_KEY)
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

# Function to pronounce text using gTTS
def pronounce_text(text):
    try:
        tts = gTTS(text)
        os.makedirs('static', exist_ok=True)
        tts.save("static/pronunciation.mp3")
        return "static/pronunciation.mp3"
    except Exception as e:
        st.error(f"Pronunciation generation failed: {e}")
        return None

# Helper function to generate AI response
def generate_response(text):
    try:
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
    except Exception as e:
        st.error(f"Response generation failed: {e}")
        return "Sorry, I'm having trouble generating a response right now."

# Function to transcribe audio using Groq Whisper API
def transcribe_audio(file_path_or_bytes, model="whisper-large-v3"):
    try:
        transcription = client.audio.transcriptions.create(
            file=("recorded_audio.wav", file_path_or_bytes),
            model=model,
            response_format="verbose_json",
        )
        return transcription
    except Exception as e:
        st.error(f"Audio transcription failed: {e}")
        return None

# Function to play audio using Deepgram TTS
def deepgram_tts(text, output_path="output_audio.mp3", module=None):
    try:
        options = SpeakOptions(
            model="aura-angus-en" if module == "Irish Slangs" else "aura-asteria-en"
        )
        audio_folder = os.path.join("static", "audio")
        os.makedirs(audio_folder, exist_ok=True)
        filename = os.path.join(audio_folder, output_path)
        deepgram.speak.v("1").save(filename, {"text": text}, options)
        return filename
    except Exception as e:
        st.error(f"TTS generation failed: {e}")
        return None

# Initialize session state
if "user_info_complete" not in st.session_state:
    st.session_state.user_info_complete = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_details" not in st.session_state:
    st.session_state.user_details = {}

# Landing Page
if not st.session_state.user_info_complete:
    st.title("Welcome to Engli - Your English Language Trainer! 🌟")
    st.subheader("Let's get started by learning a bit about you.")
    
    with st.form("user_info_form"):
        name = st.text_input("What is your name?", value="Gustavo")
        age = st.number_input("How old are you?", min_value=1, max_value=120, step=1, value=30)
        profession = st.text_input("What is your profession?", value="Software Engineer")
        nationality = st.text_input("What is your nationality?", value="Brazilian")
        
        submit = st.form_submit_button("Start Learning!")
        if submit:
            st.session_state.user_details["name"] = name
            st.session_state.user_details["age"] = age
            st.session_state.user_details["profession"] = profession
            st.session_state.user_details["nationality"] = nationality
            st.session_state.user_info_complete = True
            st.experimental_rerun()

# Main App
else:
    # Sidebar Layout
    with st.sidebar:
        st.markdown("## 🌍 Engli Language Trainer")
        
        with st.expander("👤 User Profile", expanded=True):
            st.write("Your Details:")
            st.write(f"**Name:** {st.session_state.user_details['name']}")
            st.write(f"**Age:** {st.session_state.user_details['age']}")
            st.write(f"**Profession:** {st.session_state.user_details['profession']}")
            st.write(f"**Nationality:** {st.session_state.user_details['nationality']}")
        st.markdown("---")
        module = st.radio(
            "🚀 Choose Your Learning Mode",
            ["English Conversation Friend", "Corporate English", "Irish Slangs", "Pronunciation Checker"],
            index=0,
            help="Select the type of English learning experience you want"
        )
        if st.button("Reset Conversation", type="secondary"):
            st.session_state.chat_history = []

    # Main App Logic
    st.title(f"🎤 {module}")
    
    # Pronunciation Checker Module
    if module == "Pronunciation Checker":
        st.subheader("🔊 Pronunciation Checker")
        text_to_pronounce = st.text_input("Enter text for pronunciation:", value="Dún Laoghaire")
        if text_to_pronounce:
            audio_file = pronounce_text(text_to_pronounce)
            if audio_file:
                st.audio(audio_file, format="audio/mp3", autoplay=True)
    
    # Conversation Modules
    if module != "Pronunciation Checker":
        st.markdown("### 🎙️ Voice Interaction")
        wav_audio_data = st_audiorec()
        if wav_audio_data is not None:
            transcription = transcribe_audio(wav_audio_data)
            if transcription:
                transcription_text = transcription["text"]
                st.success(f"You said: *{transcription_text}*")
                response = generate_response(transcription_text)
                response_audio_path = deepgram_tts(response, "response_audio.mp3", module)
                if response_audio_path:
                    st.audio(response_audio_path, format="audio/mp3", autoplay=True)

        # Display Chat History
        st.markdown("### 💬 Conversation")
        for message in st.session_state.chat_history[1:]:  # Skip system message
            if message["role"] == "user":
                st.markdown(f"👤 You: {message['content']}")
            elif message["role"] == "assistant":
                st.markdown(f"🤖 Engli: {message['content']}")

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        Made with ❤️ for English Language Learners in Ireland
    </div>
    """, unsafe_allow_html=True)
