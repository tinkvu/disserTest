import streamlit as st

st.set_page_config(layout="wide", page_title="Engli - English Trainer", page_icon="📖")

# Title and Introduction
st.title("Your AI English Learning Companion")
st.markdown("### Transform your English learning journey with personalized AI assistance")

# Initial Assessment Form
with st.form("initial_assessment"):
    col1, col2 = st.columns(2)
    
    with col1:
        mother_tongue = st.text_input("Your Mother Tongue:", value="Spanish")
    with col2:
        speaking_level = st.selectbox("English Speaking Level:", ["Beginner", "Intermediate", "Advanced"])
    
    submit_assessment = st.form_submit_button("Show Recommended Learning Path", use_container_width=True)

if submit_assessment or 'speaking_level' in st.session_state:
    level = speaking_level if submit_assessment else st.session_state.get('speaking_level')
    native_lang = mother_tongue if submit_assessment else st.session_state.get('mother_tongue')
    
    # Display recommended path based on level
    st.markdown("### 🎯 Your Recommended Learning Path")
    
    if level == "Beginner":
        st.info(f"""
        ### Perfect Starting Point for Beginners
        We recommend following this sequence to build a strong foundation:
        
        1. **{native_lang} to English Translation Module**
           - Start with familiar concepts
           - Learn basic vocabulary and phrases
           - Get comfortable with English structure
        
        2. **Pronunciation Checker**
           - Master basic English sounds
           - Practice common words
           - Get instant feedback
        
        3. **English Conversation Friend**
           - Begin simple conversations
           - Learn everyday phrases
           - Build confidence gradually
        """)
    
    elif level == "Intermediate":
        st.info("""
        ### Enhance Your Skills
        Focus on these modules to advance your English:
        
        1. **English Conversation Friend**
           - Practice natural conversations
           - Expand vocabulary
           - Learn idioms and expressions
        
        2. **Corporate English**
           - Develop professional communication
           - Learn business terminology
           - Master email writing
        """)
    
    else:  # Advanced
        st.info("""
        ### Perfect Your English
        Take your English to the next level:
        
        1. **Corporate English**
           - Master complex business scenarios
           - Perfect professional writing
           - Lead meetings confidently
        
        2. **Irish Slang**
           - Understand local expressions
           - Master regional accents
           - Gain cultural insights
        """)

# Main content continues with module descriptions
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

# Get Started Section
st.markdown("### 🚀 Ready to Start?")
st.markdown("Complete your profile to begin your personalized learning journey")

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
        # Pre-fill with previously selected values
        if submit_assessment:
            st.session_state['mother_tongue'] = mother_tongue
            st.session_state['speaking_level'] = speaking_level
        mother_tongue_profile = st.text_input("Your Mother Tongue:", value=st.session_state.get('mother_tongue', ''))
        speaking_level_profile = st.selectbox(
            "English Speaking Level:",
            ["Beginner", "Intermediate", "Advanced"],
            index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.get('speaking_level', 'Beginner'))
        )

    # Start button
    start_button = st.form_submit_button("Start Learning! 🚀", type="primary", use_container_width=True)
    
    if start_button:
        if not all([name, profession, nationality, mother_tongue_profile]):
            st.error("Please fill in all the fields to continue.")
        else:
            # Save user details to session state
            st.session_state.user_details = {
                "name": name,
                "age": age,
                "profession": profession,
                "nationality": nationality,
                "mother_tongue": mother_tongue_profile,
                "speaking_level": speaking_level_profile
            }
            # Redirect to main app
            st.success("Profile saved! Redirecting to the main application...")
            st.switch_page("pages/appfunctions.py")

# Footer (same as original)
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
