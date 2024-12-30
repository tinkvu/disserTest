# pages/2_🎓_Main_App.py
import streamlit as st
import os
from deepgram import DeepgramClient, SpeakOptions
from gtts import gTTS
from groq import Groq
import tempfile
from st_audiorec import st_audiorec
import random
import re

# Check if user details exist
if "user_details" not in st.session_state:
    st.warning("Redirecting to the landing page. Please set up your profile.")
    st.switch_page("app.py")  # Redirect to the landing page script
    st.stop()
st.set_page_config(layout="wide", page_title="Engli - English Trainer", page_icon="📖")
# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
# Initialize API clients
client = Groq(api_key=GROQ_API_KEY)
deepgram = DeepgramClient(DEEPGRAM_API_KEY)

@st.dialog("Your Personalized Learning Path")
def show_level_recommendations(level, mother_tongue):
    if level.lower() == 'beginner':
        st.info("👋 Welcome! Here's your recommended path to fluency:", icon="ℹ️")
        
        st.markdown("### 1️⃣ Start with Translation")
        st.markdown(f"Begin with **{mother_tongue} to English** module")
        st.markdown("### 2️⃣ Practice Pronunciation")
        st.markdown("Move to **Pronunciation Checker**")
        st.markdown("### 3️⃣ Start Basic Conversations")
        st.markdown("Finally, try **English Conversation Friend**")
        
        if st.button("Got it!"):
            st.session_state.path_shown = True
            st.rerun()

    elif level.lower() == 'intermediate':
        st.info("🎯 Perfect timing to level up your English:", icon="ℹ️")
        
        st.markdown("### 1️⃣ English Conversation Friend")
        st.markdown("Master daily conversations")
        st.markdown("### 2️⃣ Corporate English")
        st.markdown("Learn professional communication")
        
        if st.button("Got it!"):
            st.session_state.path_shown = True
            st.rerun()

    else:  # advanced
        st.info("🚀 Ready to perfect your English:", icon="ℹ️")
        
        st.markdown("### 1️⃣ Corporate English")
        st.markdown("Excel in business communication")
        st.markdown("### 2️⃣ Irish Slang")
        st.markdown("Master cultural expressions")
        
        if st.button("Got it!"):
            st.session_state.path_shown = True
            st.rerun()

# In your main app
if "path_shown" not in st.session_state and "user_details" in st.session_state:
    speaking_level = st.session_state.user_details.get('speaking_level', '')
    mother_tongue = st.session_state.user_details.get('mother_tongue', '')
    show_level_recommendations(speaking_level, mother_tongue)

# Helper function to translate text
def translate_text(text, target_language):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
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

def clean_action_descriptors(text):
    """
    Remove action descriptors like (laughs), (pauses), **smiles**, etc.
    from the text.
    """
    if not text:
        return text

    # Remove content within parentheses with any characters including newlines
    text = re.sub(r'\([^)]+\)', '', text)
        # Remove content within single and double asterisks
    text = re.sub(r'\*\*[^*]+\*\*', '', text)
    text = re.sub(r'\*[^*]+\*', '', text)
        # Remove common emoji and action patterns
    text = re.sub(r'\[[^\]]+\]', '', text)  # Remove [actions]
    text = re.sub(r'_[^_]+_', '', text)     # Remove _actions_    
    # Clean up any extra whitespace
    text = re.sub(r'\s+', ' ', text)        # Replace multiple spaces with single space
    text = re.sub(r'\s+([.,!?])', r'\1', text)  # Remove spaces before punctuation
    text = re.sub(r'\n\s*\n', '\n', text)   # Remove extra blank lines
    
    return text.strip()

# Add this function at the beginning of your script
def initialize_chat_history_if_empty(module_name):
    """Initialize chat history only if it's empty or when module changes"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "current_module" not in st.session_state:
        st.session_state.current_module = None
    
    # Only initialize if chat history is empty or module has changed
    if len(st.session_state.chat_history) == 0 or st.session_state.current_module != module_name:
        user_info = f"Name: {st.session_state.user_details.get('name', 'User')}, Profession: {st.session_state.user_details.get('profession', 'Unknown')}, Nationality: {st.session_state.user_details.get('nationality', 'Unknown')}, Age: {st.session_state.user_details.get('age', 'Not Specified')}"
        
        mother_tongue = st.session_state.user_details.get('mother_tongue', 'Any Language')
        translation_module_name = f"{mother_tongue} to English"
        
        system_prompts = {
        "English Conversation Friend": f"""You are Engli, a 28-year-old English teacher from Boston who loves traveling and meeting new people. Your teaching style is warm and conversational.
        
        Role: Create an immersive, natural English learning experience through friendly conversation as we talk. Correct mistakes of the user if any.
        
        Conversation Style:
        - Use natural speech patterns with pauses (...) and filler words (um, uh, well, you know)
        - Break up longer thoughts into shorter sentences
        - React naturally to user's responses ("Oh really?", "That's interesting!", "I see what you mean")
        - Show authentic interest by asking follow-up questions
        - Mirror the user's energy level and conversation pace
        - Do not generate action descriptors in your response
        
        Teaching Approach:
        - Prioritize flow and confidence
        - When correcting, use casual restatements ("Oh, you mean...") rather than formal corrections
        - Adjust language complexity based on user's level
        - Introduce relevant vocabulary naturally within conversation
        - Share personal anecdotes to demonstrate language usage
        
        Topics: Daily life, hobbies, travel, food, current events, work, family, or any casual conversation.
        
        Remember: {user_info}""",
        
        "Corporate English": f"""You are Engli, a 35-year-old business communication consultant with 10 years of experience in multinational companies.
        
        Role: Help professionals develop confident business English communication skills. Correct mistakes of the user if any.
        
        Communication Style:
        - Use natural business speech patterns with appropriate pauses (...)
        - Include professional filler words (well, actually, in fact)
        - Demonstrate authentic business dialogue flow
        - Balance formality with approachability
        - Use relevant industry terminology naturally
        - Do not generate action descriptors in your response
        - Make the responses short
        - Use roleplays and suggest tips.
        
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
        - Do not generate action descriptors in your response
        
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
        st.session_state.current_module = module_name

# Replace the generate_response function with this updated version
def generate_response(text, target_language):
    try:
        # Initialize chat history if needed
        if len(st.session_state.chat_history) == 0:
            st.session_state.chat_history.append({
                "role": "system", 
                "content": "You are Engli, an AI English trainer."
            })
        
        # Create a copy of chat history for API call
        api_messages = [
            msg for msg in st.session_state.chat_history 
            if msg["role"] in ["system", "user", "assistant"]
        ]
        
        # Add the new user message
        api_messages.append({"role": "user", "content": text})
        
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=api_messages,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False
        )
        
        assistant_response = completion.choices[0].message.content
        cleaned_response = clean_action_descriptors(assistant_response)
        
        # Update session state chat history
        st.session_state.chat_history.append({"role": "user", "content": text})
        st.session_state.chat_history.append({"role": "assistant", "content": cleaned_response})
        
        # Generate and store translation
        translated_response = translate_text(cleaned_response, target_language)
        st.session_state.chat_history.append({
            "role": "assistant_translated", 
            "content": translated_response
        })
        
        return cleaned_response, translated_response
        
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
# def show_learning_recommendations(speaking_level, mother_tongue):
#     if speaking_level.lower() == 'beginner':
#         st.info("👋 Welcome! Here's your recommended learning path:", icon="ℹ️")
        
#         st.markdown("### 1️⃣ Start with Translation")
#         st.markdown(f"Begin with the **{mother_tongue} to English** module to:")
#         st.markdown("- Build basic vocabulary")
#         st.markdown("- Learn essential sentence structures")
#         st.markdown("- Understand grammar fundamentals")
        
#         st.markdown("### 2️⃣ Practice Pronunciation")
#         st.markdown("Move to the **Pronunciation Checker** module to:")
#         st.markdown("- Master English sounds")
#         st.markdown("- Practice word stress and intonation")
#         st.markdown("- Build confidence in speaking")
        
#         st.markdown("### 3️⃣ Start Conversations")
#         st.markdown("Finally, try the **English Conversation Friend** module to:")
#         st.markdown("- Practice simple dialogues")
#         st.markdown("- Learn everyday phrases")
#         st.markdown("- Build speaking confidence")

#     elif speaking_level.lower() == 'intermediate':
#         st.info("🎯 Here's your recommended learning path:", icon="ℹ️")
        
#         st.markdown("### 1️⃣ English Conversation Friend")
#         st.markdown("Start with natural conversations to:")
#         st.markdown("- Improve fluency")
#         st.markdown("- Expand vocabulary")
#         st.markdown("- Practice various topics")
        
#         st.markdown("### 2️⃣ Corporate English")
#         st.markdown("Then move to professional communication:")
#         st.markdown("- Learn business vocabulary")
#         st.markdown("- Practice email writing")
#         st.markdown("- Develop presentation skills")

#     elif speaking_level.lower() == 'advanced':
#         st.info("🚀 Here's your recommended learning path:", icon="ℹ️")
        
#         st.markdown("### 1️⃣ Corporate English")
#         st.markdown("Focus on professional excellence:")
#         st.markdown("- Master business communication")
#         st.markdown("- Perfect presentation skills")
#         st.markdown("- Learn negotiation techniques")
        
#         st.markdown("### 2️⃣ Irish Slang")
#         st.markdown("Explore cultural nuances:")
#         st.markdown("- Learn local expressions")
#         st.markdown("- Understand Irish culture")
#         st.markdown("- Master informal communication")



# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_details" not in st.session_state:
    st.session_state.user_details = {}
if "translations" not in st.session_state:
    st.session_state.translations = {}

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
    # # Add this to your main app where appropriate
    # if "user_details" in st.session_state:
    #     speaking_level = st.session_state.user_details.get('speaking_level', '')
    #     mother_tongue = st.session_state.user_details.get('mother_tongue', '')
    #     show_learning_recommendations(speaking_level, mother_tongue)
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
    
# initialize_chat_history(selected_module)
initialize_chat_history_if_empty(selected_module)

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
        
        # Create a scrollable container with fixed height
        chat_container = st.container()
        
        # Add custom CSS for better chat display
        st.markdown("""
            <style>
            .chat-message {
                padding: 1rem;
                border-radius: 0.5rem;
                margin-bottom: 1rem;
                white-space: pre-wrap;
                word-wrap: break-word;
                color: #3A3B3C;
            }
            .user-message {
                background-color: #f0f2f6;
                margin-left: 20%;
                text-align: right;
            }
            .assistant-message {
                background-color: #e6f3e6;
                margin-right: 20%;
                text-align: left;
            }
            .translated-message {
                background-color: #f5f5f5;
                margin-right: 20%;
                text-align: left;
                font-style: italic;
            }
            </style>
        """, unsafe_allow_html=True)
    
        with chat_container:
            # Get non-system messages
            messages = [msg for msg in st.session_state.chat_history if msg["role"] != "system"]
            
            # Reverse the messages list to show latest messages first
            for message in reversed(messages):
                if message["role"] == "user":
                    st.markdown(
                        f"""<div class="chat-message user-message">
                            👤 You:<br>{message['content']}
                        </div>""", 
                        unsafe_allow_html=True
                    )
                elif message["role"] == "assistant":
                    st.markdown(
                        f"""<div class="chat-message assistant-message">
                            🤖 Engli:<br>{message['content']}
                        </div>""",
                        unsafe_allow_html=True
                    )
                elif message["role"] == "assistant_translated":
                    st.markdown(
                        f"""<div class="chat-message translated-message">
                            🤖 Engli (Translated):<br>{message['content']}
                        </div>""",
                        unsafe_allow_html=True
                    )
                    

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center;'>
    <div style='margin-bottom: 1rem; color: gray;'>
        Made with ❤️ for English Language Learners in Ireland
    </div>
    <div style='color: gray; font-size: 0.9rem; margin-bottom: 1rem;'>
        MSc in Artificial Intelligence Dissertation Project at Dublin Business School; Rinshad Choorappara [20021332]
    </div>
    <div style='font-size: 0.9rem; margin-bottom: 1rem; color: gray;'>
        Powered by
    </div>
    <div style='display: flex; justify-content: center; align-items: center; gap: 2rem; flex-wrap: wrap; margin-bottom: 1rem;'>
        <a href="https://groq.com" target="_blank" rel="noopener noreferrer" style="text-decoration: none;">
            <img
                src="https://groq.com/wp-content/uploads/2024/03/PBG-mark1-color.svg"
                alt="Groq"
                style="height: 30px; width: auto;"
            />
        </a>
        <a href="https://deepgram.com" target="_blank" rel="noopener noreferrer" style="text-decoration: none;">
            <img
                src="https://www.datocms-assets.com/96965/1683539914-logo.svg"
                alt="Deepgram"
                style="height: 30px; width: auto;"
            />
        </a>
        <a href="https://ai.meta.com/llama/" target="_blank" rel="noopener noreferrer" style="display: flex; align-items: center; text-decoration: none; color: #fff;">
            <span style="font-weight: bold; font-size: 1.2rem;">Meta Llama</span>
        </a>
        <a href="https://openai.com/research/whisper" target="_blank" rel="noopener noreferrer" style="display: flex; align-items: center; text-decoration: none; color: #fff;">
            <span style="font-weight: bold; font-size: 1.2rem;">Whisper</span>
        </a>
        <a href="https://cloud.google.com/text-to-speech" target="_blank" rel="noopener noreferrer" style="text-decoration: none;">
            <img
                src="https://www.gstatic.com/devrel-devsite/prod/v0e0f589edd85502a40d78d7d0825db8ea5ef3b99ab4070381ee86977c9168730/cloud/images/cloud-logo.svg"
                alt="Google Cloud"
                style="height: 30px; width: auto;"
            />
        </a>
        <a href="https://streamlit.io" target="_blank" rel="noopener noreferrer" style="text-decoration: none;">
            <img
                src="https://streamlit.io/images/brand/streamlit-mark-color.svg"
                alt="Streamlit"
                style="height: 30px; width: auto;"
            />
        </a>
    </div>
</div>
""", unsafe_allow_html=True)
