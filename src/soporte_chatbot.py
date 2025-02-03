import streamlit as st
import openai
from dotenv import load_dotenv
import os
import json
import folium
import ast
from streamlit_folium import st_folium

load_dotenv()

OPENAI = os.getenv("OPENAI")
if not OPENAI:
    raise ValueError("OPENAI no está definido en las variables de entorno")
client = openai.OpenAI(api_key=OPENAI) 


def render_image_carousel(image_urls):
    # Carousel HTML
    carousel_html = f"""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.8.1/slick.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.8.1/slick-theme.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.8.1/slick.min.js"></script>
    
    <style>
        .carousel {{
            max-width: 90%;
            margin: auto;
            height: 290px; /* Set desired height */
        }}
        .carousel img {{
            width: 100%;
            height: 290px; /* Set desired height */
            border-radius: 10px;
            object-fit: cover;
        }}
        .slick-prev:before, .slick-next:before {{
            color: #00185E;
            font-size: 24px;
        }}
    </style>

    <div class="carousel">
        {"".join([f'<div><img src="{url}" alt="carousel-image"></div>' for url in image_urls])}
    </div>

    <script>
    $(document).ready(function() {{
        $('.carousel').slick({{
            infinite: true,
            slidesToShow: 1,
            slidesToScroll: 1,
            arrows: true,
            dots: false
        }});
    }});
    </script>
    """
    st.components.v1.html(carousel_html, height=300)


# Define valid columns (to ensure GPT only outputs correct field names)
VALID_COLUMNS = [
    "codigo", "precio", "precio_por_zona", "tipo", "exterior", "planta", "ascensor", "tamanio", "habitaciones", "banios",
    "aire_acondicionado", "trastero", "terraza", "patio", "direccion", "distrito", "alquiler_predicho", 
    "puntuacion_cocina", "puntuacion_banio", "mts_cocina", "mts_banio", "Coste Total", "Rentabilidad Bruta",
    "Beneficio Antes de Impuestos", "Rentabilidad Neta", "Cuota Mensual Hipoteca", "Cash Necesario Compra", 
    "Cash Total Compra y Reforma", "Beneficio Neto", "Cashflow Antes de Impuestos", "Cashflow Después de Impuestos",
    "ROCE", "ROCE (Años)", "Cash-on-Cash Return", "COCR (Años)"
]

# Chatbot Query Function
def chatbot_query(df, user_input):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},  # Ensure JSON output
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un asistente inmobiliario especializado en interpretar consultas de búsqueda de propiedades. "
                    "Tu tarea es extraer la información relevante del usuario y devolverla como un objeto JSON con claves "
                    "que coincidan exactamente con las siguientes columnas:\n\n"
                    f"{', '.join(VALID_COLUMNS)}\n\n"
                    "### Reglas de extracción de información:\n"
                    "1. **Valores exactos:**\n"
                    "   - 'piso de 3 habitaciones' → { 'habitaciones': 3 }\n"
                    "   - 'busco un piso en la planta 5' → { 'planta': 5 }\n"
                    "   - 'ático sin terraza' → { 'terraza': False }\n"
                    "   - 'piso con aire acondicionado' → { 'aire_acondicionado': True }\n\n"
                    "2. **Rangos numéricos y comparaciones:**\n"
                    "   - 'menos de 100 metros cuadrados' → { 'tamanio_max': 100 }\n"
                    "   - 'más de 2 baños' → { 'banios_min': 2 }\n"
                    "   - 'precio inferior a 100,000' → { 'precio_max': 100000 }\n"
                    "   - 'precio superior a 200,000' → { 'precio_min': 200000 }\n"
                    "   - 'rango de precios entre 150,000 y 250,000' → { 'precio_min': 150000, 'precio_max': 250000 }\n\n"
                    "3. **Preferencias Booleanas:**\n"
                    "   - 'quiero un piso exterior' → { 'exterior': True }\n"
                    "   - 'busco un bajo con patio' → { 'planta': 0, 'patio': True }\n\n"
                    "Si el usuario menciona varias características, agrégalas al JSON. "
                    "Si la información es ambigua, ignórala en la respuesta."
                )
            },
            {"role": "user", "content": user_input}
        ]
    )

    try:
        structured_response = json.loads(response.choices[0].message.content)  # Parse JSON response

        # ✅ Filtrar solo columnas válidas
        structured_response = {k: v for k, v in structured_response.items() if k in VALID_COLUMNS}

        # ✅ Establecer un valor por defecto si no se extrae información
        if not structured_response:
            structured_response = {"tipo": "piso"}  # Default fallback

    except json.JSONDecodeError:
        structured_response = {"tipo": "piso"}  # Fallback case

    return structured_response


# Property Search Function (Returns the **Best Single Match**)
def find_best_match(df, criteria):
    filtered_df = df.copy()

    for key, value in criteria.items():
        if key in filtered_df.columns and key not in ["contacto"]:
            
            if isinstance(value, (int, float)):
                # ✅ Handle numeric filters properly (now supports more/less than)
                if key == "tamanio_max":
                    filtered_df = filtered_df[filtered_df["tamanio"] <= value]  # Less than or equal
                elif key == "tamanio_min":
                    filtered_df = filtered_df[filtered_df["tamanio"] >= value]  # More than or equal
                elif key == "precio_max":
                    filtered_df = filtered_df[filtered_df["precio"] <= value]
                elif key == "precio_min":
                    filtered_df = filtered_df[filtered_df["precio"] >= value]
                elif key == "banios_max":
                    filtered_df = filtered_df[filtered_df["banios"] <= value]  # Now supports "less than X"
                elif key == "banios_min":
                    filtered_df = filtered_df[filtered_df["banios"] >= value]  # Now supports "more than X"
                elif key == "habitaciones_max":
                    filtered_df = filtered_df[filtered_df["habitaciones"] <= value]
                elif key == "habitaciones_min":
                    filtered_df = filtered_df[filtered_df["habitaciones"] >= value]
                elif key == "planta":
                    filtered_df = filtered_df[filtered_df["planta"] == value]  # Exact match for floor number
                else:
                    filtered_df = filtered_df[filtered_df[key] == value]  # Exact match for other numbers

            elif isinstance(value, bool):
                # ✅ Handle True/False filters (e.g., aire_acondicionado, terraza)
                filtered_df = filtered_df[filtered_df[key] == value]

            elif isinstance(value, str):
                # ✅ Search for keywords in BOTH structured fields and `descripcion`
                filtered_df = filtered_df[
                    filtered_df[key].astype(str).str.contains(value, case=False, na=False)
                    | filtered_df["descripcion"].astype(str).str.contains(value, case=False, na=False)
                ]

    # ✅ If multiple results, prioritize by Rentabilidad Bruta & Precio
    if not filtered_df.empty:
        filtered_df = filtered_df.sort_values(by=["Rentabilidad Bruta", "precio"], ascending=[False, True])
        best_match = filtered_df.iloc[0].to_dict()  # Return as dictionary
        return best_match

    return "No se han encontrado viviendas con ese criterio."


# Display Property Details
def display_property_details(property_data):
    st.markdown(f"### 🏡 {property_data['tipo'].capitalize()} en {property_data['direccion']}")
    st.markdown(f"🏷️ **Precio**: {property_data['precio']:,.0f} €")
    st.markdown(f"📍 **Ubicación**: {property_data['distrito']}")
    st.markdown(f"🔗 [Ver en Idealista](https://www.idealista.com/inmueble/{property_data['codigo']}/)")
            
    col1, col2 = st.columns(2)
    
    with col1:
        # Ensure urls_imagenes is properly converted to a list
        if isinstance(property_data['urls_imagenes'], str):
            urls_imagenes = ast.literal_eval(property_data['urls_imagenes'])  # Safer than eval()
        elif isinstance(property_data['urls_imagenes'], list):
            urls_imagenes = property_data['urls_imagenes']
        else:
            urls_imagenes = []
        
        render_image_carousel(urls_imagenes)
    
    with col2:

        # Create the map
        m = folium.Map(location=[property_data['lat'], property_data['lon']], zoom_start=15)

        # Ensure markers are added
        marker = folium.Marker(
            location=[property_data['lat'], property_data['lon']],
            popup=property_data['direccion'],
            icon=folium.Icon(color="blue", icon="info-sign")
        )
        marker.add_to(m)

        # Display in Streamlit
        st_folium(m, height=300)

    # Show basic property info
    st.markdown("### 🏠 Características del Inmueble")

    col1, col2, col3 = st.columns(3)
    col1.write(f"**Tamaño**: {property_data['tamanio']:,.0f} m²")
    col1.write(f"**Habitaciones**: {property_data['habitaciones']}")
    col1.write(f"**Baños**: {property_data['banios']}")

    col2.write(f"**Planta**: {property_data['planta']}")
    col2.write(f"**Ascensor**: {'Sí' if property_data['ascensor'] else 'No'}")
    col2.write(f"**Aire acondicionado**: {'Sí' if property_data['aire_acondicionado'] else 'No'}")
    
    col3.write(f"**Patio**: {'Sí' if property_data['patio'] else 'No'}")
    col3.write(f"**Terraza**: {'Sí' if property_data['terraza'] else 'No'}")
    col3.write(f"**Trastero**: {'Sí' if property_data['trastero'] else 'No'}")

    st.write(f"**Descripción**: {property_data['descripcion']}")
    st.write(f"**Anunciante**: {property_data['anunciante']}. **Teléfono**: {property_data['contacto']}")

    # Show profitability metrics
    st.markdown("### 📈 Rentabilidad")
    col1, col2, col3 = st.columns(3)
    col1.metric("Rentabilidad Bruta", f"{property_data['Rentabilidad Bruta']}%")
    col2.metric("Rentabilidad Neta", f"{property_data['Rentabilidad Neta']}%")
    col3.metric("Beneficio Neto", f"{property_data['Beneficio Neto']:,.0f} €")
    
    col4, col5, col6 = st.columns(3)
    col4.metric("ROCE", f"{property_data['ROCE']} %")
    col5.metric("Cash-on-Cash Return", f"{property_data['Cash-on-Cash Return']}%")
    col6.metric("Cashflow Después de Impuestos", f"{property_data['Cashflow Después de Impuestos']:,.0f} €")
    
    col7, col8, col9 = st.columns(3)
    col7.metric("Cuota Mensual Hipoteca", f"{property_data['Cuota Mensual Hipoteca']:,.0f} €")
    col8.metric("Cash Necesario Compra", f"{property_data['Cash Necesario Compra']:,.0f} €")
    col9.metric("Cash Total Compra y Reforma", f"{property_data['Cash Total Compra y Reforma']:,.0f} €")
    
    col10, col11, col12 = st.columns(3)
    col10.metric("ROCE (Años)", f"{property_data['ROCE (Años)']:,.0f} años")
    col11.metric("COCR (Años)", f"{property_data['COCR (Años)']:,.0f} años")
    col12.metric("Alquiler Predicho", f"{property_data['alquiler_predicho']:,.0f} €")
