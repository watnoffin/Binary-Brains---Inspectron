import streamlit as st
import os
from PIL import Image
from datetime import datetime
from ibm_watsonx_ai.foundation_models import Model
import google.generativeai as genai
from googleapiclient.discovery import build
import requests
import json
from app import setup_page_config, show_sidebar

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


#function for tab 1
def analyze_image_with_gemini(image):
    """Analyze the image using Google's Gemini model"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = """As a professional Malaysian home inspector, provide a detailed assessment for the following issue.
        Consider Malaysian building standards, local repair costs, and availability of materials in Malaysia. 
        For each issue, provide:
        1. Type of issue
        2. Location in the house
        3. Severity (Critical, High, Medium, or Low)
        4. Step-by-step instructions on how to fix it
        5. Expert to consult if it's critical or high severity
        6. Estimated cost range (min and max)
        7. Breakdown of costs (materials, labor, permits if needed)
        8. Factors affecting the cost
        9. Timeline for repairs
        
        Please format your response exactly like this:
        Issue 1:
        Type: [issue type]
        Location: [location]
        Severity: [Critical/High/Medium/Low]
        Fix: [step-by-step instructions]
        Expert: [relevant Malaysian contractor type if Critical or High severity]
        Estimated Cost: [min and max cost range]
        Breakdown: [materials, labor, permits if needed]
        Factors: [factors affecting the cost]
        Timeline: [timeline for repairs]
        

        Your response MUST have line breaks between each field, for example, line break after Issue 1 and another line break after Type, and maintain this exact format.
        Use numbers for the Fix steps.
        If there are multiple issues, separate them with two newlines.
        """

        with st.spinner('Analyzing the image...'):
            response = model.generate_content([prompt, image])
            issues = parse_analysis_results(response.text)

            return issues

    except Exception as e:
        st.error(f"Error during AI analysis: {str(e)}")
        return [{
            "type": "Analysis Error",
            "location": "System",
            "severity": "High",
            "fix": f"Error: {str(e)}. Please try again or contact support",
        }]
        
def save_analysis(analysis_data):
    """Save analysis data to a JSON file"""
    try:
        existing_data = []
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, 'r') as f:
                existing_data = json.load(f)

        existing_data.append(analysis_data)

        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        with open(DATA_PATH, 'w') as f:
            json.dump(existing_data, f)
        return True
    except Exception as e:
        st.error(f"Error saving analysis: {str(e)}")
        return False

def parse_analysis_results(analysis_text):
    """Parses the analysis text and returns a list of issues."""
    issues = []
    current_issue = {}
    lines = analysis_text.split('\n')

    for line in lines:
        line = line.strip()
        if line.startswith('Issue'):
            if current_issue and all(
                    k in current_issue
                    for k in ['type', 'location', 'severity', 'fix','expert','estimated_cost']):
                issues.append(current_issue.copy())
            current_issue = {}
        elif ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()

            if 'type' in key:
                current_issue['type'] = value
            elif 'location' in key:
                current_issue['location'] = value
            elif 'severity' in key:
                current_issue['severity'] = value
            elif 'fix' in key:
                current_issue['fix'] = value
            elif 'expert' in key:
                current_issue['expert'] = value
            elif 'estimated cost' in key:
                current_issue['estimated_cost'] = value
            

    if current_issue and all(k in current_issue
                             for k in ['type', 'location', 'severity', 'fix', 'expert','estimated_cost']):
        issues.append(current_issue)

    if not issues:
        issues = [{
            "type": "General Observation",
            "location": "Visible areas",
            "severity": "Low",
            "fix": "Regular maintenance recommended",
        }]

    return issues

def display_analysis_results(issues):
    """Display the analysis results in a simplified format"""
    st.markdown("## 🏠 Home Inspection Results")

    # Quick Stats in a nice grid
    st.markdown("### Overview")
    total_issues = len(issues)
    stats_cols = st.columns(4)

    severity_counts = {
        'Critical': len([i for i in issues if i['severity'] == 'Critical']),
        'High': len([i for i in issues if i['severity'] == 'High']),
        'Medium': len([i for i in issues if i['severity'] == 'Medium']),
        'Low': len([i for i in issues if i['severity'] == 'Low'])
    }

    # Display stats with emojis and colors
    with stats_cols[0]:
        st.metric("🔴 Critical", severity_counts['Critical'])
    with stats_cols[1]:
        st.metric("🟠 High", severity_counts['High'])
    with stats_cols[2]:
        st.metric("🟡 Medium", severity_counts['Medium'])
    with stats_cols[3]:
        st.metric("🔵 Low", severity_counts['Low'])

    

    

    # Initialize session state for filter if not exists
    if 'severity_filter' not in st.session_state:
        st.session_state.severity_filter = "All Issues"

    # Display issues section header
    st.markdown("### Detailed Findings")

    # Create columns for filter buttons
    col1, col2, col3, col4, col5 = st.columns(5)

    # Create filter buttons instead of radio buttons

    # Filter issues based on selected severity
    filtered_issues = (issues if st.session_state.severity_filter
                       == "All Issues" else [
                           i for i in issues
                           if i['severity'] == st.session_state.severity_filter
                       ])

    # Display filtered issues
    if not filtered_issues:
        st.info(
            f"No {st.session_state.severity_filter.lower()} severity issues found."
        )
    else:
        for idx, issue in enumerate(filtered_issues):
            severity_colors = {
                "Critical": "#FF0000",
                "High": "#FFA500",
                "Medium": "#FFD700",
                "Low": "#0000FF"
            }

            severity_icons = {
                "Critical": "🚨",
                "High": "⚠️",
                "Medium": "⚡",
                "Low": "ℹ️"
            }

            st.markdown(f"""
                <div style='
                    background-color: {severity_colors[issue['severity']]}22;
                    border-left: 5px solid {severity_colors[issue['severity']]};
                    padding: 20px;
                    margin: 10px 0;
                    border-radius: 5px;
                '>
                    <h3>{severity_icons[issue['severity']]} {issue['type']}</h3>
                    <table style='margin-left: 20px;'>
                        <tr>
                            <td style='padding-right: 20px;'><strong>Location:</strong></td>
                            <td>{issue['location']}</td>
                        </tr>
                        <tr>
                            <td style='padding-right: 20px;'><strong>Severity:</strong></td>
                            <td>{issue['severity']}</td>
                        </tr>
                        <tr>
                                    <td style='padding-right: 20px;'><strong>Estimated Cost:</strong></td>
                                    <td>{issue.get('estimated_cost', 'Not specified')}</td>
                                </tr>
                    </table>
                    <div style='margin: 10px 0;'>
                        </div>
                    </div>
                    {f"<div style='margin-top: 10px; color: {severity_colors[issue['severity']]};'><strong>Expert to Consult:</strong> {issue['expert']}</div>" if issue.get('expert') else ""}
                </div>
            """,
                        unsafe_allow_html=True)

    # Add recommendations section if there are critical or high issues
    if severity_counts['Critical'] > 0 or severity_counts['High'] > 0:
        st.markdown("### 📋 Recommendations")
        st.warning("""
        Based on the inspection results, we recommend:
        1. Address critical issues immediately
        2. Schedule professional inspections for high-priority items
        3. Create a maintenance plan for medium and low priority issues
        """)
    else:
        st.markdown("### ✅ Summary")
        st.success("""
        Your property is in good condition! Remember to:
        1. Maintain regular inspection schedules
        2. Address any minor issues before they become major
        3. Keep records of all maintenance work
        """)
        
#function for tab 2
def configure_ibm_model():
    """Configure IBM Watson Studio model"""
    try:

        # Model parameters
        model_id = "flan-t5-xxl-11b"
        parameters = {
            "decoding_method": "sample",
            "max_new_tokens": 200,
            "min_new_tokens": 50,
            "random_seed": 111,
            "temperature": 0.8,
            "top_k": 50,
            "top_p": 1,
            "repetition_penalty": 2
        }

        # Get credentials from secrets
        credentials = {
            "url": st.secrets["ibm_credentials"]["IBM_URL"],
            "apikey": st.secrets["ibm_credentials"]["IBM_KEY"]
        }
        project_id = st.secrets["ibm_credentials"]["PROJECT_ID"]
        space_id = st.secrets["ibm_credentials"]["SPACE_ID"]

        # Initialize model
        model = Model(model_id=model_id,
                      params=parameters,
                      credentials=credentials,
                      project_id=project_id,
                      space_id=space_id)

        return model
    except Exception as e:
        st.error(f"Error configuring IBM model: {str(e)}")
        return None


def generate_professional_report(analysis_results):
    """Generate professional report using IBM Watson Studio"""
    try:
        # Get IBM model
        model = configure_ibm_model()
        if not model:
            return None

        # Prepare input for prompt
        issue_descriptions = []
        for issue in analysis_results['issues']:
            description = f"""
            Issue Type: {issue['type']}
            Location: {issue['location']}
            Severity: {issue['severity']}
            Recommended Fix: {issue['fix']}
            Expert to Consult: {issue['expert']}
            """
            issue_descriptions.append(description)

        combined_issues = "\n".join(issue_descriptions)
        recommendations = generate_recommendations(analysis_results)

        # Create prompt for the model
        prompt_input = f"""Generate a professional home inspection report email with the following details:

        Inspection Date: {datetime.now().strftime('%Y-%m-%d')}

        Findings:
        {combined_issues}

        Recommendations:
        {recommendations}

        Tone: Professional and informative
        Format: Email with subject line, greeting, findings section, recommendations section, and closing
        Include: Next steps and contact information

        Email"""

        # Generate report using IBM model
        generated_report = model.generate_text(prompt=prompt_input,
                                               guardrails=True)

        return generated_report

    except Exception as e:
        st.error(f"Error generating report: {str(e)}")
        return None


def generate_recommendations(analysis_results):
    """Generate prioritized recommendations based on severity"""
    high_priority = []
    medium_priority = []
    low_priority = []

    for issue in analysis_results['issues']:
        recommendation = f"- {issue['type']} ({issue['location']}): Contact {issue['expert']}"
        if issue['severity'] == 'High':
            high_priority.append(recommendation)
        elif issue['severity'] == 'Medium':
            medium_priority.append(recommendation)
        else:
            low_priority.append(recommendation)

    recommendations = []
    if high_priority:
        recommendations.append("Immediate Action Required:")
        recommendations.extend(high_priority)
    if medium_priority:
        recommendations.append("\nSchedule Soon:")
        recommendations.extend(medium_priority)
    if low_priority:
        recommendations.append("\nMonitor and Plan:")
        recommendations.extend(low_priority)

    return "\n".join(recommendations)


# Retrieve IBM API Key from Streamlit secrets
API_KEY = st.secrets["ibm_credentials"]["IBM_KEY"]


def get_ibm_bearer_token(API_KEY):
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": API_KEY
    }

    # Make the request to get the Bearer token
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status(
    )  # This will raise an error for non-200 responses
    return response.json()["access_token"]

# Fetch the Bearer token
bearer_token = get_ibm_bearer_token(API_KEY)

#functions for tab 3
# Initialize Gemini AI
genai.configure(api_key=os.getenv('GENAI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'analyses.json')

def load_analyses():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'r') as f:
            return json.load(f)
    return []

def get_expert_type(issue_type):
    """Determines the type of expert needed based on the issue"""
    issue_type = issue_type.lower()
    if any(word in issue_type for word in ['water', 'leak', 'plumbing']):
        return "Plumber"
    elif any(word in issue_type for word in ['electric', 'wiring']):
        return "Electrician"
    elif any(word in issue_type for word in ['structur', 'foundation', 'wall', 'ceiling']):
        return "Structural Engineer"
    elif any(word in issue_type for word in ['roof']):
        return "Roofing Contractor"
    elif any(word in issue_type for word in ['mold', 'pest']):
        return "Environmental Specialist"
    else:
        return "General Contractor"
#---------------------------------------------------
def display_report(analysis):
    """Displays the enhanced inspection report in the Streamlit interface"""
    st.markdown("""
        <style>
        .big-font {
            font-size:24px !important;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header with property details
    st.title("🏠 Home Inspection Report")
    st.markdown(f"### Property Details")

    # Report metadata in columns
    meta_col1, meta_col2, meta_col3 = st.columns(3)
    with meta_col1:
        st.info(f"📅 Inspection Date: {analysis.get('timestamp', 'N/A')}")
    with meta_col2:
        st.info(f"🔍 Report ID: {analysis.get('id', 'N/A')}")
    with meta_col3:
        st.info(f"📊 Total Issues: {len(analysis.get('issues', []))}")

    # Overview metrics with enhanced visualization
    st.markdown("## 📊 Issues Overview")
    col1, col2, col3, col4 = st.columns(4)

    def get_severity_color(severity):
        return {
            'Critical': 'red',
            'High': 'orange',
            'Medium': 'yellow',
            'Low': 'green'
        }.get(severity, 'blue')

    issues = analysis.get('issues', [])
    
    with col1:
        critical_count = len([i for i in issues if i.get('severity') == 'Critical'])
        st.metric("⚠️ Critical Issues", critical_count,
                  delta="Immediate Action!" if critical_count > 0 else "Clear",
                  delta_color="inverse" if critical_count > 0 else "normal")

    with col2:
        high_count = len([i for i in issues if i.get('severity') == 'High'])
        st.metric("🔴 High Priority", high_count,
                  delta="Urgent" if high_count > 0 else "Clear",
                  delta_color="inverse" if high_count > 0 else "normal")

    with col3:
        medium_count = len([i for i in issues if i.get('severity') == 'Medium'])
        st.metric("🟡 Medium Priority", medium_count,
                  delta="Attention Needed" if medium_count > 0 else "Clear")

    with col4:
        low_count = len([i for i in issues if i.get('severity') == 'Low'])
        st.metric("🟢 Low Priority", low_count,
                  delta="Monitor" if low_count > 0 else "Clear")
        
     # Sort issues by severity
    severity_order = {'Critical': 1, 'High': 2, 'Medium': 3, 'Low': 4}
    sorted_issues = sorted(analysis['issues'], key=lambda x: severity_order.get(x['severity'], 5))

    # Detailed findings with enhanced organization
    st.markdown("##  Detailed Findings")

    for severity in ['Critical', 'High', 'Medium', 'Low']:
        severity_issues = [i for i in sorted_issues if i['severity'] == severity]
        if severity_issues:
            st.subheader(f"{severity} Priority Findings")
            for i, issue in enumerate(severity_issues, 1):
                with st.expander(f"{i}. {issue['type']} - {issue['location']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**📍 Location:** {issue['location']}")
                        st.markdown(f"**🏷️ Issue Type:** {issue['type']}")
                        st.markdown(f"**⚠️ Severity:** {issue['severity']}")
                        
                    with col2:
                        st.markdown(f"**🔧 Recommended Action:** {issue['fix']}")
                        st.markdown(f"**👷 Recommended Expert:** {get_expert_type(issue['type'])}")
                        if 'timeline' in issue:
                            st.markdown(f"**⏱️ Timeline:** {issue['timeline']}")

    # Add a summary footer
    st.markdown("---")
    st.markdown("### 📝 Report Summary")
    st.markdown(f"""
    - Total issues identified: {len(analysis['issues'])}
    - Critical issues requiring immediate attention: {critical_count}
    - Generated on: {analysis['timestamp']}
    """)
#--------------------------------------------------
class InspectionReport:
    def __init__(self, analysis):
        self.analysis = analysis

    def generate_report(self):
        report = []
        report.append("Home Inspection Assessment\n")
        report.append("=" * 25 + "\n\n")

        # Report header
        report.append(f"Inspection Details\n")
        report.append(f"Inspection Date: {self.analysis.get('timestamp', 'N/A')}\n")
        report.append(f"Report ID: {self.analysis.get('id', 'N/A')}\n\n")

        # Executive summary
        report.append("Summary of Findings\n")
        report.append("-" * 17 + "\n")

        issues = self.analysis.get('issues', [])
        critical_count = len([i for i in issues if i.get('severity') == 'Critical'])
        high_count = len([i for i in issues if i.get('severity') == 'High'])
        medium_count = len([i for i in issues if i.get('severity') == 'Medium'])
        low_count = len([i for i in issues if i.get('severity') == 'Low'])

        report.append(f"Critical Issues: {critical_count}\n")
        report.append(f"High Priority Issues: {high_count}\n")
        report.append(f"Medium Priority Issues: {medium_count}\n")
        report.append(f"Low Priority Issues: {low_count}\n\n")

        # Detailed findings
        report.append("Detailed Findings\n")
        report.append("-" * 15 + "\n")

        severity_order = {'Critical': 1, 'High': 2, 'Medium': 3, 'Low': 4}
        sorted_issues = sorted(issues, 
                             key=lambda x: severity_order.get(x.get('severity', 'Low'), 5))

        for severity in ['Critical', 'High', 'Medium', 'Low']:
            severity_issues = [i for i in sorted_issues if i.get('severity') == severity]
            if severity_issues:
                report.append(f"\n{severity} Priority Findings:\n")
                for i, issue in enumerate(severity_issues, 1):
                    report.append(f"{i}. {issue.get('type', 'Unknown Issue')} - {issue.get('location', 'Unknown Location')}\n")
                    report.append(f"   Severity: {issue.get('severity', 'Unknown')}\n")
                    report.append(f"   Recommended Action: {issue.get('fix', 'No recommendations available')}\n")
                    report.append(f"   Recommended Expert: {get_expert_type(issue.get('type', ''))}\n")
                    report.append("\n")

        return "".join(report)

#main tab function
def show_page():
    
    # Setup page configuration
    setup_page_config()

    # Show sidebar
    show_sidebar()
    
    st.title("Inspectron - your AI inspector generator")
    tab1, tab2, tab3 = st.tabs(
        ["1. " "Inspector", "2. " "Report Generator", "3. " "Email Generator"])

    #upload page
    with tab1:
        st.markdown(
        "<h1 style='text-align: left; color: white; font-size: 70px;'>Home Inspection</h1>",
        unsafe_allow_html=True)
        st.write(
            "Upload or capture a photo of your home to get an AI-powered inspection report."
        )

        # Image input options
        input_method = st.radio("Choose your image input method:",
                                ("Upload Image", "Use Camera"))

        image = None
        filename = None

        if input_method == "Use Camera":
            camera_image = st.camera_input("Take a picture")
            if camera_image:
                try:
                    image = Image.open(camera_image)
                    filename = f"camera_capture_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                    st.image(image,
                            caption="Captured Image",
                            use_container_width=True)
                except Exception as e:
                    st.error(f"Error processing camera image: {str(e)}")

        else:  # Upload Image
            uploaded_file = st.file_uploader("Choose an image...",
                                            type=["jpg", "jpeg", "png"])
            if uploaded_file:
                try:
                    image = Image.open(uploaded_file)
                    filename = uploaded_file.name
                    st.image(image,
                            caption="Uploaded Image",
                            use_container_width=True)
                except Exception as e:
                    st.error(f"Error processing uploaded image: {str(e)}")

        # Analyze image button and logic
        if image and st.button("Analyze Image with AI"):
            # Debug information
            st.write(f"Image size: {image.size}")
            st.write(f"Image mode: {image.mode}")

            issues = analyze_image_with_gemini(image)

            if issues:
                # Create analysis data
                analysis_data = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "filename": filename,
                    "issues": issues
                }

                # Save analysis data
                save_successful = save_analysis(analysis_data)

                if save_successful:
                    st.session_state.last_analysis = analysis_data
                    display_analysis_results(issues)

                    st.success(
                        "✅ Analysis complete! To view your full detailed report, click on 'Reports' in the sidebar navigation."
                    )

                    # Optional: Add a visual cue to direct attention to the sidebar
                    st.sidebar.markdown("### 👆 View Full Report")
                    st.sidebar.info(
                        "Click on 'Reports' to see your detailed inspection report!"
                    )
                else:
                    st.warning(
                        "Analysis completed but couldn't be saved. Please try again."
                    )
            else:
                st.error(
                    "No issues were identified. This might be due to an error in the analysis."
                )

    #report page
    with tab2:
        st.title("Inspection Reports")

        analyses = load_analyses()

        if not analyses:
            st.warning("No inspection reports found. Please perform an inspection first.")
            if st.button("Go to Inspection"):
                st.session_state.navigation_target = 'Inspection'
                st.rerun()
            return

        if st.session_state.get('last_analysis'):
            current_analysis = st.session_state.last_analysis
            display_report(current_analysis)

            # Initialize open_expanders in session state if it doesn't exist
            if 'open_expanders' not in st.session_state:
                st.session_state.open_expanders = set()

            # Original text report download
            inspection_report = InspectionReport(current_analysis)
            exportable_report = inspection_report.generate_report()
            if exportable_report:
                st.download_button(
                    label="Download Report as Text",
                    data=exportable_report,
                    file_name=f"home_inspection_report_{current_analysis['id']}.txt",
                    mime="text/plain"
                )

            st.session_state.last_analysis = None

        if len(analyses) > 1:
            st.markdown("## Previous Reports")
            for analysis in reversed(analyses[:-1]):
                timestamp = analysis['timestamp']
                if st.button(f"View Report from {timestamp}"):
                    display_report(analysis)
                    # Provide download options for previous reports
                    inspection_report = InspectionReport(analysis)
                    exportable_report = inspection_report.generate_report()
                    if exportable_report:
                        st.download_button(
                            label=f"Download Report from {timestamp}",
                            data=exportable_report,
                            file_name=f"home_inspection_report_{analysis['id']}.txt",
                            mime="text/plain"
                        )

    #email tab
    with tab3:
        st.title("Contact Professionals Directly!")
        st.subheader(
            "Email to a professional and wait for them in front of your doorstep."
        )
        
        # Load analyses like in tab2
        analyses = load_analyses()
        current_analysis = analyses[-1] if analyses else None
        
        if not current_analysis:
            st.warning("No inspection reports found. Please perform an inspection first.")
            return

        # Define CSS for the email container
        email_css = """
            <style>
            .email-container {
                width: 100%;
                max-width: 800px;
                margin: 20px auto;
                padding: 20px;
                border: 2px solid #ddd;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
            .email-container h3 {
                text-align: center;
            }
            .email-container input, .email-container textarea {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            .email-container button {
                width: 100%;
                padding: 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
            }
            .email-container button:hover {
                background-color: #45a049;
            }
            </style>
        """

        st.markdown(email_css, unsafe_allow_html=True)

        # Container for email generation
        with st.form(key='email_form', clear_on_submit=True):
            st.markdown('<div class="email-container">', unsafe_allow_html=True)

            # Get the first issue from current analysis
            issues = current_analysis.get('issues', [])
            first_issue = issues[0] if issues else {}

            # Email subject based on the analysis result
            subject = f"Request for {first_issue.get('type', 'Home Inspection Issue')}"
            email_subject = st.text_input("Subject", value=subject)

            # Email body generation using analysis results
            if issues:
                issue_type = first_issue.get("type", "Unknown Issue")
                location = first_issue.get("location", "Unknown Location")
                severity = first_issue.get("severity", "Unknown Severity")
                steps_to_fix = first_issue.get("fix", "No steps available")

                email_body = f"""
                Dear Professional,

                I hope this email finds you well. My name is [user_name], and I recently had a home inspection conducted at my property using Inspectron that identified some issues that require professional attention.

                Inspection Findings:
                - Issue type: {issue_type}
                - Location: {location}
                - Severity: {severity}
                - Steps to Fix:
                  {steps_to_fix}

                I would greatly appreciate if you could:
                1. Review these issues and provide an estimate for the necessary repairs.
                2. Suggest a convenient time for an on-site assessment.
                3. Indicate your earliest availability for addressing these concerns.

                Please let me know if you need any additional information or specific details about the issues identified.

                Thank you for your time and consideration. I look forward to your response.

                Best regards,
                [user_name]
                """

            else:
                email_body = "Dear Professional,\n\nPlease find the inspection details below."

            email_body_input = st.text_area("Email Body",
                                            value=email_body,
                                            height=250)

            # Button to simulate sending the email
            send_button = st.form_submit_button("Send Email")

            if send_button:
                # You would replace the mock user details with actual values
                user_name = "John Doe"  # Replace this with dynamic user name

                email_body = email_body_input.replace("[user_name]", user_name)

                try:
                    # Example: Send via email API or use SMTP here
                    # You can replace this code with actual API call logic for sending email
                    st.success("Email draft generated successfully!")
                    st.info("Note: This is a demo version. In the full version, this would send the email to the relevant professional.")

                    # Display the final email for demo purposes
                    st.markdown("### Preview of Generated Email")
                    st.markdown(f"**Subject:** {email_subject}")
                    st.markdown("**Body:**")
                    st.text(email_body)

                except Exception as e:
                    st.error(f"Error: {str(e)}")

            st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    show_page()  #show_page()
