import streamlit as st
import pandas as pd
import google.generativeai as genai
import time

# Configure the API key
API_KEY = st.secrets['api_keys']['genai']
genai.configure(api_key=API_KEY)

# Initialize an empty DataFrame to store the results
columns = ["Speech Length", "Confidence", "Tone and Clarity", "Skills and Experience", "Emotion", "Score", "Explanation"]
results_df = pd.DataFrame(columns=columns)

# Streamlit app
st.set_page_config(page_title="Interview Video Analysis", layout="wide", initial_sidebar_state="expanded")

# Add a sidebar for instructions and app description
with st.sidebar:
    st.title("Welcome to Interview Analyzer")
    st.write("""
        This app analyzes video interviews by evaluating the candidate's performance based on:
        - Speech length
        - Confidence
        - Tone and clarity
        - Skills and experience
        - Emotion
        - Overall Score
        
        Upload your video and let AI do the analysis for you!
    """)
    st.markdown("### Instructions:")
    st.markdown("1. Upload your interview video (mp4, mov, avi).\n2. Click 'Analyze Video'.\n3. Review the analysis report.")
    st.image("https://via.placeholder.com/250x150.png", caption="Interview AI", use_column_width=True)

st.title("🎥 Interview Video Analysis")

# Upload video file
uploaded_file = st.file_uploader("📁 Upload your interview video", type=["mp4", "mov", "avi"])

# Process video file
if uploaded_file is not None:
    # Save the uploaded video to a temporary file
    with open("temp_video.mp4", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Display the video
    st.video("temp_video.mp4")
    
    # Add a button to start the analysis
    analyze_btn = st.button("⚙️ Analyze Video")

    if analyze_btn:
        st.info("Uploading video for analysis...")

        video_file = genai.upload_file(path="temp_video.mp4", display_name="Interview Video")

        while video_file.state.name == "PROCESSING":
            st.info('Processing your video... Please wait.')
            time.sleep(5)
            video_file = genai.get_file(video_file.name)

        if video_file.state.name == "FAILED":
            st.error("❌ Video processing failed. Please try again.")
        else:
            st.success("✅ Video processed successfully!")
            video_file = genai.get_file(name=video_file.name)

            # Prompt for interview feedback
            prompt = '''
            You are inside a streamlit app, add spaces, highlight subheaders where ever necessary.
            Analyze the given video and provide the following information, highlight wherever necessary:
            1. Is the speech too long or too short?
            2. How confident does the speaker appear?
            3. What is the overall tone and clarity of the speech?
            4. Extract information about the candidate like, skills, experience, etc.
            5. What is the overall emotion of the candidate?
            7. Give a score out of 10 for the candidate.
            8. No need to give recommendations
            here is an example of a response:
            'This is a very short interview, barely lasting 50 seconds. It feels more like a candidate reading out their resume rather than engaging in a conversation.

            Here's a breakdown:

            Speech Length: Too short. It doesn't provide enough information to form a well-rounded impression.
            Confidence: The speaker appears moderately confident. He speaks clearly, but there's a lack of passion or excitement in his voice. He seems a bit nervous.
            Tone and Clarity: The tone is neutral and factual. The speech is clear and easy to understand, although there are a couple of instances of hesitation (e.g., "uh" before "Kota") which suggests a lack of preparation or potential nervousness.
            Skills and Experience:
            Education: Appex University, Jaipur (no specific degree mentioned)
            Certifications: VCA (no context provided)
            Courses: Android Developer (from Placements Adda - no further detail)
            Work Experience: ThinkDeva (XML work, APPS, Camera-based work - no specific job title mentioned)
            Seeking: Android Developer Intern (May to August)
            Overall Emotion: Neutral. There's a lack of positive or enthusiastic energy.
            Score out of 10: 5/10. The candidate provides basic information but lacks depth and engagement.'
            
            '''
            
            # Generate content using the Gemini model
            st.info("🔍 Generating feedback... Please wait a moment.")
            response = genai.GenerativeModel("gemini-1.5-flash").generate_content([prompt, video_file])

            # Display the feedback
            st.subheader("📊 Interview Feedback")
            st.write(response.text)
            
            
else:
    st.info("📤 Please upload a video to start the analysis.")
