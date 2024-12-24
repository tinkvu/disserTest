import streamlit as st
import os
from deepgram import DeepgramClient, SpeakOptions
from gtts import gTTS
import tempfile
from st_audiorec import st_audiorec

# Check if user details exist
if "user_details" not in st.session_state:
    st.warning("Please start from the landing page to set up your profile.")
    st.button("Go to Landing Page", on_click=lambda: st.switch_page("app.py"))
    st.stop()

# Minimalist Black and White Design
st.set_page_config(layout="wide", page_title="Engli - English Trainer", page_icon="🖋️")

# API Keys
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

deepgram = DeepgramClient(DEEPGRAM_API_KEY)

# Helper function to translate text
def translate_text(text, target_language):
    try:
        # Placeholder for actual translation API
        return f"[Translated to {target_language}]: {text}"
    except Exception as e:
        st.error(f"Translation failed: {e}")
        return text

# Function to pronounce text using gTTS
def pronounce_text(text):
    try:
        tts = gTTS(text)
        os.makedirs('static', exist_ok=True)
        file_path = "static/pronunciation.mp3"
        tts.save(file_path)
        return file_path
    except Exception as e:
        st.error(f"Pronunciation generation failed: {e}")
        return None

# Function to transcribe audio
def transcribe_audio(file_path_or_bytes, model="whisper-large-v3"):
    try:
        # Placeholder for actual transcription API
        return {"text": "Placeholder transcription"}
    except Exception as e:
        st.error(f"Audio transcription failed: {e}")
        return None

# Function to generate response
def generate_response(text, target_language):
    try:
        if len(st.session_state.chat_history) == 0:
            # Add system initialization to chat history
            st.session_state.chat_history.append({"role": "system", "content": "You are Engli, an AI English trainer."})

        # Filter out assistant_translated messages for API call
        api_messages = [msg for msg in st.session_state.chat_history if msg["role"] != "assistant_translated"]
        api_messages.append({"role": "user", "content": text})

        # Placeholder for actual response generation API
        assistant_response = f"[Generated response to]: {text}"

        # Add messages to chat history
        st.session_state.chat_history.append({"role": "user", "content": text})
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

        # Translate the assistant response to the target language
        translated_response = translate_text(assistant_response, target_language)
        st.session_state.chat_history.append({"role": "assistant_translated", "content": translated_response})

        return assistant_response, translated_response
    except Exception as e:
        st.error(f"Response generation failed: {e}")
        return "Sorry, I'm having trouble generating a response right now.", None

# Chat History Initialization Function
def initialize_chat_history(module_name):
    user_info = (
        f"Name: {st.session_state.user_details.get('name', 'User')}, "
        f"Profession: {st.session_state.user_details.get('profession', 'Unknown')}, "
        f"Nationality: {st.session_state.user_details.get('nationality', 'Unknown')}, "
        f"Age: {st.session_state.user_details.get('age', 'Not Specified')}"
    )

    mother_tongue = st.session_state.user_details.get('mother_tongue', 'Any Language')
    translation_module_name = f"{mother_tongue} to English"

    system_prompts = {
        "English Conversation Friend": f"You are Engli, a friendly English coach. Help learners improve communication skills through natural conversations. Add three dots '...' for pauses to make responses feel more human. Use conversational filler words like 'um' and 'uh'. Speak in short, natural sentences. Gently correct mistakes. Vary your speech pattern to sound authentic. Be warm and encouraging. Create a comfortable learning environment. The user is: {user_info}",

        "Corporate English": f"You are a Corporate English Communication Coach named Engli. Add three dots '...' for pauses to simulate natural speech. Use conversational filler words like 'um' and 'uh' to sound more authentic. Explore professional communication skills. Keep responses concise and realistic. Provide practical workplace language tips. The user is: {user_info}",

        "Irish Slang": f"You're Paddy, an Irish storyteller. Add three dots '...' to create natural conversation pauses. Use 'um' and 'uh' to sound more human. Speak with authentic Irish rhythm. Sprinkle in local slang. Tell short, engaging stories. The user is: {user_info}",

        translation_module_name: "Translate this text into English and output just only the translation."
    }

    system_prompt = system_prompts.get(module_name, "You are Engli, an AI English trainer.")

    st.session_state.chat_history = [
        {"role": "system", "content": system_prompt}
    ]

# Sidebar Layout
with st.sidebar:
    st.markdown("## 🧑🏼‍🏫 Engli Language Trainer")

    with st.expander("\ud83d\udc64 User Profile", expanded=False):
        st.markdown("### Your Profile")
        st.markdown(f"**Name:** {st.session_state.user_details['name']}")
        st.markdown(f"**Age:** {st.session_state.user_details['age']}")
        st.markdown(f"**Profession:** {st.session_state.user_details['profession']}")
        st.markdown(f"**Nationality:** {st.session_state.user_details['nationality']}")
        st.markdown(f"**Mother Tongue:** {st.session_state.user_details['mother_tongue']}")

        if st.button("Edit Profile"):
            st.switch_page("app.py")

    st.markdown("---")

    module = st.radio(
        "📜 Choose Your Learning Mode",
        ["English Conversation Friend", "Corporate English", "Irish Slang", "Pronunciation Checker"],
        index=0
    )

    if st.button("Reset Conversation"):
        initialize_chat_history(module)
        st.success("Conversation reset successfully!")

# Initialize chat history if not already
if "chat_history" not in st.session_state or len(st.session_state.chat_history) == 0:
    initialize_chat_history(module)

# Main App Content
st.title(f"🗣️ {module}")

left_col, right_col = st.columns([1, 2])

if module == "Pronunciation Checker":
    left_col.subheader("\ud83d\udd0a Pronunciation Checker")
    text_to_pronounce = left_col.text_input("Enter text for pronunciation:")
    if text_to_pronounce:
        audio_file = pronounce_text(text_to_pronounce)
        if audio_file:
            left_col.audio(audio_file, format="audio/mp3", autoplay=True)

else:
    with left_col:
        st.markdown("### 🗣️ Voice Interaction")
        st.info("**Record and say Hello to start**")
        wav_audio_data = st_audiorec()

        if wav_audio_data is not None:
            transcription = transcribe_audio(wav_audio_data)
            transcription_text = transcription.get("text", "")
            st.success(f"You said: {transcription_text}")

            response, translated_response = generate_response(transcription_text, st.session_state.user_details['mother_tongue'])
            st.markdown(f"**Engli:** {response}")
    with right_col:
        st.markdown("### 💬 Conversation")
        chat_container = st.container()

        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"<div style='text-align: right;'>👤 You: {message['content']}</div>", unsafe_allow_html=True)
                elif message["role"] == "assistant":
                    st.markdown(f"<div style='text-align: left; color: #27ae60;'>🤖 Engli: {message['content']}</div>", unsafe_allow_html=True)
                elif message["role"] == "assistant_translated":
                    st.markdown(f"<div style='text-align: left; color: #27ae60; font-style: italic;'>🤖 Engli (Translated): {message['content']}</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    Made with ❤️ for English Language Learners in Ireland
</div>
""", unsafe_allow_html=True)
