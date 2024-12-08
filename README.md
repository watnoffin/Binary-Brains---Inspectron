Inspectron: AI Home Inspection Generator
A smarter way to inspect homes.

Overview
Inspectron is a cutting-edge system that automates home inspections using AI-powered image analysis and report generation. Designed for homebuyers, real estate agents, and homeowners, Inspectron simplifies the traditionally labor-intensive process of identifying defects in homes. With real-time analysis and actionable insights, Inspectron offers a faster, more accessible, and cost-effective alternative to manual inspections.

Key Features
1. AI-Powered Defect Detection: Upload images of specific home areas (walls, ceilings, plumbing) and detect potential issues like cracks, mold, or water damage using the Gemini.
2. Comprehensive Reports: Leverages Gemini to generate detailed, professional-grade inspection reports in natural language.
3. Actionable Recommendations: Provides repair suggestions, YouTube tutorial links, and a severity assessment for each detected defect.
4. Full Report Generation:
Leverages IBM Watsonx.ai to generate email reports to relevant authorities.
Call authorities directly if critical issues are detected.
Download a TXT version of the report for offline use.

Tech Stack
Frontend: Streamlit 
Backend: Python (Flask)
APIs:
Gemini API: Image analysis and defect detection.
IBM Watsonx.ai: Natural language email generation.
Other Tools:
File handling for image uploads.
Email API for sending reports.

Demo
Live Demo: https://drive.google.com/file/d/1GkL2Tr-020acxt9E8pc8tpNVdznjzT3Q/view?usp=drive_link

Usage Flow
Step 1: Upload an image of a home defect via the web interface.
Step 2: The backend processes the image using Gemini to detect issues.
Step 3: Inspectron generates a comprehensive report with:
Issue type and severity.
Repair steps recommendations and related YouTube tutorials.
Step 4: Use the actions provided:
Send the report via email.
Call relevant authorities.
Download a TXT version of the report.

Contributors
Nurul Fatin Amira Binti Mohd Riza - Team Leader & Developer 
Tuan Nur Afrina Zahira Binti Tuan Zainuddin - AI Engineer
Muhammad Harith Bin Noorazri - System Designer 

Acknowledgments
Thanks to Gemini API and IBM Watsonx.ai for their powerful tools.
Special thanks to the "Bridgehack to Industry" organizers for the opportunity to build this project.
