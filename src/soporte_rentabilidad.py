import pandas as pd
import numpy_financial as npf

def calcular_beneficio(precio_vivienda, ingresos_anuales, seguro_vida, intereses_hipoteca):
    """
    Calcula el beneficio antes de impuestos para una vivienda en alquiler.

    Args:
    precio_vivienda (float): Precio de la vivienda.
    ingresos_anuales (float): Ingresos anuales por alquiler.
    seguro_vida (float): Costo del seguro de vida.
    intereses_hipoteca (float): Intereses anuales de la hipoteca.

    Returns:
    float: Beneficio antes de impuestos.
    """
    # Seguro impago = 4% * ingresos
    # corresponde al 4% de la renta anual
    seguro_impago = 0.04 * ingresos_anuales

    # Seguro hogar = 176,29
    # Fuente: https://selectra.es/seguros/seguros-hogar/precios-seguros-hogar
    seguro_hogar = 176.29

    # IBI = precio_vivienda * 0,4047%
    ibi = precio_vivienda * 0.004047

    # Impuesto basuras = 283
    impuesto_basuras = 283

    # Mantenimiento y comunidad = ingresos_anuales * 10%
    # incluye la comunidad de vecinos. Fuente: https://www.donpiso.com/blog/mantener-piso-vacio-cuesta-2-300-euros-al-ano/
    mantenimiento_comunidad = ingresos_anuales * 0.10

    # Periodos vacío = ingresos_anuales * 5%
    periodos_vacios = ingresos_anuales * 0.05

    # Beneficio = ingresos - seguro impago - seguro basuras - seguro hogar 
    # - seguro vida - IBI - mantenimiento - periodos vacío - intereses hipoteca
    beneficio = (ingresos_anuales - seguro_impago - seguro_hogar - seguro_vida - 
                 ibi - impuesto_basuras - mantenimiento_comunidad - 
                 periodos_vacios - intereses_hipoteca)

    return beneficio


def calcular_rentabilidad_inmobiliaria(porcentaje_entrada, coste_compra, coste_reformas, comision_agencia, 
                                       alquiler_mensual, anios, tin, seguro_vida, tipo_irpf, 
                                       porcentaje_amortizacion):
    """
    Función para calcular las métricas de rentabilidad inmobiliaria basadas en los datos proporcionados.

    Parámetros:
    - porcentaje_entrada: Porcentaje del coste total cubierto por el pago inicial.
    - coste_compra: Coste total de la compra de la propiedad.
    - coste_reformas: Costes asociados con reformas y reparaciones.
    - comision_agencia: Comisión de la agencia o PSI.
    - alquiler_mensual: Ingresos mensuales esperados por alquiler.
    - anios: Duración de la hipoteca en años.
    - tin: Tasa de interés nominal fija anual de la hipoteca.
    - seguro_vida: Seguro de vida del propietario.
    - tipo_irpf: Porcentaje aplicado para calcular el IRPF.
    - porcentaje_amortizacion: Porcentaje anual aplicado para amortización.

    Devuelve:
    - Diccionario con las métricas calculadas.
    """
    # Cálculo del ITP (8%) y coste notario (2%)
    coste_itp = coste_compra * 0.08
    coste_notario = coste_compra * 0.02

    # Coste total
    coste_total = coste_compra + coste_reformas + comision_agencia + coste_notario + coste_itp

    # Pago inicial (inversión inicial)
    pago_entrada = porcentaje_entrada * coste_compra

    # Cash necesario para la compra y reforma
    cash_necesario_compra = pago_entrada + comision_agencia + coste_notario + coste_itp
    cash_total_compra_reforma = pago_entrada + coste_reformas + coste_notario + coste_itp
    
    # Monto del préstamo
    monto_prestamo = coste_compra*(1-porcentaje_entrada)

    # Pagos mensuales y anuales de la hipoteca
    
    hipoteca_mensual = npf.pmt(tin/12, anios*12, monto_prestamo)

    total_pagado = -hipoteca_mensual * (anios*12) 
    interes_total = total_pagado - monto_prestamo 
    capital_anual = monto_prestamo/anios
    capital_mensual = capital_anual/12
    interes_anual = interes_total / anios

    # Ingresos anuales por alquiler
    alquiler_anual = alquiler_mensual * 12

    # Cálculo del beneficio antes de impuestos usando la función calcular_beneficio
    beneficio_antes_impuestos = calcular_beneficio(
        precio_vivienda=coste_compra,
        ingresos_anuales=alquiler_anual,
        seguro_vida=seguro_vida,
        intereses_hipoteca=interes_anual
    )

    # Amortización anual
    amortizacion_anual = 0.03*(porcentaje_amortizacion*coste_compra+(coste_reformas+comision_agencia+coste_notario+coste_itp))

    # Deducción por larga duración (60%)
    deduccion_larga_duracion = (beneficio_antes_impuestos - amortizacion_anual)* 0.60

    # IRPF aplicado a larga duración
    irpf = -(deduccion_larga_duracion * tipo_irpf)

    # Beneficio neto
    beneficio_neto = beneficio_antes_impuestos + irpf

    # Rentabilidad bruta
    rentabilidad_bruta = alquiler_anual / coste_total * 100

    # Rentabilidad neta
    rentabilidad_neta = (beneficio_antes_impuestos + irpf) / coste_total * 100

    # Cashflow antes de impuestos
    cashflow_antes_impuestos = beneficio_antes_impuestos - capital_anual

    # Cashflow después de impuestos
    cashflow_despues_impuestos = beneficio_neto - capital_anual

    # ROCE (Return on Capital Employed)
    roce = alquiler_anual/(pago_entrada+coste_reformas+comision_agencia+coste_notario+coste_itp) * 100

    # ROCE Años (Return on Capital Employed)
    roce_anios = pago_entrada/(pago_entrada*roce) * 100

    # Cash-on-Cash Return (COCR)
    cash_on_cash_return = cashflow_despues_impuestos/(pago_entrada+coste_reformas+comision_agencia+coste_notario+coste_itp) * 100

    # Cash-on-Cash Return Años (COCR)
    cash_on_cash_return_anios = (pago_entrada+coste_reformas+comision_agencia+coste_notario+coste_itp) / cashflow_despues_impuestos


    # Resultados finales
    return {
        "Coste Total": coste_total,
        "Rentabilidad Bruta": round(rentabilidad_bruta, 2),
        "Beneficio Antes de Impuestos": round(beneficio_antes_impuestos,2),
        "Rentabilidad Neta": round(rentabilidad_neta,2),
        "Cuota Mensual Hipoteca": round(hipoteca_mensual,2),
        "Cash Necesario Compra": round(cash_necesario_compra,2),
        "Cash Total Compra y Reforma": round(cash_total_compra_reforma,2),
        "Beneficio Neto": round(beneficio_neto,2),
        "Rentabilidad Neta": round(rentabilidad_neta,2),
        "Cashflow Antes de Impuestos": round(cashflow_antes_impuestos,2),
        "Cashflow Después de Impuestos": round(cashflow_despues_impuestos,2),
        "ROCE": round(roce,2),
        "ROCE (Años)": round(roce_anios,2),
        "Cash-on-Cash Return": round(cash_on_cash_return,2),
        "COCR (Años)": round(cash_on_cash_return_anios,2)
    }


def calcular_rentabilidad_inmobiliaria_wrapper(df, porcentaje_entrada, coste_reformas, comision_agencia,
                                               anios, tin, seguro_vida, tipo_irpf, 
                                               porcentaje_amortizacion):
    """
    Debug version of the wrapper function that logs input values and intermediate calculations.
    """
    print("\n=== Debug Information ===")
    print(f"Input DataFrame shape: {df.shape}")
    print("\nInput Parameters:")
    print(f"- porcentaje_entrada: {porcentaje_entrada}")
    print(f"- coste_reformas: {coste_reformas}")
    print(f"- comision_agencia: {comision_agencia}")
    print(f"- anios: {anios}")
    print(f"- tin: {tin}")
    print(f"- seguro_vida: {seguro_vida}")
    print(f"- tipo_irpf: {tipo_irpf}")
    print(f"- porcentaje_amortizacion: {porcentaje_amortizacion}")
    
    print("\nDataFrame Columns:", df.columns.tolist())
    
    # Check for required columns
    if 'precio' not in df.columns:
        print("\nERROR: 'precio' column is missing from DataFrame")
        return df
    
    if 'alquiler_predicho' not in df.columns:
        print("\nERROR: 'alquiler_predicho' column is missing from DataFrame")
        return df
    
    # Sample of first few rows data
    print("\nFirst few rows of key columns:")
    sample_cols = ['precio', 'alquiler_predicho'] if 'alquiler_predicho' in df.columns else ['precio']
    print(df[sample_cols].head().to_string())
    
    def calcular_rentabilidad_fila(row):
        """Calculate profitability for a single row with debugging."""
        try:
            print(f"\nCalculating for row with precio: {row['precio']}")
            print(f"Alquiler predicho: {row['alquiler_predicho']}")
            
            result = calcular_rentabilidad_inmobiliaria(
                porcentaje_entrada=porcentaje_entrada,
                coste_compra=row['precio'],
                coste_reformas=coste_reformas,
                comision_agencia=comision_agencia,
                alquiler_mensual=row['alquiler_predicho'],
                anios=anios,
                tin=tin,
                seguro_vida=seguro_vida,
                tipo_irpf=tipo_irpf,
                porcentaje_amortizacion=porcentaje_amortizacion
            )
            
            print("Calculation successful")
            print(f"Rentabilidad Bruta: {result.get('Rentabilidad Bruta')}")
            return result
            
        except Exception as e:
            print(f"Error in calculation: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None
    
    # Create working copy
    df_work = df.copy()
    
    # Convert numeric columns
    numeric_cols = ['precio', 'alquiler_predicho']
    for col in numeric_cols:
        if col in df_work.columns:
            df_work[col] = pd.to_numeric(df_work[col], errors='coerce')
            print(f"\nNumeric conversion for {col}:")
            print(f"- Number of null values: {df_work[col].isna().sum()}")
            print(f"- Value range: {df_work[col].min()} to {df_work[col].max()}")
    
    # Calculate results
    print("\nStarting calculations for each row...")
    results = []
    for idx, row in df_work.iterrows():
        print(f"\nProcessing row {idx}")
        metrics = calcular_rentabilidad_fila(row)
        if metrics is not None:
            row_dict = row.to_dict()
            row_dict.update(metrics)
            results.append(row_dict)
    
    print(f"\nProcessed {len(results)} rows successfully")
    
    # Create final DataFrame
    if results:
        df_final = pd.DataFrame(results)
        df_final.sort_values(by="Rentabilidad Bruta", ascending=False, inplace=True)
        print("\nFinal DataFrame shape:", df_final.shape)
        return df_final
    else:
        print("\nWARNING: No valid results calculated")
        return df_work