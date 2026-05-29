import pandas as pd

def calcular_estrategia(deudas_originales, pago_mensual_total, metodo="avalancha"):
    """
    Simulación avanzada de desendeudamiento que acepta Tarjetas y Préstamos Personales.
    """
    # Copia profunda de las deudas para no alterar los inputs del usuario
    deudas = [d.copy() for d in deudas_originales]
    
    # El "pago mínimo" en un préstamo es su mensualidad fija obligatoria
    suma_minimos = sum(d['pago_minimo'] for d in deudas)
    if pago_mensual_total < suma_minimos:
        return f"Error: Tu presupuesto mensual (${pago_mensual_total:,.2f}) no cubre siquiera la suma de los pagos obligatorios (${suma_minimos:,.2f}). Necesitas un monto mayor para acelerar el plan."

    # Ordenamiento según la estrategia elegida
    if metodo == "avalancha":
        deudas.sort(key=lambda x: x['tasa_anual'], reverse=True)
    elif metodo == "bola_de_nieve":
        deudas.sort(key=lambda x: x['saldo'])

    historial_meses = []
    mes = 0
    total_intereses_pagados = 0

    while sum(d['saldo'] for d in deudas) > 0 and mes < 120:
        mes += 1
        dinero_disponible = pago_mensual_total
        interes_este_mes_total = 0
        
        # 1. Cobrar intereses del mes y aplicar el pago mínimo obligatorio
        for d in deudas:
            if d['saldo'] > 0:
                tasa_mensual = d['tasa_anual'] / 12
                interes_generado = d['saldo'] * tasa_mensual
                d['saldo'] += interes_generado
                interes_este_mes_total += interes_generado
                total_intereses_pagados += interes_generado
                
                # El pago obligatorio es el mínimo de la tarjeta o la mensualidad del préstamo
                pago_obligatorio = min(d['pago_minimo'], d['saldo'])
                d['saldo'] -= pago_obligatorio
                dinero_disponible -= pago_obligatorio

        # 2. Inyección del "Acelerador" (Dinero extra sobrante) a la deuda prioritaria
        for d in deudas:
            if d['saldo'] > 0 and dinero_disponible > 0:
                pago_extra = min(dinero_disponible, d['saldo'])
                d['saldo'] -= pago_extra
                dinero_disponible -= pago_extra

        # Guardar registro del mes para la gráfica
        registro_mes = {
            "Mes": mes,
            "Intereses del Mes ($)": round(interes_este_mes_total, 2),
            "Saldo Total Restante ($)": round(sum(d['saldo'] for d in deudas), 2)
        }
        for d in deudas:
            registro_mes[d['nombre']] = round(d['saldo'], 2)
            
        historial_meses.append(registro_mes)

    df_resultado = pd.DataFrame(historial_meses)
    return df_resultado, round(total_intereses_pagados, 2), mes