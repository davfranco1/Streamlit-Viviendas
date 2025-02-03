import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import ast
import math
import time
from datetime import datetime

import sys
sys.path.append("../src")

import src.soporte_rentabilidad as sr
import src.soporte_mongo as sm
import src.soporte_texto as stxt
import src.soporte_chatbot as sc
import src.soporte_styles as ss
import src.soporte_pdf as spdf


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
st.markdown(ss.styles, unsafe_allow_html=True)

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


if 'page' not in st.session_state:
    st.session_state.page = "Datos de compra y financiación"

if "inputs" not in st.session_state:
    st.session_state.inputs = {
        "porcentaje_entrada": 20.0,
        "coste_reformas": 5000,
        "comision_agencia": 3.0,
        "anios": 30,
        "tin": 3.0,
        "seguro_vida": 250,
        "tipo_irpf": 17.0,
        "porcentaje_amortizacion": 40.0,
    }

def handle_nav_change():
    st.session_state.page = st.session_state.navigation

def go_to_results():
    with st.spinner("Cargando resultados..."):  # Display spinner for 2 seconds
        time.sleep(2)
    st.session_state.page = "Resultados"


# Center the image in the sidebar using HTML & CSS
with st.sidebar:
    st.image("images/logo_transparent-glow.png")

    # Navigation
    st.sidebar.radio(
        "Navegación",
        ["Datos de compra y financiación", "Resultados", "Mapa", "Housebot", "Datos Completos", "Información de Soporte"],
        key="navigation",
        on_change=handle_nav_change,
        index=["Datos de compra y financiación", "Resultados", "Mapa", "Housebot", "Datos Completos", "Información de Soporte"].index(st.session_state.page)
    )

    st.markdown(
    """
    <style>
    .centered-text {
        text-align: center;
        font-family: 'Georgia', sans-serif;
        font-size: 16px;
        font-weight: normal;
        font-style: italic;
        color: #cfe2f3; /* Change color if needed */
    }
    </style>
    <p class="centered-text">Análisis inteligente para maximizar tu inversión.</p>
    """,
    unsafe_allow_html=True
    )


data = load_data()

# Ensure required columns exist in data
required_columns = ["distrito", "tamanio", "precio", "puntuacion_banio", "puntuacion_cocina", "habitaciones", "urls_imagenes", "codigo"]
for col in required_columns:
    if col not in data.columns:
        st.error(f"Missing column: {col}. Please check your dataset.")
        st.stop()


# Create layout with two columns
col1, col2 = st.columns([5, 1])  # Left side (text) is wider than the right side (image)

with col1:
    st.markdown("""
    <div class="title-main">Calculadora de Rentabilidad Inmobiliaria / ZGZ</div>
    """, unsafe_allow_html=True)

#<div class="title-sub">Zaragoza</div>

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

def update_input(key):
    st.session_state.inputs[key] = st.session_state[f"{key}_input"]


@st.cache_data(ttl=3600)  # Cache for 1 hour
def process_housebot_data(_data, aplicar_reduccion, reduccion_porcentaje, inputs):
    if aplicar_reduccion:
        filtered_data = _data.copy()
        filtered_data['precio'] = filtered_data['precio'] * (1 - reduccion_porcentaje / 100)
    else:
        filtered_data = _data.copy()
    
    return sr.calcular_rentabilidad_inmobiliaria_wrapper(
        filtered_data,
        **inputs
    )

if st.session_state.page == "Datos de compra y financiación":
    st.markdown("""<p style="color: #224094; font-size: 18px;">• Puedes conocer la descripción de cada parámetro deslizando sobre la ❓</p>""",
      unsafe_allow_html=True)

    # Create two columns
    col1, col2 = st.columns(2)

    # General inputs
    col1.write("**Datos generales**")

    # Example implementation
    st.session_state.inputs["porcentaje_entrada"] = col1.number_input(
        "Porcentaje de entrada (%)", 
        min_value=0.0, 
        max_value=100.0, 
        step=0.1, 
        value=st.session_state.inputs["porcentaje_entrada"],
        key=f"porcentaje_entrada_input",
        on_change=update_input,
        args=("porcentaje_entrada",),
        help=stxt.entrada
    )
    st.session_state.inputs["coste_reformas"] = col1.number_input(
        "Coste de reformas (€)", 
        min_value=0, 
        max_value=100000,
        value=st.session_state.inputs["coste_reformas"],
        key=f"coste_reformas_input",
        on_change=update_input,
        args=("coste_reformas",),
        help= stxt.reformas
    )
    st.session_state.inputs["comision_agencia"] = col1.number_input(
        "Comisión de agencia (%)", 
        min_value=0.0, 
        max_value=100.0, 
        step=0.1, 
        value=st.session_state.inputs["comision_agencia"],
        key=f"comision_agencia_input",
        on_change=update_input,
        args=("comision_agencia",),
        help= stxt.agencia
    )
    st.session_state.inputs["seguro_vida"] = col1.number_input(
        "Seguro de vida anual (€)", 
        min_value=0, 
        max_value=1000, 
        value=st.session_state.inputs["seguro_vida"],
        key=f"seguro_vida_input",
        on_change=update_input,
        args=("seguro_vida",),
        help= stxt.segurovida
    )

    # Loan inputs
    col2.write("**Datos de financiación**")
    st.session_state.inputs["anios"] = col2.number_input(
        "Años del préstamo", 
        min_value=1,
        max_value=40,
        step=1, 
        value=st.session_state.inputs["anios"],
        key=f"anios_input",
        on_change=update_input,
        args=("anios",),
        help= stxt.plazo
    )
    st.session_state.inputs["tin"] = col2.number_input(
        "Tasa de interés nominal (TIN %) ", 
        min_value=0.0, 
        max_value=100.0, 
        step=0.1, 
        value=st.session_state.inputs["tin"],
        key=f"tin_input",
        on_change=update_input,
        args=("tin",),
        help= stxt.tin
    )
    st.session_state.inputs["tipo_irpf"] = col2.number_input(
        "Tipo de IRPF (%)", 
        min_value=0.0, 
        max_value=100.0, 
        step=0.1, 
        value=st.session_state.inputs["tipo_irpf"],
        key=f"tipo_irpf_input",
        on_change=update_input,
        args=("tipo_irpf",),
        help= stxt.irpf
    )
    st.session_state.inputs["porcentaje_amortizacion"] = col2.number_input(
        "Porcentaje de amortización (%)", 
        min_value=0.0, 
        max_value=100.0, 
        step=0.1, 
        value=st.session_state.inputs["porcentaje_amortizacion"],
        key=f"porcentaje_amortizacion_input",
        on_change=update_input,
        args=("porcentaje_amortizacion",),
        help= stxt.amortizacion
    )

    def update_reduction_checkbox():
        st.session_state.aplicar_reduccion = st.session_state.checkbox_reduccion
        if not st.session_state.aplicar_reduccion:
            st.session_state.reduccion_porcentaje = 0

    col1, col2 = st.columns(2)
    with col1:
        # Initialize if not exists
        if "aplicar_reduccion" not in st.session_state:
            st.session_state.aplicar_reduccion = True
        
        # Checkbox with on_change callback
        st.checkbox(
            "Aplicar una reducción a los precios de compra.",
            value=st.session_state.aplicar_reduccion,
            key="checkbox_reduccion",
            on_change=update_reduction_checkbox,
            help="De media, en España, una vivienda suele venderse entre un 10 y 15% por debajo del precio publicado. Para que los cálculos de rentabilidad reflejen esta casuística, esta casilla se encuentra marcada por defecto."
        )

    with col2:
        # Slider to select the reduction percentage (visible only if checkbox is checked)
        if st.session_state.aplicar_reduccion:
            st.session_state.reduccion_porcentaje = st.slider(
                "Seleccione el porcentaje de reducción:",
                min_value=5, max_value=20, value=10, step=1,
                key="slider_reduccion",
                help="Selecciona el porcentaje de reducción a aplicar al precio de compra."
            )
        else:
            st.session_state.reduccion_porcentaje = 0  # No reduction if checkbox is unchecked

    # Display the selected reduction percentage
    st.write(f"Se aplicará una reducción del {st.session_state.reduccion_porcentaje}% al precio de compra.")

    st.markdown("""<p style="color: #224094; font-size: 14px;">‣ Los resultados son estimaciones, y nunca deben considerarse consejos de inversión. Antes de invertir, asegúrese de <strong>consultar con un experto</strong>.</p>""",
    unsafe_allow_html=True)

    # Centering the button using Markdown with CSS
    st.markdown(
        """
        <style>
        div.stButton > button {
            background-color: #170058 !important;
            color: white !important;
            border-radius: 10px;
            padding: 15px 30px;
            font-size: 18px;
            font-weight: bold;
            border: none;
            cursor: pointer;
        }
        div.stButton > button:hover {
            background-color: #2a007a !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Create a centered container for the button
    col1, col2, col3 = st.columns([1, 1, 1])  # Adjust column sizes for centering

    with col2:
        if st.button("Ver resultados", on_click=go_to_results):
            pass
    

elif st.session_state.page == "Resultados":
    st.markdown(
        '<p style="color: #224094; font-size: 18px;">• Mostrando hasta <strong>20 resultados por página</strong>, ordenados de mayor a menor rentabilidad bruta.</p>',
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
            (int(data["precio"].min()), int(data["precio"].max())),
            help="Filtro sobre el precio original, sin reducciones."
        )
        metros_min, metros_max = st.slider(
            "Metros cuadrados",
            int(data["tamanio"].min()),
            int(data["tamanio"].max()),
            (int(data["tamanio"].min()), int(data["tamanio"].max()))
        )

    with col3:
        estado_bano_min, estado_bano_max = st.slider("Estado del baño (entre 1 y 5)", 1, 5, (1, 5), help="Siendo 1 muy malo y 5 perfecto estado.")
        estado_cocina_min, estado_cocina_max = st.slider("Estado de la cocina (entre 1 y 5)", 1, 5, (1, 5), help="Siendo 1 muy malo y 5 perfecto estado.")

    # Filter data
    filtered_data = data[
        (data["distrito"].isin(selected_distritos)) &
        (data["tamanio"].between(metros_min, metros_max)) &
        (data["precio"].between(precio_min, precio_max)) &
        (data["puntuacion_banio"].between(estado_bano_min, estado_bano_max)) &
        (data["puntuacion_cocina"].between(estado_cocina_min, estado_cocina_max))
    ].dropna(subset=["lat", "lon"])

    # Show total number of results after filtering
    st.write(f"**Total de resultados filtrados:** {len(filtered_data)}")

    if not filtered_data.empty:

        # Apply price reduction if checkbox is checked
        if st.session_state.aplicar_reduccion:
            filtered_data = filtered_data.copy()  # Ensure we're not modifying the original data
            filtered_data['precio'] = filtered_data['precio'] * (1 - st.session_state.reduccion_porcentaje / 100)

        # Calculate profitability
        resultados_rentabilidad = sr.calcular_rentabilidad_inmobiliaria_wrapper(
            filtered_data,
            **st.session_state.inputs  
        )

        # Pagination setup
        results_per_page = 3
        total_pages = math.ceil(len(filtered_data) / results_per_page)

        # Apply custom styles using Streamlit's internal container system
        st.markdown(ss.card_styles, unsafe_allow_html=True)

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
                        <p><strong>Precio:</strong> {row['precio']:,.0f} €</p>
                        <p><strong>Tamaño:</strong> {row['tamanio']:,.0f} m²</p>
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
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.markdown(
                        f"""
                        - **Precio**: {row['precio']:,.0f} €
                        - **Tamaño**: {row['tamanio']:,.0f} m²
                        - **Planta**: {row['planta']}
                        - **Habitaciones**: {row['habitaciones']}
                        - **Baños**: {row['banios']}
                        - **Estado del baño**: {row['puntuacion_banio']}
                        - **Estado de la cocina**: {row['puntuacion_cocina']}
                        - **Alquiler predicho**: {row['alquiler_predicho']:,.0f} €
                        - **Anunciante**: {row['anunciante']}
                        - **Teléfono**: {row['contacto']}
                        """
                    )

                with col2:
                    if image_urls:
                        sc.render_image_carousel(image_urls)
                
                st.markdown(
                        f"""
                        - **Descripción**: {row['descripcion']}
                        """
                    )

                # Add the profitability metrics table
                st.markdown("**Métricas de rentabilidad**")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Coste Total", f"{row['Coste Total']:,.0f} €")
                    st.metric("Rentabilidad Bruta", f"{row['Rentabilidad Bruta']}%")
                    st.metric("Beneficio Antes de Impuestos", f"{row['Beneficio Antes de Impuestos']:,.0f} €")
                    st.metric("Rentabilidad Neta", f"{row['Rentabilidad Neta']}%")
                    st.metric("Cuota Mensual Hipoteca", f"{row['Cuota Mensual Hipoteca']:,.0f} €")

                with col2:
                    st.metric("Cash Necesario Compra", f"{row['Cash Necesario Compra']:,.0f} €")
                    st.metric("Cash Total Compra y Reforma", f"{row['Cash Total Compra y Reforma']:,.0f} €")
                    st.metric("Beneficio Neto", f"{row['Beneficio Neto']:,.0f} €")
                    st.metric("Cashflow Antes de Impuestos", f"{row['Cashflow Antes de Impuestos']:,.0f} €")
                    st.metric("Cashflow Después de Impuestos", f"{row['Cashflow Después de Impuestos']:,.0f} €")

                with col3:
                    st.metric("ROCE", f"{row['ROCE']}%")
                    st.metric("ROCE (Años)", f"{row['ROCE (Años)']:,.0f} años")
                    st.metric("Cash-on-Cash Return", f"{row['Cash-on-Cash Return']}%")
                    st.metric("COCR (Años)", f"{row['COCR (Años)']:,.0f} años")           
                
                st.markdown("  \n")

                col1, col2, col3 = st.columns(3)
                with col1:
                    # Generate PDF and provide download button
                    pdf_buffer = spdf.generate_pdf(row)
                    st.download_button(
                    label="📄 Descargar informe en PDF",
                    data=pdf_buffer,
                    file_name=f"detalles_vivienda_{row['direccion'].replace(' ', '_')}.pdf",  # Unique file name
                    mime="application/pdf",
                    key=f"download_pdf_{row['direccion']}"  # Unique key based on address
                    )

                with col2:
                    st.link_button("🔗 Ver en Idealista", url=idealista_url)

                with col3:
                    current_time = datetime.now().strftime("%d %b, %Y | %H:%M")
                    st.write(f'<span style="color: grey;">📅 Fecha consulta: {current_time}</span>', unsafe_allow_html=True)
                

        st.markdown("</div>", unsafe_allow_html=True)

        # Show current page and total pages
        st.markdown(f"**Página {page_number} de {total_pages}**")

    else:
        st.write("No hay propiedades que coincidan con los filtros.")


elif st.session_state.page == "Mapa":

    selected_distritos = st.multiselect("Selecciona los distritos", options=data["distrito"].unique(), default=data["distrito"].unique())

    # Create two columns for the filters
    col1, col2 = st.columns(2)

    with col1:
        precio_min, precio_max = st.slider(
            "Precio (€)",
            int(data["precio"].min()),
            int(data["precio"].max()),
            (int(data["precio"].min()), int(data["precio"].max())),
            help="Filtro sobre el precio original, sin reducciones."
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
            filtered_data = filtered_data.copy()  # Ensure we're not modifying the original data
            filtered_data['precio'] = filtered_data['precio'] * (1 - st.session_state.reduccion_porcentaje / 100)


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
                f"Precio: {row['precio']:,.0f} €<br>"
                f"Tamaño: {row['tamanio']} m²<br>"
                f"Habitaciones y baños: {row['habitaciones']} y {row['banios']}<br>"
                f"Rentabilidad Bruta: {row['Rentabilidad Bruta']:.2f}%<br>"
                f"Alquiler Predicho: {row['alquiler_predicho']:,.0f} €<br>"
                f"Cuota Mensual Hipoteca: {row['Cuota Mensual Hipoteca']:,.0f} €"
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


elif st.session_state.page == "Housebot":
    # Initialize state variables if not exist
    if 'housebot_df' not in st.session_state:
        st.session_state.housebot_df = process_housebot_data(
            data, 
            st.session_state.aplicar_reduccion, 
            st.session_state.reduccion_porcentaje, 
            st.session_state.inputs
        )
    
    # Initialize query result state
    if 'query_result' not in st.session_state:
        st.session_state.query_result = None

    # Streamlit Layout
    st.markdown("### 🏡 Encuentra tu vivienda con nuestro housebot (beta)")
    st.write("• Describe la vivienda con las características que estés buscando, y nuestro agente de inteligencia artificial encontrará la coincidencia más cercana.")
    
    user_query = st.text_input("📝 *¿Qué estás buscando?*", "", key="user_query", help="Ejemplo: Quiero un piso en Delicias con 2 habitaciones y ascensor")
    st.markdown("<style> div[data-testid='stTextInput'] input { font-size: 18px; font-weight: bold; padding: 10px; } </style>", unsafe_allow_html=True)
    
    if user_query:
        # Only process if query has changed
        if st.session_state.query_result is None or user_query != st.session_state.last_query:
            st.session_state.last_query = user_query
            chat_response = sc.chatbot_query(st.session_state.housebot_df, user_query)
            best_property = sc.find_best_match(st.session_state.housebot_df, chat_response)
            
            if isinstance(best_property, str):
                st.session_state.query_result = best_property
            else:
                st.session_state.query_result = best_property
        
        # Display the result
        if isinstance(st.session_state.query_result, str):
            st.write(st.session_state.query_result)
        else:
            sc.display_property_details(st.session_state.query_result)


elif st.session_state.page == "Datos Completos":
    st.header("Datos completos")
    st.markdown(
        '<p style="color: #224094; font-size: 18px;">• Usa los filtros para configurar la búsqueda.<br>'
        '• Los resultados se muestran en orden de Rentabilidad Bruta descendiente.</p>',
        unsafe_allow_html=True
    )

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
            key="precio_filtro",
            help="Filtro sobre el precio original, sin reducciones."
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
            filtered_data["precio"] = filtered_data["precio"] * (1 - st.session_state.reduccion_porcentaje / 100)

        # Run profitability calculations
        resultados_rentabilidad = sr.calcular_rentabilidad_inmobiliaria_wrapper(
            filtered_data,
            **st.session_state.inputs
        )

        # Columns to exclude from selection
        exclude_columns = {"lat", "lon", "urls_imagenes", "url_cocina", "url_banio", "estado", "geometry"}

        # Filter available columns after calculations
        available_columns = [col for col in resultados_rentabilidad.columns if col not in exclude_columns]

        # Default columns to show
        default_columns = ["distrito", "direccion", "tipo", "precio", "tamanio", "habitaciones", "banios", "Rentabilidad Bruta"]
        
        # Ensure only existing columns are selected
        default_columns = [col for col in default_columns if col in available_columns]

        # Column selection for display
        selected_columns = st.multiselect(
            "Añade o elimina las columnas a mostrar. Puedes escribir el nombre o utilizar el desplegable.",
            options=available_columns,
            default=default_columns,  # Show only key columns by default
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

    stxt.imprimir_metricas()