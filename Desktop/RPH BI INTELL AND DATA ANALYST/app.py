# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time
import os
import json
from dotenv import load_dotenv
import markdown_pdf

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="MABUZA BI Agent",
    page_icon="🧠",
    layout="wide"
)

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()
CREWAI_API_KEY = os.getenv("CREWAI_API_KEY")
CREWAI_CREW_URL = os.getenv("") # Get URL from .env for easy updates

# --- STYLING (Same as before) ---
st.markdown("""
<style>
    /* ... (Your existing CSS styling) ... */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #ffffff; color: #808080; text-align: center;
        padding: 10px; border-top: 1px solid #e1e4e8;
    }
</style>
""", unsafe_allow_html=True)

# --- API & HELPER FUNCTIONS (Same as before) ---
# ... (start_crew, get_crew_status, parse_report_and_generate_charts functions are the same) ...

# =====================================================================
# MAIN APPLICATION UI
# =====================================================================
st.title("🧠 MABUZA AI Business Intelligence & Data Analyst")
st.markdown("Your dedicated AI team for turning complex data into actionable strategy.")

# Initialize session state variables
if 'analysis_running' not in st.session_state:
    st.session_state.analysis_running = False
if 'report_data' not in st.session_state:
    st.session_state.report_data = None

# --- SIDEBAR FOR INPUTS ---
with st.sidebar:
    st.header("1. Upload Your Data")
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file:
        st.success(f"File '{uploaded_file.name}' ready.")
        # Save file to a temporary location
        temp_dir = "temp_data"
        if not os.path.exists(temp_dir): os.makedirs(temp_dir)
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())

    st.header("2. Define Your Goal")
    user_question = st.text_area(
        "What business question do you want to answer with this data?",
        "I want a full analysis of this sales data. Please identify key trends, top-performing products, and provide recommendations to increase profit."
    )

    if st.button("🚀 Assemble AI Team & Start Analysis"):
        if not uploaded_file:
            st.warning("Please upload a data file first.")
        elif not user_question:
            st.warning("Please define your business goal.")
        else:
            st.session_state.analysis_running = True
            st.session_state.report_data = None

# --- MAIN PANEL FOR LIVE STATUS & OUTPUTS ---
if not st.session_state.analysis_running:
    st.info("Please provide your data and business goal in the sidebar to begin.")
    # You could add an expander with instructions here
    with st.expander("How this works"):
        st.markdown("""
            1.  **Upload Data:** Provide your raw data in CSV or Excel format.
            2.  **Define Goal:** Ask a clear business question.
            3.  **AI Team Assembles:** An expert AI team is assembled to handle your request.
            4.  **Live Progress:** You will see the team work through your project step-by-step.
            5.  **Receive Report:** Get a comprehensive report with insights, charts, and recommendations.
        """)
else:
    # This is the "smart" part of the UI - showing live progress
    with st.status("Executing your Business Intelligence Request...", expanded=True) as status:
        st.write("📖 **Business Analyst:** Defining project scope...")
        time.sleep(3) # Simulate work
        
        st.write("🛠️ **Data Engineer:** Cleaning and preparing your data...")
        time.sleep(5) # Simulate work

        st.write("🔬 **Data Scientist:** Performing deep statistical analysis...")
        time.sleep(8) # Simulate work

        st.write("📈 **Market Strategist:** Researching external business context...")
        time.sleep(5) # Simulate work

        st.write("✍️ **Reporting Specialist:** Compiling final client report...")
        # In a real scenario, you would poll the CrewAI API here for actual status updates
        # For this example, we kick off the crew after showing the simulation
        kickoff_id = start_crew(file_path, user_question)
        
        if kickoff_id:
            result = get_crew_status(kickoff_id)
            if result and result["status"] == "SUCCESS":
                st.session_state.report_data = result["output"]
                st.session_state.analysis_running = False
                status.update(label="✅ Analysis Complete!", state="complete", expanded=False)
            elif result:
                status.update(label=f"❌ Error: {result['output']}", state="error")
                st.session_state.analysis_running = False
        else:
            status.update(label="❌ Failed to start the crew.", state="error")
            st.session_state.analysis_running = False

# Display results only after the analysis is complete and successful
if st.session_state.report_data:
    st.success("Your Business Intelligence Report is ready!")

    # Parse the final report into sections for a better UI
    report_content = st.session_state.report_data
    charts, text_report = parse_report_and_generate_charts(report_content)
    
    # You can further parse the text_report to find the specific sections
    try:
        executive_summary = text_report.split("### Key Insights & Visualizations")[0].replace("### Executive Summary", "")
        recommendations = text_report.split("### Actionable Recommendations")[1].split("### Appendix: Data & Methodology")[0]
        appendix = text_report.split("### Appendix: Data & Methodology")[1]
        key_insights = text_report.split("### Key Insights & Visualizations")[1].split("### Actionable Recommendations")[0]
    except IndexError:
        # Fallback if the AI didn't follow the structure perfectly
        executive_summary = "Could not parse Executive Summary."
        recommendations = "Could not parse Recommendations."
        appendix = ""
        key_insights = text_report

    tab1, tab2, tab3 = st.tabs(["📊 Executive Dashboard", "📄 Full Report", "🔬 Methodology"])

    with tab1:
        st.header("Executive Dashboard")
        st.markdown("---")
        st.subheader("Executive Summary")
        st.markdown(executive_summary)
        st.markdown("---")
        st.subheader("Key Visualizations")
        if not charts:
            st.info("No visualizations were generated for this report.")
        else:
            cols = 2
            chart_cols = st.columns(cols)
            for i, chart in enumerate(charts):
                with chart_cols[i % cols]:
                    st.plotly_chart(chart, use_container_width=True)
        st.markdown("---")
        st.subheader("Actionable Recommendations")
        st.markdown(recommendations)

    with tab2:
        st.header("Full Detailed Report")
        st.markdown(report_content)
        st.markdown("---")
        # Download Buttons
        st.download_button("⬇️ Download as Markdown", report_content, "BI_Report.md", "text/markdown")
        pdf_bytes = markdown_pdf.convert_from_string(report_content)
        st.download_button("⬇️ Download as PDF", pdf_bytes, "BI_Report.pdf", "application/pdf")

    with tab3:
        st.header("Methodology & Data Overview")
        st.markdown(appendix)

# --- FOOTER ---
st.markdown("<div class='footer'><p>empowered by MABUZA MDUDUZI</p></div>", unsafe_allow_html=True)