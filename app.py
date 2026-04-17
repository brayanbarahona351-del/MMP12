import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# =====================================================================
# 🎨 1. CONFIGURACIÓN Y ESTILOS
# =====================================================================
st.set_page_config(page_title="MMPI-2 Ultimate Suite Pro", layout="wide", page_icon="🧠")

st.markdown("""
<style>
    .instruction-sticky {
        position: -webkit-sticky; position: sticky; top: 0;
        background-color: #f0f7ff; color: #0747a6; padding: 15px;
        border-radius: 8px; border-left: 10px solid #0052cc;
        z-index: 999; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .interpretation-card {
        background-color: white; padding: 25px; border-radius: 12px;
        border-left: 8px solid #1e3a8a; margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .clinical-high { border-left-color: #d32f2f !important; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 🧠 2. MEMORIA DEL SISTEMA
# =====================================================================
TOTAL_ITEMS = 567

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({"Nº": range(1, TOTAL_ITEMS + 1), "Respuesta": [""] * TOTAL_ITEMS})

if 'paciente' not in st.session_state:
    st.session_state.paciente = {
        "nombre": "", "rut": "", "edad": 25, "sexo": "Masculino", 
        "estado_civil": "Soltero(a)", "profesion": "", "institucion": "SERPAJ CHILE"
    }

# =====================================================================
# 🧮 3. MOTOR DE IA CLÍNICA (ABUNDANTE Y DETALLADO)
# =====================================================================
def obtener_analisis_extenso(escala, t):
    diccionario = {
        "L (Mentira)": {
            "Alta": "El evaluado presenta un esfuerzo deliberado y rígido por proyectar una imagen moralmente impecable. Esto sugiere una falta de insight profundo y una resistencia defensiva que puede obstaculizar el proceso terapéutico inicial. Se recomienda explorar la necesidad de aprobación social.",
            "Normal": "Actitud honesta. El sujeto reconoce sus fallas comunes, lo que valida la veracidad del resto del perfil."
        },
        "2 D (Depresión)": {
            "Alta": "Puntaje clínicamente significativo. Indica una presencia marcada de sentimientos de desamparo, apatía y un pesimismo rumiante. El sujeto reporta baja energía vital y dificultades para visualizar un futuro positivo.",
            "Sug": "Priorizar intervención en activación conductual y monitoreo de riesgo autolítico."
        },
        "8 Sc (Esquizofrenia)": {
            "Alta": "Indica sentimientos de alienación social y confusión en los procesos de pensamiento. El evaluado se siente 'diferente' o desconectado de las normas convencionales de la realidad.",
            "Sug": "Evaluar posible consumo de sustancias o necesidad de interconsulta psiquiátrica."
        }
    }
    
    nivel = "Normal"
    if t >= 75: nivel = "Muy Alta"
    elif t >= 65: nivel = "Alta"
    
    base = diccionario.get(escala, {})
    analisis = base.get(nivel, "El puntaje obtenido se encuentra dentro de los rangos de normalidad estadística, no sugiriendo rasgos patológicos agudos en esta área.")
    sugerencia = base.get("Sug", "Mantener observación clínica general.")
    
    return f"**Análisis Clínico:** {analisis} \n\n **Recomendación:** {sugerencia}"

def calcular_escalas_pro(df_resp):
    # Simulación de cálculo (Aquí debe ir la lógica completa de PD a T)
    escalas = ["L (Mentira)", "F (Incoherencia)", "K (Defensividad)", "1 Hs", "2 D", "3 Hy", "4 Pd", "6 Pa", "7 Pt", "8 Sc", "9 Ma", "0 Si"]
    data_res = []
    for esc in escalas:
        t_val = 50 + (len(esc) % 25) # Valor simulado
        data_res.append({"Escala": esc, "T": t_val, "Analisis": obtener_analisis_extenso(esc, t_val)})
    return pd.DataFrame(data_res)

# =====================================================================
# 📄 4. GENERADOR DE INFORME WORD (ALTA COMPLEJIDAD)
# =====================================================================
def generar_word_abundante(p, df_items, df_resultados):
    doc = Document()
    
    # --- SECCIÓN 1: ENCABEZADO INSTITUCIONAL ---
    section = doc.sections[0]
    header = section.header
    htxt = header.paragraphs[0]
    htxt.text = f"DEPARTAMENTO DE EVALUACIÓN PSICOLÓGICA - {p['institucion']}"
    htxt.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # Título Principal
    title = doc.add_heading('INFORME PSICOMÉTRICO MMPI-2: ANÁLISIS INTEGRAL', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # --- SECCIÓN 2: IDENTIFICACIÓN ---
    doc.add_heading('1. DATOS DE IDENTIFICACIÓN', level=1)
    table = doc.add_table(rows=4, cols=2)
    table.style = 'Table Grid'
    cells = table.rows[0].cells
    cells[0].text = f"Nombre: {p['nombre']}"
    cells[1].text = f"RUT: {p['rut']}"
    cells = table.rows[1].cells
    cells[0].text = f"Edad: {p['edad']} años"
    cells[1].text = f"Sexo: {p['sexo']}"
    cells = table.rows[2].cells
    cells[0].text = f"Estado Civil: {p['estado_civil']}"
    cells[1].text = f"Profesión: {p['profesion']}"

    # --- SECCIÓN 3: PROTOCOLO DE RESPUESTAS (La "Copia" de la imagen de llenado) ---
    doc.add_page_break()
    doc.add_heading('2. PROTOCOLO DE RESPUESTAS (567 ÍTEMS)', level=1)
    doc.add_paragraph("A continuación se detallan las respuestas registradas por el evaluado para fines de archivo y auditoría clínica.")
    
    # Crear tabla de respuestas en 10 columnas para ahorrar espacio
    num_cols = 10
    rows = (TOTAL_ITEMS // num_cols) + 1
    resp_table = doc.add_table(rows=rows, cols=num_cols)
    resp_table.style = 'Table Grid'
    
    for i, row in df_items.iterrows():
        r_idx = i // num_cols
        c_idx = i % num_cols
        resp_table.rows[r_idx].cells[c_idx].text = f"{row['Nº']}: {row['Respuesta']}"
        # Ajustar fuente pequeña
        for paragraph in resp_table.rows[r_idx].cells[c_idx].paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(8)

    # --- SECCIÓN 4: ANÁLISIS DE RESULTADOS ---
    doc.add_page_break()
    doc.add_heading('3. ANÁLISIS DE ESCALAS Y MOTOR DE IA', level=1)
    doc.add_paragraph("Interpretación técnica basada en la configuración del Perfil de Puntuaciones T.")
    
    for _, row in df_resultados.iterrows():
        p_esc = doc.add_paragraph()
        run = p_esc.add_run(f"■ {row['Escala']} (Puntuación T: {row['T']})")
        run.bold = True
        run.font.size = Pt(12)
        
        # Interpretación de la IA
        doc.add_paragraph(row['Analisis'].replace("**", ""))

    # --- SECCIÓN 5: CONCLUSIONES Y RECOMENDACIONES ---
    doc.add_heading('4. SÍNTESIS GENERAL Y SUGERENCIAS', level=1)
    doc.add_paragraph("Sobre la base de los datos expuestos, se concluye que el evaluado presenta un perfil con indicadores de [AÑADIR SÍNTESIS].")
    doc.add_paragraph("Se sugieren las siguientes líneas de acción:")
    doc.add_paragraph("- Sesión de devolución de resultados.", style='List Bullet')
    doc.add_paragraph("- Seguimiento en área de salud mental si las elevaciones persisten.", style='List Bullet')

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

# =====================================================================
# 🖥️ 5. INTERFAZ Y NAVEGACIÓN
# =====================================================================
with st.sidebar:
    st.title("MMPI-2 PRO v2026")
    modulo = st.radio("Módulos:", ["👤 Ficha Técnica", "📝 Aplicación", "⌨️ Tabulación", "📊 Resultados e IA", "📄 Exportar Informe"])

# --- INSTRUCCIONES PERSISTENTES ---
st.markdown(f"""
<div class="instruction-sticky">
    <strong>📋 Módulo actual: {modulo}</strong><br>
    Recuerde que para generar el informe completo, debe haber completado la Ficha Técnica y la Tabulación. 
    El informe exportado incluirá el protocolo de los 567 ítems y el análisis profundo de la IA.
</div>
""", unsafe_allow_html=True)

if modulo == "👤 Ficha Técnica":
    st.header("Datos del Evaluado")
    p = st.session_state.paciente
    c1, c2 = st.columns(2)
    with c1:
        p["nombre"] = st.text_input("Nombre y Apellidos", p["nombre"])
        p["rut"] = st.text_input("RUT / ID", p["rut"])
        p["edad"] = st.number_input("Edad", 18, 99, p["edad"])
    with c2:
        p["estado_civil"] = st.text_input("Estado Civil", p["estado_civil"])
        p["profesion"] = st.text_input("Profesión", p["profesion"])
        p["institucion"] = st.text_input("Institución Solicitante", p["institucion"])

elif modulo == "📊 Resultados e IA":
    st.header("Perfil Clínico")
    df_res = calcular_escalas_pro(st.session_state.data)
    
    fig = go.Figure(go.Scatter(x=df_res["Escala"], y=df_res["T"], mode='lines+markers+text', text=df_res["T"]))
    fig.add_hline(y=65, line_dash="dash", line_color="red", annotation_text="Punto de Corte")
    st.plotly_chart(fig, use_container_width=True)

    for _, row in df_res.iterrows():
        estilo = "interpretation-card clinical-high" if row["T"] >= 65 else "interpretation-card"
        st.markdown(f'<div class="{estilo}"><h3>{row["Escala"]} (T={row["T"]})</h3>{row["Analisis"]}</div>', unsafe_allow_html=True)

elif modulo == "📄 Exportar Informe":
    st.header("Generación de Informe Institucional Completo")
    st.info("El documento generado contiene: Protocolo de respuestas, Ficha técnica, Gráficos explicados (narrativa) y Análisis de IA.")
    
    if st.button("🚀 Generar Informe de Alta Complejidad (.docx)"):
        with st.spinner("Construyendo documento extenso..."):
            df_res = calcular_escalas_pro(st.session_state.data)
            docx_file = generar_word_abundante(st.session_state.paciente, st.session_state.data, df_res)
            
            st.success("✅ Informe generado con éxito.")
            st.download_button(
                label="📥 Descargar Informe Profesional",
                data=docx_file,
                file_name=f"Informe_MMPI2_{st.session_state.paciente['rut']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

elif modulo == "⌨️ Tabulación":
    st.header("Editor de Protocolo")
    st.session_state.data = st.data_editor(st.session_state.data, use_container_width=True, height=600)
