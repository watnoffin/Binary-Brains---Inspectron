import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
from googleapiclient.discovery import build

# Configure Google APIs
#GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
#YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
#genai.configure(api_key=GOOGLE_API_KEY)
my_secret = os.environ['GENAI_API_KEY']
my_secret = os.environ['YOUTUBE_API_KEY']
genai.configure(api_key=my_secret)

# Constants
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'analyses.json')
#GET https://www.googleapis.com/youtube/v3/search

# youtube
def get_youtube_videos(query):
    """Get relevant YouTube videos based on the issue"""
    global YOUTUBE_API_KEY
    youtube = build('youtube', 'v3', developerKey='YOUTUBE_API_KEY')

    try:
        search_response = youtube.search().list(
            q=f"how to fix {query} home repair",
            part='snippet',
            maxResults=3,
            type='video').execute()

        videos = []
        for item in search_response['items']:
            video = {
                'title': item['snippet']['title'],
                'videoId': item['id']['videoId'],
                'thumbnail': item['snippet']['thumbnails']['default']['url']
            }
            videos.append(video)
        return videos
    except Exception as e:
        st.error(f"Error fetching YouTube videos: {str(e)}")
        return []


def analyze_image_with_gemini(image):
    """Analyze the image using Google's Gemini model"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = """You are an expert home inspector AI. Analyze the provided image and 
        identify potential issues or maintenance needs. 
        For each issue, provide:
        1. Type of issue
        2. Location in the house
        3. Severity (Critical, High, Medium, or Low)
        4. Step by step on how to fix it
        5. Expert to consult if it's critical or high severity

        please format your response exactly like this:
        Issue 1:
        Type: [issue type]
        Location: [location]
        Severity: [Critical/High/Medium/Low]
        Fix: [step by step instructions]
        Expert: [expert type if Critical or High severity]

        Your response MUST have line breaks between each fields, for example, line break after issue 1 and another line break after issue type, and maintain this exact format.
        Use numbers for the Fix steps.
        If there are multiple issues, separate them with two newlines."""

        with st.spinner('AI is analyzing the image...'):
            response = model.generate_content([prompt, image])

            if not response or not response.text:
                st.error("No analysis results received")
                return None

            # Get the raw analysis and format it
            raw_analysis = response.text

            # Format the raw analysis if it's all in one line
            if '\n' not in raw_analysis:
                formatted_analysis = raw_analysis
                # Add newlines after each key identifier
                for key in [
                        'Type:', 'Location:', 'Severity:', 'Fix:', 'Expert:'
                ]:
                    formatted_analysis = formatted_analysis.replace(
                        f"{key}", f"\n{key}")
                # Remove the leading newline if it exists
                formatted_analysis = formatted_analysis.lstrip('\n')
            else:
                formatted_analysis = raw_analysis

            # Display the formatted raw analysis
            # st.write("Raw Analysis:")
            # st.write(formatted_analysis)

            # Process the analysis into a structured format
            current_issue = {}
            fix_steps = []
            lines = formatted_analysis.split('\n')

            # Process each line
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    continue

                # Handle each field
                if line.startswith('Type:'):
                    current_issue['type'] = line.replace('Type:', '').strip()
                elif line.startswith('Location:'):
                    current_issue['location'] = line.replace('Location:',
                                                             '').strip()
                elif line.startswith('Severity:'):
                    current_issue['severity'] = line.replace('Severity:',
                                                             '').strip()
                elif line.startswith('Fix:'):
                    # Collect fix steps until we reach 'Expert:'
                    i += 1
                    while i < len(lines) and not lines[i].strip().startswith(
                            'Expert:'):
                        step = lines[i].strip()
                        if step:
                            fix_steps.append(step)
                        i += 1
                    current_issue['fix'] = fix_steps
                    continue
                elif line.startswith('Expert:'):
                    current_issue['expert'] = line.replace('Expert:',
                                                           '').strip()
                i += 1

            # Fetch YouTube videos
            if current_issue:
                issue_query = f"{current_issue.get('type', '')} {current_issue.get('location', '')}"
                videos = get_youtube_videos(issue_query)
                current_issue['youtube_videos'] = videos

            # Display the structured results
            if current_issue:
                with st.expander(
                        f"{current_issue.get('type', 'Issue')} - {current_issue.get('location', 'Unknown Location')}"
                ):
                    cols = st.columns(2)
                    with cols[0]:
                        st.write(
                            f"**Severity:** {current_issue.get('severity', 'N/A')}"
                        )
                        st.write(
                            f"**Expert to Consult:** {current_issue.get('expert', 'N/A')}"
                        )
                        st.write("**Recommended Fix:**")
                        for step in current_issue.get('fix', []):
                            st.write(f"- {step}")

                    with cols[1]:
                        st.subheader("Related Video Tutorials")
                        for video in current_issue.get('youtube_videos', []):
                            try:
                                st.video(
                                    f"https://www.youtube.com/watch?v={video['videoId']}"
                                )
                            except Exception as e:
                                st.error(f"Error displaying video: {str(e)}")

            return [current_issue] if current_issue else None

    except Exception as e:
        st.error(f"Error during AI analysis: {str(e)}")
        # st.error("Full error details:")
        # st.write(str(st.exception()))
    return None


def save_analysis(analysis_data):
    """Save analysis data to session state for report generation"""
    st.session_state.analysis_results = analysis_data


def show_upload_page():
    st.title("Home Inspection Upload")

    # Image input options
    input_method = st.radio("Choose your image input method:",
                            ("Upload Image", "Use Camera"))

    image = None
    if input_method == "Use Camera":
        camera_image = st.camera_input("Take a picture")
        if camera_image:
            image = Image.open(camera_image)

    else:  # Upload Image
        uploaded_file = st.file_uploader("Choose an image...",
                                         type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image = Image.open(uploaded_file)

    if image:
        st.image(image,
                 caption="Captured/Uploaded Image",
                 use_container_width=True)

    if st.button("Start Analysis"):
        analysis_results = analyze_image_with_gemini(image)

        # Add button to generate report
        # if st.button("Generate Professional Report"):
        #        st.session_state.analysis_data = analysis_results
        #        st.switch_page("report")

        st.button("Go to Report", on_click=lambda: st.switch_page("pages/report.py"))
              

if __name__ == "__main__":
    show_upload_page()
