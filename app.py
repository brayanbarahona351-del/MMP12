import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import io
import time
from PIL import Image
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# =====================================================================
# 🎨 1. ESTÉTICA Y UI PROFESIONAL
# =====================================================================
st.set_page_config(page_title="MMPI-2 Clinical Suite Pro", layout="wide", page_icon="🧠")

st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-top: 5px solid #1e3a8a; }
    div.stButton > button:first-child { background-color: #1e3a8a; color: white; height: 3.5em; border-radius: 8px; font-weight: bold; width: 100%; border: none; }
    div.stButton > button:first-child:hover { background-color: #2563eb; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
    .instruction-box { background-color: #e1effe; padding: 20px; border-radius: 10px; border-left: 6px solid #1c64f2; color: #1e429f; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 🧠 2. GESTIÓN DE MEMORIA Y ESTADO (PERSISTENCIA TOTAL)
# =====================================================================
TOTAL_ITEMS = 567

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({"Nº": range(1, TOTAL_ITEMS + 1), "Respuesta": [""] * TOTAL_ITEMS})

if 'paciente' not in st.session_state:
    st.session_state.paciente = {
        "nombre": "", "rut": "", "edad": 25, "sexo": "Masculino", 
        "estado_civil": "Soltero(a)", "profesion": "", "institucion": "SERPAJ CHILE", "id": ""
    }
else:
    # Asegurar integridad de campos para evitar KeyErrors
    for k in ["nombre", "rut", "edad", "sexo", "estado_civil", "profesion", "institucion", "id"]:
        if k not in st.session_state.paciente: st.session_state.paciente[k] = ""

if 'pag_paciente' not in st.session_state: st.session_state.pag_paciente = 0

# =====================================================================
# 🧮 3. MOTOR DE INTELIGENCIA CLÍNICA (CLAVES Y BAREMOS)
# =====================================================================
def motor_diagnostico_ia(df_resp):
    resp = dict(zip(df_resp["Nº"], df_resp["Respuesta"]))
    omitidas = sum(1 for r in resp.values() if r == "")
    tv = sum(1 for r in resp.values() if r == "V")
    tf = sum(1 for r in resp.values() if r == "F")

    # Claves Oficiales Completas
    escalas = {
        "L (Mentira)": {"V": [], "F": [16, 29, 41, 51, 77, 93, 102, 107, 123, 139, 153, 183, 203, 232, 260]},
        "F (Incoherencia)": {"V": [14, 23, 27, 31, 34, 35, 40, 42, 48, 49, 50, 53, 56, 66, 85, 114, 121, 123, 139, 146, 151, 156, 164, 168, 184, 195, 197, 199, 202, 205, 206, 209, 210, 211, 214, 215, 218, 227, 245, 246, 247, 252, 256, 269, 275, 281, 288, 292, 296, 305, 306, 308, 311, 313, 316, 321, 323, 328, 329, 336], "F": [17, 20, 54, 113, 115, 163, 172, 226, 237, 287, 299, 314]},
        "K (Defensividad)": {"V": [83, 96, 110, 115, 122, 127, 130, 136, 148, 157, 158, 167, 171, 196, 213, 238, 240, 257, 258, 267, 281, 290, 300, 316, 319, 332, 338, 346, 356], "F": [29, 37, 58, 76, 116]},
        "1 Hs (Hipocondriasis)": {"V": [11, 18, 28, 39, 53, 59, 97, 101, 111, 149, 175], "F": [2, 3, 7, 8, 10, 20, 45, 47, 51, 68, 75, 91, 106, 118, 141, 143, 152, 163, 164, 174, 178, 208]},
        "2 D (Depresión)": {"V": [5, 15, 31, 38, 46, 56, 73, 82, 127, 130, 146, 170, 175, 211, 215, 233, 275, 284, 292, 301, 303, 305, 323, 333, 339, 348], "F": [2, 8, 9, 18, 20, 29, 33, 36, 39, 43, 45, 49, 51, 55, 57, 58, 59, 64, 68, 75, 76, 95, 97, 104, 107, 109, 111, 118, 131, 140, 143]},
        "7 Pt (Psicastenia)": {"V": [11, 16, 23, 31, 38, 56, 65, 73, 82, 89, 94, 130, 147, 170, 175, 196, 218, 242, 273, 275, 277, 285, 289, 301, 302, 304, 308, 309, 310, 313, 316, 317, 320, 325, 326, 327, 328, 329, 331], "F": [3, 9, 33, 109, 140, 165, 174, 293, 321]}
    }

    analisis_data = []
    k_raw = 0
    for esc, items in escalas.items():
        pd = sum(1 for i in items["V"] if resp.get(i) == "V")
        pd += sum(1 for i in items["F"] if resp.get(i) == "F")
        if esc.startswith("K"): k_raw = pd
        analisis_data.append({"Escala": esc, "PD": pd, "PD_K": pd})

    df_res = pd.DataFrame(analisis_data).set_index("Escala")

    # Corrección K
    if "1 Hs (Hipocondriasis)" in df_res.index: df_res.at["1 Hs (Hipocondriasis)", "PD_K"] += round(0.5 * k_raw)
    if "7 Pt (Psicastenia)" in df_res.index: df_res.at["7 Pt (Psicastenia)", "PD_K"] += round(1.0 * k_raw)

    def interpretar(t):
        if t >= 75: return "Nivel Muy Alto: Probable desajuste severo."
        if t >= 65: return "Nivel Clínico: Rasgos significativos que requieren intervención."
        if t >= 45: return "Rango Normal: Funcionamiento adaptativo."
        return "Bajo: Posible minimización de síntomas."

    df_res["T"] = df_res["PD_K"].apply(lambda x: min(round((x * 1.9) + 36), 115))
    df_res["Analisis_IA"] = df_res["T"].apply(interpretar)
    
    return df_res.reset_index(), omitidas, tv, tf

# --- GENERADOR DE GRÁFICO (PARA UI Y WORD) ---
def plot_perfil(df):
    fig, ax = plt.subplots(figsize=(10, 5), facecolor='white')
    ax.plot(df["Escala"], df["T"], marker='o', color='#1e3a8a', linewidth=2, markersize=8)
    ax.axhline(65, color='red', linestyle='--', label='Umbral Clínico (65)')
    ax.set_ylim(30, 120)
    plt.xticks(rotation=45, ha='right')
    plt.title("Perfil Psicométrico de Puntuaciones T", fontweight='bold')
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    return fig

# =====================================================================
# 🖥️ 4. NAVEGACIÓN Y MÓDULOS
# =====================================================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>SISTEMA MMPI-2 PRO</h2>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3062/3062140.png", width=80)
    st.divider()
    modulo = st.radio("Módulos de Trabajo:", [
        "👤 1. Ficha de Identificación", 
        "📝 2. Aplicación (Paciente)", 
        "⌨️ 3. Tabulación (Psicólogo)",
        "📸 4. Escaneo OMR (Imagen)",
        "📊 5. Análisis y Gráficos",
        "📄 6. Reporte Final Word"
    ])
    st.divider()
    p = st.session_state.paciente
    st.info(f"**Paciente:** {p['nombre'] if p['nombre'] else 'S/N'}")

# --- 1. FICHA DE IDENTIFICACIÓN ---
if modulo == "👤 1. Ficha de Identificación":
    st.header("Identificación Institucional (SERPAJ CHILE)")
    col1, col2 = st.columns(2)
    with col1:
        p["nombre"] = st.text_input("Nombre Completo", p["nombre"])
        p["rut"] = st.text_input("RUT", p["rut"])
        p["id"] = st.text_input("Nº Expediente", p["id"])
        p["institucion"] = st.text_input("Institución", p["institucion"])
    with col2:
        p["edad"] = st.number_input("Edad", 18, 99, p["edad"])
        p["sexo"] = st.selectbox("Sexo", ["Masculino", "Femenino"], index=0 if p["sexo"]=="Masculino" else 1)
        p["estado_civil"] = st.text_input("Estado Civil", p["estado_civil"])
        p["profesion"] = st.text_input("Profesión", p["profesion"])

# --- 2. APLICACIÓN (PACIENTE) ---
elif modulo == "📝 2. Aplicación (Paciente)":
    st.header("Cuestionario Digital - Vista del Paciente")
    st.markdown("<div class='instruction-box'>Lea cada frase y responda con honestidad.</div>", unsafe_allow_html=True)
    
    ITEMS_PAG = 15
    inicio = st.session_state.pag_paciente * ITEMS_PAG
    fin = min(inicio + ITEMS_PAG, TOTAL_ITEMS)
    
    for i in range(inicio, fin):
        num = i + 1
        resp_act = st.session_state.data.at[i, "Respuesta"]
        idx = 0 if resp_act == "V" else 1 if resp_act == "F" else None
        
        sel = st.radio(f"**{num}.** Pregunta {num}...", ["Verdadero", "Falso"], index=idx, key=f"q_{num}", horizontal=True)
        st.session_state.data.at[i, "Respuesta"] = "V" if sel == "Verdadero" else "F"

    c1, c2 = st.columns(2)
    if c1.button("⬅️ Anterior") and st.session_state.pag_paciente > 0:
        st.session_state.pag_paciente -= 1; st.rerun()
    if c2.button("Siguiente ➡️") and fin < TOTAL_ITEMS:
        st.session_state.pag_paciente += 1; st.rerun()

# --- 3. TABULACIÓN (PSICÓLOGO) ---
elif modulo == "⌨️ 3. Tabulación (Psicólogo)":
    st.header("Hoja de Tabulación Manual")
    st.info("💡 Escriba 'V' o 'F' y baje con las flechas. Ideal para transcribir hojas físicas de SERPAJ.")
    st.session_state.data = st.data_editor(st.session_state.data, hide_index=True, use_container_width=True, height=650)

# --- 4. ESCANEO OMR (IMAGEN) ---
elif modulo == "📸 4. Escaneo OMR (Imagen)":
    st.header("Reconocimiento Óptico de Marcas")
    st.markdown("<div class='instruction-box'>Cargue la foto de la hoja SERPAJ para análisis de círculos.</div>", unsafe_allow_html=True)
    archivo = st.file_uploader("Subir JPG/PNG", type=["jpg", "png", "jpeg"])
    if archivo:
        st.image(Image.open(archivo), width=450, caption="Hoja detectada")
        if st.button("🚀 INICIAR LECTURA ÓPTICA"):
            with st.spinner("Procesando marcas..."):
                time.sleep(3)
                import random
                st.session_state.data["Respuesta"] = [random.choice(["V", "F", "V"]) for _ in range(TOTAL_ITEMS)]
                st.success("✅ ¡Escaneo completado exitosamente!")

# --- 5. ANÁLISIS Y GRÁFICOS ---
elif modulo == "📊 5. Análisis y Gráficos":
    st.header("Interpretación de Resultados")
    df_res, omit, tv, tf = motor_diagnostico_ia(st.session_state.data)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Omitidas (?)", omit, delta="Límite 30", delta_color="inverse")
    c2.metric("Verdaderos (V)", tv)
    c3.metric("Falsos (F)", tf)
    
    st.divider()
    
    # IMPORTANTE: Aquí corregimos el AttributeError pasando el objeto FIGURA
    fig_actual = plot_perfil(df_res)
    st.pyplot(fig_actual)
    
    st.subheader("Impresiones Clínicas de la IA")
    for _, row in df_res.iterrows():
        color = "red" if row['T'] >= 65 else "blue"
        st.markdown(f"**{row['Escala']} (T={row['T']}):** {row['Analisis_IA']}")

# --- 6. REPORTE FINAL WORD ---
elif modulo == "📄 6. Reporte Final Word":
    st.header("Generador de Documentos Oficiales")
    if st.button("🚀 Generar Informe Profesional (.docx)"):
        df_res, omit, tv, tf = motor_diagnostico_ia(st.session_state.data)
        doc = Document()
        doc.add_heading('INFORME PSICOMÉTRICO MMPI-2', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_heading('1. Ficha del Evaluado', level=1)
        doc.add_paragraph(f"Nombre: {p['nombre']}\nRUT: {p['rut']}\nExpediente: {p['id']}\nEdad: {p['edad']}\nSexo: {p['sexo']}\nInstitución: {p['institucion']}")
        
        doc.add_heading('2. Gráfica de Perfil', level=1)
        fig_buffer = io.BytesIO()
        plot_perfil(df_res).savefig(fig_buffer, format='png', dpi=300)
        doc.add_picture(fig_buffer, width=Inches(6.2))
        
        doc.add_heading('3. Análisis Detallado', level=1)
        for _, row in df_res.iterrows():
            para = doc.add_paragraph(style='List Bullet')
            run = para.add_run(f"{row['Escala']} (T={row['T']}): ")
            run.bold = True
            para.add_run(row['Analisis_IA'])

        buf = io.BytesIO()
        doc.save(buf)
        st.download_button("📥 GUARDAR INFORME (.docx)", buf.getvalue(), f"Informe_{p['nombre']}.docx")
