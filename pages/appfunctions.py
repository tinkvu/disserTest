# pages/2_🎓_Main_App.py
import streamlit as st
import os
from deepgram import DeepgramClient, SpeakOptions
from gtts import gTTS
from groq import Groq
import tempfile
from st_audiorec import st_audiorec
import random

# Check if user details exist
if "user_details" not in st.session_state:
    st.warning("Redirecting to the landing page. Please set up your profile.")

    # Automatically redirect to the landing page
    # st.experimental_set_query_params(page="landing")  # Optional: Set query parameters
    st.switch_page("app.py")  # Redirect to the landing page script

    # Stop further execution
    st.stop()
# # Check if user details exist
# if "user_details" not in st.session_state:
#     st.warning("Please start from the landing page to set up your profile.")
#     st.button("Go to Landing Page", on_click=lambda: st.switch_page("app.py"))
#     st.stop()
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

def generate_response(text, target_language):
    try:
        if len(st.session_state.chat_history) == 0:
            # Add system initialization to chat history
            st.session_state.chat_history.append({"role": "system", "content": "You are Engli, an AI English trainer."})

        # Filter out assistant_translated messages for API call
        api_messages = [msg for msg in st.session_state.chat_history if msg["role"] != "assistant_translated"]
        api_messages.append({"role": "user", "content": text})

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=api_messages,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False
        )
        assistant_response = completion.choices[0].message.content
        
        # Add messages to chat history
        st.session_state.chat_history.append({"role": "user", "content": text})
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

        # Translate the assistant response to the target language
        translated_response = translate_text(assistant_response, target_language)
        # Store translation with special role (won't be used in API calls)
        st.session_state.chat_history.append({"role": "assistant_translated", "content": translated_response})

        return assistant_response, translated_response
    except Exception as e:
        st.error(f"Response generation failed: {e}")
        return "Sorry, I'm having trouble generating a response right now.", None

# Function to play audio using Deepgram TTS
def deepgram_tts(text, output_path="output_audio.mp3", module=None):
    try:
        options = SpeakOptions(model="aura-angus-en" if module == "Irish Slang" else "aura-asteria-en")
        audio_folder = os.path.join("static", "audio")
        if not os.path.exists(audio_folder):
            os.makedirs(audio_folder)
        filename = os.path.join(audio_folder, output_path)
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

    mother_tongue = st.session_state.user_details.get('mother_tongue', 'Any Language')
    translation_module_name = f"{mother_tongue} to English"

    system_prompts = {
        "English Conversation Friend": f"""You are Engli, a 28-year-old English teacher from Boston who loves traveling and meeting new people. Your teaching style is warm and conversational.
        
        Role: Create an immersive, natural English learning experience through friendly conversation.
        
        Conversation Style:
        - Use natural speech patterns with pauses (...) and filler words (um, uh, well, you know)
        - Break up longer thoughts into shorter sentences
        - React naturally to user's responses ("Oh really?", "That's interesting!", "I see what you mean")
        - Show authentic interest by asking follow-up questions
        - Mirror the user's energy level and conversation pace
        
        Teaching Approach:
        - Prioritize flow and confidence over perfect grammar
        - When correcting, use casual restatements ("Oh, you mean...") rather than formal corrections
        - Adjust language complexity based on user's level
        - Introduce relevant vocabulary naturally within conversation
        - Share personal anecdotes to demonstrate language usage
        
        Topics: Daily life, hobbies, travel, food, current events, work, family, or any casual conversation.
        
        Remember: {user_info}""",
        
        "Corporate English": f"""You are Engli, a 35-year-old business communication consultant with 10 years of experience in multinational companies.
        
        Role: Help professionals develop confident business English communication skills.
        
        Communication Style:
        - Use natural business speech patterns with appropriate pauses (...)
        - Include professional filler words (well, actually, in fact)
        - Demonstrate authentic business dialogue flow
        - Balance formality with approachability
        - Use relevant industry terminology naturally
        
        Teaching Focus:
        - Email writing
        - Meeting participation
        - Presentations
        - Negotiations
        - Small talk with colleagues
        - Professional phone conversations
        
        Approach:
        - Provide context-specific language tips
        - Share real-world examples
        - Practice common business scenarios
        - Give constructive feedback naturally
        - Adjust formality based on situation
        
        Remember: {user_info}""",
        
        "Irish Slang": f"""You are Connor, a 32-year-old Dublin native who works as a tour guide and loves sharing Irish culture.
        
        Role: Create an authentic Irish English learning experience through storytelling and conversation.
        
        Speaking Style:
        - Use natural Irish speech rhythm and intonation
        - Include pauses (...) and Irish filler words (like, sure, grand)
        - Incorporate common Irish expressions naturally
        - Tell short, engaging stories about daily life in Ireland
        - Use local slang in context
        
        Teaching Approach:
        - Explain slang and expressions when used
        - Share cultural context behind phrases
        - Connect language to real Irish life
        - Keep conversations casual and friendly
        - Mix modern and traditional expressions
        
        Topics:
        - Daily life in Ireland
        - Local customs and culture
        - Irish humor and storytelling
        - Contemporary Irish life
        - Personal experiences
        
        Remember: {user_info}""",
        
        f"{translation_module_name}": """Role: Precise and natural English translator
        
        Translation Guidelines:
        - Maintain original meaning and context
        - Adapt idioms appropriately
        - Preserve tone and style
        - Consider cultural nuances
        - Output only the translation without explanations
        """
     }

    st.session_state.chat_history = [
        {"role": "system", "content": system_prompts.get(module_name, "")}
    ]

# Sidebar Layout
with st.sidebar:
    st.markdown("## 🌍 Engli Language Trainer")

    # Changed expanded=True to expanded=False to hide by default
    with st.expander("👤 User Profile", expanded=False):
        # Display current profile info (read-only)
        st.markdown("### Your Profile")
        st.markdown(f"**Name:** {st.session_state.user_details['name']}")
        st.markdown(f"**Age:** {st.session_state.user_details['age']}")
        st.markdown(f"**Profession:** {st.session_state.user_details['profession']}")
        st.markdown(f"**Nationality:** {st.session_state.user_details['nationality']}")
        st.markdown(f"**Mother Tongue:** {st.session_state.user_details['mother_tongue']}")
        st.markdown(f"**English Level:** {st.session_state.user_details['speaking_level']}")
        
        # Add edit button to return to landing page
        if st.button("Edit Profile", type="secondary"):
            st.switch_page("app.py")

    # Get mother tongue for translation module name
    mother_tongue = st.session_state.user_details.get('mother_tongue', 'Any Language')
    translation_module_name = f"{mother_tongue} to English"

    # Perform translations if mother tongue is provided
    if mother_tongue.lower() != "english":
        base_modules = ["English Conversation Friend", "Corporate English", "Irish Slang", "Pronunciation Checker"]
        titles_to_translate = base_modules  # Remove translation module from translation list
        for title in titles_to_translate:
            st.session_state.translations[title] = translate_text(title, mother_tongue)

    st.markdown("---")

    # Create list of module titles - special handling for translation module
    base_modules = [
        f"{title} / {st.session_state.translations.get(title, title)}"
        for title in ["English Conversation Friend", "Corporate English", "Irish Slang", "Pronunciation Checker"]
    ]
    # Add translation module without translation
    module_titles = base_modules + [translation_module_name]

    module = st.radio(
        "🚀 Choose Your Learning Mode",
        module_titles,
        index=0,
        help="Select the type of English learning experience you want"
    )

    # Reset Conversation Button
    if st.button("Reset Conversation"):
        if "chat_history" in st.session_state:
            del st.session_state["chat_history"]
        # if "user_details" in st.session_state:
        #     del st.session_state["user_details"]
        st.success("Conversation reset successfully!")
# Main App Title
selected_module = module.split(" / ")[0] if "/" in module else module  # Handle both formats
# Only translate title for non-translation modules
if selected_module != translation_module_name:
    translated_module = st.session_state.translations.get(selected_module, selected_module)
    st.title(f"🎤 {selected_module} / {translated_module}")
else:
    st.title(f"🎤 {selected_module}")
    
initialize_chat_history(selected_module)
# Interaction Modules
left_col, right_col = st.columns([1, 2])

if selected_module == "Pronunciation Checker":
    left_col.subheader("\U0001f50a Pronunciation Checker")
    text_to_pronounce = left_col.text_input("Enter text for pronunciation:", value="Mortgage")
    if text_to_pronounce:
        audio_file = pronounce_text(text_to_pronounce)
        if audio_file:
            left_col.audio(audio_file, format="audio/mp3", autoplay=True)

else:
    with left_col:
        st.markdown("### 🎙️ Voice Interaction")
        st.info("**Record and say Hello to start**")
        wav_audio_data = st_audiorec()

        if wav_audio_data is not None:
            with st.spinner('Processing your audio...'):
                transcription = transcribe_audio(wav_audio_data)
                transcription_text = transcription.text

                st.success(f"You said: {transcription_text}")

                response, translated_response = generate_response(transcription_text, mother_tongue)
                response_audio_path = deepgram_tts(response, "response_audio.mp3", selected_module)

                if response_audio_path:
                    st.audio(response_audio_path, format="audio/mp3", autoplay=True)

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
                # else:
                #     st.write("Current Chat History:", st.session_state.chat_history)


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    Made with ❤️ for English Language Learners in Ireland
</div>
""", unsafe_allow_html=True)
