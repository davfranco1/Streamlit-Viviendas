from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
import requests

def generate_pdf(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    # Prepare the story (list of flowables)
    story = []
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20
    )
    
    # Add title and subtitle
    story.append(Paragraph("Las Casas de David", title_style))
    story.append(Paragraph(f"{data['tipo'].capitalize()} en {data['direccion']}", subtitle_style))
    
    # Property Details Section
    story.append(Paragraph("Detalles del Inmueble", subtitle_style))
    
    # Create property details table
    idealista_url = f"https://www.idealista.com/inmueble/{data['codigo']}/"
    details = [
        ["Precio:", f"{data['precio']:,.0f} €"],
        ["Tamaño:", f"{data['tamanio']} m²"],
        ["Planta:", data['planta']],
        ["Habitaciones:", data['habitaciones']],
        ["Baños:", data['banios']],
        ["Estado del baño:", data['puntuacion_banio']],
        ["Estado de la cocina:", data['puntuacion_cocina']],
        ["Alquiler Predicho:", f"{data['alquiler_predicho']:,.0f} €"],
        ["Anunciante:", data['anunciante']],
        ["Teléfono:", data['contacto']],
        ["Descripción:", Paragraph(data["descripcion"], styles["BodyText"])],
        ["Idealista Link:", Paragraph(idealista_url, styles["BodyText"])]
    ]
    
    # Create and style the table
    table = Table(details, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Add property image if available
    try:
        if 'urls_imagenes' in data and data['urls_imagenes']:
            image_url = data['urls_imagenes'][0]
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                img_data = BytesIO(response.content)
                img = Image(img_data, width=4*inch, height=3*inch)
                story.append(img)
                story.append(Spacer(1, 20))
    except Exception as e:
        print(f"Error loading image: {e}")
    
    # Rentability Metrics Section
    story.append(Paragraph("Métricas de Rentabilidad", subtitle_style))
    
    metrics = [
        ["Coste Total:", f"{data['Coste Total']:,.0f} €"],
        ["Rentabilidad Bruta:", f"{data['Rentabilidad Bruta']}%"],
        ["Beneficio Antes de Impuestos:", f"{data['Beneficio Antes de Impuestos']:,.0f} €"],
        ["Rentabilidad Neta:", f"{data['Rentabilidad Neta']}%"],
        ["Cuota Mensual Hipoteca:", f"{data['Cuota Mensual Hipoteca']:,.0f} €"],
        ["Cash Necesario Compra:", f"{data['Cash Necesario Compra']:,.0f} €"],
        ["Cash Total Compra y Reforma:", f"{data['Cash Total Compra y Reforma']:,.0f} €"],
        ["Beneficio Neto:", f"{data['Beneficio Neto']:,.0f} €"],
        ["Cashflow Antes de Impuestos:", f"{data['Cashflow Antes de Impuestos']:,.0f} €"],
        ["Cashflow Después de Impuestos:", f"{data['Cashflow Después de Impuestos']:,.0f} €"],
        ["ROCE:", f"{data['ROCE']}%"],
        ["ROCE (Años):", f"{data['ROCE (Años)']:,.0f} años"],
        ["Cash-on-Cash Return:", f"{data['Cash-on-Cash Return']}%"],
        ["COCR (Años):", f"{data['COCR (Años)']:,.0f} años"]
    ]
    
    metrics_table = Table(metrics, colWidths=[3*inch, 3*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    
    story.append(metrics_table)
    
    # Build the PDF
    doc.build(story)
    buffer.seek(0)
    return buffer