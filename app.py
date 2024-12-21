import streamlit as st
import os
from deepgram import DeepgramClient, SpeakOptions
from gtts import gTTS
from groq import Groq
import tempfile
from st_audiorec import st_audiorec
import random

# Streamlit configuration
st.set_page_config(layout="wide", page_title="Engli - English Trainer", page_icon="📖")

# API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Initialize API clients
client = Groq(api_key=GROQ_API_KEY)
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

# Constants
QUESTIONS_POOL = [
    "Can you tell me about your favorite hobby?",
    "Describe your last holiday.",
    "What would you do if you could live anywhere in the world?",
    "Explain how to make a cup of tea.",
    "What are your plans for the weekend?",
    "Tell me about your favorite book or movie.",
    "What do you like to do in your free time?",
    "Describe your typical day.",
    "What is something new you learned recently?",
    "If you could meet any historical figure, who would it be and why?"
]

SYSTEM_PROMPTS = {
    "English Conversation Friend": "You are Engli, a friendly English coach. Help learners improve communication skills through natural conversations. Add three dots '...' for pauses. Use conversational filler words like 'um' and 'uh'. Speak in short, natural sentences. Gently correct mistakes. Be warm and encouraging.",
    
    "Corporate English": "You are a Corporate English Communication Coach named Engli. Add three dots '...' for pauses. Use professional yet conversational language. Focus on workplace communication. Provide practical business English tips. Keep responses concise and realistic.",
    
    "Irish Slang": "You're Connor, an Irish storyteller. Add three dots '...' for pauses. Use authentic Irish rhythm and local slang. Tell short, engaging stories. Make language learning feel like a casual chat.",
    
    "Any Language to English": "You translate text from any language to English. Output only the English translation.",
    
    "Communication Level Test": "You are an English teacher conducting a communication test assessment. Evaluate responses for grammar and provide constructive feedback."
}

def translate_text(text, target_language):
    """Translate text using Groq API."""
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": f"Translate the following text into {target_language}. Response should be just the translation."},
                {"role": "user", "content": text},
            ],
            max_tokens=512,
            temperature=0,
            top_p=1,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Translation failed: {str(e)}")
        return text

def generate_audio(text, output_path, module=None):
    """Generate audio using Deepgram TTS or gTTS."""
    try:
        if module == "Irish Slang":
            options = SpeakOptions(model="aura-angus-en")
        else:
            options = SpeakOptions(model="aura-asteria-en")

        audio_folder = os.path.join("static", "audio")
        os.makedirs(audio_folder, exist_ok=True)
        filename = os.path.join(audio_folder, output_path)

        deepgram.speak.v("1").save(filename, {"text": text}, options)
        return filename
    except Exception as e:
        # Fallback to gTTS if Deepgram fails
        try:
            tts = gTTS(text)
            tts.save(filename)
            return filename
        except Exception as e2:
            st.error(f"Audio generation failed: {str(e2)}")
            return None

def transcribe_audio(audio_data):
    """Transcribe audio using Groq API."""
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name

        transcription = client.audio.transcriptions.create(
            file=open(temp_file_path, "rb"),
            model="whisper-large-v3"
        )
        os.unlink(temp_file_path)
        return transcription.text
    except Exception as e:
        st.error(f"Transcription failed: {str(e)}")
        return None

def generate_response(text, mother_tongue):
    """Generate AI response with translation."""
    try:
        messages = st.session_state.chat_history + [{"role": "user", "content": text}]
        
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            temperature=1,
            max_tokens=1024,
            top_p=1
        )
        
        response = completion.choices[0].message.content
        translated = translate_text(response, mother_tongue) if mother_tongue.lower() != "english" else None
        
        st.session_state.chat_history.extend([
            {"role": "user", "content": text},
            {"role": "assistant", "content": response}
        ])
        
        if translated:
            st.session_state.chat_history.append({"role": "assistant_translated", "content": translated})
        
        return response, translated
    except Exception as e:
        st.error(f"Response generation failed: {str(e)}")
        return "I'm having trouble generating a response right now.", None

def initialize_session_state():
    """Initialize session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "user_details" not in st.session_state:
        st.session_state.user_details = {}
    if "translations" not in st.session_state:
        st.session_state.translations = {}
    if "question_number" not in st.session_state:
        st.session_state.question_number = 1
    if "questions" not in st.session_state:
        st.session_state.questions = random.sample(QUESTIONS_POOL, 10)
    if "responses" not in st.session_state:
        st.session_state.responses = []

def render_sidebar():
    """Render sidebar with user profile and module selection."""
    with st.sidebar:
        st.markdown("## 🌍 Engli Language Trainer")
        
        with st.expander("👤 User Profile", expanded=True):
            with st.form("user_details_form"):
                st.write("Tell us about yourself")
                fields = {
                    "name": ("Your Name:", "Gustavo"),
                    "age": ("Your Age:", 30),
                    "profession": ("Your Profession:", "Software Engineer"),
                    "nationality": ("Your Nationality:", "Brazilian"),
                    "mother_tongue": ("Your Mother Tongue:", "Portuguese"),
                    "speaking_level": ("English Speaking Level:", ["Beginner", "Intermediate", "Advanced"])
                }
                
                for field, (label, default) in fields.items():
                    if field == "age":
                        st.session_state.user_details[field] = st.number_input(label, min_value=1, max_value=120, value=default)
                    elif field == "speaking_level":
                        st.session_state.user_details[field] = st.selectbox(label, default)
                    else:
                        st.session_state.user_details[field] = st.text_input(label, value=default)
                
                submitted = st.form_submit_button("Save Profile", type="primary")

        st.markdown("---")
        
        mother_tongue = st.session_state.user_details.get("mother_tongue", "English")
        module_titles = ["English Conversation Friend", "Corporate English", "Irish Slang", 
                        "Pronunciation Checker", "Communication Level Test"]
        
        if mother_tongue.lower() != "english":
            for title in module_titles:
                st.session_state.translations[title] = translate_text(title, mother_tongue)
        
        module_options = [
            f"{title} / {st.session_state.translations.get(title, title)}"
            for title in module_titles
        ]
        
        selected_module = st.radio("🚀 Choose Your Learning Mode", module_options, index=0)
        
        if st.button("Reset Conversation", type="secondary"):
            st.session_state.chat_history = []
            initialize_chat_history(selected_module.split(" / ")[0])
        
        return selected_module.split(" / ")[0]

def render_main_content(selected_module):
    """Render main content based on selected module."""
    st.title(f"🎤 {selected_module}")
    
    left_col, right_col = st.columns([1, 2])
    
    if selected_module == "Pronunciation Checker":
        render_pronunciation_checker(left_col)
    elif selected_module == "Communication Level Test":
        render_communication_test(left_col)
    else:
        render_conversation_interface(left_col, right_col)

def render_pronunciation_checker(column):
    """Render pronunciation checker interface."""
    column.subheader("🔊 Pronunciation Checker")
    text = column.text_input("Enter text for pronunciation:", value="Hello, how are you?")
    
    if text:
        audio_file = generate_audio(text, "pronunciation.mp3")
        if audio_file:
            column.audio(audio_file, format="audio/mp3")

def render_communication_test(column):
    """Render communication test interface."""
    if st.session_state.question_number <= len(st.session_state.questions):
        current_question = st.session_state.questions[st.session_state.question_number - 1]
        column.write(f"Question {st.session_state.question_number}: {current_question}")
        
        user_response = column.text_area("Your answer:", key=f"response_{st.session_state.question_number}")
        
        if column.button("Next Question"):
            if user_response:
                st.session_state.responses.append({
                    "question": current_question,
                    "response": user_response
                })
                st.session_state.question_number += 1
                st.experimental_rerun()
    else:
        show_test_results()

def show_test_results():
    """Show communication test results."""
    evaluation_prompt = (
        "Evaluate the following English communication test responses for grammar. "
        "Provide a score out of 10 and brief feedback for each response."
    )
    
    evaluation = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": evaluation_prompt},
            {"role": "user", "content": str(st.session_state.responses)}
        ],
        max_tokens=500,
        temperature=0.7
    )
    
    st.markdown("### Test Results")
    st.write(evaluation.choices[0].message.content)

def render_conversation_interface(left_col, right_col):
    """Render main conversation interface."""
    with left_col:
        st.markdown("### 🎙️ Voice Interaction")
        st.info("Record and practice your English!")
        
        audio_data = st_audiorec()
        if audio_data is not None:
            with st.spinner('Processing your audio...'):
                transcription = transcribe_audio(audio_data)
                if transcription:
                    st.success(f"You said: *{transcription}*")
                    
                    mother_tongue = st.session_state.user_details.get("mother_tongue", "English")
                    response, translated = generate_response(transcription, mother_tongue)
                    
                    audio_path = generate_audio(response, "response.mp3")
                    if audio_path:
                        st.audio(audio_path, format="audio/mp3")

    with right_col:
        render_chat_history()

def render_chat_history():
    """Render chat history."""
    st.markdown("### 💬 Conversation")
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"<div style='text-align: right; color: #2980b9;'>👤 You: {message['content']}</div>", 
                       unsafe_allow_html=True)
        elif message["role"] == "assistant":
            st.markdown(f"<div style='text-align: left; color: #27ae60;'>🤖 Engli: {message['content']}</div>", 
                       unsafe_allow_html=True)
        elif message["role"] == "assistant_translated":
            st.markdown(f"<div style='text-align: left; color: #27ae60; font-style: italic;'>🤖 Translated: {message['content']}</div>", 
                       unsafe_allow_html=True)

def main():
    """Main application entry point."""
    initialize_session_state()
    selected_module = render_sidebar()
    render_main_content(selected_module)
    
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: gray;'>
            Made with ❤️ for English Language Learners in Ireland
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
