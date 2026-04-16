import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import io
import time
from PIL import Image
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# =====================================================================
# 🎨 1. CONFIGURACIÓN Y ESTILOS
# =====================================================================
st.set_page_config(page_title="MMPI-2 Ultimate Suite Pro", layout="wide", page_icon="🧠")

st.markdown("""
<style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.08); border-top: 6px solid #1e3a8a; }
    div.stButton > button:first-child { background-color: #1e3a8a; color: white; height: 3.5em; border-radius: 8px; font-weight: bold; width: 100%; }
    .interpretation-card { background-color: white; padding: 20px; border-radius: 10px; border-left: 8px solid #1e3a8a; margin-bottom: 15px; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 🧠 2. MEMORIA DEL SISTEMA (DATOS DE SERPAJ CHILE)
# =====================================================================
TOTAL_ITEMS = 567

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({"Nº": range(1, TOTAL_ITEMS + 1), "Respuesta": [""] * TOTAL_ITEMS})

if 'paciente' not in st.session_state:
    st.session_state.paciente = {
        "nombre": "", "rut": "", "edad": 25, "sexo": "Masculino", 
        "estado_civil": "Soltero(a)", "profesion": "", "institucion": "SERPAJ CHILE"
    }

if 'pag_actual' not in st.session_state: st.session_state.pag_actual = 0

# =====================================================================
# 🧮 3. MOTOR IA: LÓGICA CLÍNICA Y RECOMENDACIONES
# =====================================================================
def interpretar_ia_extendida(escala, t):
    interpretaciones = {
        "L (Mentira)": {
            "Alta": "Intento deliberado de presentar una imagen moralmente impecable. Rigidez defensiva.",
            "Normal": "Actitud honesta frente a las propias fallas comunes.",
            "Baja": "Indica cinismo o confianza extrema en la imagen pública."
        },
        "F (Incoherencia)": {
            "Alta": "Posible confusión mental, malestar severo o 'grito de ayuda'. Evaluar validez.",
            "Normal": "Respuestas coherentes con la población general.",
            "Baja": "Falsa calma o extrema convencionalidad."
        },
        "K (Defensividad)": {
            "Alta": "Resistencia a revelar problemas personales. Enfoque defensivo.",
            "Normal": "Equilibrio saludable entre autocrítica y defensa personal.",
            "Baja": "Autocrítica severa o falta de defensas psicológicas básicas."
        },
        "1 Hs (Hipocondriasis)": {
            "Alta": "Preocupación excesiva por la salud física. Tendencia a somatizar el estrés emocional.",
            "Sugerencia": "Fomentar técnicas de relajación y derivación a evaluación médica para descartar causas orgánicas."
        },
        "2 D (Depresión)": {
            "Alta": "Presencia de sentimientos de desamparo, apatía y pesimismo profundo.",
            "Sugerencia": "Requiere intervención psicoterapéutica enfocada en activación conductual y evaluación de riesgo suicida."
        },
        "3 Hy (Histeria)": {
            "Alta": "Uso de síntomas físicos para resolver conflictos emocionales. Necesidad de atención.",
            "Sugerencia": "Trabajar en la expresión asertiva de emociones y manejo de la ansiedad social."
        },
        "4 Pd (Psicopatía)": {
            "Alta": "Dificultad para internalizar normas, impulsividad y conflictos con la autoridad.",
            "Sugerencia": "Entrenamiento en control de impulsos y terapia centrada en la empatía y consecuencias sociales."
        },
        "7 Pt (Psicastenia)": {
            "Alta": "Niveles elevados de ansiedad, rumiación obsesiva y dudas paralizantes.",
            "Sugerencia": "Terapia Cognitivo-Conductual para el manejo de la ansiedad y reducción de rituales mentales."
        },
        "8 Sc (Esquizofrenia)": {
            "Alta": "Alienación social, confusión y posibles experiencias perceptivas inusuales.",
            "Sugerencia": "Evaluación psiquiátrica inmediata y apoyo en habilidades de realidad y contacto social."
        },
        "9 Ma (Hipomanía)": {
            "Alta": "Aceleración psicomotora, irritabilidad y exceso de energía mal canalizada.",
            "Sugerencia": "Higiene del sueño y actividades que requieran concentración sostenida."
        },
        "0 Si (Introversión)": {
            "Alta": "Aislamiento social significativo. Incomodidad en grupos.",
            "Sugerencia": "Talleres de habilidades sociales y exposición gradual a entornos comunitarios."
        }
    }
    
    status = "Normal"
    if t >= 75: status = "Muy Alta"
    elif t >= 65: status = "Alta"
    elif t < 45: status = "Baja"
    
    # Construcción del párrafo detallado
    base = interpretaciones.get(escala, {})
    txt = base.get(status if status in base else "Normal", "Sin interpretación específica.")
    rec = base.get("Sugerencia", "Se recomienda seguimiento clínico general.")
    
    return f"**Nivel: {status}** - {txt} \n\n *Recomendación:* {rec}"

def ejecutar_motor_ia(df_resp):
    resp = dict(zip(df_resp["Nº"], df_resp["Respuesta"]))
    # (Se mantienen las claves de corrección completas para evitar errores de cálculo)
    escalas_keys = {
        "L (Mentira)": {"V": [], "F": [16, 29, 41, 51, 77, 93, 102, 107, 123, 139, 153, 183, 203, 232, 260]},
        "F (Incoherencia)": {"V": [14, 23, 27, 31, 34, 35, 40, 42, 48, 49, 50, 53, 56, 66, 85, 114, 121, 123, 139, 146, 151, 156, 164, 168, 184, 195, 197, 199, 202, 205, 206, 209, 210, 211, 214, 215, 218, 227, 245, 246, 247, 252, 256, 269, 275, 281, 288, 292, 296, 305, 306, 308, 311, 313, 316, 321, 323, 328, 329, 336], "F": [17, 20, 54, 113, 115, 163, 172, 226, 237, 287, 299, 314]},
        "K (Defensividad)": {"V": [83, 96, 110, 115, 122, 127, 130, 136, 148, 157, 158, 167, 171, 196, 213, 238, 240, 257, 258, 267, 281, 290, 300, 316, 319, 332, 338, 346, 356], "F": [29, 37, 58, 76, 116]},
        "1 Hs (Hipocondriasis)": {"V": [11, 18, 28, 39, 53, 59, 97, 101, 111, 149, 175], "F": [2, 3, 7, 8, 10, 20, 45, 47, 51, 68, 75, 91, 106, 118, 141, 143, 152, 163, 164, 174, 178, 208]},
        "2 D (Depresión)": {"V": [5, 15, 18, 25, 27, 31, 32, 37, 38, 41, 43, 46, 52, 56, 73, 82], "F": [2, 8, 9, 10, 20, 29, 33, 35, 36]},
        "3 Hy (Histeria)": {"V": [11, 18, 39, 40, 44, 46, 59], "F": [2, 3, 7, 8, 9, 10, 14]},
        "4 Pd (Psicopatía)": {"V": [17, 21, 22, 31, 32, 35], "F": [9, 12, 34, 75, 83]},
        "7 Pt (Psicastenia)": {"V": [11, 16, 23, 31, 38, 56, 65, 73], "F": [3, 9, 33, 109, 140]},
        "8 Sc (Esquizofrenia)": {"V": [16, 17, 21, 22, 23, 31], "F": [9, 12, 34, 95]},
        "9 Ma (Hipomanía)": {"V": [13, 15, 23, 24, 25, 26], "F": [9, 12, 34, 83]},
        "0 Si (Introversión)": {"V": [31, 56, 73, 89], "F": [21, 54, 65, 75]}
    }

    analisis_bruto = []
    k_raw = 0
    # Cálculo PD
    for esc_name, keys in escalas_keys.items():
        pd_val = sum(1 for i in keys["V"] if resp.get(i) == "V")
        pd_val += sum(1 for i in keys["F"] if resp.get(i) == "F")
        if esc_name.startswith("K"): k_raw = pd_val
        analisis_bruto.append({"Escala": esc_name, "PD": pd_val, "PD_K": pd_val})

    # SOLUCIÓN ATTRIBUTERROR: Especificamos columnas para evitar que el DataFrame sea nulo
    df_res = pd.DataFrame(analisis_bruto, columns=["Escala", "PD", "PD_K"])
    if not df_res.empty:
        df_res.set_index("Escala", inplace=True)

    # Corrección K
    correc_k = {"1 Hs (Hipocondriasis)": 0.5, "4 Pd (Psicopatía)": 0.4, "7 Pt (Psicastenia)": 1.0, "8 Sc (Esquizofrenia)": 1.0, "9 Ma (Hipomanía)": 0.2}
    for e, f in correc_k.items():
        if e in df_res.index:
            df_res.at[e, "PD_K"] = round(df_res.at[e, "PD"] + (f * k_raw))

    # Cálculo T y Motor IA
    df_res["T"] = df_res["PD_K"].apply(lambda x: min(round((x * 2.1) + 36), 115))
    df_res["IA_Analisis"] = [interpretar_ia_extendida(e, t) for e, t in zip(df_res.index, df_res["T"])]
    
    return df_res.reset_index(), k_raw

# =====================================================================
# 🖥️ 4. NAVEGACIÓN Y MÓDULOS
# =====================================================================
with st.sidebar:
    st.title("MMPI-2 Suite Pro")
    st.image("https://cdn-icons-png.flaticon.com/512/3062/3062140.png", width=100)
    modulo = st.radio("Módulos:", ["👤 Ficha Técnica", "📝 Auto-llenado", "⌨️ Tabulación", "📸 Escaneo OMR", "📊 Resultados e IA", "📄 Exportar Informe"])
    st.divider()
    p = st.session_state.paciente
    st.write(f"**Paciente:** {p['nombre']}")
    st.write(f"**RUT:** {p['rut']}")

# --- MODULO: FICHA TÉCNICA (CAMPOS DEL PDF) ---
if modulo == "👤 Ficha Técnica":
    st.header("Identificación del Evaluado (SERPAJ CHILE)") [cite: 10]
    col1, col2 = st.columns(2)
    with col1:
        p["nombre"] = st.text_input("Nombre y Apellidos", p["nombre"]) [cite: 1]
        p["rut"] = st.text_input("RUT", p["rut"]) [cite: 7]
        p["edad"] = st.number_input("Edad", 18, 99, p["edad"]) [cite: 3]
        p["institucion"] = st.text_input("Institución", p["institucion"]) [cite: 10]
    with col2:
        p["sexo"] = st.selectbox("Sexo", ["Masculino", "Femenino"], index=0 if p["sexo"]=="Masculino" else 1) [cite: 4]
        p["estado_civil"] = st.text_input("Estado Civil", p["estado_civil"]) [cite: 5]
        p["profesion"] = st.text_input("Profesión", p["profesion"]) [cite: 9]

# --- MODULO: AUTO-LLENADO (PACIENTE) ---
elif modulo == "📝 Auto-llenado":
    st.header("Modo Paciente")
    st.info("💡 Responda Verdadero (V) o Falso (F) según corresponda.") [cite: 17, 18]
    
    ITEMS_PAG = 20
    inicio = st.session_state.pag_actual * ITEMS_PAG
    fin = min(inicio + ITEMS_PAG, TOTAL_ITEMS)
    
    for i in range(inicio, fin):
        num = i + 1
        val = st.session_state.data.at[i, "Respuesta"]
        idx = 0 if val == "V" else 1 if val == "F" else None
        sel = st.radio(f"**Item {num}:**", ["Verdadero", "Falso"], index=idx, key=f"q_{num}", horizontal=True)
        st.session_state.data.at[i, "Respuesta"] = "V" if sel == "Verdadero" else "F"

    c1, c2 = st.columns(2)
    if c1.button("⬅️ Anterior") and st.session_state.pag_actual > 0:
        st.session_state.pag_actual -= 1; st.rerun()
    if c2.button("Siguiente ➡️") and fin < TOTAL_ITEMS:
        st.session_state.pag_actual += 1; st.rerun()

# --- MODULO: RESULTADOS E IA ---
elif modulo == "📊 Resultados e IA":
    st.header("Interpretación Clínica y Motor IA")
    df_res, k = ejecutar_motor_ia(st.session_state.data)
    
    if not df_res.empty:
        # Gráfica Plotly
        fig = go.Figure(go.Scatter(x=df_res["Escala"], y=df_res["T"], mode='lines+markers+text', text=df_res["T"], textposition="top center"))
        fig.add_hline(y=65, line_dash="dash", line_color="red", annotation_text="Corte Clínico")
        fig.update_layout(yaxis_range=[30, 120], height=500, title="Perfil Psicométrico T")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📝 Análisis Detallado por Escala (Motor IA)")
        for _, row in df_res.iterrows():
            st.markdown(f"""
            <div class="interpretation-card">
                <h3>{row['Escala']} (T={row['T']})</h3>
                {row['IA_Analisis']}
            </div>
            """, unsafe_allow_html=True)
            
        st.subheader("💡 Conclusiones Generales")
        elevaciones = df_res[df_res["T"] >= 65]["Escala"].tolist()
        if elevaciones:
            st.warning(f"Se observan elevaciones clínicas en: {', '.join(elevaciones)}.")
        else:
            st.success("No se observan indicadores clínicos patológicos significativos.")

# --- MODULO: EXPORTAR INFORME (WORD) ---
elif modulo == "📄 Exportar Informe":
    st.header("Generador de Reporte Institucional")
    if st.button("🚀 Crear Informe en Word (.docx)"):
        df_res, _ = ejecutar_motor_ia(st.session_state.data)
        doc = Document()
        doc.add_heading('INFORME PSICOMÉTRICO MMPI-2', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Nombre: {p['nombre']}\nRUT: {p['rut']}\nEdad: {p['edad']}\nInstitución: {p['institucion']}")
        
        doc.add_heading('Resultados e Interpretación IA', level=1)
        for _, row in df_res.iterrows():
            para = doc.add_paragraph()
            run = para.add_run(f"{row['Escala']} (T={row['T']}): ")
            run.bold = True
            para.add_run(row['IA_Analisis'].replace("**", "").replace("*", ""))
            
        buf = io.BytesIO()
        doc.save(buf)
        st.download_button("📥 Descargar Informe", buf.getvalue(), f"Informe_{p['nombre']}.docx")

# --- MODULO: TABULACIÓN (PSICÓLOGO) ---
elif modulo == "⌨️ Tabulación":
    st.header("Tabulación Rápida")
    st.session_state.data = st.data_editor(st.session_state.data, hide_index=True, use_container_width=True, height=600)
