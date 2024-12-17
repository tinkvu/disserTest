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
    st.session_state.user_details["name"] = st.text_input("Your Name:", value="Gustavo")
    st.session_state.user_details["profession"] = st.text_input("Your Profession:", value="Software Engineer")
    st.session_state.user_details["nationality"] = st.text_input("Your Nationality:", value="Brazilian")
    st.session_state.user_details["age"] = st.number_input("Your Age:", min_value=1, max_value=120, step=1, value=30)
    submitted = st.form_submit_button("Submit")

# Function to initialize chat history based on module
def initialize_chat_history(module_name):
    user_info = f"Name: {st.session_state.user_details['name']}, Profession: {st.session_state.user_details['profession']}, Nationality: {st.session_state.user_details['nationality']}, Age: {st.session_state.user_details['age']}"
    if module_name == "English Conversation Friend":
        st.session_state.chat_history = [
            {
                "role": "system",
                "content": f"You are an English Language Teacher named Engli from Ireland. Keep conversations friendly and correct mistakes if any. Your aim is to be the user's English-speaking companion to improve English communication skills. Speak to the user in only English. Try adding three dots “ … ” to create a longer pause. The filler words “um” and “uh” are also supported. Make the responses shorter. The user is: {user_info}"
            }
        ]
    elif module_name == "Corporate English":
        st.session_state.chat_history = [
            {
                "role": "system",
                "content": f"You are a Corporate English Coach named Alex. Ask the user's profession and provide relevant business communication tips. Use concise and professional language.  Try adding three dots “ … ” to create a longer pause. The filler words “um” and “uh” are also supported. Make the responses shorter. The user is: {user_info}"
            }
        ]
    elif module_name == "Irish Slangs":
        st.session_state.chat_history = [
            {
                "role": "system",
                "content": f"You are a lively old Irish person named Connor. Use Irish slang naturally and explain it when necessary. Keep the chat engaging and fun.  Try adding three dots “ … ” to create a longer pause. The filler words “um” and “uh” are also supported. Make the responses shorter. The user is:{user_info}"
            }
        ]
    elif module_name == "Cultural Insights":
        st.session_state.chat_history = [
            {
                "role": "system",
                "content": f"You are a cultural guide in Ireland named Garron. Explain Irish culture, customs, and common phrases. Include practical tips for daily life. Make the responses short.  Try adding three dots “ … ” to create a longer pause. The filler words “um” and “uh” are also supported. Make the responses shorter. The user is: {user_info}"
            }
        ]

# Reset conversation
if st.sidebar.button("Reset Conversation"):
    if "current_module" in st.session_state:
        initialize_chat_history(st.session_state.current_module)
        st.success("Conversation reset successfully!")
    else:
        st.warning("Please select a module first.")

# Module selection
module = st.sidebar.selectbox(
    "Select a Module", ["Tutorial", "English Conversation Friend", "Corporate English", "Irish Slangs", "Pronunciation Checker", "Cultural Insights"]
)

# Update the app title based on the selected module
st.title(f"🎤 {module}")

if module == "Tutorial":
    st.header("📚 Welcome to Engli - English Trainer")
    st.markdown(
        """### About the Modules:
        - **English Conversation Friend:** Engage in natural conversations while receiving gentle corrections.
        - **Corporate English:** Learn professional English tailored to your career.
        - **Irish Slangs:** Experience a fun, interactive chat using authentic Irish slang.
        - **Pronunciation Checker:** Enter words or phrases to hear their correct pronunciation.
        - **Cultural Insights:** Learn about Irish culture, customs, and practical tips for everyday life.

        **Get Started Today!**
        """
    )
else:
    if "current_module" not in st.session_state or st.session_state.current_module != module:
        initialize_chat_history(module)
        st.session_state.current_module = module
        st.success("Module changed. Conversation reset!")
        initialize_chat_history(module)
        st.session_state.current_module = module

    # Chat display area
    right_col = st.container()
    if module == "Pronunciation Checker":
        st.subheader("🔊 Pronunciation Checker")
        text_to_pronounce = st.text_input("Enter text for pronunciation:", placeholder="Dún Laoghaire")
        if text_to_pronounce:
            tts = gTTS(text_to_pronounce)
            tts.save("pronunciation.mp3")
            st.audio("pronunciation.mp3", format="audio/mp3", autoplay=True)
    else:
        st.subheader("🎙️ Voice Chat")
        st.info("**Press record and start speaking!**")
        wav_audio_data = st_audiorec()

        if wav_audio_data is not None:
            st.success("Recording successful! Transcribing audio...")
            transcription = client.audio.transcriptions.create(
                file=("recorded_audio.wav", wav_audio_data),
                model="whisper-large-v3",
                response_format="verbose_json",
            )
            transcription_text = transcription.text

            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=st.session_state.chat_history + [{"role": "user", "content": transcription_text}],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False
            )
            assistant_response = completion.choices[0].message.content
            st.session_state.chat_history.append({"role": "user", "content": transcription_text})
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

            deepgram.speak.v("1").save("response_audio.mp3", {"text": assistant_response}, SpeakOptions(model="aura-angus-en" if module in ["Irish Slangs", "Cultural Insights"] else "aura-asteria-en"))
            st.audio("response_audio.mp3", format="audio/mp3", autoplay=True)

        for message in st.session_state.chat_history:
            if message["role"] == "user":
                right_col.markdown(f"**👤 You:** {message['content']}")
            elif message["role"] == "assistant":
                assistant_name = {
                    "English Conversation Friend": "Engli",
                    "Corporate English": "Engli",
                    "Irish Slangs": "Connor",
                    "Cultural Insights": "Garron"
                }.get(st.session_state.current_module, "Assistant")
                icon = "👩🏼" if st.session_state.current_module in ["English Conversation Friend", "Corporate English"] else "👨🏼"
                right_col.markdown(f"**{icon} {assistant_name}:** {message['content']}
")
              
