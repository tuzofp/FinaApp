# 💰 FinaApp Pro: Ecosistema Inteligente de Finanzas Personales

FinaApp Pro es una aplicación web interactiva de gestión financiera integral desarrollada en **Python** y **Streamlit**, respaldada por una arquitectura de base de datos relacional local en **SQLite**. 

A diferencia de un presupuesto tradicional, esta plataforma fusiona el control operativo diario con potentes motores algorítmicos y proyecciones matemáticas avanzadas para optimizar la toma de decisiones económicas.

---

## 🚀 Características Clave (Módulos Core)

### 1. 📊 Control de Presupuesto e Ingresos
* Diagnóstico automatizado de capacidad de pago y flujo de caja libre.
* Clasificación y persistencia local de ingresos y egresos fijos.

### 2. ⚡ Plan de Choque contra Deudas (Motor Algorítmico)
* Implementación de estrategias de aceleración financiera: **Método Avalancha** (priorización por tasa de interés más alta) y **Método Bola de Nieve** (priorización por saldo menor).
* Generación de curvas dinámicas de amortización y calendarios proyectados de liquidación mediante manipulación de datos con **Pandas**.

### 3. 📉 Simulación de Inversión Estratégica & Dollar Cost Averaging (DCA)
* Comparativa interactiva de pérdida de poder adquisitivo por inflación vs. instrumentos de Renta Fija (CETES) vs. Renta Variable.
* **Modelo Estocástico Ligero:** Simulación de fluctuaciones de mercado aplicando una distribución normal basada en volatilidad histórica para proyectar el beneficio real del DCA en activos de renta variable a 5 años.

### 4. 📝 Bitácora Histórica de Pagos Reales
* Registro transaccional con marcas de tiempo automáticas en SQLite para auditar abonos reales y visualizar el capital total amortizado.

### 5. 🎪 Presupuesto por Eventos & Distribuidor de Flujo
* Aislamiento de gastos extraordinarios (viajes, proyectos, imprevistos) mediante lógica relacional de cascada (`ON DELETE CASCADE`).
* Cálculo del **Excedente Líquido Neto** de fin de mes con interactividad para inyectar capital de forma inmediata al portafolio DCA o a la reducción de deudas.

---

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3
* **Framework Frontend:** Streamlit
* **Procesamiento de Datos:** Pandas y NumPy (Cálculo estocástico y matrices)
* **Base de Datos:** SQLite3 (Persistencia SQL local)
* **Entorno de Desarrollo:** WSL (Windows Subsystem for Linux)

---

## 💻 Instalación y Uso

Si deseas replicar este entorno de forma local, asegúrate de tener Python 3 instalado y sigue estos pasos desde tu terminal:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/TU_USUARIO/FinaApp.git](https://github.com/TU_USUARIO/FinaApp.git)
   cd FinaApp

2. Instalar dependencias necesarias
    pip install -r requirements.txt

3. Ejecutar la aplicación
    streamlit run app.py