import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import ast
import math

import sys
sys.path.append("../src")

import src.soporte_rentabilidad as sr
import src.soporte_mongo as sm

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
    .stSelectbox, .stNumberInput, .stSlider, .stRadio {
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
    st.image("images/logo_transparent.png")

    # Navigation
    st.sidebar.radio(
        "Navegación",
        ["Datos de compra y financiación", "Resultados", "Mapa", "Datos Completos", "Información de Soporte"],
        key="navigation",
        on_change=handle_nav_change,
        index=["Datos de compra y financiación", "Resultados", "Mapa", "Datos Completos", "Información de Soporte"].index(st.session_state.page)
    )


data = load_data()

# Ensure required columns exist in data
required_columns = ["distrito", "tamanio", "precio", "puntuacion_banio", "puntuacion_cocina", "habitaciones", "urls_imagenes", "codigo"]
for col in required_columns:
    if col not in data.columns:
        st.error(f"Missing column: {col}. Please check your dataset.")
        st.stop()


# Streamlit app title
# Custom CSS to style the horizontal line
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
        '<p style="color: #224094; font-size: 18px;">Mostrando hasta <strong>20 resultados por página</strong> de tu consulta, ordenados de mayor a menor rentabilidad bruta. Usa el selector de página para navegar entre los resultados. Clica en la dirección de la vivienda para ir al anuncio de idealista.</p>',
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
                        <h3><a href="{idealista_url}" target="_blank" class="custom-title">{row.get('direccion', 'Sin dirección')}</a></h3>
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
                        - **Habitaciones y baños**: {row['habitaciones']} y {row['banios']}. 
                        - **Estado del baño**: {row['puntuacion_banio']}
                        - **Estado de la cocina**: {row['puntuacion_cocina']}
                        - **Alquiler predicho**: {row['alquiler_predicho']}
                        - **Cuota de la hipoteca**: {row['Cuota Mensual Hipoteca']}€
                        - **Período de recuperación (ROCE)**: {row['ROCE (Años)']} años
                        - **Contacto**: {row['anunciante']}, {row['contacto']}
                        """
                    )

                with col2:
                    # Image carousel
                    if image_urls:
                        render_image_carousel(image_urls)
                
                st.markdown(
                        f"""
                        - **Descripción**: {row['descripcion']}
                        """
                    )


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
                f"<b>{row['direccion']}</b><br>"
                f"Precio: {row['precio']}€<br>"
                f"Tamaño: {row['tamanio']} m²<br>"
                f"Habitaciones: {row['habitaciones']}<br>"
                f"Rentabilidad Bruta: {row['Rentabilidad Bruta']:.2f}%<br>"
                f"Alquiler Predicho: {row['alquiler_predicho']}€<br>"
                f"Cuota Mensual Hipoteca: {row['Cuota Mensual Hipoteca']}€"
            ), axis=1),
            hoverinfo="text"
        ))

        # 📌 Set Proper Layout (Fix Blank Space Issue)
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


elif st.session_state.page == "Información de Soporte":

    st.header("Métricas Financieras para Inversión en Vivienda")

    st.markdown("### Métricas Básicas")
    st.write("""
    - **Coste Total**: Suma total de todos los gastos relacionados con la adquisición de la vivienda, incluyendo el precio de compra, reformas, comisiones, impuestos y gastos notariales.
    
    - **Cash Necesario Compra**: Cantidad de dinero efectivo necesario para realizar la compra, incluyendo la entrada, comisiones, gastos notariales e impuestos.
    
    - **Cash Total Compra y Reforma**: Total de efectivo necesario incluyendo tanto los gastos de compra como los de reforma.
    """)

    st.markdown("### Métricas de Rentabilidad")
    st.write("""
    - **Rentabilidad Bruta**: Porcentaje que representa los ingresos anuales por alquiler respecto al coste total de la inversión, sin considerar gastos ni impuestos.
    
    - **Rentabilidad Neta**: Porcentaje que representa el beneficio neto anual (después de todos los gastos e impuestos) respecto al coste total de la inversión.
    
    - **Beneficio Antes de Impuestos**: Ingresos por alquiler menos todos los gastos operativos y financieros, antes de aplicar impuestos.
    
    - **Beneficio Neto**: Beneficio final después de considerar todos los gastos e impuestos.
    """)

    st.markdown("### Métricas de Flujo de Caja")
    st.write("""
    - **Cashflow Antes de Impuestos**: Beneficio antes de impuestos menos el pago anual del principal de la hipoteca.
    
    - **Cashflow Después de Impuestos**: Beneficio neto menos el pago anual del principal de la hipoteca.
    """)

    st.markdown("### Métricas de Retorno de Inversión")
    st.write("""
    - **ROCE (Return on Capital Employed)**: Porcentaje que representa los ingresos anuales respecto al capital total invertido. Mide la eficiencia con la que se utiliza el capital invertido.
    
    - **ROCE Años**: Tiempo estimado en años para recuperar el capital invertido basado en el ROCE.
    
    - **Cash-on-Cash Return (COCR)**: Porcentaje que representa el flujo de caja después de impuestos respecto al capital total invertido. Mide el rendimiento efectivo anual de la inversión.
    
    - **COCR Años**: Tiempo estimado en años para recuperar la inversión inicial basado en el flujo de caja después de impuestos.
    """)

    st.markdown("### Costes Operativos")
    st.write("""
    - **Seguro Impago**: Seguro que cubre el riesgo de impago por parte del inquilino (4% de los ingresos anuales).
    
    - **Seguro Hogar**: Seguro obligatorio que cubre daños en la vivienda (coste fijo anual).
    
    - **IBI (Impuesto sobre Bienes Inmuebles)**: Impuesto municipal anual sobre la propiedad (0.4047% del valor catastral).
    
    - **Mantenimiento y Comunidad**: Gastos estimados para el mantenimiento del inmueble y cuotas de comunidad (10% de los ingresos anuales).
    
    - **Periodos Vacíos**: Provisión para períodos sin inquilinos (5% de los ingresos anuales).
    """)

    st.markdown("### Aspectos Fiscales")
    st.write("""
    - **Base Amortización**: Valor sobre el que se calcula la amortización anual, incluyendo el precio de compra y otros gastos asociados.
    
    - **Amortización Anual**: Desgaste teórico anual del inmueble que puede deducirse fiscalmente (3% de la base de amortización).
    
    - **Deducción Larga Duración**: Reducción fiscal aplicable al beneficio menos la amortización (60% del resultado).
    
    - **IRPF**: Impuesto sobre la Renta aplicado a la base imponible después de deducciones.
    """)

    st.markdown("### 1. Costes Iniciales")
    st.write("Cálculo de los costes iniciales y necesidades de efectivo.")
    st.latex(r"""
    \begin{aligned}
    \text{ITP} &= \text{Precio Compra} \times \text{Tasa ITP} \\
    \text{Coste Notario} &= \text{Precio Compra} \times \text{Tasa Notario} \\
    \text{Coste Total} &= \text{Precio Compra} + \text{Coste Reformas} + \text{Comisión Agencia} + \text{Coste Notario} + \text{ITP} \\
    \text{Pago Entrada} &= \text{Porcentaje Entrada} \times \text{Precio Compra} \\
    \text{Cash Necesario Compra} &= \text{Pago Entrada} + \text{Comisión Agencia} + \text{Coste Notario} + \text{ITP} \\
    \text{Cash Total Compra y Reforma} &= \text{Pago Entrada} + \text{Coste Reformas} + \text{Coste Notario} + \text{ITP}
    \end{aligned}
    """)

    st.markdown("### 2. Costes Operativos Anuales")
    st.write("Cálculo de los gastos operativos anuales del inmueble.")
    st.latex(r"""
    \begin{aligned}
    \text{Seguro Impago} &= \text{Tasa Seguro Impago} \times \text{Ingresos Anuales} \\
    \text{Seguro Hogar} &= \text{CONST\_SEGURO\_HOGAR} \\
    \text{IBI} &= \text{Precio Vivienda} \times \text{Tasa IBI} \\
    \text{Impuesto Basuras} &= \text{CONST\_IMPUESTO\_BASURAS} \\
    \text{Mantenimiento y Comunidad} &= \text{Tasa Mantenimiento} \times \text{Ingresos Anuales} \\
    \text{Periodos Vacíos} &= \text{Tasa Periodos Vacíos} \times \text{Ingresos Anuales}
    \end{aligned}
    """)

    st.markdown("### 3. Cálculos Hipotecarios")
    st.write("Cálculos relacionados con la hipoteca y sus pagos.")
    st.latex(r"""
    \begin{aligned}
    \text{Monto Préstamo} &= \text{Precio Compra} \times (1 - \text{Porcentaje Entrada}) \\
    \text{Hipoteca Mensual} &= \text{PMT}(\text{TIN}/12, \text{Años} \times 12, \text{Monto Préstamo}) \\
    \text{Total Pagado} &= \text{Hipoteca Mensual} \times (\text{Años} \times 12) \\
    \text{Interés Total} &= \text{Total Pagado} - \text{Monto Préstamo} \\
    \text{Capital Anual} &= \text{Monto Préstamo}/\text{Años} \\
    \text{Capital Mensual} &= \text{Capital Anual}/12 \\
    \text{Interés Anual} &= \text{Interés Total}/\text{Años}
    \end{aligned}
    """)

    st.markdown("### 4. Cálculo del Beneficio")
    st.write("Cálculo del beneficio antes de impuestos.")
    st.latex(r"""
    \begin{aligned}
    \text{Beneficio Antes de Impuestos} &= \text{Ingresos Anuales} - \text{Seguro Impago} - \text{Seguro Hogar} \\
    &- \text{Seguro Vida} - \text{IBI} - \text{Impuesto Basuras} \\
    &- \text{Mantenimiento y Comunidad} - \text{Periodos Vacíos} \\
    &- \text{Intereses Hipoteca}
    \end{aligned}
    """)

    st.markdown("### 5. Cálculos Fiscales")
    st.write("Cálculos relacionados con impuestos y deducciones.")
    st.latex(r"""
    \begin{aligned}
    \text{Base Amortización} &= \text{Porcentaje Amortización} \times \text{Precio Compra} + \\
    &(\text{Coste Reformas} + \text{Comisión Agencia} + \text{Coste Notario} + \text{ITP}) \\
    \text{Amortización Anual} &= \text{Tasa Amortización} \times \text{Base Amortización} \\
    \text{Deducción Larga Duración} &= (\text{Beneficio Antes de Impuestos} - \text{Amortización Anual}) \times \text{Tasa Deducción} \\
    \text{IRPF} &= -(\text{Deducción Larga Duración} \times \text{Tipo IRPF}) \\
    \text{Beneficio Neto} &= \text{Beneficio Antes de Impuestos} + \text{IRPF}
    \end{aligned}
    """)

    st.markdown("### 6. Métricas de Rentabilidad")
    st.write("Cálculo de las principales métricas de rentabilidad.")
    st.latex(r"""
    \begin{aligned}
    \text{Rentabilidad Bruta} &= \frac{\text{Ingresos Anuales}}{\text{Coste Total}} \times 100 \\
    \text{Rentabilidad Neta} &= \frac{\text{Beneficio Neto}}{\text{Coste Total}} \times 100 \\
    \text{Cashflow Antes de Impuestos} &= \text{Beneficio Antes de Impuestos} - \text{Capital Anual} \\
    \text{Cashflow Después de Impuestos} &= \text{Beneficio Neto} - \text{Capital Anual}
    \end{aligned}
    """)

    st.markdown("### 7. Métricas de Retorno de Inversión")
    st.write("Cálculo de métricas ROI y años de recuperación.")
    st.latex(r"""
    \begin{aligned}
    \text{Inversión Inicial} &= \text{Pago Entrada} + \text{Coste Reformas} + \text{Comisión Agencia} + \text{Coste Notario} + \text{ITP} \\
    \text{ROCE} &= \frac{\text{Ingresos Anuales}}{\text{Inversión Inicial}} \times 100 \\
    \text{ROCE Años} &= \frac{\text{Pago Entrada}}{\text{Pago Entrada} \times \text{ROCE}} \times 100 \\
    \text{COCR} &= \frac{\text{Cashflow Después de Impuestos}}{\text{Inversión Inicial}} \times 100 \\
    \text{COCR Años} &= \frac{\text{Inversión Inicial}}{\text{Cashflow Después de Impuestos}}
    \end{aligned}
    """)
    
    st.markdown("### Valores Constantes en el Cálculo")
    st.write("Algunos valores utilizados en los cálculos tienen montos fijos:")
    st.write("- Impuesto de Basuras Ayuntamiento Zaragoza: 283€")
    st.write("- Seguro de Hogar: 176.29€. Fuente: https://selectra.es/seguros/seguros-hogar/precios-seguros-hogar")
    st.write("- Seguro de Impago: 4% del ingreso anual")
    st.write("- Mantenimiento y Comunidad: 10% del ingreso anual. Fuente: https://www.donpiso.com/blog/mantener-piso-vacio-cuesta-2-300-euros-al-ano/")
    st.write("- Periodos Vacíos: 5% del ingreso anual")
    st.write("- IBI Ayuntamiento Zaragoza: 0.4047% del precio de compra")
    st.write("- Coste Notario: 2% del precio de compra")
    st.write("- ITP Zaragoza: 8% del precio de compra")
    st.write("- Tasa de Deducción por Larga Duración: 60%")
    st.write("- Tasa de Amortización: 3%")
