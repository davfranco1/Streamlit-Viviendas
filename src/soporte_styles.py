styles="""
    <style>
    .block-container {
        padding-top: 1.5rem;
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


    /* Ocultamos el header por defecto de Streamlit para que no compita con nuestro topbar */
    header[data-testid="stHeader"] {
        display: none;
    }
    /* Ocultamos el pie de página por defecto (opcional) */
    footer {visibility: hidden;
    }

    /* Markdown elements spacing */
    .stMarkdown {
        margin-top: 0.5rem;
    }

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

    .preset-button {
        display: inline-block;
        margin: 10px;
        padding: 10px 20px;
        background-color: #170058;
        color: white;
        border-radius: 5px;
        text-align: center;
        cursor: pointer;
    }
    .preset-button:hover {
        background-color: #2a007a;
    }
    .preset-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-bottom: 30px;
    }

    hr {
        border: 1px solid #0b5394 !important; /* Make the line bolder and blue */
        margin: 0px 0px; /* Add spacing above and below */
        width: 100%; /* Ensure full width */
    }

        [data-testid="stBaseButton-headerNoPadding"] {
        position: relative;
        width: auto !important;
        padding-right: 60px !important;
    }

    [data-testid="stBaseButton-headerNoPadding"]::after {
        content: "Menu";
        position: absolute;
        top: 50%;
        left: 24px;
        transform: translateY(-50%);
        white-space: wrap;
        background-color: #FFFFFF;
        padding: 10px;
        display: inline-block;
        color: #4B5F6D;       /* Sets the text color */
        font-weight: bold;    /* Makes the text bold */
    }

    [data-testid="stBaseButton-headerNoPadding"] {
        color: #FFFFFF !important;
    }

    [data-testid="stBaseButton-headerNoPadding"] svg {
        fill: #4B5F6D !important;
    }

    /* Styling input elements */
    .stTextInput, .stSelectbox, .stNumberInput, .stSlider, .stRadio {
        background-color: white;
        border: 2px solid #00185E;
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
    """


card_styles = """
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
            """