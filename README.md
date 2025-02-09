# Streamlit Las Casas de David

<img src="images/header_github.png">

Este repositorio contiene una aplicación desarrollada en **Streamlit** para el análisis y visualización de datos relacionados con la compra y alquiler de viviendas en Zaragoza. La aplicación permite explorar diferentes métricas y realizar comparaciones basadas en datos del usuario y el mercado, facilitando la toma de decisiones en el sector inmobiliario.

Corresponde al *frontend* del proyecto principal, disponible en [este repositorio](https://github.com/davfranco1/Proyecto-Rentabilidad-Viviendas).

## 🏡 Características

- **Carga y exploración de datos**: Permite cargar datos sobre viviendas en venta desde una base de datos de Mongo.
- **Personalización de resultados**: El usuario es capaz de ingresar datos particulares sobre sus finanzas, la vivienda y su financiación, para obtener resultados más fieles a su casuística personal.
- **Filtrado y segmentación**: Posibilidad de filtrar datos por ubicación, precios, características de la vivienda, entre otros.
- **Distintas visualizaciones**: Se ofrecen distintas opciones para visualizar los resultados: cartas desplegables, un informe descargable en PDF, mapa interactivo y tabla completa de datos.
- **Housebot (beta)**: Además de los filtros tradicionales, el usuario puede utilizar un *chatbot* para encontrar características especiales de una vivienda, así como como búsquedas más tradicionales.
- **Información de soporte**: Como respaldo de los cálculos, el usuario puede consultar la descripción, fórmulas y constantes de las métricas que se han utilizado.

## 📂 Estructura del repositorio

```
Streamlit-Viviendas/
│── main.py                # Script principal de la aplicación
│── .gitignore             # Archivos y carpetas a excluir del control de versiones
│── src/                   # Código fuente de la aplicación Streamlit
│   │── soporte_chatbot_langchain.py  # Funcionalidades del chatbot con LangChain
│   │── soporte_chatbot.py            # Lógica principal del chatbot
│   │── soporte_mongo.py              # Funciones de soporte para integración con MongoDB
│   │── soporte_pdf.py                # Manejo y procesamiento de archivos PDF
│   │── soporte_rentabilidad.py       # Cálculo de rentabilidad de las viviendas
│   │── soporte_styles.py             # Configuración de estilos y apariencia de la aplicación
│   │── soporte_texto.py              # Almacenamiento de texto
│── requirements.txt      # Dependencias necesarias para ejecutar la aplicación
│── README.md             # Documentación del proyecto
```

## 🛠 Instalación

Para ejecutar la aplicación localmente, sigue los siguientes pasos:

1. Clona el repositorio:
   ```bash
   git clone https://github.com/davfranco1/Streamlit-Viviendas.git
   cd Streamlit-Viviendas
   ```

2. Crea un entorno virtual y activa:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Crea un archivo `.env` en la carpeta `src` del proyecto y añade las claves necesarias:
   ```bash
   OPENAI=tu_api_key_de_openai
   MONGO_URI=tu_uri_de_mongo
   ```
   Si deseas desplegar una aplicación similar en la nube de Streamlit, debes almacenar estos *secrets* en la configuración de la aplicación.

4. Ejecuta la aplicación:
   ```bash
   streamlit run main.py
   ```

Para ejecutar la aplicación será necesario:
- Crear una cuenta en [Mongo Atlas](https://www.mongodb.com/lp/cloud/atlas/try4-reg), una base de datos y obtener la 'MONGO_URI'.
- Obtener una API Key para [OpenAI](https://platform.openai.com/docs/overview), para utilizar el chatbot.


## 📋 Requerimientos

El archivo `requirements.txt` incluye las siguientes librerías necesarias para la ejecución de la aplicación:

- `pandas>=1.3.0` - Manipulación y análisis de datos.
- `numpy>=1.21.0` - Operaciones numéricas avanzadas.
- `numpy_financial>=1.0.0` - Cálculos financieros para análisis de rentabilidad.
- `plotly>=5.0.0` - Gráficos interactivos para análisis de datos.
- `pymongo>=3.12.0` - Cliente de MongoDB para la gestión de bases de datos.
- `python-dotenv>=1.0.1` - Manejo de variables de entorno desde archivos `.env`.
- `streamlit>=1.0.0` - Framework para construir la aplicación web interactiva.
- `geopandas>=0.12.0` - Análisis geoespacial de datos.
- `shapely>=1.8.0` - Manipulación de geometrías espaciales.
- `openai>=0.27.0` - API de OpenAI para procesamiento de lenguaje natural.
- `folium` - Visualización de mapas interactivos.
- `streamlit-folium>=0.12` - Integración de mapas de Folium en Streamlit.
- `reportlab` - Generación de documentos PDF.
- `requests` - Manejo de solicitudes HTTP.


##  ☁️ También disponible en Streamlit Cloud

Se puede acceder a este proyecto directamente a través de la URL https://lascasasdedavid.streamlit.app.

---

## Autor

David Franco - [LinkedIn](https://linkedin.com/in/franco-david)

Enlace del proyecto: [https://github.com/davfranco1/Streamlit-Viviendas](https://github.com/davfranco1/Streamlit-Viviendas)

