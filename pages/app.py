# pages/1_🏠_Landing.py
import streamlit as st

st.set_page_config(layout="wide", page_title="Engli - English Trainer", page_icon="📖")

# Title and Introduction
st.title("🌟 Welcome to Engli - Your AI English Learning Companion")
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

# Key Features
st.markdown("### ✨ Key Features")
st.markdown("""
- 🎤 **Voice Interaction**: Practice speaking with real-time feedback
- 🔄 **Instant Translations**: Get translations in your native language
- 🗣️ **Pronunciation Help**: Learn correct pronunciation
- 📝 **Personalized Learning**: Adapts to your level and needs
""")

# Get Started Section
st.markdown("### 🚀 Ready to Start?")
st.markdown("Tell us about yourself to personalize your learning experience")

# User Details Form
with st.form("user_details_form"):
    st.write("### Your Profile")
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Your Name:", placeholder="Enter your name")
        age = st.number_input("Your Age:", min_value=1, max_value=120, value=25)
        profession = st.text_input("Your Profession:", placeholder="Enter your profession")
    
    with col2:
        nationality = st.text_input("Your Nationality:", placeholder="Enter your nationality")
        mother_tongue = st.text_input("Your Mother Tongue:", placeholder="Enter your native language")
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
<div style='text-align: center; color: gray;'>
    Made with ❤️ for English Language Learners in Ireland
</div>
""", unsafe_allow_html=True)
