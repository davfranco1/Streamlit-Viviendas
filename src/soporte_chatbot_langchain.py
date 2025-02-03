import os
import json
import pandas as pd
import ast
import folium
from dotenv import load_dotenv

from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent # type: ignore


from langchain.chat_models import ChatOpenAI
from streamlit_folium import st_folium
import streamlit as st


# Función para renderizar carrusel de imágenes
def render_image_carousel(imagenes):
    carrusel_html = f"""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.8.1/slick.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.8.1/slick-theme.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.8.1/slick.min.js"></script>
    
    <style>
        .carousel {{
            max-width: 90%;
            margin: auto;
            height: 290px;
        }}
        .carousel img {{
            width: 100%;
            height: 290px;
            border-radius: 10px;
            object-fit: cover;
        }}
    </style>

    <div class="carousel">
        {"".join([f'<div><img src="{url}" alt="carousel-image"></div>' for url in imagenes])}
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
    st.components.v1.html(carrusel_html, height=300)


# Cargar variables de entorno
load_dotenv()
OPENAI = os.getenv("OPENAI")

if not OPENAI:
    raise ValueError("API Key de OpenAI no encontrada en las variables de entorno.")

# Crear agente de LangChain para el DataFrame
def langchain_agent(df):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=OPENAI)
    
    # Enable execution of code inside the agent
    agent = create_pandas_dataframe_agent(llm, df, verbose=True, allow_dangerous_code=True)
    
    return agent

def extract_property_id(response, df):
    """
    Extracts a property ID from the LangChain response if possible.
    It checks if any property code (from the DataFrame) is present in the response.
    
    :param response: The response from LangChain (string)
    :param df: The DataFrame containing property data
    :return: The matched property ID or None
    """
    for property_id in df["codigo"].astype(str):  # Ensure IDs are strings for matching
        if property_id in response:
            return property_id
    return None

# Función para consultar el DataFrame
def consultar_dataframe(agent, consulta_usuario, df):
    try:
        response = agent.run(consulta_usuario)

        # If the response is a DataFrame, return the first row
        if isinstance(response, pd.DataFrame) and not response.empty:
            return response.iloc[0]  # Ensures a single row is returned

        # If response is a string, try to extract property ID
        elif isinstance(response, str):
            property_id = extract_property_id(response, df)
            if property_id is not None:
                return df.loc[df["codigo"] == property_id].iloc[0]

            return None  # Return None instead of a string to avoid TypeError

    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None  # Ensure we return None instead of a string

    return None  # Ensure we always return a Pandas Series or None


def display_property_details(property_data):
    st.markdown(f"### 🏡 {property_data['tipo'].capitalize()} en {property_data['direccion']}")
    st.markdown(f"🏷️ **Precio**: {property_data['precio']:,.0f} €")
    st.markdown(f"📍 **Ubicación**: {property_data['distrito']}")
    st.markdown(f"🔗 [Ver en Idealista](https://www.idealista.com/inmueble/{property_data['codigo']}/)")
            
    col1, col2 = st.columns(2)
    
    with col1:
        if isinstance(property_data['urls_imagenes'], str):
            urls_imagenes = ast.literal_eval(property_data['urls_imagenes'])  # Safer than eval()
        elif isinstance(property_data['urls_imagenes'], list):
            urls_imagenes = property_data['urls_imagenes']
        else:
            urls_imagenes = []
        
        render_image_carousel(urls_imagenes)
    
    with col2:
        # Crear el mapa
        mapa = folium.Map(location=[property_data['lat'], property_data['lon']], zoom_start=15)

        # Asegurar que se agregan marcadores
        folium.Marker(
            location=[property_data['lat'], property_data['lon']],
            popup=property_data['direccion'],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(mapa)

        # Mostrar en Streamlit
        st_folium(mapa, height=300)

    # Mostrar información básica del inmueble
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

    # Mostrar métricas de rentabilidad
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


# agent = sc2.langchain_agent(df)
# consulta = "¿Cuál es el piso más barato?"
# best_match = sc2.consultar_dataframe(agent, consulta, df)

# sc2.display_property_details(best_match)