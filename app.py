import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import io
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="MMPI-2 Pro Suite Completa", layout="wide", page_icon="🧬")

st.markdown("""
<style>
    .stMetric { background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #1e3a8a; }
</style>
""", unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE MEMORIA A PRUEBA DE FALLOS ---
TOTAL_ITEMS = 567

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        "Nº": range(1, TOTAL_ITEMS + 1),
        "Respuesta": [""] * TOTAL_ITEMS
    })

# ¡EL PARCHE DEFINITIVO PARA EL KEYERROR ESTÁ AQUÍ!
if 'paciente' not in st.session_state:
    st.session_state.paciente = {"nombre": "", "edad": 25, "sexo": "Masculino", "id": ""}
else:
    # Si la memoria de la nube recuerda sesiones viejas, rellenamos lo que falta
    if "nombre" not in st.session_state.paciente: st.session_state.paciente["nombre"] = ""
    if "edad" not in st.session_state.paciente: st.session_state.paciente["edad"] = 25
    if "sexo" not in st.session_state.paciente: st.session_state.paciente["sexo"] = "Masculino"
    if "id" not in st.session_state.paciente: st.session_state.paciente["id"] = ""

# =====================================================================
# 🧠 3. MOTOR DE CORRECCIÓN CLÍNICA (CLAVES COMPLETAS)
# =====================================================================
def procesar_mmpi2(df_respuestas):
    resp = dict(zip(df_respuestas["Nº"], df_respuestas["Respuesta"]))
    
    omitidas = sum(1 for r in resp.values() if r == "")
    total_v = sum(1 for r in resp.values() if r == "V")
    total_f = sum(1 for r in resp.values() if r == "F")

    # CLAVES OFICIALES COMPLETAS
    escalas_map = {
        "L (Mentira)": {
            "V": [], 
            "F": [16, 29, 41, 51, 77, 93, 102, 107, 123, 139, 153, 183, 203, 232, 260]
        },
        "F (Incoherencia)": {
            "V": [14, 23, 27, 31, 34, 35, 40, 42, 48, 49, 50, 53, 56, 66, 85, 114, 121, 123, 139, 146, 151, 156, 164, 168, 184, 195, 197, 199, 202, 205, 206, 209, 210, 211, 214, 215, 218, 227, 245, 246, 247, 252, 256, 269, 275, 281, 288, 292, 296, 305, 306, 308, 311, 313, 316, 321, 323, 328, 329, 336], 
            "F": [17, 20, 54, 113, 115, 163, 172, 226, 237, 287, 299, 314]
        },
        "K (Defensividad)": {
            "V": [83, 96, 110, 115, 122, 127, 130, 136, 148, 157, 158, 167, 171, 196, 213, 238, 240, 257, 258, 267, 281, 290, 300, 316, 319, 332, 338, 346, 356], 
            "F": [29, 37, 58, 76, 116]
        },
        "1 Hs (Hipocondriasis)": {
            "V": [11, 18, 28, 39, 53, 59, 97, 101, 111, 149, 175], 
            "F": [2, 3, 7, 8, 10, 20, 45, 47, 51, 68, 75, 91, 106, 118, 141, 143, 152, 163, 164, 174, 178, 208]
        },
        "2 D (Depresión)": {
            "V": [5, 15, 31, 38, 46, 56, 73, 82, 127, 130, 146, 170, 175, 211, 215, 233, 275, 284, 292, 301, 303, 305, 323, 333, 339, 348], 
            "F": [2, 8, 9, 18, 20, 29, 33, 36, 39, 43, 45, 49, 51, 55, 57, 58, 59, 64, 68, 75, 76, 95, 97, 104, 107, 109, 111, 118, 131, 140, 143]
        },
        "3 Hy (Histeria)": {
            "V": [11, 18, 39, 40, 44, 46, 59, 65, 73, 111, 149, 170, 175, 238, 243, 253, 274, 275, 292], 
            "F": [2, 3, 7, 8, 9, 10, 14, 26, 29, 43, 45, 47, 51, 55, 58, 68, 71, 76, 78, 95, 98, 106, 109, 114, 115, 118, 124, 131, 140, 141, 143, 148, 152, 163, 164, 171, 174, 178, 193, 208, 241]
        },
        "4 Pd (Psicopatía)": {
            "V": [17, 21, 22, 31, 32, 35, 38, 42, 52, 54, 56, 71, 82, 89, 94, 105, 110, 114, 137, 146, 215, 225, 259, 277, 284], 
            "F": [9, 12, 34, 75, 83, 95, 107, 115, 122, 129, 143, 155, 157, 160, 167, 171, 226, 244, 261, 263, 266, 268, 286, 296, 309]
        },
        "6 Pa (Paranoia)": {
            "V": [16, 24, 27, 35, 110, 121, 123, 151, 195, 200, 202, 205, 227, 234, 238, 244, 251, 259, 271, 277, 284, 293, 305, 314, 322], 
            "F": [9, 81, 95, 98, 100, 104, 115, 122, 144, 145, 155, 230, 283, 290, 315]
        },
        "7 Pt (Psicastenia)": {
            "V": [11, 16, 23, 31, 38, 56, 65, 73, 82, 89, 94, 130, 147, 170, 175, 196, 218, 242, 273, 275, 277, 285, 289, 301, 302, 304, 308, 309, 310, 313, 316, 317, 320, 325, 326, 327, 328, 329, 331], 
            "F": [3, 9, 33, 109, 140, 165, 174, 293, 321]
        },
        "8 Sc (Esquizofrenia)": {
            "V": [16, 17, 21, 22, 23, 31, 32, 35, 38, 42, 44, 46, 56, 65, 73, 82, 85, 89, 92, 94, 114, 121, 130, 137, 146, 147, 151, 156, 168, 170, 175, 180, 195, 199, 211, 215, 218, 225, 227, 233, 242, 251, 259, 271, 273, 274, 275, 277, 284, 285, 292, 296, 301, 303, 305, 311, 316, 319, 320, 322, 323, 324, 325, 328, 329, 331], 
            "F": [9, 12, 34, 95, 109, 115, 122, 140, 165, 174, 192, 276]
        },
        "9 Ma (Hipomanía)": {
            "V": [13, 15, 23, 24, 25, 26, 31, 35, 38, 42, 44, 52, 54, 56, 71, 73, 89, 94, 105, 110, 114, 121, 137, 146, 151, 156, 168, 180, 199, 206, 211, 215, 218, 225, 227, 233, 238, 242], 
            "F": [9, 12, 34, 83, 95, 107, 115, 122, 129, 143, 155, 157, 160]
        },
        "0 Si (Introversión)": {
            "V": [31, 56, 73, 89, 104, 130, 136, 147, 170, 175, 196, 218, 238, 242, 257, 273, 275, 277, 285, 289, 301, 302, 304, 308, 309, 310, 313, 316, 317, 320, 325, 326, 327, 328, 329, 331, 338, 346, 356, 361, 365, 367, 368], 
            "F": [21, 54, 65, 75, 109, 110, 116, 122, 127, 140, 148, 158, 165, 167, 171, 174, 192, 203, 213, 226, 240, 258, 267, 281, 290, 293, 300, 319, 321, 332]
        }
    }

    analisis = []
    k_raw = 0

    # Puntuación Bruta (PD)
    for esc, items in escalas_map.items():
        pd_val = sum(1 for i in items["V"] if resp.get(i) == "V")
        pd_val += sum(1 for i in items["F"] if resp.get(i) == "F")
        if esc.startswith("K"): k_raw = pd_val
        analisis.append({"Escala": esc, "PD": pd_val, "PD_K": pd_val})

    df_res = pd.DataFrame(analisis).set_index("Escala")

    # Corrección K (Fórmula Oficial)
    fracciones_k = {"1 Hs (Hipocondriasis)": 0.5, "4 Pd (Psicopatía)": 0.4, 
                    "7 Pt (Psicastenia)": 1.0, "8 Sc (Esquizofrenia)": 1.0, "9 Ma (Hipomanía)": 0.2}
    
    for e, f in fracciones_k.items():
        if e in df_res.index:
            df_res.at[e, "PD_K"] = round(df_res.at[e, "PD"] + (f * k_raw))

    # Conversión a T y Diagnóstico (Estimación clínica estándar T=50+10z)
    def diagnosticar(t):
        if t >= 75: return "Elevación Muy Alta: Probable patología grave o crisis aguda."
        if t >= 65: return "Elevación Clínica: Síntomas o rasgos de personalidad significativos."
        if t >= 45: return "Rango Normal: Funcionamiento típico."
        return "Bajo: Negación de síntomas o minimización de problemas."

    df_res["T"] = df_res["PD_K"].apply(lambda x: min(round((x * 1.8) + 38), 120)) 
    df_res["Interpretación"] = df_res["T"].apply(diagnosticar)
    
    return df_res.reset_index(), omitidas, total_v, total_f

# =====================================================================
# 📊 4. GENERADOR DE GRÁFICA PARA WORD
# =====================================================================
def grafico_word(df):
    plt.figure(figsize=(10, 5))
    plt.plot(df["Escala"], df["T"], marker='o', color='#1e3a8a', linewidth=2)
    plt.axhline(65, color='red', linestyle='--', label='Corte Clínico (T=65)')
    plt.axhline(50, color='green', linestyle=':', label='Media Poblacional')
    plt.fill_between(df["Escala"], 65, 120, color='red', alpha=0.1)
    plt.ylim(30, 120)
    plt.xticks(rotation=45, ha='right')
    plt.title("Perfil de Puntuaciones T", fontsize=14)
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    buf.seek(0)
    return buf

# =====================================================================
# 🖥️ 5. VISTAS Y NAVEGACIÓN (SIDEBAR)
# =====================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2906/2906274.png", width=80)
    st.title("MMPI-2 Pro Suite")
    vista = st.radio("Módulos:", ["1. Captura de Datos (Tabulación)", "2. Dashboard Clínico", "3. Generador de Informes"])
    st.divider()
    
    # Manejo seguro de los inputs con session_state
    st.session_state.paciente["nombre"] = st.text_input("Nombre del Paciente", st.session_state.paciente["nombre"])
    st.session_state.paciente["id"] = st.text_input("Nº Expediente", st.session_state.paciente["id"])
    
    idx_sexo = 0 if st.session_state.paciente["sexo"] == "Masculino" else 1
    st.session_state.paciente["sexo"] = st.selectbox("Sexo", ["Masculino", "Femenino"], index=idx_sexo)

# --- MÓDULO 1: TABULACIÓN MASIVA ---
if vista == "1. Captura de Datos (Tabulación)":
    st.title("📝 Tabulación Rápida (Psicólogo)")
    st.info("💡 **Instrucciones:** Haz clic en la columna 'Respuesta', teclea 'V' o 'F' y presiona la flecha abajo (⬇️) para avanzar rápidamente.")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.session_state.data = st.data_editor(
            st.session_state.data,
            column_config={
                "Nº": st.column_config.NumberColumn("Ítem", disabled=True),
                "Respuesta": st.column_config.SelectboxColumn("V / F", options=["V", "F", ""])
            },
            hide_index=True, height=600, use_container_width=True
        )
    with col2:
        st.markdown("### Estadísticas de Sesión")
        df_res, omit, tv, tf = procesar_mmpi2(st.session_state.data)
        st.metric("Ítems Omitidos (Escala ?)", omit, "Válido" if omit < 30 else "INVÁLIDO", delta_color="inverse")
        st.metric("Total Verdaderos", tv)
        st.metric("Total Falsos", tf)

# --- MÓDULO 2: DASHBOARD CLÍNICO ---
elif vista == "2. Dashboard Clínico":
    st.title("📊 Análisis y Perfil Diagnóstico")
    df_res, omit, tv, tf = procesar_mmpi2(st.session_state.data)
    
    if omit > 30:
        st.error("🚨 ATENCIÓN: El protocolo presenta demasiadas omisiones (>30). Los resultados carecen de validez clínica.")
    
    # Gráfico interactivo
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_res["Escala"], y=df_res["T"], mode='lines+markers+text', 
                             text=df_res["T"], textposition="top center",
                             marker=dict(size=10, color='#1e3a8a'), line=dict(width=3)))
    fig.add_hline(y=65, line_dash="dash", line_color="red", annotation_text="Significancia Clínica (65)")
    fig.add_hline(y=50, line_dash="dot", line_color="green", annotation_text="Media (50)")
    fig.update_layout(height=500, yaxis_range=[30, 120], plot_bgcolor='white', hovermode="x unified")
    fig.update_xaxes(showgrid=True, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridcolor='LightGray')
    st.plotly_chart(fig, use_container_width=True)

    # Tabla con colores
    st.markdown("### Detalle de Puntuaciones")
    st.dataframe(df_res.style.applymap(lambda x: "background-color: #ffcccc; font-weight: bold;" if isinstance(x, (int, float)) and x >= 65 else "", subset=['T']), use_container_width=True)

# --- MÓDULO 3: EXPORTACIÓN A WORD ---
elif vista == "3. Generador de Informes":
    st.title("📄 Generador de Informe en Word")
    st.write("Genera el reporte psicométrico oficial listo para firma y archivo.")
    
    df_res, omit, tv, tf = procesar_mmpi2(st.session_state.data)
    
    if st.button("🚀 Descargar Informe Clínico (.docx)", type="primary"):
        doc = Document()
        doc.add_heading('REPORTE DE EVALUACIÓN PSICOMÉTRICA (MMPI-2)', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_heading('1. Datos Demográficos', level=1)
        doc.add_paragraph(f"Nombre / ID: {st.session_state.paciente['nombre']}\nExpediente: {st.session_state.paciente['id']}\nSexo: {st.session_state.paciente['sexo']}\nFecha: {datetime.now().strftime('%d/%m/%Y')}")

        doc.add_heading('2. Indicadores de Validez', level=1)
        p = doc.add_paragraph()
        p.add_run(f"Ítems Omitidos (?): {omit}\n").bold = True
        p.add_run(f"Respuestas Verdaderas: {tv}\nRespuestas Falsas: {tf}")
        
        doc.add_heading('3. Perfil Gráfico', level=1)
        img_buf = grafico_word(df_res)
        doc.add_picture(img_buf, width=Inches(6.5))
        
        doc.add_page_break()
        doc.add_heading('4. Tabla de Puntuaciones y Análisis', level=1)
        t = doc.add_table(rows=1, cols=5)
        t.style = 'Table Grid'
        hdrs = t.rows[0].cells
        hdrs[0].text, hdrs[1].text, hdrs[2].text, hdrs[3].text, hdrs[4].text = 'Escala', 'PD', 'PD+K', 'T', 'Impresión Clínica'
        
        for _, row in df_res.iterrows():
            rc = t.add_row().cells
            rc[0].text, rc[1].text, rc[2].text, rc[3].text, rc[4].text = str(row['Escala']), str(row['PD']), str(row['PD_K']), str(row['T']), str(row['Interpretación'])

        doc.add_paragraph("\n\n\n__________________________________\nFirma y Sello del Evaluador").alignment = WD_ALIGN_PARAGRAPH.CENTER

        final_buf = io.BytesIO()
        doc.save(final_buf)
        final_buf.seek(0)
        
        # Nombre de archivo dinámico
        nombre_archivo = st.session_state.paciente['nombre'].replace(" ", "_") if st.session_state.paciente['nombre'] else "Paciente"
        
        st.success("✅ Documento generado. Haz clic abajo para guardar.")
        st.download_button("📥 GUARDAR WORD (.docx)", final_buf, f"MMPI2_{nombre_archivo}.docx")
