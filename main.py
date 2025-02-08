import sys
import math
import time
import ast
from datetime import datetime

import pandas as pd
import re
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
from streamlit_javascript import st_javascript

# Append local modules path and import custom modules
sys.path.append("../src")
import src.soporte_rentabilidad as sr
import src.soporte_mongo as sm
import src.soporte_texto as stxt
import src.soporte_chatbot as sc
import src.soporte_styles as ss
import src.soporte_pdf as spdf

# -------------------------------------------------------------------
# Page configuration and theme options
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Las Casas de David: Calculadora de Rentabilidad Inmobiliaria",
    page_icon="🏡",
    layout="wide"
)

st.config.set_option("theme.base", "light")
st.config.set_option("theme.primaryColor", "#170058")
st.config.set_option("theme.backgroundColor", "#EFEFEF")
st.config.set_option("theme.secondaryBackgroundColor", "#EFEFEF")
st.config.set_option("theme.textColor", "#00185E")
st.config.set_option("theme.font", "sans serif")

# Add custom styles
st.markdown(ss.styles, unsafe_allow_html=True)

# -------------------------------------------------------------------
# Setup: MongoDB connection and presets
# -------------------------------------------------------------------
bd = sm.conectar_a_mongo("ProyectoRentabilidad")
PRESETS = stxt.PRESETS

# -------------------------------------------------------------------
# Utility functions and callbacks
# -------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        data = sm.importar_a_geodataframe(bd, "ventafinal")
        if "geometry" in data.columns:
            data["lat"] = data["geometry"].apply(lambda x: x.y if hasattr(x, "y") else None)
            data["lon"] = data["geometry"].apply(lambda x: x.x if hasattr(x, "x") else None)
        if "urls_imagenes" in data.columns:
            data["urls_imagenes"] = data["urls_imagenes"].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else x
            )
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def is_mobile():
    # Get user agent string
    user_agent = st_javascript("navigator.userAgent")  

    # Ensure it's a string before running regex
    if not isinstance(user_agent, str):
        return False  # Default to False if the value is unexpected

    # Check if user agent contains mobile keywords
    mobile_pattern = re.compile(r"Mobile|Android|iPhone|iPad|iPod", re.IGNORECASE)
    return bool(mobile_pattern.search(user_agent))

def render_top_nav():
    if is_mobile():
        st.image("images/mobile_logo.png")

    else: 
        st.markdown(
            f"""
            <div class="top-nav">
                <div class="title-main">Calculadora de Rentabilidad Inmobiliaria / ZGZ</div>
                <div class="top-nav-logo">
                    <img src="https://raw.githubusercontent.com/davfranco1/Streamlit-Viviendas/refs/heads/main/images/zaragoza.png" alt="Logo">
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

def handle_tipo_vivienda_change():
    apply_preset(st.session_state.tipo_vivienda_radio)
    st.session_state.tipo_vivienda = st.session_state.tipo_vivienda_radio

def apply_preset(preset_name):
    if preset_name in PRESETS:
        st.session_state.inputs.update(PRESETS[preset_name])
        for key in PRESETS[preset_name]:
            st.session_state[f"{key}_input"] = PRESETS[preset_name][key]

def update_input(key):
    st.session_state.inputs[key] = st.session_state[f"{key}_input"]

def process_housebot_data(_data, aplicar_reduccion, reduccion_porcentaje, inputs):
    filtered_data = _data.copy()
    if aplicar_reduccion:
        filtered_data["precio"] = filtered_data["precio"] * (1 - reduccion_porcentaje / 100)
    return sr.calcular_rentabilidad_inmobiliaria_wrapper(filtered_data, **inputs)

def handle_nav_change():
    if "navigation" in st.session_state:
        st.session_state.page = st.session_state.navigation

def go_to_results():
    st.session_state.loading = True
    st.session_state.page = "Resultados"

def update_reduction_checkbox():
    st.session_state.aplicar_reduccion = st.session_state.checkbox_reduccion
    if not st.session_state.aplicar_reduccion:
        st.session_state.reduccion_porcentaje = 0

# -------------------------------------------------------------------
# Page rendering functions
# -------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.image("images/logo_transparent-glow.png")
        options = [
            "Datos de compra y financiación",
            "Resultados",
            "Mapa",
            "Housebot",
            "Insights",
            "Datos Completos",
            "Información de Soporte"
        ]
        st.sidebar.radio(
            "Navegación",
            options,
            key="navigation",
            on_change=handle_nav_change,
            index=options.index(st.session_state.page)
        )
        st.markdown(
            """
            <style>
            .centered-text {
                text-align: center;
                font-family: "Georgia", sans-serif;
                font-size: 16px;
                font-weight: normal;
                font-style: italic;
                color: #cfe2f3;
            }
            </style>
            <p class="centered-text">Análisis inteligente para maximizar tu inversión.</p>
            """,
            unsafe_allow_html=True
        )

def render_header():
    if is_mobile():
        st.markdown(
            """
            <div class="title-sub">Calculadora de Rentabilidad Inmobiliaria / ZGZ</div>
            """,
            unsafe_allow_html=True
        )

    else: 
        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown(
                """
                <div class="title-main">Calculadora de Rentabilidad Inmobiliaria / ZGZ</div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                        """
                        <div style="display: flex; justify-content: flex-end;">
                            <img src="https://raw.githubusercontent.com/davfranco1/Streamlit-Viviendas/refs/heads/main/images/zaragoza.png" width="60">
                        </div>
                        """,
                        unsafe_allow_html=True
            )
    st.markdown("<hr>", unsafe_allow_html=True)

def render_datos_compra_financiacion(data):
    st.write("\n\n")
    st.radio(
        "Selecciona el tipo de inversión que vas a realizar para aplicar los valores predefinidos. Modifícalos para adaptarse a tus condiciones personales.",
        options=["primera_vivienda", "segunda_vivienda", "inversion"],
        format_func=lambda x: {
            "primera_vivienda": "Primera Vivienda",
            "segunda_vivienda": "Segunda Vivienda",
            "inversion": "Inversión"
        }[x],
        horizontal=True,
        key="tipo_vivienda_radio",
        on_change=handle_tipo_vivienda_change,
        help="De acuerdo con el tipo de inversión que vayas a realizar, los parámetros pueden variar."
    )
    col1, col2 = st.columns(2)
    
    # Datos generales
    col1.write("**Datos generales**")
    if "porcentaje_entrada_input" not in st.session_state:
        st.session_state["porcentaje_entrada_input"] = st.session_state.inputs["porcentaje_entrada"]
    col1.number_input(
        "Porcentaje de entrada (%)",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        key="porcentaje_entrada_input",
        on_change=update_input,
        args=("porcentaje_entrada",),
        help=stxt.entrada
    )
    
    if "coste_reformas_input" not in st.session_state:
        st.session_state["coste_reformas_input"] = st.session_state.inputs["coste_reformas"]
    col1.number_input(
        "Coste de reformas (€)",
        min_value=0,
        max_value=100000,
        key="coste_reformas_input",
        on_change=update_input,
        args=("coste_reformas",),
        help=stxt.reformas
    )
    
    if "comision_agencia_input" not in st.session_state:
        st.session_state["comision_agencia_input"] = st.session_state.inputs["comision_agencia"]
    col1.number_input(
        "Comisión de agencia (%)",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        key="comision_agencia_input",
        on_change=update_input,
        args=("comision_agencia",),
        help=stxt.agencia
    )
    
    if "seguro_vida_input" not in st.session_state:
        st.session_state["seguro_vida_input"] = st.session_state.inputs["seguro_vida"]
    col1.number_input(
        "Seguro de vida anual (€)",
        min_value=0,
        max_value=1000,
        key="seguro_vida_input",
        on_change=update_input,
        args=("seguro_vida",),
        help=stxt.segurovida
    )
    
    # Datos de financiación
    col2.write("**Datos de financiación**")
    if "anios_input" not in st.session_state:
        st.session_state["anios_input"] = st.session_state.inputs["anios"]
    col2.number_input(
        "Años del préstamo",
        min_value=1,
        max_value=40,
        step=1,
        key="anios_input",
        on_change=update_input,
        args=("anios",),
        help=stxt.plazo
    )
    
    if "tin_input" not in st.session_state:
        st.session_state["tin_input"] = st.session_state.inputs["tin"]
    col2.number_input(
        "Tasa de interés nominal (TIN %)",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        key="tin_input",
        on_change=update_input,
        args=("tin",),
        help=stxt.tin
    )
    
    if "tipo_irpf_input" not in st.session_state:
        st.session_state["tipo_irpf_input"] = st.session_state.inputs["tipo_irpf"]
    col2.number_input(
        "Tipo de IRPF (%)",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        key="tipo_irpf_input",
        on_change=update_input,
        args=("tipo_irpf",),
        help=stxt.irpf
    )
    
    if "porcentaje_amortizacion_input" not in st.session_state:
        st.session_state["porcentaje_amortizacion_input"] = st.session_state.inputs["porcentaje_amortizacion"]
    col2.number_input(
        "Porcentaje de amortización (%)",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        key="porcentaje_amortizacion_input",
        on_change=update_input,
        args=("porcentaje_amortizacion",),
        help=stxt.amortizacion
    )
    
    # Reduction options
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
            # Default to 10 when checkbox is checked
            st.session_state.reduccion_porcentaje = st.slider(
                "Selecciona el porcentaje de reducción:",
                min_value=5, 
                max_value=20, 
                value=10,  # Always default to 10 when checkbox is checked 
                step=1,
                key="slider_reduccion",
                help="Selecciona el porcentaje de reducción a aplicar al precio de compra."
            )
        else:
            st.session_state.reduccion_porcentaje = 0  # No reduction if checkbox is unchecked

        # Display the selected reduction percentage
        if st.session_state.reduccion_porcentaje != 0:
            st.write(f"Se aplicará una reducción del {st.session_state.reduccion_porcentaje}% al precio de compra.")
    
    # Custom button style
    st.markdown(
        """
        <style>
        div.stButton > button {
            background-color: #170058 !important;
            color: white !important;
            border-radius: 10px;
            padding: 15px 40px;
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
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Ver resultados", on_click=go_to_results):
            pass
    st.markdown(
        """
        <p style="color: #808080; font-size: 14px;">
        ‣ Los resultados son estimaciones, y nunca deben considerarse consejos de inversión.
        Antes de invertir, asegúrese de <strong>consultar con un experto.</strong><br>
        ‣ Esta herramienta <strong>no muestra</strong> viviendas que requieran una reforma integral o casas de campo.
        </p>
        """,
        unsafe_allow_html=True
    )

def render_resultados(data):
    st.markdown(
        '<p style="color: #224094; font-size: 18px;">• Mostrando resultados ordenados <strong>de mayor a menor rentabilidad bruta</strong>.<br>• No se muestran propiedades que requieran de una reforma integral o casas de campo.</p>',
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_distritos = st.multiselect(
            "Selecciona uno o más distritos",
            options=data["distrito"].unique(),
            default=list(data["distrito"].unique())
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
        estado_bano_min, estado_bano_max = st.slider(
            "Estado del baño (entre 1 y 5)", 0, 5, (3, 5),
            help="Siendo 0 imagen no detectada, 1 muy malo y 5 perfecto estado."
        )
        estado_cocina_min, estado_cocina_max = st.slider(
            "Estado de la cocina (entre 1 y 5)", 0, 5, (3, 5),
            help="Siendo 0 imagen no detectada, 1 muy malo y 5 perfecto estado."
        )
    filtered_data = data[
        (data["distrito"].isin(selected_distritos)) &
        (data["tamanio"].between(metros_min, metros_max)) &
        (data["precio"].between(precio_min, precio_max)) &
        (data["puntuacion_banio"].between(estado_bano_min, estado_bano_max)) &
        (data["puntuacion_cocina"].between(estado_cocina_min, estado_cocina_max))
    ].dropna(subset=["lat", "lon"])
    st.write(f"**Total de resultados filtrados:** {len(filtered_data)}")
    if not filtered_data.empty:
        if st.session_state.aplicar_reduccion:
            filtered_data = filtered_data.copy()
            filtered_data["precio"] = filtered_data["precio"] * (1 - st.session_state.reduccion_porcentaje / 100)
        resultados_rentabilidad = sr.calcular_rentabilidad_inmobiliaria_wrapper(
            filtered_data,
            **st.session_state.inputs
        )
        results_per_page = 10
        total_pages = math.ceil(len(filtered_data) / results_per_page)
        st.markdown(ss.card_styles, unsafe_allow_html=True)
        with st.container():
            page_number = st.selectbox(
                "Página:",
                options=list(range(1, total_pages + 1)),
                index=0,
                key="pagination_dropdown"
            )
        start_idx = (page_number - 1) * results_per_page
        end_idx = start_idx + results_per_page
        paginated_data = resultados_rentabilidad.iloc[start_idx:end_idx]
        for _, row in paginated_data.iterrows():
            image_urls = row["urls_imagenes"] if row["urls_imagenes"] else []
            rentabilidad_bruta = (
                f"{float(row['Rentabilidad Bruta']):.2f}%" if pd.notna(row.get("Rentabilidad Bruta")) else "N/A"
            )
            idealista_url = f"https://www.idealista.com/inmueble/{row['codigo']}/"
            st.markdown(
                f"""
                <div class="card">
                    <div class="card-details">
                        <h3><a href="{idealista_url}" target="_blank" class="custom-title">
                        {row.get("tipo", "Sin tipo")} en {row.get("direccion", "Sin dirección")}</a></h3>
                        <p><strong>Distrito:</strong> {row["distrito"]}</p>
                        <p><strong>Precio:</strong> {row["precio"]:,.0f} €</p>
                        <p><strong>Tamaño:</strong> {row["tamanio"]:,.0f} m²</p>
                        <p><strong>Habitaciones:</strong> {row["habitaciones"]}</p>
                        <p><strong>Rentabilidad Bruta:</strong> {rentabilidad_bruta}</p>
                    </div>
                    <div>
                        <img src="{image_urls[0] if image_urls else ''}" alt="Imagen de la propiedad">
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.expander(f"Más detalles: {row.get('direccion', 'Sin dirección')}"):
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "Información General",
                    "Descripción",
                    "Mapa",
                    "Métricas de rentabilidad",
                    "Contacto"
                ])
                with tab1:
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        st.markdown(
                            f"""
                            - **Precio**: {row["precio"]:,.0f} €
                            - **Tamaño**: {row["tamanio"]:,.0f} m²
                            - **Planta**: {row["planta"]}
                            - **Habitaciones**: {row["habitaciones"]}
                            - **Baños**: {row["banios"]}
                            - **Estado del baño**: {int(row["puntuacion_banio"])}
                            - **Estado de la cocina**: {int(row["puntuacion_cocina"])}
                            """
                        )
                    with col2:
                        st.markdown(
                            f"""
                            - **Exterior**: {'Sí' if row['exterior'] else 'No'}
                            - **Ascensor**: {'Sí' if row['ascensor'] else 'No'}
                            - **Aire acondicionado**: {'Sí' if row['ascensor'] else 'No'}
                            - **Terraza**: {'Sí' if row['terraza'] else 'No'}
                            - **Patio**: {'Sí' if row['patio'] else 'No'}
                            - **Trastero**: {'Sí' if row['trastero'] else 'No'}
                            - **Parking**: {'Sí' if row['trastero'] else 'No'}
                            """
                        )
                    with col3:
                        if image_urls:
                            sc.render_image_carousel(image_urls)
                with tab2:
                    st.markdown(f"- **Descripción**: {row['descripcion']}")
                with tab3:
                    m = folium.Map(location=[row["lat"], row["lon"]], zoom_start=15)
                    marker = folium.Marker(
                        location=[row["lat"], row["lon"]],
                        popup=row["direccion"].title(),
                        icon=folium.Icon(color="blue", icon="info-sign")
                    )
                    marker.add_to(m)
                    st_folium(m, height=300)
                with tab4:
                    st.markdown(f"- **Alquiler predicho**: {row['alquiler_predicho']:,.0f} €")
                    col1_tab4, col2_tab4, col3_tab4 = st.columns(3)
                    with col1_tab4:
                        st.metric("Coste Total", f"{row['Coste Total']:,.0f} €")
                        st.metric("Rentabilidad Bruta", f"{row['Rentabilidad Bruta']}%")
                        st.metric("Beneficio Antes de Impuestos", f"{row['Beneficio Antes de Impuestos']:,.0f} €")
                        st.metric("Rentabilidad Neta", f"{row['Rentabilidad Neta']}%")
                        st.metric("Cuota Mensual Hipoteca", f"{abs(row['Cuota Mensual Hipoteca']):,.0f} €")
                    with col2_tab4:
                        st.metric("Cash Necesario Compra", f"{row['Cash Necesario Compra']:,.0f} €")
                        st.metric("Cash Total Compra y Reforma", f"{row['Cash Total Compra y Reforma']:,.0f} €")
                        st.metric("Beneficio Neto", f"{row['Beneficio Neto']:,.0f} €")
                        st.metric("Cashflow Antes de Impuestos", f"{row['Cashflow Antes de Impuestos']:,.0f} €")
                        st.metric("Cashflow Después de Impuestos", f"{row['Cashflow Después de Impuestos']:,.0f} €")
                    with col3_tab4:
                        st.metric("ROCE", f"{row['ROCE']}%")
                        st.metric("ROCE (Años)", f"{row['ROCE (Años)']:,.0f} años")
                        st.metric("Cash-on-Cash Return", f"{row['Cash-on-Cash Return']}%")
                        st.metric("COCR (Años)", f"{row['COCR (Años)']:,.0f} años")
                with tab5:
                    st.markdown(
                        f"""
                        - **Anunciante**: {row["anunciante"]}
                        - **Teléfono**: {row["contacto"]}
                        """
                    )
                st.markdown("  \n")
                col1_final, col2_final, col3_final = st.columns(3)
                with col1_final:
                    pdf_buffer = spdf.generate_pdf(row)
                    unique_key = f"download_pdf_{row['direccion'].replace(' ', '_')}_{row.name}"
                    st.download_button(
                        label="📄 Descargar informe en PDF",
                        data=pdf_buffer,
                        file_name=f"detalles_vivienda_{row['direccion'].replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        key=unique_key
                    )
                with col2_final:
                    st.link_button("🔗 Ver en Idealista", url=idealista_url)
                with col3_final:
                    current_time = datetime.now().strftime("%d %b, %Y | %H:%M")
                    st.write(
                        f'<span style="color: grey;">📅 Fecha consulta: {current_time}</span>',
                        unsafe_allow_html=True
                    )
        st.markdown(f"**Página {page_number} de {total_pages}**")
    else:
        st.write("No hay propiedades que coincidan con los filtros.")

def render_mapa(data):
    selected_distritos = st.multiselect(
        "Selecciona los distritos",
        options=data["distrito"].unique(),
        default=list(data["distrito"].unique())
    )
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
    filtered_data = data[
        (data["distrito"].isin(selected_distritos)) &
        (data["tamanio"].between(metros_min, metros_max)) &
        (data["precio"].between(precio_min, precio_max))
    ].dropna(subset=["lat", "lon"])
    if not filtered_data.empty:
        if st.session_state.aplicar_reduccion:
            filtered_data = filtered_data.copy()
            filtered_data["precio"] = filtered_data["precio"] * (1 - st.session_state.reduccion_porcentaje / 100)
        resultados_rentabilidad = sr.calcular_rentabilidad_inmobiliaria_wrapper(
            filtered_data,
            **st.session_state.inputs
        )
        fig = go.Figure()
        fig.add_trace(go.Scattermapbox(
            lat=resultados_rentabilidad["lat"],
            lon=resultados_rentabilidad["lon"],
            mode="markers",
            marker=dict(size=10, symbol="circle", color="#3253aa"),
            text=resultados_rentabilidad.apply(lambda row: (
                f"<b><a href=\"https://www.idealista.com/inmueble/{row['codigo']}/\" target=\"_blank\" style=\"color:#3253aa;\">"
                f"{row['tipo'].capitalize()} en {row['direccion']} (ver en idealista)</a></b><br>"
                f"Precio: {row['precio']:,.0f} €<br>"
                f"Tamaño: {row['tamanio']} m²<br>"
                f"Habitaciones y baños: {row['habitaciones']} y {row['banios']}<br>"
                f"Rentabilidad Bruta: {row['Rentabilidad Bruta']:.2f}%<br>"
                f"Alquiler Predicho: {row['alquiler_predicho']:,.0f} €<br>"
                f"Cuota Mensual Hipoteca: {abs(row['Cuota Mensual Hipoteca']):,.0f} €"
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
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No hay datos para mostrar en el mapa.")

def render_housebot(data):
    if "housebot_df" not in st.session_state:
        st.session_state.housebot_df = process_housebot_data(
            data,
            st.session_state.aplicar_reduccion,
            st.session_state.reduccion_porcentaje,
            st.session_state.inputs
        )
    if "query_result" not in st.session_state:
        st.session_state.query_result = None
    st.markdown("### 🏡 Encuentra tu vivienda con nuestro housebot (beta)")
    st.write("• Describe la vivienda con las características que estés buscando, y nuestro agente de inteligencia artificial encontrará la coincidencia más cercana.")
    user_query = st.text_input(
        "📝 *¿Qué estás buscando?*",
        "",
        key="user_query",
        help="Ejemplo: Quiero un piso en Delicias con 2 habitaciones y ascensor"
    )
    st.markdown(
        "<style> div[data-testid=\"stTextInput\"] input { font-size: 18px; font-weight: bold; padding: 10px; } </style>",
        unsafe_allow_html=True
    )
    if user_query:
        if st.session_state.query_result is None or user_query != st.session_state.last_query:
            with st.spinner("🔍 Buscando la vivienda que mejor se ajuste a tu búsqueda..."):
                st.session_state.last_query = user_query
                chat_response = sc.chatbot_query(st.session_state.housebot_df, user_query)
                best_property = sc.find_best_match(st.session_state.housebot_df, chat_response)
                st.session_state.query_result = best_property
        if isinstance(st.session_state.query_result, str):
            st.write(st.session_state.query_result)
        else:
            sc.display_property_details(st.session_state.query_result)

def render_insights(data):
    st.header("💡 Insights Inmobiliarios")

    filtered_data = data
    if st.session_state.aplicar_reduccion:
        filtered_data = filtered_data.copy()
        filtered_data["precio"] = filtered_data["precio"] * (1 - st.session_state.reduccion_porcentaje / 100)
    df = sr.calcular_rentabilidad_inmobiliaria_wrapper(
        filtered_data,
        **st.session_state.inputs
    )

    # Filtros en la página principal
    st.write("Opciones de Filtro")

    # Filtro para distritos
    opciones_distrito = df["distrito"].unique()
    distritos_seleccionados = st.multiselect(
        "Selecciona el distrito(s)",
        options=opciones_distrito,
        default=["Delicias", "San José", "Casco Histórico"]
    )

    # Filtro para tipo de vivienda
    opciones_tipo = df["tipo"].unique()
    tipos_seleccionados = st.multiselect(
        "Seleccione el tipo(s) de vivienda",
        options=opciones_tipo,
        default=["piso", "estudio", "ático"]
    )

    # Filtrar el DataFrame según los distritos y tipo seleccionados
    df_filtrado = df[
        (df["distrito"].isin(distritos_seleccionados)) &
        (df["tipo"].isin(tipos_seleccionados))
    ].copy()

    # Eliminar filas donde el tamaño ("tamanio") no sea positivo para evitar errores
    df_filtrado = df_filtrado[df_filtrado["tamanio"] > 0]

    # Convertir la columna "planta" a numérico, convirtiendo a NaN los valores no convertibles
    df_filtrado["planta"] = pd.to_numeric(df_filtrado["planta"], errors="coerce")

    # Crear columnas adicionales para el análisis
    df_filtrado["alquiler_por_m2"] = df_filtrado["alquiler_predicho"] / df_filtrado["tamanio"]
    df_filtrado["precio_por_m2"] = df_filtrado["precio"] / df_filtrado["tamanio"]

    # Sección de Métricas Clave
    st.header("Métricas Clave")
    if not df_filtrado.empty:
        mediana_alquiler_m2 = df_filtrado["alquiler_por_m2"].median()
        mediana_precio_m2 = df_filtrado["precio_por_m2"].median()
        promedio_tamanio = df_filtrado["tamanio"].mean()
        promedio_habitaciones = df_filtrado["habitaciones"].mean()
        promedio_banios = df_filtrado["banios"].mean()
        promedio_planta = df_filtrado["planta"].median()
        
        col1, col2 = st.columns(2)
        col1.metric("💵 Mediana Alquiler", f"{mediana_alquiler_m2:,.0f} €/m²")
        col2.metric("🏷️ Mediana Venta", f"{mediana_precio_m2:,.0f} €/m²")
        
        col3, col4 = st.columns(2)
        col3.metric("📏 Tamaño Promedio", f"{promedio_tamanio:,.0f} m²")
        col4.metric("🛏️ Habitaciones Promedio", f"{promedio_habitaciones:,.1f}")
        
        col5, col6 = st.columns(2)
        col5.metric("🛁 Baños Promedio", f"{promedio_banios:,.1f}")
        col6.metric("🏢 Planta Promedio", f"{promedio_planta:,.1f}")
    else:
        st.write("No hay datos disponibles para los filtros seleccionados.")

    # Sección de Visualizaciones
    st.header("Visualizaciones")
    if not df_filtrado.empty:
        # Agrupar por distrito para calcular las medianas
        df_agrupado = df_filtrado.groupby("distrito").agg({
            "alquiler_por_m2": "median",
            "precio_por_m2": "median"
        }).reset_index()
        
        # Gráfico 1: Mediana de Alquiler/m² por Distrito
        fig_alquiler = px.bar(
            df_agrupado,
            x="distrito",
            y="alquiler_por_m2",
            title="Mediana Alquiler/m² por Distrito",
            labels={"distrito": "Distrito", "alquiler_por_m2": "Alquiler/m²"},
            text_auto=".2f"  # Añade etiquetas con dos decimales
        )
        st.plotly_chart(fig_alquiler, use_container_width=True)
        
        # Gráfico 2: Mediana de Precio/m² por Distrito
        fig_precio = px.bar(
            df_agrupado,
            x="distrito",
            y="precio_por_m2",
            title="Mediana Precio/m² por Distrito",
            labels={"distrito": "Distrito", "precio_por_m2": "Precio/m²"},
            text_auto=".2f"
        )
        st.plotly_chart(fig_precio, use_container_width=True)
        
        # Gráfico 3: Diagrama de dispersión Precio vs Tamaño de la Propiedad
        fig_dispersion = px.scatter(
            df_filtrado,
            x="tamanio",
            y="precio",
            color="tipo",
            hover_data=["distrito", "habitaciones", "banios"],
            title="Precio vs Tamaño de la Propiedad"
        )
        st.plotly_chart(fig_dispersion, use_container_width=True)
        
        # Gráfico 4: Rentabilidad Bruta Promedio por Tipo y Distrito (visualización simplificada)
        if "Rentabilidad Bruta" in df_filtrado.columns:
            df_rentabilidad = df_filtrado.groupby(["tipo", "distrito"]).agg({"Rentabilidad Bruta": "mean"}).reset_index()
            fig_rent = px.bar(
                df_rentabilidad,
                x="tipo",
                y="Rentabilidad Bruta",
                color="distrito",
                barmode="group",
                title="Rentabilidad Bruta Promedio por Tipo y Distrito",
                labels={
                    "tipo": "Tipo de Propiedad",
                    "Rentabilidad Bruta": "Rentabilidad Bruta Promedio",
                    "distrito": "Distrito"
                },
                text_auto=".2f"
            )
            st.plotly_chart(fig_rent, use_container_width=True)
    else:
        st.write("No hay visualizaciones para mostrar.")

def render_datos_completos(data):
    st.header("Datos completos")
    st.markdown(
        '<p style="color: #224094; font-size: 18px;">• Usa los filtros para configurar la búsqueda.<br>'
        "• Los resultados se muestran en orden de Rentabilidad Bruta descendiente.</p>",
        unsafe_allow_html=True
    )
    selected_distritos = st.multiselect(
        "Selecciona distritos",
        options=data["distrito"].unique(),
        default=list(data["distrito"].unique()),
        key="distrito_filtro"
    )
    col1, col2 = st.columns(2)
    with col1:
        precio_min, precio_max = st.slider(
            "Precio (€)",
            int(data["precio"].min()),
            int(data["precio"].max()),
            (int(data["precio"].min()), int(data["precio"].max())),
            key="precio_filtro",
            help="Filtro sobre el precio original, sin reducciones."
        )
    with col2:
        metros_min, metros_max = st.slider(
            "Metros cuadrados",
            int(data["tamanio"].min()),
            int(data["tamanio"].max()),
            (int(data["tamanio"].min()), int(data["tamanio"].max())),
            key="metros_filtro"
        )
    filtered_data = data[
        (data["distrito"].isin(selected_distritos)) &
        (data["tamanio"].between(metros_min, metros_max)) &
        (data["precio"].between(precio_min, precio_max))
    ]
    if not filtered_data.empty:
        if st.session_state.aplicar_reduccion:
            filtered_data = filtered_data.copy()
            filtered_data["precio"] = filtered_data["precio"] * (1 - st.session_state.reduccion_porcentaje / 100)
        resultados_rentabilidad = sr.calcular_rentabilidad_inmobiliaria_wrapper(
            filtered_data,
            **st.session_state.inputs
        )
        exclude_columns = {"lat", "lon", "urls_imagenes", "url_cocina", "url_banio", "estado", "geometry"}
        available_columns = [col for col in resultados_rentabilidad.columns if col not in exclude_columns]
        default_columns = ["distrito", "direccion", "tipo", "precio", "tamanio", "habitaciones", "banios", "Rentabilidad Bruta"]
        default_columns = [col for col in default_columns if col in available_columns]
        selected_columns = st.multiselect(
            "Añade o elimina las columnas a mostrar. Puedes escribir el nombre o utilizar el desplegable.",
            options=available_columns,
            default=default_columns,
            key="columnas_filtro"
        )
        if "Rentabilidad Bruta" in resultados_rentabilidad.columns:
            resultados_rentabilidad = resultados_rentabilidad.sort_values(by="Rentabilidad Bruta", ascending=False)
        st.dataframe(resultados_rentabilidad[selected_columns])
    else:
        st.write("No hay datos que coincidan con los filtros.")

def render_informacion_soporte():
    stxt.imprimir_metricas()

# -------------------------------------------------------------------
# Main function
# -------------------------------------------------------------------

def main():
    # Ensure session state variables exist
    st.session_state.setdefault("page", "Datos de compra y financiación")
    st.session_state.setdefault("tipo_vivienda", "primera_vivienda")
    st.session_state.setdefault("inputs", {
        "porcentaje_entrada": 20.0,
        "coste_reformas": 5000,
        "comision_agencia": 3.0,
        "anios": 30,
        "tin": 3.0,
        "seguro_vida": 250,
        "tipo_irpf": 17.0,
        "porcentaje_amortizacion": 40.0,
    })
    st.session_state.setdefault("aplicar_reduccion", True)
    st.session_state.setdefault("reduccion_porcentaje", 10)
    st.session_state.setdefault("loading", False)

    data = load_data()

    # Render components
    render_sidebar()
    render_top_nav()

    # Render the selected page
    if st.session_state.page == "Datos de compra y financiación":
        render_datos_compra_financiacion(data)
    elif st.session_state.page == "Resultados":
        render_resultados(data)
    elif st.session_state.page == "Mapa":
        render_mapa(data)
    elif st.session_state.page == "Housebot":
        render_housebot(data)
    elif st.session_state.page == "Insights":
        render_insights(data)
    elif st.session_state.page == "Datos Completos":
        render_datos_completos(data)
    elif st.session_state.page == "Información de Soporte":
        render_informacion_soporte()

if __name__ == "__main__":
    main()