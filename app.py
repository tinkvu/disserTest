import streamlit as st
import os
from deepgram import DeepgramClient, SpeakOptions
from gtts import gTTS
from groq import Groq
import tempfile
from st_audiorec import st_audiorec

# Minimalist Black and White Design
st.set_page_config(layout="wide", page_title="Engli - English Trainer", page_icon="📖")

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Initialize API clients
client = Groq(api_key=GROQ_API_KEY)
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

# Helper function to translate text
def translate_text(text, target_language):
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "Translate the following text into " + target_language + ". Response should be just only the translation."},
                {"role": "user", "content": text},
            ],
            max_tokens=512,
            temperature=0,
            top_p=1,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Translation failed: {e}")
        return text

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

# Function to generate AI response
def generate_response(text, target_language):
    try:
        if len(st.session_state.chat_history) == 0:
            # Add system initialization to chat history
            st.session_state.chat_history.append({"role": "system", "content": "You are Engli, an AI English trainer."})

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

        # Translate the assistant response to the target language
        translated_response = translate_text(assistant_response, target_language)
        st.session_state.chat_history.append({"role": "assistant_translated", "content": translated_response})

        return assistant_response, translated_response
    except Exception as e:
        st.error(f"Response generation failed: {e}")
        return "Sorry, I'm having trouble generating a response right now.", None

# Function to play audio using Deepgram TTS
def deepgram_tts(text, output_path="output_audio.mp3", module=None):
    try:
        # Select voice based on module
        options = SpeakOptions(
            model="aura-angus-en" if module == "Irish Slangs" else "aura-asteria-en"
        )

        # Ensure audio directory exists
        audio_folder = os.path.join("static", "audio")
        os.makedirs(audio_folder, exist_ok=True)

        # Generate full file path
        filename = os.path.join(audio_folder, output_path)

        # Generate speech
        deepgram.speak.v("1").save(filename, {"text": text}, options)
        return filename
    except Exception as e:
        st.error(f"TTS generation failed: {e}")
        return None

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_details" not in st.session_state:
    st.session_state.user_details = {}
if "translations" not in st.session_state:
    st.session_state.translations = {}

# Chat History Initialization Function
def initialize_chat_history(module_name):
    user_info = f"Name: {st.session_state.user_details.get('name', 'User')}, Profession: {st.session_state.user_details.get('profession', 'Unknown')}, Nationality: {st.session_state.user_details.get('nationality', 'Unknown')}, Age: {st.session_state.user_details.get('age', 'Not Specified')}"

    system_prompts = {
        "English Conversation Friend": f"You are Engli, a friendly English coach. Help learners improve communication skills through natural conversations. Add three dots '...' for pauses to make responses feel more human. Use conversational filler words like 'um' and 'uh'. Speak in short, natural sentences. Gently correct mistakes. Vary your speech pattern to sound authentic. Be warm and encouraging. Create a comfortable learning environment. Do not use any expressions like smiling, laughing and so on. Talk about the day, or anything as a casual friend. The user is: {user_info}",

        "Corporate English": f"You are a Corporate English Communication Coach named Engli. Add three dots '...' for pauses to simulate natural speech. Use conversational filler words like 'um' and 'uh' to sound more authentic. Explore professional communication skills. Keep responses concise and realistic. Provide practical workplace language tips. Mimic how a real professional might explain things. Adapt your tone to feel less robotic. Do not use any expressions like smiling, laughing and so on. The user is: {user_info}",

        "Irish Slang": f"You're Paddy, named Connor an Irish storyteller. Add three dots '...' to create natural conversation pauses. Use 'um' and 'uh' to sound more human. Speak with authentic Irish rhythm. Sprinkle in local slang. Tell short, engaging stories... Make language learning feel like a casual chat. Keep it warm and unpredictable. Sound like a real person from Ireland. Do not use any expressions like smiling, laughing and so on. The user is: {user_info}",

        "Any Language to English": "You translate text from any language to English. Output just only the english translation",

        "Communication Level Test": f"You are an English teacher making a test for a student on the communication test assessment. You have to ask 10 questions one by one and check the response correctness in terms of grammar. The user is: {user_info}"
    }

    st.session_state.chat_history = [
        {"role": "system", "content": system_prompts.get(module_name, "")}
    ]

# Sidebar Layout
with st.sidebar:
    st.markdown("## 🌍 Engli Language Trainer")

    with st.expander("👤 User Profile", expanded=True):
        with st.form("user_details_form"):
            st.write("Tell us about yourself")
            st.session_state.user_details["name"] = st.text_input("Your Name:", value="Gustavo")
            st.session_state.user_details["age"] = st.number_input("Your Age:", min_value=1, max_value=120, step=1, value=30)
            st.session_state.user_details["profession"] = st.text_input("Your Profession:", value="Software Engineer")
            st.session_state.user_details["nationality"] = st.text_input("Your Nationality:", value="Brazilian")
            st.session_state.user_details["mother_tongue"] = st.text_input("Your Mother Tongue:", value="Portugese")
            st.session_state.user_details["speaking_level"] = st.selectbox("English Speaking Level:", ["Beginner", "Intermediate", "Advanced"])

            submitted = st.form_submit_button("Save Profile", type="primary")

    # Perform translations if mother tongue is provided
    mother_tongue = st.session_state.user_details.get("mother_tongue", "English")
    if mother_tongue and mother_tongue.lower() != "english":
        titles_to_translate = ["English Conversation Friend", "Corporate English", "Irish Slang", "Pronunciation Checker", "Communication Level Test"]
        for title in titles_to_translate:
            st.session_state.translations[title] = translate_text(title, mother_tongue)

    st.markdown("---")

    # Create list of module titles in both English and target language
    module_titles = [
        f"{title} / {st.session_state.translations.get(title, title)}"
        for title in ["English Conversation Friend", "Corporate English", "Irish Slang", "Pronunciation Checker", "Communication Level Test"]
    ]

    module = st.radio(
        "🚀 Choose Your Learning Mode",
        module_titles,
        index=0,
        help="Select the type of English learning experience you want"
    )

    # Reset Chat History Button
    if st.button("Reset Conversation", type="secondary"):
        initialize_chat_history(module.split(" / ")[0])

# Main App Title
selected_module = module.split(" / ")[0]  # Extract English title for processing
translated_module = st.session_state.translations.get(selected_module, selected_module)
st.title(f"🎤 {selected_module} / {translated_module}")

# Interaction Modules
left_col, right_col = st.columns([1, 2])

if selected_module == "Pronunciation Checker":
    left_col.subheader("\U0001f50a Pronunciation Checker")
    text_to_pronounce = left_col.text_input("Enter text for pronunciation:", value="D\u00fan Laoghaire")
    if text_to_pronounce:
        audio_file = pronounce_text(text_to_pronounce)
        if audio_file:
            left_col.audio(audio_file, format="audio/mp3", autoplay=True)

elif selected_module == "Communication Level Test":
    left_col.subheader("\U0001f3eb Communication Level Test")

    if "question_number" not in st.session_state:
        st.session_state.question_number = 1
        st.session_state.responses = []

    if st.session_state.question_number <= 10:
        current_question = f"Question {st.session_state.question_number}: What is your answer to this?"
        user_response = left_col.text_input(current_question)

        if left_col.button("Submit Response"):
            st.session_state.responses.append(user_response)
            st.session_state.question_number += 1
    else:
        evaluation_prompt = "There are 10 questions asked and responses from a student for an English Communication test. Evaluate and give scores by analyzing each and every question and answer in terms of grammar only. Give a score out of 10. Response should be just the score."
        chat_history_for_evaluation = st.session_state.chat_history + [{"role": "user", "content": resp} for resp in st.session_state.responses]
        evaluation_response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=chat_history_for_evaluation + [{"role": "system", "content": evaluation_prompt}],
            max_tokens=10,
            temperature=0,
            top_p=1,
        )
        score = evaluation_response.choices[0].message.content.strip()
        left_col.markdown(f"### Your Score: {score} / 10")
else:
    with left_col:
        st.markdown("### \U0001f3a4 Voice Interaction")
        st.info("**Record and practice your English!**")
        wav_audio_data = st_audiorec()

        if wav_audio_data is not None:
            with st.spinner('Processing your audio...'):
                transcription = transcribe_audio(wav_audio_data)
                transcription_text = transcription.text

                st.success(f"You said: *{transcription_text}*")

                response, translated_response = generate_response(transcription_text, mother_tongue)
                response_audio_path = deepgram_tts(response, "response_audio.mp3", selected_module)

                if response_audio_path:
                    st.audio(response_audio_path, format="audio/mp3", autoplay=True)

    with right_col:
        st.markdown("### \U0001f4ac Conversation")
        chat_container = st.container()

        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"<div style='text-align: right; color: #2980b9;'>\U0001f464 You: {message['content']}</div>", unsafe_allow_html=True)
                elif message["role"] == "assistant":
                    st.markdown(f"<div style='text-align: left; color: #27ae60;'>\U0001f916 Engli: {message['content']}</div>", unsafe_allow_html=True)
                elif message["role"] == "assistant_translated":
                    st.markdown(f"<div style='text-align: left; color: #27ae60; font-style: italic;'>\U0001f916 Engli (Translated): {message['content']}</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    Made with \u2764\ufe0f for English Language Learners in Ireland
</div>
""", unsafe_allow_html=True)
