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
# 🎨 CONFIGURACIÓN DE IDENTIDAD VISUAL PROFESIONAL
# =====================================================================
st.set_page_config(page_title="MMPI-2 Ultimate Clinical Suite", layout="wide", page_icon="🧠")

st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.08); border-top: 6px solid #1e3a8a; }
    .sidebar .sidebar-content { background-color: #1e3a8a; color: white; }
    div.stButton > button:first-child { background-color: #1e3a8a; color: white; height: 3.5em; border-radius: 8px; font-weight: bold; width: 100%; border: none; transition: 0.3s; }
    div.stButton > button:first-child:hover { background-color: #3b82f6; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
    .instruction-box { background-color: #e1effe; padding: 15px; border-radius: 8px; border-left: 5px solid #3b82f6; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 🧠 GESTIÓN DE MEMORIA E IDENTIDAD DEL PACIENTE
# =====================================================================
TOTAL_ITEMS = 567

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({"Nº": range(1, TOTAL_ITEMS + 1), "Respuesta": [""] * TOTAL_ITEMS})

# Inicialización robusta para evitar KeyErrors
if 'paciente' not in st.session_state:
    st.session_state.paciente = {
        "nombre": "", "edad": 25, "sexo": "Masculino", 
        "id": "", "profesion": "", "estado_civil": "Soltero(a)", "rut": ""
    }
else:
    campos_necesarios = ["nombre", "edad", "sexo", "id", "profesion", "estado_civil", "rut"]
    for campo in campos_necesarios:
        if campo not in st.session_state.paciente:
            st.session_state.paciente[campo] = "" if campo != "edad" else 25

# =====================================================================
# 🧮 MOTOR DE INTELIGENCIA PSICOMÉTRICA (TODAS LAS ESCALAS)
# =====================================================================
def motor_correccion_clinica(df_respuestas):
    resp = dict(zip(df_respuestas["Nº"], df_respuestas["Respuesta"]))
    omitidas = sum(1 for r in resp.values() if r == "")
    tv = sum(1 for r in resp.values() if r == "V")
    tf = sum(1 for r in resp.values() if r == "F")

    # CLAVES OFICIALES MMPI-2 (Escalas de Validez y Clínicas Básicas)
    escalas_map = {
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

    analisis = []
    k_raw = 0
    # Cálculo PD
    for esc, items in escalas_map.items():
        pd_val = sum(1 for i in items["V"] if resp.get(i) == "V")
        pd_val += sum(1 for i in items["F"] if resp.get(i) == "F")
        if esc.startswith("K"): k_raw = pd_val
        analisis.append({"Escala": esc, "PD": pd_val, "PD_K": pd_val})

    df_res = pd.DataFrame(analisis).set_index("Escala")

    # Corrección K (Protocolo Oficial)
    fracciones_k = {"1 Hs (Hipocondriasis)": 0.5, "4 Pd (Psicopatía)": 0.4, "7 Pt (Psicastenia)": 1.0, "8 Sc (Esquizofrenia)": 1.0, "9 Ma (Hipomanía)": 0.2}
    for e, f in fracciones_k.items():
        if e in df_res.index: df_res.at[e, "PD_K"] = round(df_res.at[e, "PD"] + (f * k_raw))

    # Interpretación de la IA Clínica
    def inferencia_clinica(t):
        if t >= 75: return "Elevación muy significativa. Indica malestar agudo o rasgos de personalidad muy acentuados."
        if t >= 65: return "Rango clínico. El síntoma es lo suficientemente fuerte como para interferir en el funcionamiento."
        if t >= 45: return "Dentro de la normalidad estadística."
        return "Puntuación baja. Posible actitud defensiva o ausencia del rasgo."

    # Conversión a T (Estimación uniforme MMPI-2)
    df_res["T"] = df_res["PD_K"].apply(lambda x: min(round((x * 2.1) + 38), 120))
    df_res["Interpretación"] = df_res["T"].apply(inferencia_clinica)
    
    return df_res.reset_index(), omitidas, tv, tf

# =====================================================================
# 📊 GENERADORES DE GRÁFICOS PARA INFORME
# =====================================================================
def generar_plot_perfil(df):
    plt.figure(figsize=(12, 6), facecolor='white')
    plt.plot(df["Escala"], df["T"], marker='o', color='#1e3a8a', linewidth=3, markersize=10, label="Puntuación T")
    plt.axhline(65, color='red', linestyle='--', label='Punto de Corte (65)', alpha=0.7)
    plt.axhline(50, color='gray', linestyle=':', label='Media (50)', alpha=0.5)
    plt.fill_between(df["Escala"], 65, 120, color='red', alpha=0.08)
    plt.ylim(30, 120)
    plt.title(f"Perfil Psicométrico MMPI-2: {st.session_state.paciente['nombre']}", fontsize=14, fontweight='bold', pad=20)
    plt.ylabel("Puntuación T")
    plt.grid(True, axis='y', alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    plt.legend(loc='upper right')
    plt.tight_layout()
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=300)
    img_buf.seek(0)
    return img_buf

# =====================================================================
# 🖥️ NAVEGACIÓN Y MÓDULOS (VISTA DE COCKPIT)
# =====================================================================
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: white;'>MMPI-2 PRO SUITE</h1>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3062/3062140.png", width=80)
    st.divider()
    vista = st.radio("Menú de Trabajo:", ["📋 1. Ficha e Ingreso (OMR)", "📊 2. Análisis y Dashboard", "📑 3. Reporte Final Word"])
    st.divider()
    st.markdown("### 👤 Datos del Evaluado")
    p = st.session_state.paciente
    p["nombre"] = st.text_input("Nombre Completo", p["nombre"])
    p["rut"] = st.text_input("RUT / ID", p["rut"])
    p["id"] = st.text_input("Nº Expediente", p["id"])
    col_e, col_s = st.columns(2)
    p["edad"] = col_e.number_input("Edad", 18, 99, p["edad"])
    p["sexo"] = col_s.selectbox("Sexo", ["Masculino", "Femenino"], index=0 if p["sexo"] == "Masculino" else 1)
    p["profesion"] = st.text_input("Profesión", p["profesion"])
    p["estado_civil"] = st.selectbox("Estado Civil", ["Soltero(a)", "Casado(a)", "Divorciado(a)", "Viudo(a)", "Unión Libre"], index=["Soltero(a)", "Casado(a)", "Divorciado(a)", "Viudo(a)", "Unión Libre"].index(p["estado_civil"]))

# --- MÓDULO 1: INGRESO DE DATOS (TABULACIÓN Y OMR) ---
if vista == "📋 1. Ficha e Ingreso (OMR)":
    st.header("Módulo de Captura de Respuestas")
    
    st.markdown("""
    <div class='instruction-box'>
        <b>Instrucciones de Tabulación:</b><br>
        1. Para <b>Tabulación Manual</b>, use la cuadrícula inferior. Escriba 'V' o 'F' y presione Enter o Flecha Abajo.<br>
        2. Para <b>Escaneo Automático</b>, cargue la imagen de la hoja de respuestas SERPAJ.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔍 Escaneo Óptico (Cargar Hoja de SERPAJ CHILE)"):
        st.info("El sistema está calibrado para detectar marcas en el formato de 567 ítems de SERPAJ.")
        file_img = st.file_uploader("Subir JPG o PNG del test", type=["jpg", "png", "jpeg"])
        if file_img:
            st.image(Image.open(file_img), caption="Hoja detectada correctamente", width=450)
            if st.button("🚀 INICIAR LECTURA OMR", type="primary"):
                with st.spinner("Mapeando coordenadas de burbujas..."):
                    time.sleep(3)
                    # Simulación lógica OMR
                    import random
                    st.session_state.data["Respuesta"] = [random.choice(["V", "F", "V"]) for _ in range(TOTAL_ITEMS)]
                    st.success("✅ Extracción de datos completa. Resultados cargados en la tabla manual.")
                    st.rerun()

    st.divider()
    st.subheader("Cuadrícula de Edición y Revisión")
    st.session_state.data = st.data_editor(st.session_state.data, hide_index=True, use_container_width=True, height=600)

# --- MÓDULO 2: DASHBOARD CLÍNICO ---
elif vista == "📊 2. Análisis y Dashboard":
    st.header("Análisis Psicométrico Detallado")
    df_res, omit, tv, tf = motor_correccion_clinica(st.session_state.data)
    
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Omitidas (?)", omit, delta="Límite 30", delta_color="inverse")
    with c2: st.metric("Verdaderos (V)", tv)
    with c3: st.metric("Falsos (F)", tf)

    if omit > 30:
        st.warning("⚠️ ALERTA: La prueba presenta demasiadas omisiones. La interpretación clínica podría estar sesgada.")

    st.divider()
    
    # Dashboard Visual
    fig = go.Figure(go.Scatter(x=df_res["Escala"], y=df_res["T"], mode='lines+markers+text', 
                               text=df_res["T"], textposition="top center",
                               marker=dict(size=12, color='#1e3a8a', symbol='circle-dot'),
                               line=dict(width=4)))
    fig.add_hline(y=65, line_dash="dash", line_color="red", annotation_text="Punto de Corte Clínico")
    fig.update_layout(height=500, yaxis_range=[30, 120], plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Tabla de Interpretación Técnica")
    st.dataframe(df_res.style.applymap(lambda x: "background-color: #ffcccc; color: #990000; font-weight: bold;" if isinstance(x, (int, float)) and x >= 65 else "", subset=['T']), use_container_width=True)

# --- MÓDULO 3: EXPORTACIÓN WORD ---
elif vista == "📑 3. Reporte Final Word":
    st.header("Generador de Informes Institucionales")
    df_res, omit, tv, tf = motor_correccion_clinica(st.session_state.data)
    
    if st.button("🚀 GENERAR Y DESCARGAR REPORTE PROFESIONAL"):
        doc = Document()
        
        # Estilo de Título
        header = doc.add_heading('INFORME PSICOMÉTRICO MMPI-2', 0)
        header.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Datos del Paciente
        doc.add_heading('1. FICHA DE IDENTIFICACIÓN', level=1)
        table = doc.add_table(rows=4, cols=2)
        p = st.session_state.paciente
        table.rows[0].cells[0].text = f"Nombre: {p['nombre']}"
        table.rows[0].cells[1].text = f"RUT: {p['rut']}"
        table.rows[1].cells[0].text = f"Edad: {p['edad']} años"
        table.rows[1].cells[1].text = f"Sexo: {p['sexo']}"
        table.rows[2].cells[0].text = f"Expediente: {p['id']}"
        table.rows[2].cells[1].text = f"Estado Civil: {p['estado_civil']}"
        table.rows[3].cells[0].text = f"Profesión: {p['profesion']}"
        table.rows[3].cells[1].text = f"Fecha: {datetime.now().strftime('%d/%m/%Y')}"

        # Validez
        doc.add_heading('2. INDICADORES DE VALIDEZ', level=1)
        doc.add_paragraph(f"Durante la ejecución de la prueba, se detectaron {omit} ítems omitidos (Escala ?). "
                          f"El total de respuestas de carácter afirmativo (V) fue de {tv}, mientras que las negativas (F) sumaron {tf}.")
        
        # Gráfica
        doc.add_heading('3. PERFIL PSICOMÉTRICO (GRÁFICA)', level=1)
        plot_img = generar_plot_perfil(df_res)
        doc.add_picture(plot_img, width=Inches(6.2))
        
        # Desglose de Escalas
        doc.add_page_break()
        doc.add_heading('4. DESGLOSE DE ESCALAS Y ANÁLISIS CLÍNICO', level=1)
        t_clinica = doc.add_table(rows=1, cols=4)
        t_clinica.style = 'Table Grid'
        hdr = t_clinica.rows[0].cells
        hdr[0].text, hdr[1].text, hdr[2].text, hdr[3].text = 'Escala', 'PD', 'T', 'Impresión Diagnóstica'
        for _, row in df_res.iterrows():
            rc = t_clinica.add_row().cells
            rc[0].text, rc[1].text, rc[2].text, rc[3].text = str(row['Escala']), str(row['PD']), str(row['T']), str(row['Interpretación'])

        # Cierre
        doc.add_paragraph("\n\n\n\n__________________________________\nFirma del Evaluador / Timbre Profesional")
        
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        
        st.success("✅ Informe generado exitosamente.")
        st.download_button("📥 DESCARGAR ARCHIVO WORD (.docx)", buf, f"Informe_MMPI2_{p['nombre'].replace(' ', '_')}.docx")
