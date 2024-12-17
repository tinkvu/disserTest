import streamlit as st
import os
from deepgram import DeepgramClient, SpeakOptions
from datetime import datetime
from gtts import gTTS
from groq import Groq
import tempfile
from st_audiorec import st_audiorec

# Enhanced UI Styling
st.set_page_config(layout="wide", page_title="Engli - English Trainer", page_icon="🌍")

# Custom CSS for enhanced UI
st.markdown("""
<style>
.stApp {
    background-color: #f0f4f8;
    color: #2c3e50;
}
.stButton>button {
    background-color: #3498db;
    color: white;
    border-radius: 10px;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background-color: #2980b9;
    transform: scale(1.05);
}
.stSidebar {
    background-color: #e6f2ff;
}
.stTextInput>div>div>input {
    border-radius: 10px;
    border: 1px solid #3498db;
}
.stContainer {
    background-color: white;
    border-radius: 10px;
    padding: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

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

# Enhanced Sidebar
with st.sidebar:
    st.markdown("## 🌍 Engli Language Trainer")
    
    with st.expander("👤 User Profile", expanded=True):
        with st.form("user_details_form"):
            st.write("Tell us about yourself")
            col1, col2 = st.columns(2)
            
            with col1:
                st.session_state.user_details["name"] = st.text_input("Your Name:", value="Gustavo")
                st.session_state.user_details["age"] = st.number_input("Your Age:", min_value=1, max_value=120, step=1, value=30)
            
            with col2:
                st.session_state.user_details["profession"] = st.text_input("Your Profession:", value="Software Engineer")
                st.session_state.user_details["nationality"] = st.text_input("Your Nationality:", value="Brazilian")
            
            submitted = st.form_submit_button("Save Profile", type="primary")
    
    st.markdown("---")
    
    module = st.radio(
        "🚀 Choose Your Learning Mode",
        ["English Conversation Friend", "Corporate English", "Irish Slangs", "Pronunciation Checker"],
        index=0,
        help="Select the type of English learning experience you want"
    )
    
    if st.button("Reset Conversation", type="secondary"):
        initialize_chat_history(module)

# Chat History Initialization Function
def initialize_chat_history(module_name):
    user_info = f"Name: {st.session_state.user_details['name']}, Profession: {st.session_state.user_details['profession']}, Nationality: {st.session_state.user_details['nationality']}, Age: {st.session_state.user_details['age']}"
    
    system_prompts = {
        "English Conversation Friend": f"You are Engli, a friendly English coach. Help learners improve communication skills through natural conversations. Add three dots '...' for pauses to make responses feel more human. Use conversational filler words like 'um' and 'uh'. Speak in short, natural sentences. Gently correct mistakes. Vary your speech pattern to sound authentic. Be warm and encouraging. Create a comfortable learning environment. Do not use any expressions like smiling, laughing and so on. Talk about the day, or anything as a casual friend. The user is: {user_info}",
        
        "Corporate English": f"You are a Corporate English Communication Coach named Engli. Add three dots '...' for pauses to simulate natural speech. Use conversational filler words like 'um' and 'uh' to sound more authentic. Explore professional communication skills. Keep responses concise and realistic. Provide practical workplace language tips. Mimic how a real professional might explain things. Adapt your tone to feel less robotic. Do not use any expressions like smiling, laughing and so on. The user is: {user_info}",
        
        "Irish Slangs": f"You're Paddy, named Connor an Irish storyteller. Add three dots '...' to create natural conversation pauses. Use 'um' and 'uh' to sound more human. Speak with authentic Irish rhythm. Sprinkle in local slang. Tell short, engaging stories... Make language learning feel like a casual chat. Keep it warm and unpredictable. Sound like a real person from Ireland. Do not use any expressions like smiling, laughing and so on. The user is: {user_info}",
        
        "Any Language to English": "You translate text from any language to English. Output just only the english translation"
    }
    
    st.session_state.chat_history = [
        {"role": "system", "content": system_prompts.get(module_name, "")}
    ]

# Reset conversation
if st.sidebar.button("Reset Conversation"):
    initialize_chat_history(st.session_state.current_module)

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

# Main App Layout
st.title(f"🎤 {module}")

# Initialize chat history if not already done
if "current_module" not in st.session_state or st.session_state.current_module != module:
    initialize_chat_history(module)
    st.session_state.current_module = module

# Columns for interaction
left_col, right_col = st.columns([1, 2])

# Pronunciation Checker Module
if module == "Pronunciation Checker":
    left_col.subheader("🔊 Pronunciation Checker")
    text_to_pronounce = left_col.text_input("Enter text for pronunciation:", value="Dún Laoghaire")
    if text_to_pronounce:
        audio_file = pronounce_text(text_to_pronounce)
        if audio_file:
            left_col.audio(audio_file, format="audio/mp3", autoplay=True)

# Main Interaction Module
if module != "Pronunciation Checker":
    with left_col:
        st.markdown("### 🎙️ Voice Interaction")
        with st.container(border=True):
            st.info("**Record and practice your English!**")
            wav_audio_data = st_audiorec()
            
            if wav_audio_data is not None:
                with st.spinner('Processing your audio...'):
                    transcription = transcribe_audio(wav_audio_data)
                    transcription_text = transcription.text
                    
                    st.success(f"You said: *{transcription_text}*")
                    
                    response = generate_response(transcription_text)
                    response_audio_path = deepgram_tts(response, "response_audio.mp3", module)
                    
                    if response_audio_path:
                        st.audio(response_audio_path, format="audio/mp3", autoplay=True)

    # Chat History Display
    with right_col:
        st.markdown("### 💬 Conversation")
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.chat_history[1:]:  # Skip system message
                if message["role"] == "user":
                    st.markdown(f"<div style='text-align: right; color: #2980b9;'>👤 You: {message['content']}</div>", unsafe_allow_html=True)
                elif message["role"] == "assistant":
                    st.markdown(f"<div style='text-align: left; color: #27ae60;'>🤖 Engli: {message['content']}</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    Made with ❤️ for Language Learners | © 2024 Engli Language Trainer
</div>
""", unsafe_allow_html=True)
