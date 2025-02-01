import streamlit as st

def imprimir_metricas():
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