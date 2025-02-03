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
            color: #3253AA;
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


# Chatbot Functionality (Updated API with structured JSON response)
import json
from openai import OpenAI

client = OpenAI()

def chatbot_query(df, user_input):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},  # Ensure JSON output
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un asistente inmobiliario. Extrae información relevante de la consulta del usuario y devuélvela "
                    "como un JSON con claves que coincidan exactamente con las columnas del dataset de propiedades, excluyendo 'descripcion', 'contacto'.\n"
                    "El dataset de propiedades contiene las siguientes columnas relevantes:\n"
                    "- 'tipo' (Ej: 'piso', 'ático')\n"
                    "- 'direccion' (Ej: 'Calle de Terminillo, 5')\n"
                    "- 'distrito' (Ej: 'Delicias')\n"
                    "- 'precio' (Ej: 150000)\n"
                    "- 'tamanio' (Ej: 80) # En m²\n"
                    "- 'habitaciones' (Ej: 3)\n"
                    "- 'banios' (Ej: 2)\n"
                    "- 'ascensor' (Ej: True o False)\n"
                    "- 'terraza' (Ej: True o False)\n"
                    "- 'aire_acondicionado' (Ej: True o False)\n"
                    "- 'planta' (Ej: 5)  # Número de piso en el edificio\n"
                    "- 'Rentabilidad Bruta' (Ej: 5.4)  # En porcentaje\n"
                    "Si el usuario menciona valores numéricos con comparaciones:\n"
                    "- 'menos de 100 metros cuadrados' → usa 'tamanio': 100 y filtra en tu código (df[df['tamanio'] <= 100])\n"
                    "- 'más de 2 baños' → usa 'banios': 2 y filtra (df[df['banios'] >= 2])\n"
                    "- 'piso de 3 habitaciones' → usa 'habitaciones': 3\n"
                    "- 'precio inferior a 100,000' → usa 'precio': 100000 y filtra (df[df['precio'] <= 100000])\n"
                    "- 'busco un piso en la planta 5' → usa 'planta': 5\n"
                    "- 'ático sin terraza' → usa 'terraza': False\n"
                    "- 'piso con aire acondicionado' → usa 'aire_acondicionado': True\n"
                    "Responde **únicamente** con un JSON válido. Ejemplo:\n"
                    "{ \"tipo\": \"piso\", \"tamanio\": 100, \"banios\": 2, \"aire_acondicionado\": True, \"planta\": 5, \"precio\": 100000 }"
                )
            },
            {"role": "user", "content": user_input}
        ]
    )

    try:
        structured_response = response.choices[0].message.content  # Direct JSON object response

        # Filtrar solo columnas válidas
        valid_fields = [col for col in df.columns if col not in ["descripcion", "contacto"]]
        structured_response = {k: v for k, v in structured_response.items() if k in valid_fields}

        if not structured_response:
            structured_response = {"tipo": "piso"}  # Default fallback

    except json.JSONDecodeError:
        structured_response = {"tipo": "piso"}  # Fallback case

    return structured_response


# Property Search Based on Chatbot Output (Optimized for Best Match)
def find_best_match(df, criteria):
    filtered_df = df.copy()

    for key, value in criteria.items():
        if key in filtered_df.columns and key not in ["urls_imagenes", "url_cocina", "url_banio"]:
            
            if isinstance(value, (int, float)):
                # Handle numeric filters based on query intent
                if key == "tamanio":
                    filtered_df = filtered_df[filtered_df["tamanio"] <= value]  # Less than or equal
                elif key == "precio":
                    filtered_df = filtered_df[filtered_df["precio"] <= value]  # Less than or equal
                elif key == "banios":
                    filtered_df = filtered_df[filtered_df["banios"] >= value]  # More than or equal
                elif key == "habitaciones":
                    filtered_df = filtered_df[filtered_df["habitaciones"] >= value]  # More than or equal
                else:
                    filtered_df = filtered_df[filtered_df[key] == value]  # Exact match for other numbers

            elif isinstance(value, bool):
                # Handle True/False filters (e.g., aire_acondicionado, terraza)
                filtered_df = filtered_df[filtered_df[key] == value]

            elif isinstance(value, str):
                # Allow partial matches for text fields, especially for addresses
                filtered_df = filtered_df[filtered_df[key].astype(str).str.contains(value, case=False, na=False)]

    # If multiple results, prioritize by Rentabilidad Bruta and precio
    if not filtered_df.empty:
        filtered_df = filtered_df.sort_values(by=["Rentabilidad Bruta", "precio"], ascending=[False, True])
        return filtered_df.iloc[0]  # Return the best match

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
