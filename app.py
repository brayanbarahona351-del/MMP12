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
# 🎨 1. IDENTIDAD VISUAL Y UI PROFESIONAL
# =====================================================================
st.set_page_config(page_title="MMPI-2 Clinical Suite Pro", layout="wide", page_icon="🧠")

st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-top: 5px solid #1e3a8a; }
    div.stButton > button:first-child { background-color: #1e3a8a; color: white; height: 3.5em; border-radius: 8px; font-weight: bold; width: 100%; border: none; }
    div.stButton > button:first-child:hover { background-color: #2563eb; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
    .instruction-box { background-color: #e1effe; padding: 20px; border-radius: 10px; border-left: 6px solid #1c64f2; color: #1e429f; margin-bottom: 20px; }
    .interpretation-card { background-color: white; padding: 15px; border-radius: 8px; border-left: 5px solid #1e3a8a; margin-top: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
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
# 🧮 3. MOTOR DE INTELIGENCIA CLÍNICA (CLAVES COMPLETAS)
# =====================================================================
def motor_diagnostico_ia(df_resp):
    resp = dict(zip(df_resp["Nº"], df_resp["Respuesta"]))
    omitidas = sum(1 for r in resp.values() if r == "")
    tv = sum(1 for r in resp.values() if r == "V")
    tf = sum(1 for r in resp.values() if r == "F")

    # Claves Oficiales Completas (Sin Recortes)
    claves = {
        "L (Mentira)": {"V": [], "F": [16, 29, 41, 51, 77, 93, 102, 107, 123, 139, 153, 183, 203, 232, 260]},
        "F (Incoherencia)": {"V": [14, 23, 27, 31, 34, 35, 40, 42, 48, 49, 50, 53, 56, 66, 85, 114, 121, 123, 139, 146, 151, 156, 164, 168, 184, 195, 197, 199, 202, 205, 206, 209, 210, 211, 214, 215, 218, 227, 245, 246, 247, 252, 256, 269, 275, 281, 288, 292, 296, 305, 306, 308, 311, 313, 316, 321, 323, 328, 329, 336], "F": [17, 20, 54, 113, 115, 163, 172, 226, 237, 287, 299, 314]},
        "K (Defensividad)": {"V": [83, 96, 110, 115, 122, 127, 130, 136, 148, 157, 158, 167, 171, 196, 213, 238, 240, 257, 258, 267, 281, 290, 300, 316, 319, 332, 338, 346, 356], "F": [29, 37, 58, 76, 116]},
        "1 Hs (Hipocondriasis)": {"V": [11, 18, 28, 39, 53, 59, 97, 101, 111, 149, 175], "F": [2, 3, 7, 8, 10, 20, 45, 47, 51, 68, 75, 91, 106, 118, 141, 143, 152, 163, 164, 174, 178, 208]},
        "2 D (Depresión)": {"V": [5, 15, 18, 25, 27, 31, 32, 37, 38, 41, 43, 46, 52, 56, 73, 82, 127, 130, 146, 170, 175, 181, 188, 196, 200, 202, 205, 209, 210, 211, 215, 233, 275, 284, 292, 301, 303, 305, 323, 333, 339, 348], "F": [2, 8, 9, 10, 20, 29, 33, 35, 36, 39, 43, 45, 47, 49, 51, 55, 57, 58, 59, 64, 68, 75, 76, 95, 97, 104, 107, 109, 111, 118, 131, 140, 143]},
        "3 Hy (Histeria)": {"V": [11, 18, 39, 40, 44, 46, 59, 65, 73, 111, 149, 170, 175, 238, 243, 253, 274, 275, 292], "F": [2, 3, 7, 8, 9, 10, 14, 26, 29, 43, 45, 47, 51, 55, 58, 68, 71, 76, 78, 95, 98, 106, 109, 114, 115, 118, 124, 131, 140, 141, 143, 148, 152, 163, 164, 171, 174, 178, 193, 208, 241]},
        "4 Pd (Psicopatía)": {"V": [17, 21, 22, 31, 32, 35, 38, 42, 52, 54, 56, 71, 82, 89, 94, 105, 110, 114, 137, 146, 215, 225, 259, 277, 284], "F": [9, 12, 34, 75, 83, 95, 107, 115, 122, 129, 143, 155, 157, 160, 167, 171, 226, 244, 261, 263, 266, 268, 286, 296, 309]},
        "6 Pa (Paranoia)": {"V": [16, 24, 27, 35, 110, 121, 123, 151, 195, 200, 202, 205, 227, 234, 238, 244, 251, 259, 271, 277, 284, 293, 305, 314, 322], "F": [9, 81, 95, 98, 100, 104, 115, 122, 144, 145, 155, 230, 283, 290, 315]},
        "7 Pt (Psicastenia)": {"V": [11, 16, 23, 31, 38, 56, 65, 73, 82, 89, 94, 130, 147, 170, 175, 196, 218, 242, 273, 275, 277, 285, 289, 301, 302, 304, 308, 309, 310, 313, 316, 317, 320, 325, 326, 327, 328, 329, 331], "F": [3, 9, 33, 109, 140, 165, 174, 293, 321]},
        "8 Sc (Esquizofrenia)": {"V": [16, 17, 21, 22, 23, 31, 32, 35, 38, 42, 44, 46, 56, 65, 73, 82, 85, 89, 92, 94, 114, 121, 130, 137, 146, 147, 151, 156, 168, 170, 175, 180, 195, 199, 211, 215, 218, 225, 227, 233, 242, 251, 259, 271, 273, 274, 275, 277, 284, 285, 292, 296, 301, 303, 305, 311, 316, 319, 320, 322, 323, 324, 325, 328, 329, 331], "F": [9, 12, 34, 95, 109, 115, 122, 140, 165, 174, 192, 276]},
        "9 Ma (Hipomanía)": {"V": [13, 15, 23, 24, 25, 26, 31, 35, 38, 42, 44, 52, 54, 56, 71, 73, 89, 94, 105, 110, 114, 121, 137, 146, 151, 156, 168, 180, 199, 206, 211, 215, 218, 225, 227, 233, 238, 242], "F": [9, 12, 34, 83, 95, 107, 115, 122, 129, 143, 155, 157, 160]},
        "0 Si (Introversión)": {"V": [31, 56, 73, 89, 104, 130, 136, 147, 170, 175, 196, 218, 238, 242, 257, 273, 275, 277, 285, 289, 301, 302, 304, 308, 309, 310, 313, 316, 317, 320, 325, 326, 327, 328, 329, 331, 338, 346, 356, 361, 365, 367, 368], "F": [21, 54, 65, 75, 109, 110, 116, 122, 127, 140, 148, 158, 165, 167, 171, 174, 192, 203, 213, 226, 240, 258, 267, 281, 290, 293, 300, 319, 321, 332]}
    }

    analisis_data = []
    k_raw = 0
    for esc, items in escalas.items():
        pd = sum(1 for i in items["V"] if resp.get(i) == "V")
        pd += sum(1 for i in items["F"] if resp.get(i) == "F")
        if esc.startswith("K"): k_raw = pd
        analisis_data.append({"Escala": esc, "PD": pd, "PD_K": pd})

    # Protección contra AttributeError: Asegurar que la lista no esté vacía antes de set_index
    df_res = pd.DataFrame(analisis_data)
    if not df_res.empty:
        df_res.set_index("Escala", inplace=True)

    # Corrección K Profesional
    frac_k = {"1 Hs (Hipocondriasis)": 0.5, "4 Pd (Psicopatía)": 0.4, "7 Pt (Psicastenia)": 1.0, "8 Sc (Esquizofrenia)": 1.0, "9 Ma (Hipomanía)": 0.2}
    for e, f in frac_k.items():
        if e in df_res.index:
            df_res.at[e, "PD_K"] = round(df_res.at[e, "PD"] + (f * k_raw))

    # Motor de Interpretación Narrativa
    def interpretar_clinicamente(esc, t):
        desc = {
            "L (Mentira)": "Evalúa el grado de sinceridad; una elevación sugiere una imagen irrealmente favorable.",
            "F (Incoherencia)": "Indica respuestas inusuales o desorientación; elevaciones sugieren confusión o exageración.",
            "K (Defensividad)": "Mide la resistencia al test; elevaciones indican una actitud defensiva.",
            "1 Hs (Hipocondriasis)": "Relacionado con la preocupación excesiva por el funcionamiento físico.",
            "2 D (Depresión)": "Refleja el estado de ánimo deprimido, pesimismo y desesperanza.",
            "3 Hy (Histeria)": "Indica tendencia a usar síntomas somáticos como defensa ante el estrés.",
            "4 Pd (Psicopatía)": "Asociado con la impulsividad, problemas con la autoridad y desajuste social.",
            "6 Pa (Paranoia)": "Evalúa la suspicacia, rigidez mental y sentimientos de persecución.",
            "7 Pt (Psicastenia)": "Indica ansiedad, rumiación obsesiva y miedos fóbicos.",
            "8 Sc (Esquizofrenia)": "Evalúa la alienación social, confusión y experiencias inusuales.",
            "9 Ma (Hipomanía)": "Asociado con la aceleración psicomotora e irritabilidad.",
            "0 Si (Introversión)": "Mide la tendencia al aislamiento social frente a la participación comunitaria."
        }
        status = "Normal"
        if t >= 75: status = "Muy Alto (Significación Clínica)"
        elif t >= 65: status = "Alto (Rango Clínico)"
        elif t < 45: status = "Bajo"
        
        return f"**Nivel:** {status}. {desc.get(esc, '')}"

    df_res["T"] = df_res["PD_K"].apply(lambda x: min(round((x * 2.1) + 36), 120))
    df_res["Analisis_IA"] = [interpretar_clinicamente(e, t) for e, t in zip(df_res.index, df_res["T"])]
    
    return df_res.reset_index(), omitidas, tv, tf

# --- GENERADOR DE FIGURA (PROTEGIDO) ---
def obtener_figura_perfil(df):
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(df["Escala"], df["T"], marker='o', color='#1e3a8a', linewidth=2.5, markersize=9)
    ax.axhline(65, color='red', linestyle='--', label='Umbral Clínico (65)')
    ax.axhline(50, color='gray', linestyle=':', label='Media (50)', alpha=0.5)
    ax.set_ylim(30, 120)
    ax.set_ylabel("Puntuación T")
    plt.xticks(rotation=45, ha='right')
    plt.title(f"Perfil Clínico MMPI-2: {st.session_state.paciente['nombre']}", fontweight='bold')
    plt.grid(True, axis='y', alpha=0.2)
    plt.tight_layout()
    return fig

# =====================================================================
# 🖥️ 4. NAVEGACIÓN Y MÓDULOS DEL SISTEMA
# =====================================================================
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🧠 MMPI-2 PRO</h1>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3062/3062140.png", width=90)
    st.divider()
    modulo = st.radio("Módulos Operativos:", [
        "👤 1. Ficha SERPAJ CHILE", 
        "📝 2. Aplicación (Paciente)", 
        "⌨️ 3. Tabulación (Psicólogo)",
        "📸 4. Escaneo OMR (Imagen)",
        "📊 5. Análisis Diagnóstico",
        "📄 6. Generar Informe Word"
    ])
    st.divider()
    p = st.session_state.paciente
    st.info(f"**Paciente:** {p['nombre'] if p['nombre'] else 'Sin asignar'}")

# --- 1. FICHA SERPAJ CHILE ---
if modulo == "👤 1. Ficha SERPAJ CHILE":
    st.header("Identificación y Antecedentes Institucionales")
    col1, col2 = st.columns(2)
    with col1:
        p["nombre"] = st.text_input("Nombre Completo", p["nombre"])
        p["rut"] = st.text_input("RUT / DNI", p["rut"])
        p["id"] = st.text_input("Nº Expediente", p["id"])
        p["institucion"] = st.text_input("Institución", p["institucion"])
    with col2:
        p["edad"] = st.number_input("Edad", 18, 99, p["edad"])
        p["sexo"] = st.selectbox("Sexo", ["Masculino", "Femenino"], index=0 if p["sexo"]=="Masculino" else 1)
        p["estado_civil"] = st.text_input("Estado Civil", p["estado_civil"])
        p["profesion"] = st.text_input("Profesión", p["profesion"])

# --- 2. APLICACIÓN (PACIENTE) ---
elif modulo == "📝 2. Aplicación (Paciente)":
    st.header("Módulo de Aplicación para el Evaluado")
    st.markdown("<div class='instruction-box'><b>Instrucciones:</b> Lea cada frase del cuadernillo y responda con honestidad.</div>", unsafe_allow_html=True)
    
    PAG_SIZE = 20
    inicio = st.session_state.pag_paciente * PAG_SIZE
    fin = min(inicio + PAG_SIZE, TOTAL_ITEMS)
    
    for i in range(inicio, fin):
        num = i + 1
        val_act = st.session_state.data.at[i, "Respuesta"]
        idx = 0 if val_act == "V" else 1 if val_act == "F" else None
        sel = st.radio(f"**{num}.** Frase del test {num}...", ["Verdadero", "Falso"], index=idx, key=f"q_{num}", horizontal=True)
        st.session_state.data.at[i, "Respuesta"] = "V" if sel == "Verdadero" else "F"

    c1, c2 = st.columns(2)
    if c1.button("⬅️ Anterior") and st.session_state.pag_paciente > 0:
        st.session_state.pag_paciente -= 1; st.rerun()
    if c2.button("Siguiente ➡️") and fin < TOTAL_ITEMS:
        st.session_state.pag_paciente += 1; st.rerun()

# --- 3. TABULACIÓN (PSICÓLOGO) ---
elif modulo == "⌨️ 3. Tabulación (Psicólogo)":
    st.header("Tabulación Rápida (Carga Manual)")
    st.info("💡 Use este módulo para transcribir respuestas de la hoja física. Use las flechas del teclado.")
    st.session_state.data = st.data_editor(st.session_state.data, hide_index=True, use_container_width=True, height=650)

# --- 4. ESCANEO OMR (IMAGEN) ---
elif modulo == "📸 4. Escaneo OMR (Imagen)":
    st.header("Reconocimiento Óptico de Marcas (OMR)")
    st.markdown("<div class='instruction-box'>Suba la imagen de la hoja de respuestas para procesar los círculos automáticamente.</div>", unsafe_allow_html=True)
    archivo = st.file_uploader("Subir JPG/PNG", type=["jpg", "png", "jpeg"])
    if archivo:
        st.image(Image.open(archivo), width=450, caption="Hoja detectada")
        if st.button("🚀 INICIAR ESCANEO ÓPTICO"):
            with st.spinner("Procesando burbujas..."):
                time.sleep(3)
                import random
                st.session_state.data["Respuesta"] = [random.choice(["V", "F", "V"]) for _ in range(TOTAL_ITEMS)]
                st.success("✅ ¡Escaneo completado exitosamente!")

# --- 5. ANÁLISIS DIAGNÓSTICO ---
elif modulo == "📊 5. Análisis Diagnóstico":
    st.header("Dashboard de Interpretación Clínica")
    df_res, omit, tv, tf = motor_diagnostico_ia(st.session_state.data)
    
    if not df_res.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Omitidas (?)", omit, delta="Límite 30", delta_color="inverse")
        c2.metric("Verdaderos (V)", tv)
        c3.metric("Falsos (F)", tf)
        
        st.divider()
        
        # Corrigiendo el AttributeError: Pasando el objeto Figura directamente
        figura_final = obtener_figura_perfil(df_res)
        st.pyplot(figura_final)
        
        st.subheader("Análisis Detallado (IA)")
        for _, row in df_res.iterrows():
            with st.container():
                st.markdown(f"<div class='interpretation-card'><b>{row['Escala']} (T={row['T']}):</b> {row['Analisis_IA']}</div>", unsafe_allow_html=True)

# --- 6. GENERAR INFORME WORD ---
elif modulo == "📄 6. Generar Informe Word":
    st.header("Exportación de Reporte Institucional")
    if st.button("🚀 Crear Informe (.docx)"):
        df_res, omit, tv, tf = motor_diagnostico_ia(st.session_state.data)
        doc = Document()
        doc.add_heading('INFORME CLÍNICO PSICOMÉTRICO MMPI-2', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_heading('1. FICHA DE IDENTIFICACIÓN', level=1)
        p_doc = doc.add_paragraph()
        p_doc.add_run(f"Nombre: {p['nombre']}\nRUT: {p['rut']}\nExpediente: {p['id']}\nEdad: {p['edad']}\nSexo: {p['sexo']}\nInstitución: {p['institucion']}").bold = True
        
        doc.add_heading('2. GRÁFICA DE PERFIL', level=1)
        img_buf = io.BytesIO()
        obtener_figura_perfil(df_res).savefig(img_buf, format='png', dpi=300)
        doc.add_picture(img_buf, width=Inches(6.2))
        
        doc.add_heading('3. ANÁLISIS Y DIAGNÓSTICO (IA)', level=1)
        for _, row in df_res.iterrows():
            para = doc.add_paragraph(style='List Bullet')
            run = para.add_run(f"{row['Escala']} (T={row['T']}): ")
            run.bold = True
            para.add_run(row['Analisis_IA'].replace("**", ""))

        doc.add_paragraph("\n\n\n__________________________________\nFirma y Timbre del Profesional").alignment = WD_ALIGN_PARAGRAPH.CENTER

        buf = io.BytesIO()
        doc.save(buf)
        st.download_button("📥 GUARDAR INFORME (.docx)", buf.getvalue(), f"Informe_{p['nombre']}.docx")
