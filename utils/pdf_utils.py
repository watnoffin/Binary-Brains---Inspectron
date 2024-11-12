from fpdf import FPDF

def generate_pdf(analysis):
    """Generate PDF report"""
    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Inspectron Defect Analysis Report', ln=True, align='C')
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)

    # Content
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Defect Type: {analysis['defect_type']}", ln=True)
    pdf.cell(0, 10, f"Severity: {analysis['severity']}", ln=True)
    pdf.cell(0, 10, f"Risk Level: {analysis['risk_level']}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, "Description:", ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, analysis['description'])

    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Recommendations:", ln=True)
    pdf.set_font('Arial', '', 12)
    for rec in analysis['recommendations']:
        pdf.multi_cell(0, 10, f"• {rec}")

    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Estimated Cost: {analysis['estimated_cost']}", ln=True)
    pdf.cell(0, 10, f"Timeline: {analysis['timeline']}", ln=True)

    return pdf.output(dest='S').encode('latin-1')