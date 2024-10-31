from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

def generate_pdf(variables, fileName='Medical_Report.pdf', documentTitle='Medical Report'):
    # Setup the document
    doc = SimpleDocTemplate(fileName, pagesize=letter)
    story = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='Title', fontSize=22, alignment=1, spaceAfter=20, leading=22, textColor=colors.HexColor("#0072C6")
    )
    header_style = ParagraphStyle(
        name='Header', fontSize=14, spaceAfter=10, leading=14, textColor=colors.HexColor("#0072C6"), fontName="Helvetica-Bold"
    )
    normal_style = styles['Normal']
    normal_style.fontSize = 12
    normal_style.leading = 14
    small_text_style = ParagraphStyle(
        name='SmallText', fontSize=10, leading=12
    )

    # Title
    title = documentTitle
    story.append(Paragraph(title, title_style))

    # Patient Information
    story.append(Paragraph("<b>Patient Information:</b>", header_style))
    patient_info = [
        ['DNI:', variables['dni']],
        ['Age:', variables['edad']],
    ]
    table = Table(patient_info, colWidths=[100, 350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E0E0E0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#000000")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8F8F8")),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#D3D3D3")),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))

    # Medical History
    story.append(Paragraph("<b>Medical History:</b>", header_style))
    medical_history = [
        ['Operations:', variables['operaciones']],
        ['Allergies:', variables['alergias']],
        ['Chronic Diseases:', variables['enfermedades_cronicas']],
    ]
    table = Table(medical_history, colWidths=[100, 350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E0E0E0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#000000")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8F8F8")),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#D3D3D3")),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))

    # Current Medications
    story.append(Paragraph("<b>Current Medications:</b>", header_style))
    current_medications = variables['medicamentos_actuales']
    medications_paragraph = Paragraph(current_medications, normal_style)
    story.append(medications_paragraph)
    story.append(Spacer(1, 0.25 * inch))

    # Signature or generic closing message
    signed_by_text = "Firma del facultativo"
    story.append(Paragraph(signed_by_text, small_text_style))

    # Build the PDF
    doc.build(story)

    generate_pdf(variables)
