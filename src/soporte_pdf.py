from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import requests

def generate_pdf(data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Define page dimensions
    page_width, page_height = letter
    margin_x = 50
    y_position = page_height - 70  # Start position below the title

    # Idealista Listing URL
    idealista_url = f"https://www.idealista.com/inmueble/{data['codigo']}/"

    def check_page_break(c, y_position, min_height_needed=100):
        """Checks if there is enough space, otherwise creates a new page."""
        if y_position < min_height_needed:
            c.showPage()  # Create a new page
            return page_height - 70  # Reset y_position to top of new page
        return y_position

    # Title Section
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin_x, y_position, "Las Casas de David")  
    y_position -= 25
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_x, y_position, f"{data['tipo'].capitalize()} en {data['direccion']}")
    y_position -= 40  # Space before the image

    # Load and Display Listing Image (Properly Sized & Positioned)
    try:
        if 'urls_imagenes' in data and data['urls_imagenes']:
            image_url = data['urls_imagenes'][0]  # First image in the listing
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                image = ImageReader(BytesIO(response.content))
                
                # Adjust Image Size & Position
                display_width = 180  # Smaller image width
                display_height = 120  # Adjusted height

                # Ensure enough space before placing the image
                y_position = check_page_break(c, y_position, display_height + 30)
                image_x = margin_x
                image_y = y_position - display_height  # Position image
                c.drawImage(image, image_x, image_y, width=display_width, height=display_height)
                
                y_position -= display_height + 40  # Extra spacing after the image
    except Exception as e:
        print(f"Error loading image: {e}")

    # Property Details Title
    y_position = check_page_break(c, y_position, 50)  # Ensure space for the title
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_x, y_position, "Detalles del Inmueble")
    y_position -= 30  # Space before the table

    styles = getSampleStyleSheet()
    description_text = Paragraph(data["descripcion"], styles["BodyText"])  # Wrap text properly

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
        ["Descripción:", description_text],  # Wrapped description
        ["Idealista Link:", idealista_url]
    ]

    # Ensure enough space before drawing the table
    y_position = check_page_break(c, y_position, len(details) * 20 + 50)

    table = Table(details, colWidths=[140, 350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    
    table.wrapOn(c, page_width, page_height)
    table.drawOn(c, margin_x, y_position - len(details) * 20)
    y_position -= len(details) * 20 + 50

    # Move "Métricas de Rentabilidad" to a New Page
    c.showPage()
    y_position = page_height - 70  # Reset position for new page

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_x, y_position, "Métricas de Rentabilidad")
    y_position -= 30  # Space before the table

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

    table_metrics = Table(metrics, colWidths=[180, 300])
    table_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))

    table_metrics.wrapOn(c, page_width, page_height)
    table_metrics.drawOn(c, margin_x, y_position - len(metrics) * 20)

    # Save the PDF
    c.save()
    buffer.seek(0)
    return buffer