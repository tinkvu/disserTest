import streamlit as st

st.set_page_config(layout="wide", page_title="Engli - English Trainer", page_icon="📖")

# Title and Introduction
st.title("Your AI English Learning Companion")
st.markdown("### Transform your English learning journey with personalized AI assistance")

# Brief introduction
st.markdown("""
Our AI-powered platform offers multiple specialized modules to help you master English:
""")

st.markdown("""
### Think your English is flawless? 🧐  
If you believe you can understand any Irish accent, put your skills to the test! Watch the video below and see if you can follow what this person is saying.  
""")

# Embed the YouTube video using iframe
st.components.v1.html(
    """
    <div style="display: flex; justify-content: center; margin-top: 20px;">
        <iframe width="560" height="315" 
        src="https://www.youtube.com/embed/nJ7QB3om-QY?si=MnoNtWFO8J7sJ2NU&amp;start=27" 
        title="YouTube video player" frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
        referrerpolicy="strict-origin-when-cross-origin" allowfullscreen>
        </iframe>
    </div>
    """,
    height=315,
)

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

# Get Started Section
st.markdown("### 🚀 Ready to Start?")
st.markdown("Complete your profile to get your personalized learning path")

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
            
            # Show personalized recommendations based on level
            st.markdown("### 🎯 Your Personalized Learning Path")
            
            if speaking_level == "Beginner":
                st.info(f"""
                ### Welcome to Your English Journey! 🌟
                Based on your profile, here's your recommended learning path:
                
                1. **Start with {mother_tongue} to English Translation Module**
                   - Begin with familiar concepts from your native language
                   - Build basic vocabulary and phrases
                   - Understand English sentence structure
                
                2. **Move to Pronunciation Checker**
                   - Master fundamental English sounds
                   - Practice common words and phrases
                   - Get real-time pronunciation feedback
                
                3. **Progress to English Conversation Friend**
                   - Start with simple daily conversations
                   - Build confidence gradually
                   - Learn everyday expressions
                
                This path will help you build a strong foundation in English step by step.
                """)
            
            elif speaking_level == "Intermediate":
                st.info("""
                ### Ready to Level Up! 🚀
                Here's your recommended path to advance your English skills:
                
                1. **Start with English Conversation Friend**
                   - Engage in natural, flowing conversations
                   - Expand your vocabulary
                   - Practice idioms and expressions
                   - Get contextual feedback
                
                2. **Proceed to Corporate English**
                   - Learn professional communication
                   - Master business terminology
                   - Practice email writing
                   - Develop presentation skills
                
                This combination will help you transition from everyday English to professional fluency.
                """)
            
            else:  # Advanced
                st.info("""
                ### Perfect Your English! ⭐
                Here's your path to mastery:
                
                1. **Focus on Corporate English**
                   - Handle complex business scenarios
                   - Perfect professional writing
                   - Lead meetings confidently
                   - Master negotiation skills
                
                2. **Explore Irish Slang**
                   - Understanding local expressions
                   - Master regional accents
                   - Gain cultural insights
                   - Navigate casual conversations fluently
                
                This path will help you achieve near-native fluency and cultural understanding.
                """)
            
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
