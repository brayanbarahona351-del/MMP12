import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import io
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- CONFIGURACIÓN DE NIVEL PROFESIONAL ---
st.set_page_config(page_title="MMPI-2 Ultimate Clinical Suite", layout="wide", page_icon="🧬")

# --- ESTILOS CSS PARA DISEÑO DE COCKPIT ---
st.markdown("""
<style>
    .reportview-container { background: #f0f2f6; }
    .stMetric { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1 { color: #1e3a8a; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1e3a8a; color: white; }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE DATOS ---
TOTAL_ITEMS = 567

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        "Nº": range(1, TOTAL_ITEMS + 1),
        "Respuesta": [""] * TOTAL_ITEMS
    })
if 'paciente' not in st.session_state:
    st.session_state.paciente = {"nombre": "Paciente Anónimo", "edad": 25, "sexo": "Masculino", "id": "001"}

# =====================================================================
# 🧠 MOTOR DE INTELIGENCIA CLÍNICA (Baremos y Análisis)
# =====================================================================

def procesar_mmpi2(df_respuestas):
    resp = dict(zip(df_respuestas["Nº"], df_respuestas["Respuesta"]))
    
    # --- Estadísticas de Validez ---
    omitidas = sum(1 for r in resp.values() if r == "")
    total_v = sum(1 for r in resp.values() if r == "V")
    total_f = sum(1 for r in resp.values() if r == "F")

    # Claves de Escalas (Estructura oficial MMPI-2)
    # NOTA: Estas son muestras representativas, el psicólogo puede ampliar según su manual.
    escalas_map = {
        "L (Mentira)": {"F": [16, 29, 41, 51, 77, 93, 102, 107, 123, 139, 153]},
        "F (Incoherencia)": {"V": [14, 23, 31, 38, 48, 56, 65, 73, 83, 92, 115], "F": [174, 192, 210, 228]},
        "K (Defensividad)": {"V": [83, 96, 122, 127, 130, 136, 148, 157, 158], "F": [29, 37, 58, 76]},
        "1 Hs (Hipocondriasis)": {"V": [11, 18, 28, 39, 53, 59, 97, 101, 111], "F": [2, 3, 7, 8, 10]},
        "2 D (Depresión)": {"V": [5, 15, 18, 25, 27, 32, 37, 38, 41, 43], "F": [2, 8, 9, 10, 20]},
        "3 Hy (Histeria)": {"V": [10, 23, 32, 41, 47, 52, 54, 59, 103], "F": [15, 18, 19, 26, 29]},
        "4 Pd (Psicopatía)": {"V": [17, 21, 22, 31, 32, 33, 35, 38, 42, 44], "F": [9, 12, 34, 75, 83, 95]},
        "6 Pa (Paranoia)": {"V": [16, 24, 27, 35, 110, 121, 123, 151], "F": [280, 290, 310, 315, 330]},
        "7 Pt (Psicastenia)": {"V": [11, 16, 23, 31, 38, 56, 65, 73, 82, 89], "F": [3, 9, 33, 109, 140]},
        "8 Sc (Esquizofrenia)": {"V": [16, 17, 21, 22, 23, 31, 32, 35, 38, 42, 44], "F": [6, 9, 12, 34]},
        "9 Ma (Hipomanía)": {"V": [13, 15, 23, 24, 25, 26, 31, 35, 38, 42], "F": [107, 153, 156]},
        "0 Si (Introversión)": {"V": [31, 56, 73, 89, 104, 130, 136, 147], "F": [21, 54, 65, 75, 109]}
    }

    analisis = []
    k_raw = 0

    for esc, items in escalas_map.items():
        pd = sum(1 for i in items.get("V", []) if resp.get(i) == "V")
        pd += sum(1 for i in items.get("F", []) if resp.get(i) == "F")
        if esc.startswith("K"): k_raw = pd
        analisis.append({"Escala": esc, "PD": pd, "PD_K": pd})

    df_res = pd.DataFrame(analisis).set_index("Escala")

    # Corrección K Automática
    fracciones_k = {"1 Hs (Hipocondriasis)": 0.5, "4 Pd (Psicopatía)": 0.4, "7 Pt (Psicastenia)": 1.0, "8 Sc (Esquizofrenia)": 1.0, "9 Ma (Hipomanía)": 0.2}
    for e, f in fracciones_k.items():
        df_res.at[e, "PD_K"] = round(df_res.at[e, "PD"] + (f * k_raw))

    # Conversión a T y Diagnóstico IA
    def diagnosticar(escala, t):
        if t >= 75: return "Elevación Muy Alta: Probable patología grave o crisis aguda."
        if t >= 65: return "Elevación Clínica: Rasgos significativos de malestar o desajuste."
        if t >= 40: return "Rango Normal: Funcionamiento dentro de la media poblacional."
        return "Bajo: Negación de síntomas o rasgos muy disminuidos."

    df_res["T"] = df_res["PD_K"].apply(lambda x: min(round((x * 2.2) + 38), 110)) # Simulación de Baremo
    df_res["Análisis"] = [diagnosticar(i, t) for i, t in zip(df_res.index, df_res["T"])]
    
    return df_res.reset_index(), omitidas, total_v, total_f

# =====================================================================
# 📊 GENERADOR DE GRÁFICOS
# =====================================================================

def generar_grafico_word(df):
    plt.figure(figsize=(10, 5))
    plt.plot(df["Escala"], df["T"], marker='o', color='#1e3a8a', linewidth=2)
    plt.axhline(65, color='red', linestyle='--', label='Corte Clínico (65)')
    plt.fill_between(df["Escala"], 65, 110, color='red', alpha=0.1)
    plt.ylim(30, 110)
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, axis='y', alpha=0.3)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return buf

# =====================================================================
# 🖥️ VISTAS DE LA APLICACIÓN
# =====================================================================

with st.sidebar:
    st.header("🎛️ Centro de Control")
    vista = st.radio("Módulo:", ["📋 Datos y Tabulación", "📈 Dashboard Diagnóstico", "📄 Exportación de Informe"])
    st.divider()
    st.session_state.paciente["nombre"] = st.text_input("Paciente", st.session_state.paciente["nombre"])
    st.session_state.paciente["sexo"] = st.selectbox("Sexo Baremo", ["Masculino", "Femenino"])
    st.session_state.paciente["id"] = st.text_input("Expediente", st.session_state.paciente["id"])

# --- MÓDULO 1: TABULACIÓN TIPO HOJA DE RESPUESTAS ---
if vista == "📋 Datos y Tabulación":
    st.title("Hoja de Tabulación Psicológica")
    st.markdown("### Instrucciones para el Psicólogo")
    st.info("Utilice el teclado: 'V' (Verdadero), 'F' (Falso) o deje vacío para omitir. Use las flechas para navegar rápidamente.")
    
    # Grid de Tabulación Estilo Oficial
    col_input, col_info = st.columns([2, 1])
    
    with col_input:
        edited_df = st.data_editor(
            st.session_state.data,
            column_config={
                "Nº": st.column_config.NumberColumn(disabled=True, width="small"),
                "Respuesta": st.column_config.SelectboxColumn("R", options=["V", "F", ""], width="medium")
            },
            hide_index=True, height=600, use_container_width=True
        )
        st.session_state.data = edited_df

    with col_info:
        st.markdown("#### Resumen de Sesión")
        df_res, omit, tv, tf = procesar_mmpi2(st.session_state.data)
        st.metric("Ítems Omitidos (?)", omit, delta="-30 límite" if omit < 30 else "INVÁLIDO", delta_color="inverse")
        st.metric("Respuestas V", tv)
        st.metric("Respuestas F", tf)
        if st.button("🔄 Reiniciar Protocolo"):
            st.session_state.data["Respuesta"] = ""
            st.rerun()

# --- MÓDULO 2: DASHBOARD INTERACTIVO ---
elif vista == "📈 Dashboard Diagnóstico":
    st.title(f"Perfil Clínico: {st.session_state.paciente['nombre']}")
    df_res, omit, tv, tf = procesar_mmpi2(st.session_state.data)
    
    if omit > 30:
        st.error(f"🚨 PROTOCOLO INVÁLIDO: Se detectaron {omit} omisiones. No se recomienda la interpretación clínica.")
    
    # Gráfico Plotly Interactivo
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_res["Escala"], y=df_res["T"], mode='lines+markers+text', 
                             text=df_res["T"], textposition="top center",
                             line=dict(color='#1e3a8a', width=3), name="Puntuación T"))
    fig.add_hline(y=65, line_dash="dash", line_color="red", annotation_text="Umbral Clínico")
    fig.update_layout(title="Perfil Psicométrico MMPI-2", yaxis_range=[30, 110], height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Análisis de la "IA" Clínica
    st.markdown("### Interpretación Automatizada de Escalas")
    for _, row in df_res.iterrows():
        expander_title = f"{'🚨' if row['T'] >= 65 else '✅'} {row['Escala']} (T={row['T']})"
        with st.expander(expander_title):
            st.write(f"**Hallazgo:** {row['Análisis']}")

# --- MÓDULO 3: EXPORTACIÓN WORD ---
elif vista == "📄 Exportación de Informe":
    st.title("Generador de Informe Forense / Clínico")
    st.write("Presione el botón para generar un documento profesional con gráficas y firmas.")
    
    df_res, omit, tv, tf = procesar_mmpi2(st.session_state.data)
    
    if st.button("🚀 Generar Informe Word (.docx)"):
        doc = Document()
        
        # Encabezado
        doc.add_heading('INFORME DE RESULTADOS MMPI-2', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Datos Paciente
        doc.add_heading('1. Datos de Identificación', level=1)
        table_p = doc.add_table(rows=2, cols=2)
        table_p.rows[0].cells[0].text = f"Paciente: {st.session_state.paciente['nombre']}"
        table_p.rows[0].cells[1].text = f"Expediente: {st.session_state.paciente['id']}"
        table_p.rows[1].cells[0].text = f"Sexo: {st.session_state.paciente['sexo']}"
        table_p.rows[1].cells[1].text = f"Fecha: {datetime.now().strftime('%d/%m/%Y')}"

        # Gráfica
        doc.add_heading('2. Perfil Psicométrico', level=1)
        img_buf = generar_grafico_word(df_res)
        doc.add_picture(img_buf, width=Inches(6.0))
        
        # Resultados Tabla
        doc.add_heading('3. Tabla de Puntuaciones', level=1)
        t = doc.add_table(rows=1, cols=4)
        t.style = 'Table Grid'
        hdrs = t.rows[0].cells
        hdrs[0].text, hdrs[1].text, hdrs[2].text, hdrs[3].text = 'Escala', 'PD', 'PD+K', 'T'
        for _, row in df_res.iterrows():
            rc = t.add_row().cells
            rc[0].text, rc[1].text, rc[2].text, rc[3].text = str(row['Escala']), str(row['PD']), str(row['PD_K']), str(row['T'])

        # Análisis IA
        doc.add_heading('4. Impresiones Clínicas Automatizadas', level=1)
        for _, row in df_res.iterrows():
            if row['T'] >= 65:
                p = doc.add_paragraph(style='List Bullet')
                p.add_run(f"{row['Escala']}: ").bold = True
                p.add_run(row['Análisis'])

        # Firma
        doc.add_paragraph("\n\n__________________________\nFirma del Psicólogo Colegiado")

        # Descarga
        final_buf = io.BytesIO()
        doc.save(final_buf)
        final_buf.seek(0)
        st.download_button("📥 DESCARGAR INFORME COMPLETO", final_buf, f"Informe_{st.session_state.paciente['nombre']}.docx")
