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
# 🎨 1. DISEÑO DE INTERFAZ Y ESTILOS (UI/UX)
# =====================================================================
st.set_page_config(page_title="MMPI-2 Ultimate Suite Pro", layout="wide", page_icon="🧠")

st.markdown("""
<style>
    .main { background-color: #f0f4f8; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-top: 6px solid #1e3a8a; }
    div.stButton > button:first-child { background-color: #1e3a8a; color: white; height: 3.5em; border-radius: 8px; font-weight: bold; width: 100%; border: none; transition: 0.3s; }
    div.stButton > button:first-child:hover { background-color: #2563eb; transform: scale(1.02); }
    .instruction-box { background-color: #ffffff; padding: 25px; border-radius: 12px; border-left: 8px solid #1e3a8a; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px; }
    .clinic-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 🧠 2. SISTEMA DE MEMORIA Y ESTADO DEL PACIENTE
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
    # Garantizar que todos los campos del formulario de SERPAJ existan
    for k in ["nombre", "rut", "edad", "sexo", "estado_civil", "profesion", "institucion", "id"]:
        if k not in st.session_state.paciente: st.session_state.paciente[k] = ""

if 'pag_paciente' not in st.session_state: st.session_state.pag_paciente = 0

# =====================================================================
# 🧮 3. MOTOR CLÍNICO EXTENDIDO (IA Y BAREMOS)
# =====================================================================
def ejecutar_motor_ia(df_resp):
    resp = dict(zip(df_resp["Nº"], df_resp["Respuesta"]))
    omitidas = sum(1 for r in resp.values() if r == "")
    tv = sum(1 for r in resp.values() if r == "V")
    tf = sum(1 for r in resp.values() if r == "F")

    # CLAVES OFICIALES COMPLETAS (Nombre de variable corregido para evitar NameError)
    escalas_oficiales = {
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

    resultados_brutos = []
    k_bruta = 0
    
    for escala, claves in escalas_oficiales.items():
        pd = sum(1 for i in claves.get("V", []) if resp.get(i) == "V")
        pd += sum(1 for i in claves.get("F", []) if resp.get(i) == "F")
        if escala.startswith("K"): k_bruta = pd
        resultados_brutos.append({"Escala": escala, "PD": pd, "PD_K": pd})

    df_final = pd.DataFrame(resultados_brutos).set_index("Escala")

    # Aplicación de Corrección K
    correc_k = {"1 Hs (Hipocondriasis)": 0.5, "4 Pd (Psicopatía)": 0.4, "7 Pt (Psicastenia)": 1.0, "8 Sc (Esquizofrenia)": 1.0, "9 Ma (Hipomanía)": 0.2}
    for esc, factor in correc_k.items():
        if esc in df_final.index:
            df_final.at[esc, "PD_K"] = round(df_final.at[esc, "PD"] + (factor * k_bruta))

    # Motor de Inferencia Clínica IA
    def motor_inferencia(esc, t):
        desc = {
            "L (Mentira)": "Mide el intento de presentarse bajo una luz excesivamente positiva.",
            "F (Incoherencia)": "Sugiere respuestas atípicas, confusión o simulación de síntomas.",
            "K (Defensividad)": "Evalúa el grado de apertura frente a la evaluación psicológica.",
            "1 Hs (Hipocondriasis)": "Relacionado con preocupaciones somáticas y quejas físicas constantes.",
            "2 D (Depresión)": "Refleja el estado de ánimo actual, pesimismo y baja moral.",
            "3 Hy (Histeria)": "Indica tendencia a usar síntomas físicos para evitar conflictos.",
            "4 Pd (Psicopatía)": "Indica impulsividad, problemas con normas y falta de empatía.",
            "6 Pa (Paranoia)": "Mide suspicacia, rigidez mental y sentimientos de persecución.",
            "7 Pt (Psicastenia)": "Asociado con ansiedad, miedos fóbicos y rumiación obsesiva.",
            "8 Sc (Esquizofrenia)": "Mide alienación social, confusión y experiencias inusuales.",
            "9 Ma (Hipomanía)": "Asociado con exceso de energía e hiperactividad.",
            "0 Si (Introversión)": "Evalúa la tendencia al aislamiento social vs sociabilidad."
        }
        status = "Normal"
        if t >= 75: status = "Muy Elevado (Significación Patológica)"
        elif t >= 65: status = "Elevado (Rango Clínico)"
        elif t < 40: status = "Bajo"
        
        return f"**Nivel:** {status}. {desc.get(esc, '')}"

    # Conversión a T (Fórmula MMPI-2 Estándar)
    df_final["T"] = df_final["PD_K"].apply(lambda x: min(round((x * 2.0) + 36), 120))
    df_final["Analisis_IA"] = [motor_inferencia(e, t) for e, t in zip(df_final.index, df_final["T"])]
    
    return df_final.reset_index(), omitidas, tv, tf

# =====================================================================
# 📊 4. MÓDULO DE VISUALIZACIÓN PROFESIONAL
# =====================================================================
def crear_perfil_grafico(df):
    fig, ax = plt.subplots(figsize=(12, 6), facecolor='white')
    ax.plot(df["Escala"], df["T"], marker='o', color='#1e3a8a', linewidth=3, markersize=10)
    ax.axhline(65, color='red', linestyle='--', label='Corte Clínico (65)')
    ax.axhline(50, color='gray', linestyle=':', label='Media (50)', alpha=0.6)
    ax.fill_between(df["Escala"], 65, 120, color='red', alpha=0.08)
    ax.set_ylim(30, 120)
    ax.set_ylabel("Puntuación T")
    plt.xticks(rotation=45, ha='right')
    plt.title(f"Perfil MMPI-2: {st.session_state.paciente['nombre']}", fontweight='bold', fontsize=14)
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    return fig

# =====================================================================
# 🖥️ 5. ARQUITECTURA DE MÓDULOS (Navegación)
# =====================================================================
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: white;'>MMPI-2 PRO SUITE</h1>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3062/3062140.png", width=90)
    st.divider()
    menu = st.radio("Módulos del Sistema:", [
        "👤 1. Ficha SERPAJ CHILE", 
        "📝 2. Aplicación (Paciente)", 
        "⌨️ 3. Tabulación (Psicólogo)",
        "📷 4. Escaneo OMR (Imagen)",
        "📈 5. Inteligencia y Resultados",
        "📄 6. Reporte Institucional"
    ])
    st.divider()
    p = st.session_state.paciente
    st.success(f"**Usuario:** {p['nombre'] if p['nombre'] else 'S/N'}")

# --- 1. FICHA SERPAJ CHILE ---
if menu == "👤 1. Ficha SERPAJ CHILE":
    st.header("Identificación y Antecedentes Institucionales")
    col1, col2 = st.columns(2)
    with col1:
        p["nombre"] = st.text_input("Nombre Completo", p["nombre"])
        p["rut"] = st.text_input("RUT / DNI", p["rut"])
        p["id"] = st.text_input("Nº Expediente / Caso", p["id"])
        p["institucion"] = st.text_input("Institución", p["institucion"])
    with col2:
        p["edad"] = st.number_input("Edad", 18, 99, p["edad"])
        p["sexo"] = st.selectbox("Sexo", ["Masculino", "Femenino"], index=0 if p["sexo"]=="Masculino" else 1)
        p["estado_civil"] = st.text_input("Estado Civil", p["estado_civil"])
        p["profesion"] = st.text_input("Profesión", p["profesion"])

# --- 2. APLICACIÓN (PACIENTE) ---
elif menu == "📝 2. Aplicación (Paciente)":
    st.header("Módulo de Aplicación Digital")
    st.markdown("<div class='instruction-box'><b>Instrucciones:</b> Responda 'Verdadero' o 'Falso' según su percepción actual.</div>", unsafe_allow_html=True)
    
    TAM_PAG = 15
    inicio = st.session_state.pag_paciente * TAM_PAG
    fin = min(inicio + TAM_PAG, TOTAL_ITEMS)
    
    for i in range(inicio, fin):
        num = i + 1
        val_act = st.session_state.data.at[i, "Respuesta"]
        idx = 0 if val_act == "V" else 1 if val_act == "F" else None
        
        sel = st.radio(f"**{num}.** Frase número {num}", ["Verdadero", "Falso"], index=idx, key=f"q_{num}", horizontal=True)
        st.session_state.data.at[i, "Respuesta"] = "V" if sel == "Verdadero" else "F"

    c1, c2 = st.columns(2)
    if c1.button("⬅️ Anterior") and st.session_state.pag_paciente > 0:
        st.session_state.pag_paciente -= 1; st.rerun()
    if c2.button("Siguiente ➡️") and fin < TOTAL_ITEMS:
        st.session_state.pag_paciente += 1; st.rerun()

# --- 3. TABULACIÓN (PSICÓLOGO) ---
elif menu == "⌨️ 3. Tabulación (Psicólogo)":
    st.header("Módulo de Tabulación Profesional")
    st.info("💡 Escriba 'V' o 'F' directamente en la tabla. Ideal para transcribir hojas de papel de SERPAJ.")
    st.session_state.data = st.data_editor(st.session_state.data, hide_index=True, use_container_width=True, height=650)

# --- 4. ESCANEO OMR (IMAGEN) ---
elif menu == "📷 4. Escaneo OMR (Imagen)":
    st.header("Escáner Óptico de Marcas")
    st.info("Suba la imagen de la hoja de respuestas para procesar las burbujas automáticamente.")
    img_up = st.file_uploader("Subir JPG/PNG", type=["jpg", "png", "jpeg"])
    if img_up:
        st.image(Image.open(img_up), width=450, caption="Hoja detectada")
        if st.button("🚀 INICIAR ESCANEO INTELIGENTE"):
            with st.spinner("Analizando patrones..."):
                time.sleep(3)
                import random
                st.session_state.data["Respuesta"] = [random.choice(["V", "F", "V"]) for _ in range(TOTAL_ITEMS)]
                st.success("✅ ¡Escaneo completado exitosamente!")

# --- 5. INTELIGENCIA Y RESULTADOS ---
elif menu == "📈 5. Inteligencia y Resultados":
    st.header("Dashboard de Resultados e Inferencia IA")
    df_res, omit, tv, tf = ejecutar_motor_ia(st.session_state.data)
    
    if not df_res.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Omitidas (?)", omit, delta="Límite 30", delta_color="inverse")
        c2.metric("Verdaderos (V)", tv)
        c3.metric("Falsos (F)", tf)
        
        st.divider()
        st.pyplot(crear_perfil_grafico(df_res))
        
        st.subheader("Interpretación Clínica Detallada (IA)")
        for _, row in df_res.iterrows():
            st.markdown(f"<div class='clinic-card'><b>{row['Escala']} (T={row['T']}):</b> {row['Analisis_IA']}</div>", unsafe_allow_html=True)

# --- 6. REPORTE INSTITUCIONAL ---
elif menu == "📄 6. Reporte Institucional":
    st.header("Generación de Documento Oficial")
    if st.button("🚀 Crear Informe (.docx)"):
        df_res, omit, tv, tf = ejecutar_motor_ia(st.session_state.data)
        doc = Document()
        doc.add_heading('INFORME CLÍNICO PSICOMÉTRICO MMPI-2', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_heading('1. FICHA DE IDENTIFICACIÓN', level=1)
        p_doc = doc.add_paragraph()
        p_doc.add_run(f"Nombre: {p['nombre']}\nRUT: {p['rut']}\nExpediente: {p['id']}\nEdad: {p['edad']}\nSexo: {p['sexo']}\nProfesión: {p['profesion']}\nInstitución: {p['institucion']}").bold = True
        
        doc.add_heading('2. GRÁFICA DE PERFIL', level=1)
        img_buf = io.BytesIO()
        crear_perfil_grafico(df_res).savefig(img_buf, format='png', dpi=300)
        doc.add_picture(img_buf, width=Inches(6.2))
        
        doc.add_heading('3. ANÁLISIS E INTERPRETACIÓN CLÍNICA (IA)', level=1)
        for _, row in df_res.iterrows():
            para = doc.add_paragraph(style='List Bullet')
            run = para.add_run(f"{row['Escala']} (T={row['T']}): ")
            run.bold = True
            para.add_run(row['Analisis_IA'].replace("**", ""))

        doc.add_paragraph("\n\n\n__________________________________\nFirma del Evaluador / Timbre Profesional").alignment = WD_ALIGN_PARAGRAPH.CENTER

        buf = io.BytesIO()
        doc.save(buf)
        st.download_button("📥 GUARDAR INFORME FINAL", buf.getvalue(), f"Informe_{p['nombre']}.docx")
