#Landing Page
import streamlit as st

st.set_page_config(layout="wide", page_title="Engli - English Trainer", page_icon="📖")

# Title and Introduction
st.title("Your AI English Learning Companion")
st.markdown("### Transform your English learning journey with personalized AI assistance")

# Brief introduction
st.markdown("""
Our AI-powered platform offers multiple specialized modules to help you master English:
""")

# Module descriptions using columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 🗣️ English Conversation Friend
    Practice everyday English with a friendly AI companion that:
    - Engages in natural conversations
    - Helps improve your speaking skills
    - Provides gentle corrections
    - Adapts to your level
    
    #### 💼 Corporate English
    Master professional English with focused practice on:
    - Business communication
    - Professional vocabulary
    - Meeting participation
    - Email writing
    """)
    # Key Features
    st.markdown("### ✨ Key Features")
    st.markdown("""
    - 🎤 **Voice Interaction**: Practice speaking with real-time feedback
    - 🔄 **Instant Translations**: Get translations in your native language
    - 🗣️ **Pronunciation Help**: Learn correct pronunciation
    - 📝 **Personalized Learning**: Adapts to your level and needs
    """)

with col2:
    st.markdown("""
    #### ☘️ Irish Slang
    Dive into Irish English with:
    - Authentic Irish expressions
    - Cultural context
    - Local pronunciation
    - Real-life usage examples
    
    #### 🎯 Translation Assistant
    Get instant translations with:
    - Native language to English conversion
    - Pronunciation guidance
    - Context-aware translations
    - Natural English equivalents
    """)

    # Languages that Work Best
    st.markdown("### 🌐 Languages that Work Best")
    st.markdown("""
    **European**:
    English, Spanish, French, German, Italian, Portuguese (European and Brazilian), Dutch, Russian, Polish, Ukrainian  
    **Asian**:
    Mandarin Chinese, Japanese, Korean, Hindi, Bengali, Turkish, Vietnamese, Thai  
    **Middle Eastern & African**:
    Arabic, Swahili  
    **South American**:
    Spanish, Portuguese (Brazilian)  
    These languages are optimized for accuracy and natural communication.
    """)
# Get Started Section
st.markdown("### 🚀 Ready to Start?")
st.markdown("Tell us about yourself to personalize your learning experience")

# User Details Form
with st.form("user_details_form"):
    st.write("### Your Profile")
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Enter your name:", value="Enrique")
        age = st.number_input("Your Age:", min_value=1, max_value=120, value=25)
        profession = st.text_input("What is your profession? 💼", value="Software Engineer")
    
    with col2:
        nationality = st.text_input("Your Nationality:", value="Mexico")
        mother_tongue = st.text_input("Your Mother Tongue:", value="Spanish")
        speaking_level = st.selectbox("English Speaking Level:", ["Beginner", "Intermediate", "Advanced"])

    # Start button
    start_button = st.form_submit_button("Start Learning! 🚀", type="primary", use_container_width=True)
    
    if start_button:
        if not all([name, profession, nationality, mother_tongue]):
            st.error("Please fill in all the fields to continue.")
        else:
            # Save user details to session state
            st.session_state.user_details = {
                "name": name,
                "age": age,
                "profession": profession,
                "nationality": nationality,
                "mother_tongue": mother_tongue,
                "speaking_level": speaking_level
            }
            # Redirect to main app
            st.success("Profile saved! Redirecting to the main application...")
            st.switch_page("pages/appfunctions.py")

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
            <img
                src="https://static.xx.fbcdn.net/rsrc.php/y9/r/tL_v571NdZ0.svg"
                alt="Meta Llama"
                style="height: 30px; width: auto;"
            />
            
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
    </div>
</div>
""", unsafe_allow_html=True)
