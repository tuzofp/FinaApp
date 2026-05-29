import sqlite3
from datetime import datetime
import pandas as pd

DB_NAME = "finaapp.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def inicializar_bd():
    conn = conectar()
    cursor = conn.cursor()
    
    # Tablas previas estables
    cursor.execute("CREATE TABLE IF NOT EXISTS ingresos (id INTEGER PRIMARY KEY AUTOINCREMENT, concepto TEXT NOT NULL, monto REAL NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS egresos (id INTEGER PRIMARY KEY AUTOINCREMENT, concepto TEXT NOT NULL, monto REAL NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS deudas (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, tipo TEXT NOT NULL, saldo REAL NOT NULL, tasa_anual REAL NOT NULL, pago_minimo REAL NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS ahorro (id INTEGER PRIMARY KEY AUTOINCREMENT, monto_mensual REAL NOT NULL, tasa_inflacion REAL NOT NULL, tasa_rendimiento REAL NOT NULL, pct_renta_variable REAL DEFAULT 0.0, rend_variable_est REAL DEFAULT 12.0, volatilidad_est REAL DEFAULT 15.0)")
    cursor.execute("CREATE TABLE IF NOT EXISTS pagos_historicos (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL, deuda_nombre TEXT NOT NULL, monto_pagado REAL NOT NULL, notas TEXT)")
    
    # 6. NUEVA TABLA: Eventos Especiales
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            presupuesto_limite REAL NOT NULL
        )
    """)
    
    # 7. NUEVA TABLA: Gastos por Evento
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos_evento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evento_id INTEGER NOT NULL,
            concepto TEXT NOT NULL,
            monto REAL NOT NULL,
            FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE
        )
    """)
    
    # Semillas básicas si está vacía
    cursor.execute("SELECT COUNT(*) FROM ingresos")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO ingresos (concepto, monto) VALUES (?, ?)", [("Sueldo Neto", 18000.0), ("Freelance / Negocio", 3000.0)])
        cursor.executemany("INSERT INTO egresos (concepto, monto) VALUES (?, ?)", [("Renta / Hipoteca", 5000.0), ("Despensa / Comida", 3500.0), ("Servicios (Luz, Agua)", 1200.0), ("Transporte / Gasolina", 1800.0)])
        cursor.executemany("INSERT INTO deudas (nombre, tipo, saldo, tasa_anual, pago_minimo) VALUES (?, ?, ?, ?, ?)", [("Tarjeta Oro", "Tarjeta de Crédito", 45000.0, 75.0, 2200.0), ("Préstamo Bancario", "Préstamo Personal", 25000.0, 35.0, 1500.0)])
        cursor.execute("INSERT INTO ahorro (monto_mensual, tasa_inflacion, tasa_rendimiento, pct_renta_variable, rend_variable_est, volatilidad_est) VALUES (?, ?, ?, ?, ?, ?)", (2000.0, 4.5, 11.0, 30.0, 12.0, 15.0))
        
    conn.commit()
    conn.close()

# --- FUNCIONES DE PERSISTENCIA ANTERIORES ---
def obtener_datos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT concepto, monto FROM ingresos")
    ingresos = [{"concepto": r[0], "monto": r[1]} for r in cursor.fetchall()]
    cursor.execute("SELECT concepto, monto FROM egresos")
    egresos = [{"concepto": r[0], "monto": r[1]} for r in cursor.fetchall()]
    cursor.execute("SELECT nombre, tipo, saldo, tasa_anual, pago_minimo FROM deudas")
    deudas = [{"nombre": r[0], "tipo": r[1], "saldo": r[2], "tasa_anual": r[3], "pago_minimo": r[4]} for r in cursor.fetchall()]
    cursor.execute("SELECT monto_mensual, tasa_inflacion, tasa_rendimiento, pct_renta_variable, rend_variable_est, volatilidad_est FROM ahorro ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    ahorro = {"monto_mensual": row[0], "tasa_inflacion": row[1], "tasa_rendimiento": row[2], "pct_renta_variable": row[3], "rend_variable_est": row[4], "volatilidad_est": row[5]} if row else {"monto_mensual": 2000.0, "tasa_inflacion": 4.5, "tasa_rendimiento": 11.0, "pct_renta_variable": 30.0, "rend_variable_est": 12.0, "volatilidad_est": 15.0}
    conn.close()
    return ingresos, egresos, deudas, ahorro

def guardar_datos_completos(ingresos, egresos, deudas, ahorro):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ingresos")
    cursor.execute("DELETE FROM egresos")
    cursor.execute("DELETE FROM deudas")
    cursor.execute("DROP TABLE IF EXISTS ahorro")
    cursor.execute("CREATE TABLE IF NOT EXISTS ahorro (id INTEGER PRIMARY KEY AUTOINCREMENT, monto_mensual REAL NOT NULL, tasa_inflacion REAL NOT NULL, tasa_rendimiento REAL NOT NULL, pct_renta_variable REAL, rend_variable_est REAL, volatilidad_est REAL)")
    for i in ingresos: cursor.execute("INSERT INTO ingresos (concepto, monto) VALUES (?, ?)", (i['concepto'], i['monto']))
    for e in egresos: cursor.execute("INSERT INTO egresos (concepto, monto) VALUES (?, ?)", (e['concepto'], e['monto']))
    for d in deudas: cursor.execute("INSERT INTO deudas (nombre, tipo, saldo, tasa_anual, pago_minimo) VALUES (?, ?, ?, ?, ?)", (d['nombre'], d['tipo'], d['saldo'], d['tasa_anual'], d['pago_minimo']))
    cursor.execute("INSERT INTO ahorro (monto_mensual, tasa_inflacion, tasa_rendimiento, pct_renta_variable, rend_variable_est, volatilidad_est) VALUES (?, ?, ?, ?, ?, ?)", (ahorro['monto_mensual'], ahorro['tasa_inflacion'], ahorro['tasa_rendimiento'], ahorro['pct_renta_variable'], ahorro['rend_variable_est'], ahorro['volatilidad_est']))
    conn.commit()
    conn.close()

def registrar_pago(deuda_nombre, monto, notas=""):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pagos_historicos (fecha, deuda_nombre, monto_pagado, notas) VALUES (?, ?, ?, ?)", (datetime.now().strftime("%Y-%m-%d %H:%M"), deuda_nombre, monto, notas))
    conn.commit()
    conn.close()

def obtener_historial_pagos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT fecha, deuda_nombre, monto_pagado, notas FROM pagos_historicos ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return pd.DataFrame(rows, columns=["Fecha/Hora", "Deuda", "Monto Abonado ($)", "Notas/Comentarios"])

def limpiar_bitacora():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pagos_historicos")
    conn.commit()
    conn.close()

# --- NUEVAS FUNCIONES PARA EL CONTROL DE EVENTOS ---
def crear_evento(nombre, presupuesto):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO eventos (nombre, presupuesto_limite) VALUES (?, ?)", (nombre, presupuesto))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Si el evento ya existe, lo ignoramos de forma segura
    conn.close()

def eliminar_evento(evento_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM eventos WHERE id = ?", (evento_id,))
    cursor.execute("DELETE FROM gastos_evento WHERE evento_id = ?", (evento_id,))
    conn.commit()
    conn.close()

def obtener_eventos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, presupuesto_limite FROM eventos")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "nombre": r[1], "presupuesto_limite": r[2]} for r in rows]

def agregar_gasto_evento(evento_id, concepto, monto):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO gastos_evento (evento_id, concepto, monto) VALUES (?, ?, ?)", (evento_id, concepto, monto))
    conn.commit()
    conn.close()

def obtener_gastos_de_evento(evento_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT concepto, monto FROM gastos_evento WHERE evento_id = ?", (evento_id,))
    rows = cursor.fetchall()
    conn.close()
    return pd.DataFrame(rows, columns=["Concepto Gasto", "Monto ($)"])