import streamlit as st
import pandas as pd
import numpy as np
from motor_finanzas import calcular_estrategia
from base_datos import (
    inicializar_bd, obtener_datos, guardar_datos_completos,
    registrar_pago, obtener_historial_pagos, limpiar_bitacora,
    crear_evento, obtener_eventos, eliminar_evento, agregar_gasto_evento, obtener_gastos_de_evento
)

st.set_page_config(page_title="FinaApp Pro Ultimate", page_icon="💰", layout="wide")
inicializar_bd()

st.title("💰 FinaApp Pro: Ecosistema Financiero Total")
st.markdown("Presupuestos fijos, control de deudas, simulaciones DCA y gestión de gastos extraordinarios por eventos.")

# ==========================================
# RECOLECCIÓN DE DATA CORE SQLITE
# ==========================================
if "datos_cargados" not in st.session_state:
    db_ingresos, db_egresos, db_deudas, db_ahorro = obtener_datos()
    st.session_state.lista_deudas = db_deudas
    st.session_state.ingresos = db_ingresos
    st.session_state.egresos = db_egresos
    st.session_state.ahorro_config = db_ahorro
    st.session_state.datos_cargados = True

def agregar_deuda(): st.session_state.lista_deudas.append({"nombre": f"Nueva Deuda {len(st.session_state.lista_deudas)+1}", "tipo": "Tarjeta de Crédito", "saldo": 10000.0, "tasa_anual": 40.0, "pago_minimo": 500.0})
def eliminar_deuda(index): 
    if len(st.session_state.lista_deudas) > 1: st.session_state.lista_deudas.pop(index)
def agregar_ingreso(): st.session_state.ingresos.append({"concepto": "Nuevo Ingreso", "monto": 0.0})
def eliminar_ingreso(index):
    if len(st.session_state.ingresos) > 1: st.session_state.ingresos.pop(index)
def agregar_egreso(): st.session_state.egresos.append({"concepto": "Nuevo Egreso", "monto": 0.0})
def eliminar_egreso(index):
    if len(st.session_state.egresos) > 1: st.session_state.egresos.pop(index)

ingresos_procesados = []
egresos_procesados = []
deudas_procesadas = []

# ==========================================
# DELINEACIÓN DE TABS (5 PESTAÑAS)
# ==========================================
tab_presupuesto, tab_deudas, tab_anti_tanda, tab_bitacora, tab_eventos = st.tabs([
    "📊 Control de Gastos e Ingresos", 
    "⚡ Plan de Choque Contra Deudas",
    "📉 El Efecto Tanda y Estrategia DCA",
    "📝 Bitácora de Pagos Reales",
    "🎪 Control de Eventos y Flujo Final"
])

# ---- TABS 1, 2, 3 y 4 (Mantienen estabilidad absoluta) ----
with tab_presupuesto:
    st.header("📝 Tu Presupuesto Mensual")
    col_ing, col_egr = st.columns(2)
    with col_ing:
        st.subheader("🟢 Ingresos Mensuales")
        for i, ing in enumerate(st.session_state.ingresos):
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1: con_ing = st.text_input("Concepto", value=ing['concepto'], key=f"con_ing_{i}")
            with c2: mon_ing = st.number_input("Monto ($)", value=float(ing['monto']), step=500.0, key=f"mon_ing_{i}")
            with c3:
                st.write(""); st.write("")
                st.button("🗑️", key=f"del_ing_{i}", on_click=eliminar_ingreso, args=(i,))
            ingresos_procesados.append({"concepto": con_ing, "monto": mon_ing})
        st.button("➕ Agregar Ingreso", on_click=agregar_ingreso, key="btn_add_ing")
        total_ingresos = sum(item['monto'] for item in ingresos_procesados)
        st.metric("Total Ingresos", f"${total_ingresos:,.2f} MXN")
    with col_egr:
        st.subheader("🔴 Egresos / Gastos Mensuales")
        for i, egr in enumerate(st.session_state.egresos):
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1: con_egr = st.text_input("Concepto", value=egr['concepto'], key=f"con_egr_{i}")
            with c2: mon_egr = st.number_input("Monto ($)", value=float(egr['monto']), step=100.0, key=f"mon_egr_{i}")
            with c3:
                st.write(""); st.write("")
                st.button("🗑️", key=f"del_egr_{i}", on_click=eliminar_egreso, args=(i,))
            egresos_procesados.append({"concepto": con_egr, "monto": mon_egr})
        st.button("➕ Agregar Egreso", on_click=agregar_egreso, key="btn_add_egr")
        total_egresos = sum(item['monto'] for item in egresos_procesados)
        st.metric("Total Egresos (Sin deudas)", f"${total_egresos:,.2f} MXN")
    st.write("---")
    st.subheader("💡 Diagnóstico Financiero")
    capacidad_pago_calculada = total_ingresos - total_egresos
    if capacidad_pago_calculada > 0: st.success(f"Tienes un remanente disponible de **${capacidad_pago_calculada:,.2f} MXN** al mes.")
    else: st.error(f"Tus gastos superan tus ingresos por **${abs(capacidad_pago_calculada):,.2f} MXN**.")

with tab_deudas:
    st.header("⚡ Plan de Aceleración de Deudas")
    col1, col2 = st.columns([1.1, 1.9])
    with col1:
        st.subheader("📋 Cuentas Pendientes")
        for i, deuda in enumerate(st.session_state.lista_deudas):
            with st.expander(f"📌 {deuda['nombre']} ({deuda['tipo']})", expanded=True):
                col_t1, col_t2 = st.columns([3, 2])
                with col_t1: nuevo_nombre = st.text_input("Nombre", value=deuda['nombre'], key=f"nom_{i}")
                with col_t2: nuevo_tipo = st.selectbox("Tipo", ["Tarjeta de Crédito", "Préstamo Personal"], index=0 if deuda['tipo'] == "Tarjeta de Crédito" else 1, key=f"tipo_{i}")
                c_s, c_t, c_m = st.columns(3)
                with c_s: nuevo_saldo = st.number_input("Saldo ($)", value=float(deuda['saldo']), step=1000.0, key=f"sal_{i}")
                with c_t: nueva_tasa = st.number_input("Tasa Anual (%)", value=float(deuda['tasa_anual'] if deuda['tasa_anual'] > 1 else deuda['tasa_anual']*100), step=5.0, key=f"tas_{i}")
                with c_m:
                    label_pago = "Mínimo ($)" if nuevo_tipo == "Tarjeta de Crédito" else "Mensualidad ($)"
                    nuevo_minimo = st.number_input(label_pago, value=float(deuda['pago_minimo']), step=100.0, key=f"min_{i}")
                if len(st.session_state.lista_deudas) > 1: st.button(f"🗑️ Eliminar cuenta", key=f"del_{i}", on_click=eliminar_deuda, args=(i,))
                deudas_procesadas.append({"nombre": nuevo_nombre, "tipo": nuevo_tipo, "saldo": nuevo_saldo, "tasa_anual": nueva_tasa, "pago_minimo": nuevo_minimo})
        st.button("➕ Añadir otra deuda", on_click=agregar_deuda, type="primary", key="btn_add_deuda")
        st.write("---")
        pago_mensual_total = st.number_input("Presupuesto Mensual Total Destinado ($)", value=max(float(capacidad_pago_calculada), 0.0), step=500.0)
        metodo_seleccionado = st.selectbox("Estrategia algorítmica:", ["avalancha", "bola_de_nieve"])
    with col2:
        st.subheader("📊 Ruta de Escape Calculada")
        deudas_motor = [d.copy() for d in deudas_procesadas]
        for d in deudas_motor: d['tasa_anual'] = d['tasa_anual'] / 100
        resultado = calcular_estrategia(deudas_motor, pago_mensual_total, metodo=metodo_seleccionado)
        if isinstance(resultado, str): st.error(resultado)
        else:
            df_resultado, total_intereses, meses = resultado
            m1, m2 = st.columns(2)
            m1.metric(label="Tiempo estimado de liquidación", value=f"{meses} meses")
            m2.metric(label="Total de intereses proyectados", value=f"${total_intereses:,} MXN")
            st.subheader("📉 Curva de Amortización de Saldos")
            nombres_columnas = [d['nombre'] for d in deudas_procesadas]
            st.line_chart(df_resultado.set_index("Mes")[nombres_columnas])
            st.subheader("📅 Calendario Mensual de Saldos de Cierre")
            st.dataframe(df_resultado)

with tab_anti_tanda:
    st.header("📉 Inversión Estratégica: Tanda vs Renta Fija vs Dollar Cost Averaging (DCA)")
    c_ant1, c_ant2 = st.columns([1, 2])
    with c_ant1:
        st.subheader("⚙️ Configuración del Portafolio")
        cfg = st.session_state.ahorro_config
        monto_ahorro_mensual = st.number_input("Aportación Mensual Total ($)", value=float(cfg.get('monto_mensual', 2000.0)), step=500.0)
        tasa_inflacion_est = st.number_input("Tasa de Inflación Anual (%)", value=float(cfg.get('tasa_inflacion', 4.5)), step=0.1)
        tasa_cetes_est = st.number_input("Rendimiento Renta Fija Anual (ej. CETES) (%)", value=float(cfg.get('tasa_rendimiento', 11.0)), step=0.5)
        st.write("---")
        st.subheader("📊 Componente Variable (Estrategia DCA)")
        pct_rv = st.slider("Porcentaje asignado a Renta Variable (DCA) (%)", min_value=0, max_value=100, value=int(cfg.get('pct_renta_variable', 30)))
        rend_rv = st.number_input("Rendimiento Anual Estimado Renta Variable (%)", value=float(cfg.get('rend_variable_est', 12.0)), step=0.5)
        volatilidad_rv = st.number_input("Volatilidad Histórica (Desviación Estándar) (%)", value=float(cfg.get('volatilidad_est', 15.0)), step=1.0)
        ahorro_actualizado = {"monto_mensual": monto_ahorro_mensual, "tasa_inflacion": tasa_inflacion_est, "tasa_rendimiento": tasa_cetes_est, "pct_renta_variable": float(pct_rv), "rend_variable_est": rend_rv, "volatilidad_est": volatilidad_rv}
    with c_ant2:
        st.subheader("📈 Proyección Comparativa a 5 Años")
        np.random.seed(42)
        meses_proyeccion = 60
        historial_ahorro = []
        acumulado_nominal, acumulado_real_inflacion, acumulado_renta_fija, acumulado_dca_rf, acumulado_dca_rv = 0.0, 0.0, 0.0, 0.0, 0.0
        inf_mensual, rf_mensual, rv_mensual_esperada, vol_mensual = (tasa_inflacion_est / 100) / 12, (tasa_cetes_est / 100) / 12, (rend_rv / 100) / 12, (volatilidad_rv / 100) / np.sqrt(12)
        monto_rf_puro, monto_rv_puro = monto_ahorro_mensual * (1 - (pct_rv / 100)), monto_ahorro_mensual * (pct_rv / 100)
        for m in range(1, meses_proyeccion + 1):
            acumulado_nominal += monto_ahorro_mensual
            acumulado_real_inflacion = (acumulado_real_inflacion + monto_ahorro_mensual) * (1 - inf_mensual)
            acumulado_renta_fija = (acumulado_renta_fija + monto_ahorro_mensual) * (1 + rf_mensual)
            acumulado_dca_rf = (acumulado_dca_rf + monto_rf_puro) * (1 + rf_mensual)
            rendimiento_mercado_este_mes = rv_mensual_esperada + (vol_mensual * np.random.normal(0, 1))
            acumulado_dca_rv = (acumulado_dca_rv + monto_rv_puro) * (1 + rendimiento_mercado_este_mes)
            if m in [12, 24, 36, 48, 60]:
                historial_ahorro.append({"Año": f"Año {m//12}", "Tanda (Efectivo)": round(acumulado_nominal, 2), "Poder de Compra Real": round(acumulado_real_inflacion, 2), "100% Renta Fija (CETES)": round(acumulado_renta_fija, 2), "Portafolio DCA Híbrido": round(acumulado_dca_rf + acumulado_dca_rv, 2)})
        df_ahorro = pd.DataFrame(historial_ahorro)
        st.bar_chart(df_ahorro.set_index("Año"))

with tab_bitacora:
    st.header("📝 Historial y Registro de Abonos")
    c_bit1, c_bit2 = st.columns([1, 2])
    with c_bit1:
        st.subheader("📥 Registrar Nuevo Abono")
        nombres_deudas_activas = [d['nombre'] for d in deudas_procesadas]
        deuda_seleccionada = st.selectbox("Selecciona la Deuda que pagaste:", nombres_deudas_activas if nombres_deudas_activas else ["Sin deudas"])
        monto_abonado = st.number_input("Monto total depositado ($)", min_value=1.0, value=1000.0, step=100.0)
        notas_pago = st.text_input("Notas (ej. 'Mensualidad Mayo')", value="")
        if st.button("🚀 Registrar Abono en Bitácora", type="primary", use_container_width=True) and nombres_deudas_activas:
            registrar_pago(deuda_seleccionada, monto_abonado, notas_pago)
            st.success("¡Abono registrado!"); st.rerun()
    with c_bit2:
        st.subheader("📋 Registro Histórico de Operaciones")
        df_pagos = obtener_historial_pagos()
        if df_pagos.empty: st.info("Sin abonos registrados.")
        else:
            st.metric("Total Amortizado", f"${df_pagos['Monto Abonado ($)'].sum():,.2f} MXN")
            st.dataframe(df_pagos, use_container_width=True)
            if st.button("🗑️ Limpiar Bitácora Completa"): limpiar_bitacora(); st.rerun()

# ==========================================
# 🎪 NUEVA PESTAÑA 5: GESTIÓN DE EVENTOS Y FLUJO FINAL
# ==========================================
with tab_eventos:
    st.header("🎪 Control de Gastos por Eventos Especiales")
    st.markdown("Administra proyectos extraordinarios (viajes, reparaciones, fiestas) sin alterar tu presupuesto mensual base.")
    
    col_ev1, col_ev2 = st.columns([1, 2])
    
    with col_ev1:
        st.subheader("🆕 Crear o Eliminar Eventos")
        nuevo_ev_nombre = st.text_input("Nombre del Evento (ej. 'Viaje Acapulco', 'Fisura Auto')", value="")
        nuevo_ev_presupuesto = st.number_input("Presupuesto Máximo Asignado ($)", min_value=100.0, value=5000.0, step=500.0)
        
        if st.button("➕ Dar de Alta Evento", type="primary", use_container_width=True):
            if nuevo_ev_nombre:
                crear_evento(nuevo_ev_nombre, nuevo_ev_presupuesto)
                st.success(f"Evento '{nuevo_ev_nombre}' creado.")
                st.rerun()
                
        st.write("---")
        st.subheader("💸 Cargar Gasto a un Evento")
        lista_eventos = obtener_eventos()
        
        if lista_eventos:
            dict_eventos = {e['nombre']: e['id'] for e in lista_eventos}
            ev_seleccionado = st.selectbox("Selecciona el Evento:", list(dict_eventos.keys()))
            concepto_gasto_ev = st.text_input("Concepto del Gasto (ej. 'Casetas', 'Refacción')", value="")
            monto_gasto_ev = st.number_input("Monto Gastado ($)", min_value=1.0, value=200.0, step=50.0)
            
            if st.button("📉 Registrar Gasto en Evento", use_container_width=True):
                if concepto_gasto_ev:
                    agregar_gasto_evento(dict_eventos[ev_seleccionado], concepto_gasto_ev, monto_gasto_ev)
                    st.success("Gasto cargado exitosamente.")
                    st.rerun()
        else:
            st.info("Crea un evento primero para poder asignarle gastos.")

    with col_ev2:
        st.subheader("📊 Monitor de Proyectos y Presupuestos Activos")
        lista_eventos_activos = obtener_eventos()
        
        total_gastado_todos_los_eventos = 0.0
        
        if not lista_eventos_activos:
            st.info("No hay eventos especiales activos este mes.")
        else:
            for ev in lista_eventos_activos:
                df_gastos_ev = obtener_gastos_de_evento(ev['id'])
                gastos_totales_ev = df_gastos_ev["Monto ($)"].sum() if not df_gastos_ev.empty else 0.0
                total_gastado_todos_los_eventos += gastos_totales_ev
                
                # Visualización tipo Tarjeta por cada evento
                with st.expander(f"🎪 {ev['nombre']} — Progreso: ${gastos_totales_ev:,.2f} / ${ev['presupuesto_limite']:,.2f}", expanded=True):
                    c_tar1, c_tar2 = st.columns([3, 1])
                    with c_tar1:
                        # Barra de progreso visual
                        porcentaje = min(gastos_totales_ev / ev['presupuesto_limite'], 1.0) if ev['presupuesto_limite'] > 0 else 0.0
                        st.progress(porcentaje)
                        st.dataframe(df_gastos_ev, use_container_width=True)
                    with c_tar2:
                        remanente_ev = ev['presupuesto_limite'] - gastos_totales_ev
                        st.metric("Disponible", f"${remanente_ev:,.2f}")
                        if st.button("🗑️ Cerrar", key=f"del_ev_{ev['id']}"):
                            eliminar_evento(ev['id'])
                            st.rerun()

        # ==========================================
        # 🔥 EL CORAZÓN DE TU SOLICITUD: FLUJO DE EFECTIVO FINAL
        # ==========================================
        st.write("---")
        st.header("🔀 Distribuidor de Flujo de Efectivo Final de Mes")
        st.markdown("Este es el cálculo neto integrando tus cuentas fijas mensuales y el impacto de tus eventos extraordinarios:")
        
        flujo_operativo_base = total_ingresos - total_egresos
        flujo_neto_efectivo_disponible = flujo_operativo_base - total_gastado_todos_los_eventos
        
        f1, f2, f3 = st.columns(3)
        f1.metric("Flujo Base Mensual", f"${flujo_operativo_base:,.2f} MXN")
        f2.metric("Gastos en Eventos", f"${total_gastado_todos_los_eventos:,.2f} MXN", delta_color="inverse")
        
        if flujo_neto_efectivo_disponible >= 0:
            f3.metric("🔥 Excedente Líquido", f"${flujo_neto_efectivo_disponible:,.2f} MXN", "Dinero Libre", delta_color="normal")
            st.success(f"¡Felicidades! Tienes un excedente real de **${flujo_neto_efectivo_disponible:,.2f} MXN** al cierre de mes. ¿A dónde deseas inyectar este capital extra?")
            
            # Botonera de Acción Financiera Directa
            col_acc1, col_acc2 = st.columns(2)
            with col_acc1:
                if st.button("⚡ Enviar Todo a Aceleración de Deuda (Abono Especial)", type="primary", use_container_width=True):
                    # Inyectamos directo a la primera deuda activa como ejemplo dinámico
                    if nombres_deudas_activas:
                        registrar_pago(nombres_deudas_activas[0], flujo_neto_efectivo_disponible, "Inyección de excedente de fin de mes (Control de Eventos)")
                        st.balloons()
                        st.success(f"¡Dinero enviado! Se registró un abono de ${flujo_neto_efectivo_disponible:,.2f} a la deuda '{nombres_deudas_activas[0]}'.")
                    else:
                        st.info("No tienes deudas activas para amortizar.")
            with col_acc2:
                if st.button("📈 Enviar Todo al Portafolio de Inversión (DCA)", use_container_width=True):
                    st.balloons()
                    st.success(f"¡Estrategia ejecutada! Se programó la compra extraordinaria de ${flujo_neto_efectivo_disponible:,.2f} MXN en tu portafolio bajo la metodología Dollar Cost Averaging.")
        else:
            f3.metric("🚨 Déficit de Caja", f"${flujo_neto_efectivo_disponible:,.2f} MXN", "Alerta de Ajuste", delta_color="inverse")
            st.error(f"¡Atención! Debido a los gastos de tus eventos, estás sobregirado este mes por **${abs(flujo_neto_efectivo_disponible):,.2f} MXN**. Se recomienda recortar gastos variables o no realizar aportaciones extraordinarias.")

# ==========================================
# ACTUALIZACIÓN GLOBAL Y SYNC DE SESIÓN
# ==========================================
st.session_state.ingresos = ingresos_procesados
st.session_state.egresos = egresos_procesados
st.session_state.lista_deudas = deudas_procesadas
st.session_state.ahorro_config = ahorro_actualizado

with st.sidebar:
    st.header("⚙️ Menú de Datos")
    if st.button("💾 Guardar Configuración", type="primary", use_container_width=True):
        guardar_datos_completos(st.session_state.ingresos, st.session_state.egresos, st.session_state.lista_deudas, st.session_state.ahorro_config)
        st.sidebar.success("¡Configuración guardada en SQLite!")