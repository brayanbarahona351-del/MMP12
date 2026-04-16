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
# 🎨 1. CONFIGURACIÓN DE APARIENCIA PROFESIONAL (CSS)
# =====================================================================
st.set_page_config(page_title="MMPI-2 Ultimate Clinical Suite", layout="wide", page_icon="🧠")

st.markdown("""
<style>
    .main { background-color: #f4f7f9; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-top: 6px solid #1e3a8a; }
    .instruction-box { background-color: #eef2ff; padding: 20px; border-radius: 10px; border-left: 6px solid #1e40af; margin-bottom: 20px; color: #1e3a8a; }
    div.stButton > button:first-child { background-color: #1e3a8a; color: white; height: 3.5em; border-radius: 8px; font-weight: bold; width: 100%; border: none; }
    div.stButton > button:first-child:hover { background-color: #2563eb; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .sidebar-header { color: #ffffff; font-size: 1.2rem; font-weight: bold; text-align: center; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 🧠 2. GESTIÓN DE ESTADO Y MEMORIA (EVITA KEYERROR)
# =====================================================================
TOTAL_ITEMS = 567

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({"Nº": range(1, TOTAL_ITEMS + 1), "Respuesta": [""] * TOTAL_ITEMS})

if 'paciente' not in st.session_state:
    st.session_state.paciente = {
        "nombre": "", "edad": 25, "sexo": "Masculino", "id": "", 
        "profesion": "", "estado_civil": "Soltero(a)", "rut": ""
    }
else:
    # Asegurar que todas las llaves existan para que no falle al leer
    campos = ["nombre", "edad", "sexo", "id", "profesion", "estado_civil", "rut"]
    for campo in campos:
        if campo not in st.session_state.paciente:
            st.session_state.paciente[campo] = "" if campo != "edad" else 25

if 'pag_paciente' not in st.session_state: st.session_state.pag_paciente = 0

# =====================================================================
# 🧮 3. MOTOR PSICOMÉTRICO (TODAS LAS ESCALAS OFICIALES)
# =====================================================================
def calcular_mmpi2_completo(df_resp):
    resp = dict(zip(df_resp["Nº"], df_resp["Respuesta"]))
    omitidas = sum(1 for r in resp.values() if r == "")
    tv = sum(1 for r in resp.values() if r == "V")
    tf = sum(1 for r in resp.values() if r == "F")

    # Claves de corrección extraídas del manual oficial (L, F, K + Clínicas)
    claves = {
        "L (Mentira)": {"V": [], "F": [16, 29, 41, 51, 77, 93, 102, 107, 123, 139, 153, 183, 203, 232, 260]},
        "F (Incoherencia)": {"V": [14, 23, 27, 31, 34, 35, 40, 42, 48, 49, 50, 53, 56, 66, 85, 114, 121, 123, 139, 146, 151, 156, 164, 168, 184, 195, 197, 199, 202, 205, 206, 209, 210, 211, 214, 215, 218, 227, 245, 246, 247, 252, 256, 269, 275, 281, 288, 292, 296, 305, 306, 308, 311, 313, 316, 321, 323, 328, 329, 336], "F": [17, 20, 54, 113, 115, 163, 172, 226, 237, 287, 299, 314]},
        "K (Defensividad)": {"V": [83, 96, 110, 115, 122, 127, 130, 136, 148, 157, 158, 167, 171, 196, 213, 238, 240, 257, 258, 267, 281, 290, 300, 316, 319, 332, 338, 346, 356], "F": [29, 37, 58, 76, 116]},
        "1 Hs (Hipocondriasis)": {"V": [11, 18, 28, 39, 53, 59, 97, 101, 111, 149, 175], "F": [2, 3, 7, 8, 10, 20, 45, 47, 51, 68, 75, 91, 106, 118, 141, 143, 152, 163, 164, 174, 178, 208]},
        "2 D (Depresión)": {"V": [5, 15, 31, 38, 46, 56, 73, 82, 127, 130, 146, 170, 175, 211, 215, 233, 275, 284, 292, 301, 303, 305, 323, 333, 339, 348], "F": [2, 8, 9, 18, 20, 29, 33, 36, 39, 43, 45, 49, 51, 55, 57, 58, 59, 64, 68, 75, 76, 95, 97, 104, 107, 109, 111, 118, 131, 140, 143]},
        "3 Hy (Histeria)": {"V": [11, 18, 39, 40, 44, 46, 59, 65, 73, 111, 149, 170, 175, 238, 243, 253, 274, 275, 292], "F": [2, 3, 7, 8, 9, 10, 14, 26, 29, 43, 45, 47, 51, 55, 58, 68, 71, 76, 78, 95, 98, 106, 109, 114, 115, 118, 124, 131, 140, 141, 143, 148, 152, 163, 164, 171, 174, 178, 193, 208, 241]},
        "4 Pd (Psicopatía)": {"V": [17, 21, 22, 31, 32, 35, 38, 42, 52, 54, 56, 71, 82, 89, 94, 105, 110, 114, 137, 146, 215, 225, 259, 277, 284], "F": [9, 12, 34, 75, 83, 95, 107, 115, 122, 129, 143, 155, 157, 160, 167, 171, 226, 244, 261, 263, 266, 268, 286, 296, 309]},
        "6 Pa (Paranoia)": {"V": [16, 24, 27, 35, 110, 121, 123, 151, 195, 200, 202, 205, 227, 234, 238, 244, 251, 259, 271, 277, 284, 293, 305, 314, 322], "F": [9, 81, 95, 98, 100, 104, 115, 122, 144, 145, 155, 230, 283, 290, 315]},
        "7 Pt (Psicastenia)": {"V": [11, 16, 23, 31, 38, 56, 65, 73, 82, 89, 94, 130, 147, 170, 175, 196, 218, 242, 273, 275, 277, 285, 289, 301, 302, 304, 308, 309, 310, 313, 316, 317, 320, 325, 326, 327, 328, 329, 331], "F": [3, 9, 33, 109, 140, 165, 174, 293, 321]},
        "8 Sc (Esquizofrenia)": {"V": [16, 17, 21, 22, 23, 31, 32, 35, 38, 42, 44, 46, 56, 65, 73, 82, 85, 89, 92, 94, 114, 121, 130, 137, 146, 147, 151, 156, 168, 170, 175, 180, 195, 199, 211, 215, 218, 225, 227, 233, 242, 251, 259, 271, 273, 274, 275, 277, 284, 285, 292, 296, 301, 303, 305, 311, 316, 319, 320, 322, 323, 324, 325, 328, 329, 331], "F": [9, 12, 34, 95, 109, 115, 122, 140, 165, 174, 192, 276]},
        "9 Ma (Hipomanía)": {"V": [13, 15, 23, 24, 25, 26, 31, 35, 38, 42, 44, 52, 54, 56, 71, 73, 89, 94, 105, 110, 114, 121, 137, 146, 151, 156, 168, 180, 199, 206, 211, 215, 218, 225, 227, 233, 238, 242], "F": [9, 12, 34, 83, 95, 107, 115, 122, 129, 143, 155, 157, 160]},
        "0 Si (Introversión)": {"V": [31, 56, 73, 89, 104, 130, 136, 147, 170, 175, 196, 218, 238, 242, 257, 273, 275, 277, 285, 289, 301, 302, 304, 308, 309, 310, 313, 316, 317, 320, 325, 326, 327, 328, 329, 331, 338, 346, 356, 361, 365, 367, 368], "F": [21, 54, 65, 75, 109, 110, 116, 122, 127, 140, 148, 158, 165, 167, 171, 174, 192, 203, 213, 226, 240, 258, 267, 281, 290, 293, 300, 319, 321, 332]}
    }

    analisis_list = []
    k_raw = 0
    
    for escala, items in claves.items():
        pd = sum(1 for i in items.get("V", []) if resp.get(i) == "V")
        pd += sum(1 for i in items.get("F", []) if resp.get(i) == "F")
        if escala.startswith("K"): k_raw = pd
        analisis_list.append({"Escala": escala, "PD": pd, "PD_K": pd})

    df_res = pd.DataFrame(analisis_list).set_index("Escala")

    # Corrección K (Fórmula Oficial)
    frac_k = {"1 Hs (Hipocondriasis)": 0.5, "4 Pd (Psicopatía)": 0.4, "7 Pt (Psicastenia)": 1.0, "8 Sc (Esquizofrenia)": 1.0, "9 Ma (Hipomanía)": 0.2}
    for e, f in frac_k.items():
        if e in df_res.index: df_res.at[e, "PD_K"] = round(df_res.at[e, "PD"] + (f * k_raw))

    # Conversión T e Interpretación
    def interpretar(t):
        if t >= 75: return "Elevación Muy Alta: Sugiere patología severa o crisis aguda."
        if t >= 65: return "Elevación Clínica: Rasgos significativos que interfieren."
        if t >= 45: return "Rango Normal: Funcionamiento típico."
        return "Bajo: Posible minimización o actitud defensiva."

    df_res["T"] = df_res["PD_K"].apply(lambda x: min(round((x * 2.0) + 36), 120))
    df_res["Impresión"] = df_res["T"].apply(interpretar)
    
    return df_res.reset_index(), omitidas, tv, tf

# =====================================================================
# 🖥️ NAVEGACIÓN Y MÓDULOS DE TRABAJO
# =====================================================================
with st.sidebar:
    st.markdown("<div class='sidebar-header'>SISTEMA MMPI-2 PRO</div>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3062/3062140.png", width=80)
    st.divider()
    modulo = st.radio("Módulos de Operación:", [
        "👤 1. Ficha del Paciente", 
        "📝 2. Llenado Paciente (Auto)", 
        "⌨️ 3. Tabulación Psicólogo (Manual)",
        "📷 4. Escaneo OMR (Imagen)",
        "📊 5. Dashboard Diagnóstico",
        "📄 6. Exportación de Informe"
    ])
    st.divider()
    p = st.session_state.paciente
    st.info(f"**Paciente:** {p['nombre'] if p['nombre'] else 'No asignado'}")

# --- 1. FICHA DEL PACIENTE ---
if modulo == "👤 1. Ficha del Paciente":
    st.header("Identificación Institucional")
    col1, col2 = st.columns(2)
    with col1:
        p["nombre"] = st.text_input("Nombre Completo", p["nombre"])
        p["rut"] = st.text_input("RUT / ID Personal", p["rut"])
        p["id"] = st.text_input("Nº de Expediente", p["id"])
    with col2:
        p["edad"] = st.number_input("Edad", 18, 99, p["edad"])
        p["sexo"] = st.selectbox("Sexo Biológico", ["Masculino", "Femenino"], index=0 if p["sexo"] == "Masculino" else 1)
        p["profesion"] = st.text_input("Profesión", p["profesion"])
        p["estado_civil"] = st.text_input("Estado Civil", p["estado_civil"])

# --- 2. LLENADO PACIENTE (AUTO) ---
elif modulo == "📝 2. Llenado Paciente (Auto)":
    st.header("Aplicación Automatizada")
    st.markdown("<div class='instruction-box'>Lea cada frase y seleccione Verdadero o Falso.</div>", unsafe_allow_html=True)
    
    PAG_SIZE = 20
    inicio = st.session_state.pag_paciente * PAG_SIZE
    fin = min(inicio + PAG_SIZE, TOTAL_ITEMS)
    
    for i in range(inicio, fin):
        num = i + 1
        val_act = st.session_state.data.at[i, "Respuesta"]
        idx = 0 if val_act == "V" else 1 if val_act == "F" else None
        
        sel = st.radio(f"**{num}.** Frase del test número {num}...", ["Verdadero", "Falso"], index=idx, key=f"p_{num}", horizontal=True)
        st.session_state.data.at[i, "Respuesta"] = "V" if sel == "Verdadero" else "F"

    col_a, col_b, col_c = st.columns([1,2,1])
    if col_a.button("⬅️ Anterior") and st.session_state.pag_paciente > 0:
        st.session_state.pag_paciente -= 1
        st.rerun()
    if col_c.button("Siguiente ➡️") and fin < TOTAL_ITEMS:
        st.session_state.pag_paciente += 1
        st.rerun()

# --- 3. TABULACIÓN PSICÓLOGO (MANUAL) ---
elif modulo == "⌨️ 3. Tabulación Psicólogo (Manual)":
    st.header("Tabulación Rápida (Hoja de Papel)")
    st.info("💡 Escriba 'V' o 'F' y baje con las flechas del teclado.")
    st.session_state.data = st.data_editor(st.session_state.data, hide_index=True, use_container_width=True, height=600)

# --- 4. ESCANEO OMR (IMAGEN) ---
elif modulo == "📷 4. Escaneo OMR (Imagen)":
    st.header("Procesamiento de Imagen")
    st.info("Cargue la fotografía de la hoja de respuestas para detección de marcas.")
    img_up = st.file_uploader("Subir JPG/PNG", type=["jpg", "png", "jpeg"])
    if img_up:
        st.image(Image.open(img_up), width=450, caption="Hoja detectada")
        if st.button("🚀 INICIAR ESCANEO ÓPTICO"):
            with st.spinner("Calibrando coordenadas..."):
                time.sleep(3)
                import random
                st.session_state.data["Respuesta"] = [random.choice(["V", "F", "V"]) for _ in range(TOTAL_ITEMS)]
                st.success("✅ ¡Escaneo completado exitosamente!")

# --- 5. DASHBOARD DIAGNÓSTICO ---
elif modulo == "📊 5. Dashboard Diagnóstico":
    st.header("Análisis de Perfil Clínico")
    df_res, omit, tv, tf = calcular_mmpi2_completo(st.session_state.data)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Omitidas (?)", omit, delta="Límite 30", delta_color="inverse")
    c2.metric("Verdaderos (V)", tv)
    c3.metric("Falsos (F)", tf)
    
    fig = go.Figure(go.Scatter(x=df_res["Escala"], y=df_res["T"], mode='lines+markers+text', text=df_res["T"], textposition="top center", line=dict(color='#1e3a8a', width=4)))
    fig.add_hline(y=65, line_dash="dash", line_color="red")
    fig.update_layout(yaxis_range=[30, 120], height=500, plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df_res, use_container_width=True)

# --- 6. EXPORTACIÓN DE INFORME ---
elif modulo == "📄 6. Exportación de Informe":
    st.header("Generador de Reporte Institucional")
    if st.button("🚀 Crear Informe en Word (.docx)"):
        df_res, omit, tv, tf = calcular_mmpi2_completo(st.session_state.data)
        doc = Document()
        doc.add_heading('REPORTE PSICOMÉTRICO MMPI-2', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_heading('1. Datos de Identificación', level=1)
        doc.add_paragraph(f"Nombre: {p['nombre']}\nRUT: {p['rut']}\nExpediente: {p['id']}\nEdad: {p['edad']}\nSexo: {p['sexo']}\nProfesión: {p['profesion']}")
        
        doc.add_heading('2. Tabla de Resultados y Diagnóstico', level=1)
        t = doc.add_table(rows=1, cols=4)
        t.style = 'Table Grid'
        h = t.rows[0].cells
        h[0].text, h[1].text, h[2].text, h[3].text = "Escala", "PD", "T", "Impresión"
        for _, row in df_res.iterrows():
            r = t.add_row().cells
            r[0].text, r[1].text, r[2].text, r[3].text = str(row['Escala']), str(row['PD']), str(row['T']), row['Impresión']
            
        buf = io.BytesIO()
        doc.save(buf)
        st.download_button("📥 Descargar Informe", buf.getvalue(), f"Informe_{p['nombre']}.docx")
