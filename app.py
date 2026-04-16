import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# =====================================================================
# 🎨 1. CONFIGURACIÓN Y ESTILOS PROFESIONALES
# =====================================================================
st.set_page_config(page_title="MMPI-2 Ultimate Suite Pro", layout="wide", page_icon="🧠")

st.markdown("""
<style>
    .main { background-color: #f4f7f9; }
    /* Instrucciones persistentes */
    .instruction-bar {
        background-color: #1e3a8a;
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 25px;
        border-left: 10px solid #fbbf24;
    }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .interpretation-card {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        border-left: 8px solid #1e3a8a;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .high-score { border-left-color: #dc2626 !important; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 🧠 2. MEMORIA Y ESTADO DE SESIÓN
# =====================================================================
TOTAL_ITEMS = 567

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        "Nº": range(1, TOTAL_ITEMS + 1),
        "Respuesta": [""] * TOTAL_ITEMS
    })

if 'paciente' not in st.session_state:
    st.session_state.paciente = {
        "nombre": "", "rut": "", "edad": 25, "sexo": "Masculino", 
        "estado_civil": "Soltero(a)", "profesion": "", "institucion": "SERPAJ CHILE",
        "codigo_unico": f"EXP-{pd.Timestamp.now().strftime('%Y%m%d-%H%M')}"
    }

# =====================================================================
# 🧮 3. MOTOR IA: LÓGICA CLÍNICA EXTENSA
# =====================================================================
def interpretar_ia_detallada(escala, t):
    interpretaciones = {
        "L (Mentira)": {
            "Alta": "Presenta una tendencia marcada a la negación de fallas morales menores. El evaluado busca proyectar una imagen de perfección inalcanzable, lo que sugiere rigidez defensiva y falta de insight.",
            "Normal": "Actitud de respuesta honesta y capacidad de autocrítica saludable.",
            "Baja": "Indica un cinismo social o una independencia extrema de las normas convencionales.",
        },
        "2 D (Depresión)": {
            "Alta": "Puntaje clínicamente significativo. Sugiere un estado de desánimo profundo, pesimismo, posible enlentecimiento psicomotor y sentimientos de inutilidad. El sujeto se siente abrumado por las exigencias del entorno.",
            "Normal": "Nivel de energía y estado de ánimo dentro de la normalidad estadística.",
            "Sug": "Se recomienda evaluación de riesgo suicida y terapia de activación conductual."
        },
        "8 Sc (Esquizofrenia)": {
            "Alta": "Indica sentimientos de alienación, confusión mental y posibles alteraciones en la percepción de la realidad. El evaluado puede sentirse incomprendido o 'diferente' de manera disfuncional.",
            "Normal": "Buen contacto con la realidad y procesos de pensamiento coherentes.",
            "Sug": "Es imperativo descartar consumo de sustancias o condiciones orgánicas cerebrales."
        }
    }
    
    nivel = "Normal"
    if t >= 75: nivel = "Muy Alta"
    elif t >= 65: nivel = "Alta"
    elif t < 45: nivel = "Baja"
    
    base = interpretaciones.get(escala, {})
    analisis = base.get(nivel if nivel in base else "Normal", f"El puntaje obtenido (T={t}) sugiere rasgos de personalidad dentro del promedio o con variaciones leves no patológicas.")
    sugerencia = base.get("Sug", "Continuar con el monitoreo clínico habitual.")
    
    return f"**Análisis:** {analisis}\n\n**Recomendación Terapéutica:** {sugerencia}"

def ejecutar_motor_ia(df_resp):
    resp = dict(zip(df_resp["Nº"], df_resp["Respuesta"]))
    
    # Ejemplo de claves (Esto debe completarse con el manual MMPI-2 oficial)
    escalas_config = {
        "L (Mentira)": {"V": [], "F": [16, 29, 41, 51, 77, 93, 102]},
        "2 D (Depresión)": {"V": [5, 15, 18, 25, 31, 32], "F": [2, 8, 9, 10]},
        "8 Sc (Esquizofrenia)": {"V": [16, 17, 21, 22, 23], "F": [9, 12, 34]}
    }

    resultados = []
    for esc, keys in escalas_config.items():
        pd_val = sum(1 for i in keys["V"] if resp.get(i) == "V")
        pd_val += sum(1 for i in keys["F"] if resp.get(i) == "F")
        t_val = min(round((pd_val * 2.5) + 35), 110) # Simulación de baremo
        resultados.append({
            "Escala": esc,
            "PD": pd_val,
            "T": t_val,
            "IA_Analisis": interpretar_ia_detallada(esc, t_val)
        })
    
    return pd.DataFrame(resultados)

# =====================================================================
# 🖥️ 4. INTERFAZ Y NAVEGACIÓN
# =====================================================================
with st.sidebar:
    st.title("MMPI-2 Suite Pro")
    st.image("https://cdn-icons-png.flaticon.com/512/3062/3062140.png", width=80)
    modulo = st.radio("Módulos del Sistema:", 
        ["👤 Ficha Técnica", "📝 Aplicación (Paciente)", "⌨️ Tabulación Profesional", "📊 Resultados e IA", "📄 Informe Final"])
    st.divider()
    st.caption(f"ID Sesión: {st.session_state.paciente['codigo_unico']}")

# --- INSTRUCCIONES PERSISTENTES ---
st.markdown(f"""
<div class="instruction-bar">
    <strong>📋 INSTRUCCIONES ACTUALES - MÓDULO {modulo.upper()}</strong><br>
    Verifique que los datos del paciente sean correctos. En caso de duda, consulte el manual técnico. 
    Los datos se guardan automáticamente en la sesión local.
</div>
""", unsafe_allow_html=True)

if modulo == "👤 Ficha Técnica":
    st.header("Identificación del Evaluado")
    p = st.session_state.paciente
    col1, col2 = st.columns(2)
    with col1:
        p["nombre"] = st.text_input("Nombre Completo", p["nombre"])
        p["rut"] = st.text_input("RUT / Pasaporte", p["rut"])
        p["profesion"] = st.text_input("Ocupación/Profesión", p["profesion"])
    with col2:
        p["edad"] = st.number_input("Edad", 18, 99, p["edad"])
        p["sexo"] = st.selectbox("Sexo", ["Masculino", "Femenino"], index=0 if p["sexo"]=="Masculino" else 1)
        p["institucion"] = st.text_input("Institución Solicitante", p["institucion"])

elif modulo == "📝 Aplicación (Paciente)":
    st.header("Formulario de Auto-llenado")
    items_por_hoja = 20
    hoja = st.number_input("Hoja N°", 1, (TOTAL_ITEMS // items_por_hoja) + 1, 1) - 1
    
    inicio = hoja * items_por_hoja
    fin = min(inicio + items_por_hoja, TOTAL_ITEMS)
    
    st.progress(fin / TOTAL_ITEMS)
    
    for i in range(inicio, fin):
        num = i + 1
        val_actual = st.session_state.data.at[i, "Respuesta"]
        idx = 0 if val_actual == "V" else 1 if val_actual == "F" else None
        
        # Aquí puedes colocar las preguntas reales si las tienes en un CSV
        sel = st.radio(f"**{num}.** Pregunta o reactivo número {num}", 
                       ["Verdadero", "Falso"], index=idx, key=f"p_{num}", horizontal=True)
        st.session_state.data.at[i, "Respuesta"] = "V" if sel == "Verdadero" else "F"

elif modulo == "⌨️ Tabulación Profesional":
    st.header("Entrada Rápida para Profesionales")
    st.info("Utilice esta tabla para transcribir respuestas de un cuadernillo físico de forma masiva.")
    st.session_state.data = st.data_editor(
        st.session_state.data, 
        hide_index=True, 
        use_container_width=True, 
        height=500,
        column_config={"Respuesta": st.column_config.SelectboxColumn("V/F", options=["V", "F"], required=True)}
    )

elif modulo == "📊 Resultados e IA":
    st.header("Análisis Psicométrico Proyectado")
    df_res = ejecutar_motor_ia(st.session_state.data)
    
    # Gráfico de Perfil
    fig = go.Figure(go.Scatter(x=df_res["Escala"], y=df_res["T"], mode='lines+markers+text', 
                               text=df_res["T"], textposition="top center", 
                               line=dict(color='#1e3a8a', width=3)))
    fig.add_hline(y=65, line_dash="dash", line_color="red", annotation_text="Corte Clínico (T=65)")
    fig.update_layout(title="Perfil MMPI-2", yaxis_range=[30, 120], height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Interpretación Cualitativa (Motor IA)")
    for _, row in df_res.iterrows():
        estilo = "high-score" if row["T"] >= 65 else ""
        st.markdown(f"""
        <div class="interpretation-card {estilo}">
            <h3 style="margin-top:0;">{row['Escala']} — Puntaje T: {row['T']}</h3>
            {row['IA_Analisis']}
        </div>
        """, unsafe_allow_html=True)

elif modulo == "📄 Informe Final":
    st.header("Exportación de Resultados")
    if st.button("🚀 Generar Informe .docx de Alta Complejidad"):
        df_res = ejecutar_motor_ia(st.session_state.data)
        doc = Document()
        
        # Encabezado
        titulo = doc.add_heading('INFORME PSICOMÉTRICO MMPI-2', 0)
        titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Datos
        p = st.session_state.paciente
        info = doc.add_paragraph()
        info.add_run(f"NOMBRE: {p['nombre']}\n").bold = True
        info.add_run(f"ID: {p['rut']} | EDAD: {p['edad']} | SEXO: {p['sexo']}\n")
        info.add_run(f"FECHA: {pd.Timestamp.now().strftime('%d/%m/%Y')}\n")
        info.add_run(f"INSTITUCIÓN: {p['institucion']}").italic = True
        
        doc.add_heading('Análisis por Escalas Clínicas', level=1)
        for _, row in df_res.iterrows():
            para = doc.add_paragraph()
            run = para.add_run(f"■ {row['Escala']} (T={row['T']}): ")
            run.bold = True
            doc.add_paragraph(row['IA_Analisis'].replace("**", ""))

        buf = io.BytesIO()
        doc.save(buf)
        st.download_button("📥 Descargar Reporte Profesional", buf.getvalue(), f"Informe_{p['rut']}.docx")
