import streamlit as st
from datetime import datetime
from ibm_watsonx_ai.foundation_models import Model
# from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


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


def show_report_page():
    st.title("Professional Inspection Report")

    if 'analysis_results' not in st.session_state:
        st.warning("Please complete an inspection first.")
        if st.button("Go to Inspection"):
            st.switch_page("pages/upload.py")
        return

    analysis_results = st.session_state.analysis_results

    # Generate report
    with st.spinner("Generating professional report..."):
        report = generate_professional_report(analysis_results)

    if report:
        st.subheader("Generated Report")
        st.text_area("Professional Report", report, height=400)

        # Download options
        st.download_button(
            label="Download Report",
            data=report,
            file_name=
            f"home_inspection_report_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain")

        # Clear results option
        if st.button("Start New Inspection"):
            del st.session_state.analysis_results
            st.switch_page("pages/upload.py")


if __name__ == "__main__":
    show_report_page()
