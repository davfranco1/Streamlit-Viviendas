import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import ast
import math
import openai
from dotenv import load_dotenv
import os
import json
import folium
from streamlit_folium import st_folium

import sys
sys.path.append("../src")

import src.soporte_rentabilidad as sr
import src.soporte_mongo as sm
import src.soporte_texto as stxt

# Set Streamlit page config
st.set_page_config(page_title="Rentabilidad Inmobiliaria",
                   page_icon="images/favicon.ico",
                   layout="wide")

st.config.set_option("theme.base", "light")
st.config.set_option("theme.primaryColor", "#170058")
st.config.set_option("theme.backgroundColor", "#EFEFEF")  # White background
st.config.set_option("theme.secondaryBackgroundColor", "#EFEFEF")  # Light gray sidebar
st.config.set_option("theme.textColor", "#00185E")  # text
st.config.set_option("theme.font", "sans serif")  # Default font

# Add custom styles
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 5rem;
        padding-bottom: 5rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    
    /* Make padding responsive on mobile */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }

    /* Hide top padding in other elements */
    .element-container {
        margin-top: -0.5rem;
    }

    /* Markdown elements spacing */
    .stMarkdown {
        margin-top: 0.5rem;
    }

    /* Styling input elements */
    .stTextInput, .stSelectbox, .stNumberInput, .stSlider, .stRadio {
        background-color: white;
        border: 2px solid #138cc6;
        border-radius: 10px;
        padding: 10px;
    }

    .stApp {
        background-color: #EFEFEF;
        border-radius: 15px;
        padding: 20px;
    }

    /* Responsive scrollable container */
    .scrollable-container {
        min-height: 300px;
        max-height: 70vh; /* Makes it relative to the viewport height */
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #cccccc;
        border-radius: 10px;
        background-color: #f9f9f9;
    }

    .card {
        background-color: #ffffff;
        border: 1px solid #cccccc;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
    }

    .card img {
        width: 150px;
        height: 150px;
        object-fit: cover;
        border-radius: 10px;
        border: 1px solid #cccccc;
    }

    .card-details {
        flex: 1;
        padding-right: 15px;
    }

    .card-details h3 {
        color: #007bff;
        margin-bottom: 5px;
        text-decoration: none;
    }

    .card-details h3 a {
        color: #007bff;
        text-decoration: none;
    }

    .card-details h3 a:hover {
        text-decoration: underline;
    }

    .card-details p {
        margin: 5px 0;
    }

    /* Responsive Sidebar */
    [data-testid="stSidebar"] {
        background: #4B5F6D !important;
        padding: 15px !important;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2) !important;
        color: white !important;
    }

    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            padding: 10px !important;
        }
    }

    .custom-title {
    text-transform: capitalize;
    color: #3253AA !important;  /* Ensure color applies */
    font-weight: bold;
    text-decoration: none;  /* Remove underline */
    }
    .custom-title:hover {
        text-decoration: underline; /* Add underline on hover */
    }

    </style>
    """,
    unsafe_allow_html=True
)

# Create MongoDB connection
bd = sm.conectar_a_mongo('ProyectoRentabilidad')

# Load the data
@st.cache_data
def load_data():
    try:
        # Load dataset
        #data = pd.read_pickle("ejemplo.pkl")
        data = sm.importar_a_geodataframe(bd, 'ventafinal')

        # Process geometry column if it exists
        if "geometry" in data.columns:
            data["lat"] = data["geometry"].apply(lambda x: x.y if hasattr(x, "y") else None)
            data["lon"] = data["geometry"].apply(lambda x: x.x if hasattr(x, "x") else None)

        # Convert `urls_imagenes` from string to list if needed
        if "urls_imagenes" in data.columns:
            data["urls_imagenes"] = data["urls_imagenes"].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else x
            )

        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


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


if 'page' not in st.session_state:
    st.session_state.page = "Datos de compra y financiación"

if "inputs" not in st.session_state:
    st.session_state.inputs = {
        "porcentaje_entrada": 20.0,
        "coste_reformas": 5000,
        "comision_agencia": 3.0,
        "anios": 30,
        "tin": 3.0,
        "seguro_vida": 0,
        "tipo_irpf": 17.0,
        "porcentaje_amortizacion": 40.0,
    }

def handle_nav_change():
    st.session_state.page = st.session_state.navigation

def go_to_results():
    st.session_state.page = "Resultados"


# Center the image in the sidebar using HTML & CSS
with st.sidebar:
    st.image("images/logo_transparent-glow.png")

    # Navigation
    st.sidebar.radio(
        "Navegación",
        ["Datos de compra y financiación", "Resultados", "Mapa", "Chatbot", "Datos Completos", "Información de Soporte"],
        key="navigation",
        on_change=handle_nav_change,
        index=["Datos de compra y financiación", "Resultados", "Mapa", "Chatbot", "Datos Completos", "Información de Soporte"].index(st.session_state.page)
    )


data = load_data()

# Ensure required columns exist in data
required_columns = ["distrito", "tamanio", "precio", "puntuacion_banio", "puntuacion_cocina", "habitaciones", "urls_imagenes", "codigo"]
for col in required_columns:
    if col not in data.columns:
        st.error(f"Missing column: {col}. Please check your dataset.")
        st.stop()


# Create layout with two columns
col1, col2 = st.columns([3, 1])  # Left side (text) is wider than the right side (image)

with col1:
    st.markdown("""
    <style>
    .title-main {
        color: #0b5394;
        font-size: 36px;
        font-weight: bold;
    }
    .title-sub {
        color: #0b5394;
        font-size: 20px;
        font-weight: bold;
    }
    hr {
        border: 1px solid #0b5394 !important; /* Make the line bolder and blue */
        margin: 0px 0; /* Add spacing above and below */
        width: 100%; /* Ensure full width */
    }
    </style>
    <div class="title-main">Calculadora de Rentabilidad Inmobiliaria</div>
    <div class="title-sub">Zaragoza</div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(
        """
        <div style="display: flex; justify-content: flex-end;">
            <img src="https://raw.githubusercontent.com/davfranco1/Streamlit-Viviendas/refs/heads/main/images/zaragoza.png" width="100">
        </div>
        """,
        unsafe_allow_html=True
    )


# Insert a bold, colored horizontal line
st.markdown("<hr>", unsafe_allow_html=True)


# Inject JavaScript to remove the number input spinner buttons
st.markdown("""
    <script>
        // Wait until the page fully loads
        document.addEventListener("DOMContentLoaded", function() {
            let inputs = document.querySelectorAll('input[type=number]');
            inputs.forEach(input => {
                input.style.cssText = 'appearance: textfield; -moz-appearance: textfield;';
            });
        });
    </script>
""", unsafe_allow_html=True)


if st.session_state.page == "Datos de compra y financiación":
    st.markdown('<p style="color: #224094; font-size: 18px;">Introduce los datos correspondientes a la compra y la financiación, seguido del botón <strong>Ver resultados<strong>.</p>', unsafe_allow_html=True)

    # Create two columns
    col1, col2 = st.columns(2)

    # General inputs
    col1.write("**Datos generales**")
    st.session_state.inputs["porcentaje_entrada"] = col1.number_input(
        "Porcentaje de entrada (%)", 
        min_value=0.0, 
        max_value=100.0, 
        step=0.1, 
        value=st.session_state.inputs["porcentaje_entrada"],
        key="porcentaje_entrada"
    )
    st.session_state.inputs["coste_reformas"] = col1.number_input(
        "Coste de reformas (€)", 
        min_value=0, 
        step=1000, 
        value=st.session_state.inputs["coste_reformas"],
        key="coste_reformas"
    )
    st.session_state.inputs["comision_agencia"] = col1.number_input(
        "Comisión de agencia (%)", 
        min_value=0.0, 
        max_value=100.0, 
        step=0.1, 
        value=st.session_state.inputs["comision_agencia"],
        key="comision_agencia"
    )
    st.session_state.inputs["seguro_vida"] = col1.number_input(
        "Seguro de vida (€)", 
        min_value=0, 
        step=50, 
        value=st.session_state.inputs["seguro_vida"],
        key="seguro_vida"
    )

    # Loan inputs
    col2.write("**Datos de financiación**")
    st.session_state.inputs["anios"] = col2.number_input(
        "Años del préstamo", 
        min_value=1, 
        step=1, 
        value=st.session_state.inputs["anios"],
        key="anios"
    )
    st.session_state.inputs["tin"] = col2.number_input(
        "Tasa de interés nominal (TIN %) ", 
        min_value=0.0, 
        max_value=100.0, 
        step=0.1, 
        value=st.session_state.inputs["tin"],
        key="tin"
    )
    st.session_state.inputs["tipo_irpf"] = col2.number_input(
        "Tipo de IRPF (%)", 
        min_value=0.0, 
        max_value=100.0, 
        step=0.1, 
        value=st.session_state.inputs["tipo_irpf"],
        key="tipo_irpf"
    )
    st.session_state.inputs["porcentaje_amortizacion"] = col2.number_input(
        "Porcentaje de amortización (%)", 
        min_value=0.0, 
        max_value=100.0, 
        step=0.1, 
        value=st.session_state.inputs["porcentaje_amortizacion"],
        key="porcentaje_amortizacion"
    )

    # Add price reduction checkbox
    if "aplicar_reduccion" not in st.session_state:
        st.session_state.aplicar_reduccion = True
    
    st.session_state.aplicar_reduccion = st.checkbox(
        "Aplicar una reducción del 10% a los precios de compra.",
        value=st.session_state.aplicar_reduccion,
        key="checkbox_reduccion"
    )

    if st.button("Ver resultados", on_click=go_to_results):
        pass
    

elif st.session_state.page == "Resultados":
    st.markdown(
        '<p style="color: #224094; font-size: 18px;">Mostrando hasta <strong>20 resultados por página</strong>, ordenados de mayor a menor rentabilidad bruta. Usa el selector de página para navegar entre los resultados. Haz click en la dirección de la vivienda para ir al anuncio de idealista.</p>',
        unsafe_allow_html=True
    )

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_distritos = st.multiselect(
            "Selecciona uno o más distritos",
            options=data["distrito"].unique(),
            default=data["distrito"].unique()
        )

    with col2:
        precio_min, precio_max = st.slider(
            "Precio (€)",
            int(data["precio"].min()),
            int(data["precio"].max()),
            (int(data["precio"].min()), int(data["precio"].max()))
        )
        metros_min, metros_max = st.slider(
            "Metros cuadrados",
            int(data["tamanio"].min()),
            int(data["tamanio"].max()),
            (int(data["tamanio"].min()), int(data["tamanio"].max()))
        )

    with col3:
        estado_bano = st.slider("Estado del baño (1-5)", 1, 5)
        estado_cocina = st.slider("Estado de la cocina (1-5)", 1, 5)

    # Filter data
    filtered_data = data[
        (data["distrito"].isin(selected_distritos)) &
        (data["tamanio"].between(metros_min, metros_max)) &
        (data["precio"].between(precio_min, precio_max)) &
        (data["puntuacion_banio"] >= estado_bano) &
        (data["puntuacion_cocina"] >= estado_cocina)
    ].dropna(subset=["lat", "lon"])

    # Show total number of results after filtering
    st.write(f"**Total de resultados filtrados:** {len(filtered_data)}")

    if not filtered_data.empty:

        # Apply price reduction if checkbox is checked
        if st.session_state.aplicar_reduccion:
            filtered_data = filtered_data.copy()
            filtered_data['precio'] = filtered_data['precio'] * 0.9

        # Calculate profitability
        resultados_rentabilidad = sr.calcular_rentabilidad_inmobiliaria_wrapper(
            filtered_data,
            **st.session_state.inputs  
        )

        # Pagination setup
        results_per_page = 3
        total_pages = math.ceil(len(filtered_data) / results_per_page)

        # Apply custom styles using Streamlit's internal container system
        st.markdown(
            """
            <style>
                /* Ensure only this specific selectbox is targeted */
                div[data-testid="stSelectbox"] {
                    max-width: 100px !important;  /* Reduce width */
                }

                /* Remove background, border, and shadow */
                div[data-testid="stSelectbox"] > div {
                    background-color: transparent !important;  /* Make background invisible */
                    border: none !important;  /* No borders */
                    box-shadow: none !important;  /* No shadow */
                    padding: 2px 5px !important;  /* Adjust padding */
                }

                /* Keep text readable */
                div[data-testid="stSelectbox"] > div span {
                    color: black !important;  /* Ensure text is visible */
                    font-size: 14px !important;
                }

                /* Remove hover and focus effects */
                div[data-testid="stSelectbox"] > div:hover,
                div[data-testid="stSelectbox"] > div:focus {
                    background-color: transparent !important;
                    border: none !important;
                    outline: none !important;
                    box-shadow: none !important;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Place pagination selector inside a Streamlit container to ensure the styling applies correctly
        with st.container():
            page_number = st.selectbox(
                "Página:",
                options=list(range(1, total_pages + 1)),
                index=0,
                key="pagination_dropdown"
            )
        
        # Calculate indexes for slicing data
        start_idx = (page_number - 1) * results_per_page
        end_idx = start_idx + results_per_page

        # Get paginated data
        paginated_data = resultados_rentabilidad.iloc[start_idx:end_idx]

        for _, row in paginated_data.iterrows():
            image_urls = row["urls_imagenes"] if row["urls_imagenes"] else []
            rentabilidad_bruta = (
                f"{float(row['Rentabilidad Bruta']):.2f}%" 
                if pd.notna(row.get("Rentabilidad Bruta")) 
                else "N/A"
            )
            idealista_url = f"https://www.idealista.com/inmueble/{row['codigo']}/"

            st.markdown(
                f"""
                <div class="card">
                    <div class="card-details">
                        <h3><a href="{idealista_url}" target="_blank" class="custom-title">{row.get('tipo', 'Sin tipo')} en {row.get('direccion', 'Sin dirección')}</a></h3>
                        <p><strong>Distrito:</strong> {row['distrito']}</p>
                        <p><strong>Precio:</strong> {row['precio']}€</p>
                        <p><strong>Tamaño:</strong> {row['tamanio']} m²</p>
                        <p><strong>Habitaciones:</strong> {row['habitaciones']}</p>
                        <p><strong>Rentabilidad Bruta:</strong> {rentabilidad_bruta}</p>
                    </div>
                    <div>
                        <img src="{image_urls[0]}" alt="Imagen de la propiedad">
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Expandable details with carousel and bullets
            with st.expander(f"Más detalles: {row.get('direccion', 'Sin dirección')}"):
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.markdown(
                        f"""
                        - **Precio**: {row['precio']}€
                        - **Tamaño**: {row['tamanio']} m²
                        - **Planta**: {row['planta']}
                        - **Habitaciones**: {row['habitaciones']}
                        - **Baños**: {row['banios']}
                        - **Estado del baño**: {row['puntuacion_banio']}
                        - **Estado de la cocina**: {row['puntuacion_cocina']}
                        - **Alquiler predicho**: {row['alquiler_predicho']}€
                        - **Contacto**: {row['anunciante']}, {row['contacto']}
                        """
                    )

                with col2:
                    if image_urls:
                        render_image_carousel(image_urls)
                
                st.markdown(
                        f"""
                        - **Descripción**: {row['descripcion']}
                        """
                    )

                # Add the profitability metrics table
                st.markdown("**Métricas de rentabilidad**")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Coste Total", f"€{row['Coste Total']:,.0f}")
                    st.metric("Rentabilidad Bruta", f"{row['Rentabilidad Bruta']}%")
                    st.metric("Beneficio Antes de Impuestos", f"€{row['Beneficio Antes de Impuestos']:,.0f}")
                    st.metric("Rentabilidad Neta", f"{row['Rentabilidad Neta']}%")
                    st.metric("Cuota Mensual Hipoteca", f"€{row['Cuota Mensual Hipoteca']:,.0f}")

                with col2:
                    st.metric("Cash Necesario Compra", f"€{row['Cash Necesario Compra']:,.0f}")
                    st.metric("Cash Total Compra y Reforma", f"€{row['Cash Total Compra y Reforma']:,.0f}")
                    st.metric("Beneficio Neto", f"€{row['Beneficio Neto']:,.0f}")
                    st.metric("Cashflow Antes de Impuestos", f"€{row['Cashflow Antes de Impuestos']:,.0f}")
                    st.metric("Cashflow Después de Impuestos", f"€{row['Cashflow Después de Impuestos']:,.0f}")

                with col3:
                    st.metric("ROCE", f"{row['ROCE']}%")
                    st.metric("ROCE (Años)", f"{row['ROCE (Años)']} años")
                    st.metric("Cash-on-Cash Return", f"{row['Cash-on-Cash Return']}%")
                    st.metric("COCR (Años)", f"{row['COCR (Años)']} años")           

        st.markdown("</div>", unsafe_allow_html=True)

        # Show current page and total pages
        st.markdown(f"**Página {page_number} de {total_pages}**")

    else:
        st.write("No hay propiedades que coincidan con los filtros.")


elif st.session_state.page == "Mapa":
    st.markdown('<p style="color: #224094; font-size: 18px;">Configura tus filtros.</p>', unsafe_allow_html=True)

    selected_distritos = st.multiselect("Selecciona los distritos", options=data["distrito"].unique(), default=data["distrito"].unique())

    # Create two columns for the filters
    col1, col2 = st.columns(2)

    with col1:
        precio_min, precio_max = st.slider(
            "Precio (€)",
            int(data["precio"].min()),
            int(data["precio"].max()),
            (int(data["precio"].min()), int(data["precio"].max()))
        )

    with col2:
        metros_min, metros_max = st.slider(
            "Metros cuadrados",
            int(data["tamanio"].min()),
            int(data["tamanio"].max()),
            (int(data["tamanio"].min()), int(data["tamanio"].max()))
        )

    # Filter the data based on selected options
    filtered_data = data[
        (data["distrito"].isin(selected_distritos)) &
        (data["tamanio"].between(metros_min, metros_max)) &
        (data["precio"].between(precio_min, precio_max))
    ].dropna(subset=["lat", "lon"])

    if not filtered_data.empty:
        # Apply price reduction if checkbox is checked
        if st.session_state.aplicar_reduccion:
            filtered_data = filtered_data.copy()
            filtered_data['precio'] = filtered_data['precio'] * 0.9


        # Calculate profitability
        resultados_rentabilidad = sr.calcular_rentabilidad_inmobiliaria_wrapper(
            filtered_data,
            **st.session_state.inputs
        )

        # Base Map Figure
        fig = go.Figure()

        # Add Property Locations
        fig.add_trace(go.Scattermapbox(
            lat=resultados_rentabilidad["lat"],
            lon=resultados_rentabilidad["lon"],
            mode="markers",
            marker=dict(
                size=10,
                symbol="circle",
                color="#3253aa"
            ),
            text=resultados_rentabilidad.apply(lambda row: (
                f"<b><a href='https://www.idealista.com/inmueble/{row['codigo']}/' target='_blank' style='color:#3253aa;'>"
                f"{row['direccion']} (ir a idealista)</a></b><br>"
                f"Precio: {row['precio']}€<br>"
                f"Tamaño: {row['tamanio']} m²<br>"
                f"Habitaciones: {row['habitaciones']}<br>"
                f"Rentabilidad Bruta: {row['Rentabilidad Bruta']:.2f}%<br>"
                f"Alquiler Predicho: {row['alquiler_predicho']}€<br>"
                f"Cuota Mensual Hipoteca: {row['Cuota Mensual Hipoteca']}€"
            ), axis=1),
            hoverinfo="text"
        ))

        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                zoom=11,
                center=dict(
                    lat=resultados_rentabilidad["lat"].mean(),
                    lon=resultados_rentabilidad["lon"].mean()
                )
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            #height=600  # Set fixed height to prevent blank space
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.write("No hay datos para mostrar en el mapa.")


elif st.session_state.page == "Datos Completos":
    st.header("Datos completos con filtros")
    st.markdown('<p style="color: #224094; font-size: 18px;">Los resultados se muestran en orden de Rentabilidad Bruta descendiente.</p>', unsafe_allow_html=True)


    # Dropdown to select districts
    selected_distritos = st.multiselect(
        "Selecciona distritos",
        options=data["distrito"].unique(),
        default=data["distrito"].unique(),
        key="distrito_filtro"
    )

    # Create two columns for filters
    col1, col2 = st.columns(2)

    with col1:
        # Slider for price range
        precio_min, precio_max = st.slider(
            "Precio (€)",
            int(data["precio"].min()), int(data["precio"].max()),
            (int(data["precio"].min()), int(data["precio"].max())),
            key="precio_filtro"
        )

    with col2:
        # Slider for square meters range
        metros_min, metros_max = st.slider(
            "Metros cuadrados",
            int(data["tamanio"].min()), int(data["tamanio"].max()),
            (int(data["tamanio"].min()), int(data["tamanio"].max())),
            key="metros_filtro"
        )

    # Apply filters
    filtered_data = data[
        (data["distrito"].isin(selected_distritos)) &
        (data["tamanio"].between(metros_min, metros_max)) &
        (data["precio"].between(precio_min, precio_max))
    ]

    if not filtered_data.empty:
        # Apply price reduction if checkbox is checked
        if st.session_state.aplicar_reduccion:
            filtered_data = filtered_data.copy()
            filtered_data['precio'] = filtered_data['precio'] * 0.9

        # Run profitability calculations
        resultados_rentabilidad = sr.calcular_rentabilidad_inmobiliaria_wrapper(
            filtered_data,
            **st.session_state.inputs
        )

        # Columns to exclude from selection
        exclude_columns = {"lat", "lon", "urls_imagenes", "url_cocina", "url_banio", "estado", "geometry"}

        # Filter available columns after calculations
        available_columns = [col for col in resultados_rentabilidad.columns if col not in exclude_columns]

        # Column selection for display
        selected_columns = st.multiselect(
            "Selecciona columnas a mostrar",
            options=available_columns,
            default=available_columns,  # Show all allowed columns by default
            key="columnas_filtro"
        )

        # Sort the data by "Rentabilidad Bruta" in descending order
        if "Rentabilidad Bruta" in resultados_rentabilidad.columns:
            resultados_rentabilidad = resultados_rentabilidad.sort_values(by="Rentabilidad Bruta", ascending=False)

        # Display DataFrame with selected columns
        st.dataframe(resultados_rentabilidad[selected_columns])

    else:
        st.write("No hay datos que coincidan con los filtros.")


elif st.session_state.page == "Chatbot":

    load_dotenv()

    OPENAI = os.getenv("OPENAI")
    if not OPENAI:
        raise ValueError("OPENAI no está definido en las variables de entorno")
    client = openai.OpenAI(api_key=OPENAI) 

    if st.session_state.aplicar_reduccion:
        filtered_data = data.copy()
        filtered_data['precio'] = filtered_data['precio'] * 0.9

    # Run profitability calculations
    df = sr.calcular_rentabilidad_inmobiliaria_wrapper(
        filtered_data,
        **st.session_state.inputs
    )

    # Chatbot Functionality (Updated API with structured JSON response)
    def chatbot_query(user_input):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un asistente inmobiliario. Extrae información relevante de la consulta del usuario y devuélvela "
                        "como un JSON con claves exactas que coincidan con las columnas del dataset de propiedades, excluyendo 'urls_imagenes', 'url_cocina', y 'url_banio'. "
                        "El dataset de propiedades contiene las siguientes columnas:\n"
                        "- tipo (Ej: 'piso', 'ático')\n"
                        "- direccion (Ej: 'Calle de Terminillo, 5')\n"
                        "- distrito (Ej: 'Delicias')\n"
                        "- precio (Ej: 150000)\n"
                        "- tamanio (Ej: 80)  # En m²\n"
                        "- habitaciones (Ej: 3)\n"
                        "- banios (Ej: 2)\n"
                        "- ascensor (Ej: True o False)\n"
                        "- terraza (Ej: True o False)\n"
                        "- Rentabilidad Bruta (Ej: 5.4)  # En porcentaje\n"
                        "Si el usuario menciona valores numéricos con comparaciones (ejemplo: 'menos de 50 metros cuadrados'), usa claves como 'tamanio_max': 50. "
                        "Si el usuario menciona valores mínimos (ejemplo: 'más de 2 baños'), usa claves como 'banios_min': 2. "
                        "Si el usuario menciona una calle o dirección específica, usa la clave 'direccion'. "
                        "Ejemplo de respuesta JSON válida:\n"
                        "{ \"tipo\": \"piso\", \"direccion\": \"Calle de Terminillo\", \"tamanio_max\": 50, \"banios_min\": 2 }"
                    )
                },
                {"role": "user", "content": user_input}
            ]
        )

        try:
            structured_response = json.loads(response.choices[0].message.content)

            # Filtrar solo columnas válidas
            valid_fields = [col for col in df.columns if col not in ["urls_imagenes", "url_cocina", "url_banio"]]
            structured_response = {k: v for k, v in structured_response.items() if k in valid_fields}

            if not structured_response:
                structured_response = {"tipo": "piso"}  # Default a "piso"

        except json.JSONDecodeError:
            structured_response = {"tipo": "piso"}  # Fallback case

        return structured_response

    # Property Search Based on Chatbot Output (Optimized for Best Match)
    def find_best_match(criteria):
        filtered_df = df.copy()

        for key, value in criteria.items():
            if key in filtered_df.columns and key not in ["urls_imagenes", "url_cocina", "url_banio"]:
                if isinstance(value, (int, float)):
                    # Handle comparisons (e.g., tamanio_max, banios_min)
                    if "max" in key:
                        column_name = key.replace("_max", "")
                        if column_name in filtered_df.columns:
                            filtered_df = filtered_df[filtered_df[column_name] <= value]
                    elif "min" in key:
                        column_name = key.replace("_min", "")
                        if column_name in filtered_df.columns:
                            filtered_df = filtered_df[filtered_df[column_name] >= value]
                    else:
                        filtered_df = filtered_df[filtered_df[key] == value]

                elif isinstance(value, str):
                    # Allow partial matches for text fields, especially for addresses
                    filtered_df = filtered_df[filtered_df[key].astype(str).str.contains(value, case=False, na=False)]

        # If multiple results, prioritize by price and rentability
        if not filtered_df.empty:
            filtered_df = filtered_df.sort_values(by=["Rentabilidad Bruta", "precio"], ascending=[False, True])
            return filtered_df.iloc[0]  # Return the best match

        return "No se han encontrado viviendas con ese criterio."


    # Display Property Details
    def display_property_details(property_data):
        st.markdown(f"### 🏡 {property_data['tipo'].capitalize()} en {property_data['direccion']}")
        st.markdown(f"🏷️ **Precio**: {property_data['precio']}€")
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

        # Create a Folium map
            m = folium.Map(location=[property_data['lat'], property_data['lon']], zoom_start=15)

            # Add a marker
            folium.Marker(
                [property_data['lat'], property_data['lon']], 
                popup=property_data['direccion']
            ).add_to(m)

            # Display the map in Streamlit
            st_folium(m, height=300)

        # Show basic property info
        st.markdown("### 🏠 Características del Inmueble")

        col1, col2, col3 = st.columns(3)
        col1.write(f"**Tamaño**: {property_data['tamanio']} m²")
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
        col3.metric("Beneficio Neto", f"€{property_data['Beneficio Neto']}")
        
        col4, col5, col6 = st.columns(3)
        col4.metric("ROCE", f"{property_data['ROCE']}%")
        col5.metric("Cash-on-Cash Return", f"{property_data['Cash-on-Cash Return']}%")
        col6.metric("Cashflow Después de Impuestos", f"€{property_data['Cashflow Después de Impuestos']}")
        
        col7, col8, col9 = st.columns(3)
        col7.metric("Cuota Mensual Hipoteca", f"€{property_data['Cuota Mensual Hipoteca']}")
        col8.metric("Cash Necesario Compra", f"€{property_data['Cash Necesario Compra']}")
        col9.metric("Cash Total Compra y Reforma", f"€{property_data['Cash Total Compra y Reforma']}")
        
        col10, col11, col12 = st.columns(3)
        col10.metric("ROCE (Años)", f"{property_data['ROCE (Años)']} años")
        col11.metric("COCR (Años)", f"{property_data['COCR (Años)']} años")
        col12.metric("Alquiler Predicho", f"{property_data['alquiler_predicho']}€")

    # Streamlit Layout
    st.markdown("### 🏡 Encuentra tu vivienda con nuestro chatbot (beta)")
    st.write("Describe la vivienda con las características que estés buscando, y nuestro agente de inteligencia artificial encontrará la coincidencia más cercana.")

    user_query = st.text_input("📝 Ingresa tu búsqueda:", "", key="user_query", help="Ejemplo: Quiero un piso en Delicias con 2 habitaciones y ascensor")
    st.markdown("<style> div[data-testid='stTextInput'] input { font-size: 18px; font-weight: bold; padding: 10px; } </style>", unsafe_allow_html=True)

    if user_query:
        chat_response = chatbot_query(user_query)
        best_property = find_best_match(chat_response)

        if isinstance(best_property, str):
            st.write(best_property)
        else:
            display_property_details(best_property)


elif st.session_state.page == "Información de Soporte":

    stxt.imprimir_metricas()