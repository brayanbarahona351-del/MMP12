import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# =====================================================================
# 🎨 1. CONFIGURACIÓN Y ESTILOS (UI PROFESIONAL)
# =====================================================================
st.set_page_config(page_title="MMPI-2 Ultimate Suite Pro", layout="wide", page_icon="🧠")

st.markdown("""
<style>
    /* Instrucciones siempre visibles (Sticky) */
    .instruction-sticky {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        background-color: #fefce8;
        color: #854d0e;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #fef08a;
        border-left: 8px solid #ca8a04;
        margin-bottom: 20px;
        z-index: 999;
        font-weight: 500;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #e5e7eb; }
    .interpretation-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 8px solid #1e3a8a;
        margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .high-score { border-left: 8px solid #dc2626 !important; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 🧠 2. GESTIÓN DE MEMORIA (EVITA KEYERROR)
# =====================================================================
TOTAL_ITEMS = 567

# Inicialización segura de session_state
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({"Nº": range(1, TOTAL_ITEMS + 1), "Respuesta": [""] * TOTAL_ITEMS})

if 'paciente' not in st.session_state:
    st.session_state.paciente = {
        "nombre": "", "rut": "", "edad": 25, "sexo": "Masculino", 
        "estado_civil": "Soltero(a)", "profesion": "", "institucion": "SERPAJ CHILE",
        "codigo_unico": f"EXP-{pd.Timestamp.now().strftime('%Y%m%d-%H%M%S')}"
    }

# Parche de seguridad para sesiones existentes sin 'codigo_unico'
if "codigo_unico" not in st.session_state.paciente:
    st.session_state.paciente["codigo_unico"] = f"EXP-{pd.Timestamp.now().strftime('%Y%m%d-%H%M%S')}"

# =====================================================================
# 🧮 3. MOTOR DE INTELIGENCIA CLÍNICA
# =====================================================================
def motor_ia_detallado(escala, t):
    """Genera análisis clínicos extensos según el puntaje T."""
    diagnosticos = {
        "L (Mentira)": {
            "Alta": "Elevación significativa. Sugiere un intento ingenuo pero persistente de negar fallas comunes. Indica rigidez defensiva, falta de insight y una autoimagen idealizada que dificulta el proceso terapéutico.",
            "Normal": "Actitud honesta y cooperadora frente a la evaluación.",
            "Baja": "Sujeto con independencia de criterio o cinismo social elevado."
        },
        "F (Incoherencia)": {
            "Alta": "Puntaje clínico. Podría indicar distress emocional severo, confusión mental o un 'grito de ayuda'. Es imperativo descartar que el sujeto haya respondido al azar o con intención de simular patología.",
            "Normal": "Perfil de respuesta coherente y adecuado."
        },
        "2 D (Depresión)": {
            "Alta": "Elevación clínica. Indica presencia de anhedonia, rumiación pesimista, baja energía y sentimientos de desamparo. El sujeto percibe su realidad como abrumadora.",
            "Rec": "Se sugiere intervención en activación conductual y evaluación de ideación suicida."
        },
        "4 Pd (Psicopatía)": {
            "Alta": "Sugiere dificultades marcadas con la internalización de normas sociales, impulsividad y tendencia a externalizar la culpa en conflictos interpersonales.",
            "Rec": "Trabajar en la empatía y la responsabilidad sobre las consecuencias de sus actos."
        }
    }
    
    status = "Normal"
    if t >= 75: status = "Muy Alta"
    elif t >= 65: status = "Alta"
    elif t < 45: status = "Baja"
    
    base = diagnosticos.get(escala, {})
    analisis = base.get(status if status in base else "Normal", "Puntaje dentro de los parámetros esperados para la población general.")
    rec = base.get("Rec", "Continuar con seguimiento clínico estándar.")
    
    return f"**Estado:** {status} \n\n **Análisis Clínico:** {analisis} \n\n **Sugerencia:** {rec}"

def calcular_escalas(df):
    resp = dict(zip(df["Nº"], df["Respuesta"]))
    # Simulación de escalas principales (Mapear claves reales aquí)
    escalas_list = ["L (Mentira)", "F (Incoherencia)", "K (Defensividad)", "1 Hs", "2 D", "3 Hy", "4 Pd", "6 Pa", "7 Pt", "8 Sc", "9 Ma", "0 Si"]
    resultados = []
    
    for e in escalas_list:
        pd_val = sum(1 for i in range(1, 15) if resp.get(i) == "V") # Simulación de sumatoria
        t_val = min(round((pd_val * 2.8) + 38), 115)
        resultados.append({
            "Escala": e, "PD": pd_val, "T": t_val, 
            "Analisis": motor_ia_detallado(e, t_val)
        })
    return pd.DataFrame(resultados)

# =====================================================================
# 🖥️ 4. INTERFAZ Y NAVEGACIÓN
# =====================================================================
with st.sidebar:
    st.title("MMPI-2 PRO Suite")
    st.caption(f"ID: {st.session_state.paciente.get('codigo_unico')}")
    modulo = st.radio("Menú Principal:", ["👤 Ficha Técnica", "📝 Modo Paciente", "⌨️ Modo Profesional", "📊 Resultados e IA", "📄 Exportar Informe"])
    st.divider()
    if st.button("🗑️ Limpiar Todo"):
        st.session_state.clear()
        st.rerun()

# --- BARRA DE INSTRUCCIONES PERSISTENTE ---
st.markdown(f"""
<div class="instruction-sticky">
    <strong>💡 Instrucciones del Sistema:</strong><br>
    Usted se encuentra en el módulo <strong>{modulo}</strong>. 
    Asegúrese de que el evaluado responda con sinceridad. En caso de tabulación profesional, ingrese 'V' o 'F' directamente en la tabla.
</div>
""", unsafe_allow_html=True)

if modulo == "👤 Ficha Técnica":
    st.header("Datos de Identificación")
    p = st.session_state.paciente
    c1, c2 = st.columns(2)
    with c1:
        p["nombre"] = st.text_input("Nombre Completo", p["nombre"])
        p["rut"] = st.text_input("RUT / Documento", p["rut"])
        p["edad"] = st.number_input("Edad", 18, 99, p["edad"])
    with c2:
        p["sexo"] = st.selectbox("Sexo", ["Masculino", "Femenino"], index=0 if p["sexo"]=="Masculino" else 1)
        p["profesion"] = st.text_input("Profesión", p["profesion"])
        p["institucion"] = st.text_input("Institución", p["institucion"])

elif modulo == "📝 Modo Paciente":
    st.header("Aplicación del Reactivo (Auto-llenado)")
    items_por_hoja = 20
    hoja = st.slider("Seleccione Bloque de Preguntas", 1, (TOTAL_ITEMS // items_por_hoja) + 1, 1)
    
    inicio = (hoja - 1) * items_por_hoja
    fin = min(inicio + items_por_hoja, TOTAL_ITEMS)
    
    st.progress(fin / TOTAL_ITEMS)
    
    for i in range(inicio, fin):
        num = i + 1
        val = st.session_state.data.at[i, "Respuesta"]
        idx = 0 if val == "V" else 1 if val == "F" else None
        
        sel = st.radio(f"**Pregunta {num}:** Declaración del MMPI-2 número {num}", 
                       ["Verdadero", "Falso"], index=idx, key=f"p_{num}", horizontal=True)
        st.session_state.data.at[i, "Respuesta"] = "V" if sel == "Verdadero" else "F"

elif modulo == "⌨️ Modo Profesional":
    st.header("Tabulación Rápida de Resultados")
    st.info("Utilice esta tabla para ingresar las respuestas del cuadernillo físico (V/F).")
    # Editor masivo de datos
    st.session_state.data = st.data_editor(st.session_state.data, hide_index=True, use_container_width=True, height=500)

elif modulo == "📊 Resultados e IA":
    st.header("Análisis de Perfil e Interpretación IA")
    df_res = calcular_escalas(st.session_state.data)
    
    # Gráfico Plotly
    fig = go.Figure(go.Scatter(x=df_res["Escala"], y=df_res["T"], mode='lines+markers+text', text=df_res["T"]))
    fig.add_hline(y=65, line_dash="dash", line_color="red", annotation_text="Corte Clínico")
    fig.update_layout(yaxis_range=[30, 120], height=500, title="Perfil Psicométrico T")
    st.plotly_chart(fig, use_container_width=True)
    
    # Cartas de Interpretación
    for _, row in df_res.iterrows():
        estilo = "high-score" if row["T"] >= 65 else ""
        st.markdown(f"""
        <div class="interpretation-card {estilo}">
            <h3>{row['Escala']} (T={row['T']})</h3>
            {row['Analisis']}
        </div>
        """, unsafe_allow_html=True)

elif modulo == "📄 Exportar Informe":
    st.header("Generación de Informe Institucional")
    if st.button("🚀 Crear Informe en Word"):
        df_res = calcular_escalas(st.session_state.data)
        doc = Document()
        doc.add_heading('INFORME PSICOMÉTRICO MMPI-2', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        p = st.session_state.paciente
        header = doc.add_paragraph()
        header.add_run(f"Expediente: {p['codigo_unico']}\n").bold = True
        header.add_run(f"Nombre: {p['nombre']}\nRUT: {p['rut']} | Edad: {p['edad']}\nInstitución: {p['institucion']}")
        
        doc.add_heading('Interpretación Detallada', level=1)
        for _, row in df_res.iterrows():
            para = doc.add_paragraph()
            run = para.add_run(f"■ {row['Escala']} (T={row['T']}): ")
            run.bold = True
            para.add_run(row['Analisis'].replace("**", ""))
            
        buf = io.BytesIO()
        doc.save(buf)
        st.download_button("📥 Descargar Reporte (.docx)", buf.getvalue(), f"Informe_{p['rut']}.docx")
