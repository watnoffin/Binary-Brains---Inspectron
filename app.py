import streamlit as st
import os


def init_session_state():
    """Initialize session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None


def setup_page_config():
    """Configure page settings"""
    st.set_page_config(page_title="Inspectron",
                       page_icon="🏠",
                       layout="wide",
                       initial_sidebar_state="expanded")

    # Inject custom CSS
    st.markdown("""
        <style>
        .stApp {
            background: black;
            background-size: cover;
            background-position: center;
        }
        .main-header {
            color: #dcccec;
            font-size: 80px;
            font-family: 'Source Sans Pro', sans-serif;
            text-align: left;
        }
        .sub-header {
            color: white;
            font-size: 18px;
            font-family: Arial, sans-serif;
            text-align: center;
        }
        .feature-container {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .nav-button {
            background-color: #4A4A4A;
            color: white;
            border-radius: 5px;
            padding: 10px;
            margin: 5px;
            text-align: center;
        }
        </style>
        """,
                unsafe_allow_html=True)


def show_hero_section():
    """Display hero section with CTA"""
    side1, side2 = st.columns(2)

    with side1:
        st.markdown(
            "<h1 class='main-header'>Inspectron your AI inspector generator</h1>",
            unsafe_allow_html=True)
        st.write(
            "Our AI-powered system provides real-time inspections of your home, "
            "identifying potential issues before they become major problems. "
            "Get instant feedback and expert recommendations to protect your investment. "
            "With AI Home Inspector, you can trust your home to be safe and secure."
        )
        if st.button("Start Inspection →", key="hero-cta"):
            st.switch_page("pages/mainpage.py")

    # with side2:
    #     header_path = os.path.join("HOME-INSPECTOR", "pages", "header.png")
    #     if os.path.exists(header_path):
    #         st.image(header_path)
    #     else:
    #         st.warning("Header image not found. Please check the path.")


def show_features():
    """Display feature section"""
    st.markdown(
        "<h1 class='sub-header'>Discover a New Era of Home Inspection</h1>",
        unsafe_allow_html=True)
    st.markdown(
        "<h2 class='sub-header'>The Future of Home Inspections is Here: "
        "Intelligent, Efficient, Accurate.</h2>",
        unsafe_allow_html=True)

    # Feature boxes
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("### 🔍 Smart Detection")
            st.write("Advanced AI algorithms to detect structural issues, "
                     "water damage, and more.")

    with col2:
        with st.container(border=True):
            st.markdown("### ⚡ Fast Results")
            st.write(
                "Get detailed inspection reports within minutes, not days.")

    with col3:
        with st.container(border=True):
            st.markdown("### 📊 Accurate Analysis")
            st.write(
                "High-precision analysis with historical data comparison.")


def show_sidebar():
    """Configure sidebar content"""
    with st.sidebar:
        st.markdown("### Quick Links")
        if st.button("📸 New Inspection", use_container_width=True):
            st.switch_page("pages/mainpage.py")
        if st.button("📄 View Reports", use_container_width=True):
            st.switch_page("pages/mainpage.py")

        # Add useful information
        st.markdown("### How It Works")
        st.write("1. Upload or take a photo\n"
                 "2. AI analyzes the image\n"
                 "3. Get instant results\n"
                 "4. Generate professional report")


def main():
    """Main application function"""
    # Initialize session state
    init_session_state()

    # Setup page configuration
    setup_page_config()

    # Show sidebar
    show_sidebar()

    # Main content based on current page
    if st.session_state.current_page == "Home":
        show_hero_section()
        st.markdown("---")
        show_features()

    # Add error handling
    try:
        pass  # Add any additional functionality here
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.button("Reload App", on_click=st.session_state.clear())


if __name__ == "__main__":
    main()
