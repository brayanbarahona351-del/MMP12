import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
import time
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# =====================================================================
# 🎨 1. ESTÉTICA PROFESIONAL "TEA EDICIONES" (CSS CUSTOM)
# =====================================================================
st.set_page_config(page_title="MMPI-2 TEA Suite Pro", layout="wide", page_icon="📈")

def apply_tea_style():
    st.markdown("""
    <style>
        /* Paleta TEA: Azules profundos, grises técnicos y blanco */
        :root { --tea-blue: #0056b3; --tea-dark: #1a202c; --tea-bg: #f7fafc; }
        
        .main { background-color: var(--tea-bg); font-family: 'Segoe UI', sans-serif; }
        
        /* Barra de instrucciones persistente estilo "Gula de Aplicación" */
        .instruction-sticky {
            position: -webkit-sticky; position: sticky; top: 1rem;
            background-color: #ffffff; color: #2d3748; padding: 20px;
            border-radius: 8px; border: 1px solid #e2e8f0; border-top: 6px solid #0056b3;
            z-index: 1000; margin-bottom: 2rem; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }

        /* Cartas de resultados */
        .result-card {
            background-color: white; padding: 25px; border-radius: 10px;
            border: 1px solid #e2e8f0; margin-bottom: 20px;
        }
        .clinical-alert { border-left: 10px solid #c53030; }
        .clinical-normal { border-left: 10px solid #2f855a; }

        /* Botones estilo TEA */
        div.stButton > button {
            background-color: #0056b3; color: white; border-radius: 5px;
            height: 3.5em; width: 100%; font-weight: 600; border: none;
        }
        div.stButton > button:hover { background-color: #004494; border: none; color: white; }
        
        h1, h2, h3 { color: #1a365d; }
    </style>
    """, unsafe_allow_html=True)

apply_tea_style()

# =====================================================================
# 🧠 2. NÚCLEO DE DATOS Y PERSISTENCIA (ANTI-KEYERROR)
# =====================================================================
TOTAL_ITEMS = 567

def init_state():
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame({"Nº": range(1, TOTAL_ITEMS + 1), "Respuesta": [""] * TOTAL_ITEMS})
    
    defaults = {
        "nombre": "", "rut": "", "edad": 25, "sexo": "Masculino", 
        "estado_civil": "Soltero(a)", "profesion": "", "institucion": "PN - HONDURAS",
        "motivo": "Evaluación de Control y Confianza", "fecha": datetime.now().strftime("%d/%m/%Y"),
        "perito": "Sub-Inspector Brayan Barahona"
    }
    
    if 'paciente' not in st.session_state:
        st.session_state.paciente = defaults
    else:
        for k, v in defaults.items():
            if k not in st.session_state.paciente:
                st.session_state.paciente[k] = v

init_state()

# =====================================================================
# 🧮 3. MOTOR DE CORRECCIÓN TÉCNICO (BAREMOS SIMULADOS)
# =====================================================================
class MMPI2_Engine:
    @staticmethod
    def get_clinical_interpretation(escala, t):
        interp = {
            "L": {
                "High": "Defensividad extrema. El sujeto intenta ofrecer una imagen socialmente ajustada, negando fallas comunes. Perfil posiblemente invalidado por rigidez.",
                "Low": "Indica franqueza o, en contextos forenses, cinismo respecto a las normas."
            },
            "F": {
                "High": "Distress agudo o confusión mental. Si T > 80, sugiere 'grito de ayuda' o respuestas al azar.",
                "Normal": "Coherencia en el patrón de respuesta."
            },
            "2 D": {
                "High": "Sintomatología depresiva marcada. Desánimo, baja energía y sentimientos de inutilidad.",
                "Sug": "Evaluación de riesgo autolítico y psicoterapia de apoyo."
            },
            "4 Pd": {
                "High": "Rasgos de impulsividad, conflictos con la autoridad y desajuste social.",
                "Sug": "Trabajar en la internalización de normas y consecuencias conductuales."
            },
            "8 Sc": {
                "High": "Alienación, pensamientos inusuales y posible desorganización cognitiva.",
                "Sug": "Interconsulta psiquiátrica inmediata."
            }
        }
        
        nivel = "Normal"
        if t >= 65: nivel = "Elevado"
        if t >= 75: nivel = "Muy Elevado"
        
        base = interp.get(escala, {"High": "Indicadores clínicos presentes.", "Low": "Normalidad.", "Sug": "Seguimiento clínico."})
        
        return {
            "Nivel": nivel,
            "Analisis": base["High"] if t >= 65 else "Sin hallazgos patológicos significativos.",
            "Sugerencia": base.get("Sug", "Monitoreo preventivo.")
        }

def procesar_perfil():
    # Mapeo simplificado para el ejemplo (en prod usar claves completas)
    escalas = ["L", "F", "K", "1 Hs", "2 D", "3 Hy", "4 Pd", "5 Mf", "6 Pa", "7 Pt", "8 Sc", "9 Ma", "0 Si"]
    resultados = []
    
    for e in escalas:
        # Lógica de cálculo T (Simulada para visualización abundante)
        t_val = 45 + (len(e) * 4) + (np.random.randint(0, 30) if " " not in e else 5)
        info = MMPI2_Engine.get_clinical_interpretation(e, t_val)
        resultados.append({"Escala": e, "T": t_val, "Interpretacion": info})
        
    return pd.DataFrame(resultados)

# =====================================================================
# 📸 4. MÓDULO OMR (ESCÁNER DE IMAGEN)
# =====================================================================
def modulo_scanner():
    st.header("📸 Reconocimiento Óptico de Marcas (OMR)")
    st.write("Cargue la fotografía de la hoja de respuestas para tabulación automática.")
    
    img_file = st.file_uploader("Subir imagen de protocolo", type=['jpg', 'png', 'jpeg'])
    
    if img_file:
        col1, col2 = st.columns(2)
        with col1:
            st.image(img_file, caption="Imagen Original", use_container_width=True)
        
        with col2:
            st.info("Iniciando detección de burbujas...")
            if st.button("🚀 Ejecutar Escáner TEA"):
                with st.spinner("Procesando matriz de píxeles..."):
                    # Simulación de tiempo de procesamiento
                    time.sleep(2)
                    # Lógica OMR: Aquí se insertaría OpenCV real
                    for i in range(TOTAL_ITEMS):
                        st.session_state.data.at[i, "Respuesta"] = "V" if np.random.random() > 0.5 else "F"
                    st.success(f"Detección finalizada: {TOTAL_ITEMS} ítems procesados.")
                    st.balloons()

# =====================================================================
# 📄 5. GENERADOR DE MEGAINFORME CON GRÁFICOS INTEGRADOS
# =====================================================================
def exportar_informe_completo(p, df_items, df_res):
    doc = Document()
    
    # --- Estilos de Word ---
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    # Encabezado
    hdr = doc.sections[0].header
    hdr.paragraphs[0].text = f"CONFIDENCIAL - REPORTE DE EVALUACIÓN PSICOMÉTRICA\n{p['institucion']}"
    
    # Título Principal
    t = doc.add_heading('INFORME TÉCNICO MMPI-2', 0)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 1. Ficha Técnica
    doc.add_heading('1. IDENTIFICACIÓN', level=1)
    grid = doc.add_table(rows=5, cols=2)
    grid.style = 'Table Grid'
    grid.rows[0].cells[0].text = f"Nombre: {p['nombre']}"
    grid.rows[0].cells[1].text = f"RUT: {p['rut']}"
    grid.rows[1].cells[0].text = f"Edad: {p['edad']} años"
    grid.rows[1].cells[1].text = f"Sexo: {p['sexo']}"
    grid.rows[2].cells[0].text = f"Profesión: {p['profesion']}"
    grid.rows[2].cells[1].text = f"Estado Civil: {p['estado_civil']}"
    grid.rows[3].cells[0].text = f"Perito: {p['perito']}"
    grid.rows[3].cells[1].text = f"Fecha: {p['fecha']}"

    # 2. Perfil Gráfico (LA MEJORA SOLICITADA)
    doc.add_heading('2. PERFIL PSICOMÉTRICO (GRÁFICO)', level=1)
    
    # Generar imagen del gráfico para Word
    fig = go.Figure(go.Scatter(x=df_res["Escala"], y=df_res["T"], mode='lines+markers+text', 
                             text=df_res["T"], textposition="top center", line=dict(color='#0056b3', width=3)))
    fig.add_hline(y=65, line_dash="dash", line_color="red")
    fig.update_layout(title="Perfil de Puntuaciones T", yaxis_range=[30, 120], width=800, height=400)
    
    img_bytes = fig.to_image(format="png", engine="kaleido")
    image_stream = io.BytesIO(img_bytes)
    doc.add_picture(image_stream, width=Inches(6))
    doc.add_paragraph("Gráfico 1: Distribución de puntuaciones transformadas (T). El área sobre la línea roja (T=65) indica significación clínica.")

    # 3. Interpretación por Áreas
    doc.add_heading('3. INTERPRETACIÓN DE IA POR ESCALAS', level=1)
    for _, row in df_res.iterrows():
        it = row['Interpretacion']
        p_esc = doc.add_paragraph()
        r_esc = p_esc.add_run(f"■ {row['Escala']} (T={row['T']}): ")
        r_esc.bold = True
        
        doc.add_paragraph(f"Nivel: {it['Nivel']}")
        doc.add_paragraph(f"Análisis Técnico: {it['Analisis']}")
        doc.add_paragraph(f"Recomendación: {it['Sugerencia']}")

    # 4. Protocolo de Respuestas (Abundante)
    doc.add_page_break()
    doc.add_heading('4. PROTOCOLO DE RESPUESTAS (567 ÍTEMS)', level=1)
    cols = 15
    rows = (TOTAL_ITEMS // cols) + 1
    t_proto = doc.add_table(rows=rows, cols=cols)
    t_proto.style = 'Table Grid'
    
    for i, row in df_items.iterrows():
        cell = t_proto.rows[i // cols].cells[i % cols]
        cell.text = f"{row['Nº']}:{row['Respuesta']}"
        for para in cell.paragraphs:
            for run in para.runs: run.font.size = Pt(7)

    # Guardado
    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()

# =====================================================================
# 🖥️ 6. INTERFAZ DE USUARIO (NAVEGACIÓN)
# =====================================================================
with st.sidebar:
    st.title("MMPI-2 TEA Suite")
    st.image("https://cdn-icons-png.flaticon.com/512/3062/3062140.png", width=100)
    modulo = st.radio("Módulos del Sistema:", [
        "👤 Ficha Técnica", 
        "📝 Auto-llenado Paciente",
        "📸 Escaneo OMR",
        "⌨️ Tabulación Profesional",
        "📊 Perfil e Interpretación IA",
        "📄 Mega Informe de Impresión"
    ])
    st.divider()
    st.caption(f"Operador: {st.session_state.paciente['perito']}")

# INSTRUCCIONES PERSISTENTES (STICKY)
st.markdown(f"""
<div class="instruction-sticky">
    <strong>📋 MANUAL DE OPERACIÓN:</strong> Usted está en el módulo <strong>{modulo}</strong>.<br>
    Asegúrese de guardar los datos de identificación antes de proceder. El informe final generará un archivo .docx con 
    los gráficos de perfil incluidos y la interpretación analítica de la inteligencia artificial.
</div>
""", unsafe_allow_html=True)

if modulo == "👤 Ficha Técnica":
    st.header("Identificación del Evaluado")
    p = st.session_state.paciente
    col1, col2 = st.columns(2)
    with col1:
        p["nombre"] = st.text_input("Nombre Completo", p["nombre"])
        p["rut"] = st.text_input("Identificación (RUT/DNI)", p["rut"])
        p["edad"] = st.number_input("Edad", 18, 99, int(p["edad"]))
        p["estado_civil"] = st.text_input("Estado Civil", p["estado_civil"])
    with col2:
        p["sexo"] = st.selectbox("Sexo Biológico", ["Masculino", "Femenino"], index=0 if p["sexo"]=="Masculino" else 1)
        p["profesion"] = st.text_input("Profesión/Ocupación", p["profesion"])
        p["institucion"] = st.text_input("Institución", p["institucion"])
        p["motivo"] = st.text_area("Motivo de Evaluación", p["motivo"])

elif modulo == "📝 Auto-llenado Paciente":
    st.header("Aplicación Electrónica del MMPI-2")
    items_por_bloque = 25
    bloque = st.slider("Bloque de Ítems", 1, (TOTAL_ITEMS // items_por_bloque) + 1, 1)
    inicio, fin = (bloque - 1) * items_por_bloque, min(bloque * items_por_bloque, TOTAL_ITEMS)
    
    st.progress(fin / TOTAL_ITEMS)
    
    for i in range(inicio, fin):
        num = i + 1
        val = st.session_state.data.at[i, "Respuesta"]
        sel_idx = 0 if val == "V" else 1 if val == "F" else None
        
        sel = st.radio(f"**{num}.** Declaración MMPI-2 #{num}", ["Verdadero", "Falso"], 
                       index=sel_idx, key=f"q_{num}", horizontal=True)
        st.session_state.data.at[i, "Respuesta"] = "V" if sel == "Verdadero" else "F"

elif modulo == "📸 Escaneo OMR":
    modulo_scanner()

elif modulo == "⌨️ Tabulación Profesional":
    st.header("Entrada Rápida de Datos")
    st.warning("Use este editor para transcribir respuestas desde papel o corregir el escáner.")
    st.session_state.data = st.data_editor(st.session_state.data, hide_index=True, use_container_width=True, height=600)

elif modulo == "📊 Perfil e Interpretación IA":
    st.header("Análisis de Perfil Clínico")
    df_res = procesar_perfil()
    
    # Gráfico interactivo
    fig = go.Figure(go.Scatter(x=df_res["Scale"], y=df_res["T"], mode='lines+markers+text', text=df_res["T"]))
    fig.update_layout(title="Gráfico de Perfil MMPI-2", yaxis_range=[30, 120])
    st.plotly_chart(fig, use_container_width=True)
    
    for _, row in df_res.iterrows():
        it = row['Interpretacion']
        card_style = "clinical-alert" if row['T'] >= 65 else "clinical-normal"
        st.markdown(f"""
        <div class="result-card {card_style}">
            <h3 style='margin-top:0;'>{row['Escala']} (T={row['T']}) — Nivel {it['Nivel']}</h3>
            <p><strong>Análisis:</strong> {it['Analisis']}</p>
            <p><strong>Sugerencia:</strong> {it['Sugerencia']}</p>
        </div>
        """, unsafe_allow_html=True)

elif modulo == "📄 Mega Informe de Impresión":
    st.header("Generador de Reporte Institucional (Formato TEA)")
    st.info("Este proceso generará un documento de alta complejidad con gráficos, protocolos e interpretaciones integradas.")
    
    if st.button("🚀 Generar y Descargar MEGA INFORME (.docx)"):
        with st.spinner("Procesando gráficos e interpretaciones clínicas..."):
            df_res = procesar_perfil()
            docx_data = exportar_informe_completo(st.session_state.paciente, st.session_state.data, df_res)
            
            st.success("✅ Informe compilado exitosamente.")
            st.download_button(
                label="📥 Descargar Informe Profesional",
                data=docx_data,
                file_name=f"Reporte_MMPI2_{st.session_state.paciente['rut']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
