from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from io import BytesIO
import requests
import os
from datetime import datetime

def add_page_elements(canvas, doc):
    # Add the footer on each page
    canvas.saveState()
    
    # Footer style
    footer_text = "Los resultados son estimaciones, y nunca deben considerarse consejos de inversión. Antes de invertir, asegúrese de consultar con un experto."
    timestamp = f"||  Las Casas de David. Análisis inteligente para maximizar tu inversión.  || {datetime.now().strftime("Generado el %d/%m/%Y a las %H:%M")}"
    
    # Set font for footer
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.grey)
    
    # Draw timestamp
    canvas.drawCentredString(doc.pagesize[0]/2, 0.75 * inch, timestamp)
    
    # Draw disclaimer
    canvas.drawCentredString(doc.pagesize[0]/2, 0.5 * inch, footer_text)
    
    canvas.restoreState()

def generate_pdf(data):
    buffer = BytesIO()
    
    # Create document with extra margin for footer
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=70,
        bottomMargin=85  # Increased to accommodate footer
    )
    
    # Define brand colors
    PRIMARY_COLOR = HexColor('#1a365d')
    SECONDARY_COLOR = HexColor('#2d5a88')
    ACCENT_COLOR = HexColor('#f0f4f8')
    
    story = []
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=PRIMARY_COLOR,
        spaceAfter=15,
        alignment=1
    )
    
    # Add logo
    logo_path = "images/logo_transparent.png"
    if os.path.exists(logo_path):
        logo = Image(logo_path)
        # Make logo square and smaller
        logo.drawHeight = 1.5 * inch
        logo.drawWidth = 1.5 * inch
        story.append(logo)
        story.append(Spacer(1, 20))
    
    # Property Title Section - Combined tipo and direccion
    combined_title = f"{data['tipo'].capitalize()} en {data['direccion']}"
    story.append(Paragraph(combined_title, title_style))
    story.append(Spacer(1, 20))
    
    # Prepare image for side-by-side layout
    property_image = None
    try:
        if 'urls_imagenes' in data and data['urls_imagenes']:
            image_url = data['urls_imagenes'][0]
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                img_data = BytesIO(response.content)
                property_image = Image(img_data)
                property_image.drawWidth = 3 * inch
                property_image.drawHeight = 2.5 * inch
    except Exception as e:
        print(f"Error loading image: {e}")
    
    # Key Highlights Box
    highlights = [
        [Paragraph(f"<font color='#{PRIMARY_COLOR.hexval()[2:]}'>Precio</font>", styles["BodyText"]), 
         Paragraph(f"<b>{data['precio']:,.0f} €</b>", styles["BodyText"])],
        [Paragraph(f"<font color='#{PRIMARY_COLOR.hexval()[2:]}'>Tamaño</font>", styles["BodyText"]), 
         Paragraph(f"<b>{data['tamanio']} m²</b>", styles["BodyText"])],
        [Paragraph(f"<font color='#{PRIMARY_COLOR.hexval()[2:]}'>Habitaciones</font>", styles["BodyText"]), 
         Paragraph(f"<b>{data['habitaciones']}</b>", styles["BodyText"])],
        [Paragraph(f"<font color='#{PRIMARY_COLOR.hexval()[2:]}'>Baños</font>", styles["BodyText"]), 
         Paragraph(f"<b>{data['banios']}</b>", styles["BodyText"])]
    ]
    
    highlights_table = Table(highlights, colWidths=[1.5*inch, 1.5*inch])
    highlights_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ACCENT_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, SECONDARY_COLOR),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    # Create side-by-side layout for highlights and image
    if property_image:
        side_by_side_data = [[highlights_table, property_image]]
        side_by_side = Table(side_by_side_data, colWidths=[3.5*inch, 3.5*inch])
        side_by_side.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(side_by_side)
    else:
        story.append(highlights_table)
    
    story.append(Spacer(1, 30))
    
    # Property Details Section
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=PRIMARY_COLOR,
        spaceBefore=20,
        spaceAfter=10,
        borderColor=PRIMARY_COLOR,
        borderWidth=1,
        borderPadding=8,
    )
    
    story.append(Paragraph("Detalles del Inmueble", section_header_style))
    
    # Create property details table
    idealista_url = f"https://www.idealista.com/inmueble/{data['codigo']}/"
    details = [
        ["Estado del baño:", data['puntuacion_banio']],
        ["Estado de la cocina:", data['puntuacion_cocina']],
        ["Alquiler Predicho:", f"{data['alquiler_predicho']:,.0f} €"],
        ["Anunciante:", data['anunciante']],
        ["Teléfono:", data['contacto']],
        ["Descripción:", Paragraph(data["descripcion"], styles["BodyText"])],
        ["Enlace Idealista:", Paragraph(idealista_url, styles["BodyText"])]
    ]
    
    table = Table(details, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), ACCENT_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, SECONDARY_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Wrap all profitability metrics in KeepTogether
    profitability_section = []
    
    # Rentability Metrics Section
    profitability_section.append(Paragraph("Métricas de Rentabilidad", section_header_style))
    
    # Key metrics in a highlighted box
    key_metrics = [
        ["Rentabilidad Bruta", "Rentabilidad Neta", "ROCE", "Cash-on-Cash Return"],
        [f"{data['Rentabilidad Bruta']}%", 
         f"{data['Rentabilidad Neta']}%", 
         f"{data['ROCE']}%", 
         f"{data['Cash-on-Cash Return']}%"]
    ]
    
    key_metrics_table = Table(key_metrics, colWidths=[2*inch] * 4)
    key_metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
        ('BACKGROUND', (0, 1), (-1, 1), ACCENT_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, 1), PRIMARY_COLOR),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    profitability_section.append(key_metrics_table)
    profitability_section.append(Spacer(1, 20))
    
    # Detailed metrics table
    metrics = [
        ["Coste Total:", f"{data['Coste Total']:,.0f} €"],
        ["Beneficio Antes de Impuestos:", f"{data['Beneficio Antes de Impuestos']:,.0f} €"],
        ["Cuota Mensual Hipoteca:", f"{data['Cuota Mensual Hipoteca']:,.0f} €"],
        ["Cash Necesario Compra:", f"{data['Cash Necesario Compra']:,.0f} €"],
        ["Cash Total Compra y Reforma:", f"{data['Cash Total Compra y Reforma']:,.0f} €"],
        ["Beneficio Neto:", f"{data['Beneficio Neto']:,.0f} €"],
        ["Cashflow Antes de Impuestos:", f"{data['Cashflow Antes de Impuestos']:,.0f} €"],
        ["Cashflow Después de Impuestos:", f"{data['Cashflow Después de Impuestos']:,.0f} €"],
        ["ROCE (Años):", f"{data['ROCE (Años)']:,.0f} años"],
        ["COCR (Años):", f"{data['COCR (Años)']:,.0f} años"]
    ]
    
    metrics_table = Table(metrics, colWidths=[3*inch, 3*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), ACCENT_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, SECONDARY_COLOR)
    ]))
    
    profitability_section.append(metrics_table)
    
    # Keep all profitability metrics together
    story.append(KeepTogether(profitability_section))
    
    # Build the PDF with the footer function
    doc.build(story, onFirstPage=add_page_elements, onLaterPages=add_page_elements)
    buffer.seek(0)
    return buffer