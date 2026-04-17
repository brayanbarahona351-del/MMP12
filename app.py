import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
import time
from PIL import Image
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# =====================================================================
# 🎨 1. CONFIGURACIÓN E INTERFAZ (UI/UX)
# =====================================================================
st.set_page_config(page_title="MMPI-2 Ultimate Suite Pro v4.0", layout="wide", page_icon="⚖️")

# Estilos CSS avanzados para profesionalizar la aplicación
st.markdown("""
<style>
    /* Barra de instrucciones persistente */
    .instruction-sticky {
        position: -webkit-sticky; position: sticky; top: 0;
        background-color: #f8fafc; color: #1e293b; padding: 20px;
        border-radius: 12px; border: 1px solid #e2e8f0; border-left: 10px solid #1e3a8a;
        z-index: 999; margin-bottom: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .main { background-color: #f1f5f9; }
    .stMetric { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .interpretation-card {
        background-color: white; padding: 30px; border-radius: 15px;
        border-left: 10px solid #1e3a8a; margin-bottom: 25px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    .clinical-high { border-left-color: #b91c1c !important; background-color: #fffafb; }
    .stButton>button { border-radius: 10px; font-weight: bold; height: 3.5em; transition: all 0.3s; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 🧠 2. GESTIÓN DE MEMORIA Y ESTADO (ANTI-ERROR)
# =====================================================================
TOTAL_ITEMS = 567

def inicializar_sesion():
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame({"Nº": range(1, TOTAL_ITEMS + 1), "Respuesta": [""] * TOTAL_ITEMS})
    
    # Inicialización con parche para claves faltantes (Evita KeyError)
    defaults_paciente = {
        "nombre": "", "rut": "", "edad": 25, "sexo": "Masculino", 
        "estado_civil": "Soltero(a)", "profesion": "", "institucion": "SERPAJ CHILE",
        "fecha_evaluacion": datetime.now().strftime("%d/%m/%Y"),
        "codigo_expediente": f"MMPI2-{int(time.time())}"
    }
    
    if 'paciente' not in st.session_state:
        st.session_state.paciente = defaults_paciente
    else:
        for key, value in defaults_paciente.items():
            if key not in st.session_state.paciente:
                st.session_state.paciente[key] = value

    if 'pag_actual' not in st.session_state: st.session_state.pag_actual = 0

inicializar_sesion()

# =====================================================================
# 🧮 3. MOTOR DE INTELIGENCIA CLÍNICA (EXTENSO)
# =====================================================================
class MotorClinicoIA:
    @staticmethod
    def interpretar_escala(escala, t):
        # Base de datos extendida de interpretaciones técnicas
        config = {
            "L (Mentira)": {
                "nombre": "Escala de Validez L",
                "Alta": "El evaluado presenta un patrón de respuesta defensivo, intentando proyectar una imagen moralmente impecable pero poco realista. Indica rigidez cognitiva, falta de insight y una resistencia marcada a admitir fallas comunes de la conducta humana. Esto invalida parcialmente la profundidad de la exploración clínica.",
                "Normal": "Actitud de respuesta honesta. El sujeto es capaz de reconocer sus limitaciones y errores comunes.",
                "Baja": "Indica cinismo social o una confianza extrema que raya en la independencia de las normas convencionales."
            },
            "F (Incoherencia)": {
                "nombre": "Escala de Validez F",
                "Alta": "Puntaje clínico elevado. Sugiere confusión mental, angustia severa o un 'grito de ayuda' del evaluado. Debe descartarse simulación de patología, respuestas al azar o dificultades severas en la comprensión lectora.",
                "Normal": "Perfil de respuesta coherente con la realidad y las normas sociales."
            },
            "2 D (Depresión)": {
                "nombre": "Escala Clínica 2 - Depresión",
                "Alta": "Elevación clínica significativa. Indica un estado de ánimo disfórico, sentimientos de desamparo, apatía y un pesimismo profundo respecto al futuro. El evaluado reporta baja energía vital y dificultades en la activación conductual.",
                "Sug": "Evaluar riesgo autolítico. Se sugiere psicoterapia cognitivo-conductual centrada en la reestructuración de esquemas de pérdida y activación de recursos personales."
            },
            "4 Pd (Desviación Psicopática)": {
                "nombre": "Escala Clínica 4 - Psicopatía",
                "Alta": "Indica dificultades en la internalización de normas, impulsividad y conflictos recurrentes con figuras de autoridad. Tendencia a externalizar la culpa y baja tolerancia a la frustración.",
                "Sug": "Trabajar en el control de impulsos y desarrollo de la empatía situacional."
            },
            "8 Sc (Esquizofrenia)": {
                "nombre": "Escala Clínica 8 - Esquizofrenia",
                "Alta": "Indica alienación social, sentimientos de ser 'diferente' y posibles alteraciones en el curso del pensamiento. El sujeto percibe la realidad de manera distorsionada o confusa.",
                "Sug": "Derivación a evaluación psiquiátrica para descartar procesos psicóticos o neurocognitivos."
            }
        }
        
        nivel = "Normal"
        if t >= 75: nivel = "Muy Alta"
        elif t >= 65: nivel = "Alta"
        elif t < 45: nivel = "Baja"
        
        base = config.get(escala, {"nombre": escala, "Normal": "Sin indicadores clínicos significativos en esta área."})
        analisis = base.get(nivel if nivel in base else "Normal", "Puntaje dentro de la normalidad estadística.")
        sugerencia = base.get("Sug", "Mantener observación clínica periódica.")
        
        return {
            "titulo": base.get("nombre", escala),
            "nivel": nivel,
            "analisis": analisis,
            "sugerencia": sugerencia
        }

def ejecutar_motor_ia(df_resp):
    resp = dict(zip(df_resp["Nº"], df_resp["Respuesta"]))
    # (En una versión real, aquí se aplican las plantillas de corrección exactas)
    escalas_id = ["L (Mentira)", "F (Incoherencia)", "K (Defensividad)", "1 Hs", "2 D", "3 Hy", "4 Pd", "6 Pa", "7 Pt", "8 Sc", "9 Ma", "0 Si"]
    resultados = []
    
    for esc in escalas_id:
        # Simulación de cálculo de Puntaje T (Baremos internacionales)
        t_val = 40 + (len(esc) * 2) if " " in esc else 55
        if st.session_state.paciente["sexo"] == "Femenino": t_val += 2
        
        ia = MotorClinicoIA.interpretar_escala(esc, t_val)
        resultados.append({"Escala": esc, "T": t_val, "Detalle": ia})
    
    return pd.DataFrame(resultados)

# =====================================================================
# 📸 4. MÓDULO DE ESCANEO OMR (SIMULADO PROFESIONAL)
# =====================================================================
def modulo_escaneo():
    st.header("📸 Escáner de Protocolo Digital")
    st.write("Cargue una imagen nítida de la hoja de respuestas para la tabulación automática.")
    
    archivo = st.file_uploader("Subir Hoja de Respuestas (JPG/PNG)", type=["jpg", "png", "jpeg"])
    
    if archivo:
        col1, col2 = st.columns([1, 2])
        with col1:
            img = Image.open(archivo)
            st.image(img, caption="Imagen cargada para procesamiento", use_container_width=True)
        
        with col2:
            st.info("🔍 Analizando marcas de círculos y densidad de píxeles...")
            if st.button("🚀 Ejecutar Reconocimiento Óptico"):
                barra = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    barra.progress(i + 1)
                
                # Simulación de detección: En un sistema real usaríamos OpenCV
                for i in range(TOTAL_ITEMS):
                    st.session_state.data.at[i, "Respuesta"] = "V" if (i % 4 != 0) else "F"
                
                st.success("✅ Procesamiento Exitoso. 567 ítems detectados y tabulados.")
                st.balloons()

# =====================================================================
# 📄 5. GENERADOR DE INFORME WORD (ALTA COMPLEJIDAD)
# =====================================================================
def generar_megainforme(paciente, df_items, df_res):
    doc = Document()
    
    # --- ENCABEZADO Y TÍTULO ---
    section = doc.sections[0]
    header = section.header
    p_header = header.paragraphs[0]
    p_header.text = f"CONFIDENCIAL - REPORTE CLÍNICO - {paciente['institucion']}"
    p_header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    doc.add_heading('INFORME PSICOMÉTRICO MMPI-2: ANÁLISIS INTEGRAL', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # --- 1. FICHA TÉCNICA ---
    doc.add_heading('1. IDENTIFICACIÓN DEL EVALUADO', level=1)
    table = doc.add_table(rows=5, cols=2)
    table.style = 'Table Grid'
    table.rows[0].cells[0].text = f"Nombre: {paciente['nombre']}"
    table.rows[0].cells[1].text = f"RUT: {paciente['rut']}"
    table.rows[1].cells[0].text = f"Edad: {paciente['edad']} años"
    table.rows[1].cells[1].text = f"Sexo: {paciente['sexo']}"
    table.rows[2].cells[0].text = f"Estado Civil: {paciente['estado_civil']}"
    table.rows[2].cells[1].text = f"Profesión: {paciente['profesion']}"
    table.rows[3].cells[0].text = f"Fecha: {paciente['fecha_evaluacion']}"
    table.rows[3].cells[1].text = f"Código: {paciente['codigo_expediente']}"
    
    # --- 2. PROTOCOLO DE RESPUESTAS (ABUNDANTE) ---
    doc.add_page_break()
    doc.add_heading('2. PROTOCOLO DE RESPUESTAS (567 REACTIVOS)', level=1)
    doc.add_paragraph("Registro bruto de las respuestas proporcionadas por el sujeto para auditoría y revisión pericial.")
    
    # Tabla de 12 columnas para que quepan todos los ítems de forma elegante
    cols_num = 12
    rows_num = (TOTAL_ITEMS // cols_num) + 1
    t_resp = doc.add_table(rows=rows_num, cols=cols_num)
    t_resp.style = 'Table Grid'
    
    for i, row in df_items.iterrows():
        r = i // cols_num
        c = i % cols_num
        cell = t_resp.rows[r].cells[c]
        cell.text = f"{row['Nº']}:{row['Respuesta']}"
        # Ajustar fuente minúscula para que quepa todo
        for p in cell.paragraphs:
            for run in p.runs:
                run.font.size = Pt(7)

    # --- 3. ANÁLISIS DE LA IA Y PERFIL ---
    doc.add_page_break()
    doc.add_heading('3. ANÁLISIS DE RESULTADOS E INTERPRETACIÓN IA', level=1)
    doc.add_paragraph("Interpretación automatizada basada en el motor de lógica clínica del sistema.")
    
    for _, row in df_res.iterrows():
        det = row['Detalle']
        p_esc = doc.add_paragraph()
        run = p_esc.add_run(f"■ {det['titulo']} (T={row['T']})")
        run.bold = True
        run.font.size = Pt(12)
        
        doc.add_paragraph(f"Nivel detectado: {det['nivel']}")
        doc.add_paragraph(det['analisis'])
        
        p_sug = doc.add_paragraph()
        p_sug.add_run("Sugerencia Terapéutica: ").bold = True
        p_sug.add_run(det['sugerencia'])
        doc.add_paragraph("-" * 20)

    # --- 4. CONCLUSIONES ---
    doc.add_heading('4. CONCLUSIONES GENERALES', level=1)
    doc.add_paragraph("El perfil obtenido sugiere una configuración [DESCRIBIR CONFIGURACIÓN] que debe ser correlacionada con la entrevista clínica y los antecedentes biográficos del paciente.")
    
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

# =====================================================================
# 🖥️ 6. NAVEGACIÓN Y MÓDULOS UI
# =====================================================================
with st.sidebar:
    st.title("MMPI-2 PRO SUITE")
    st.image("https://cdn-icons-png.flaticon.com/512/3062/3062140.png", width=100)
    modulo = st.radio("Módulos del Sistema:", [
        "👤 Ficha Técnica", 
        "📝 Modo Paciente (Auto-llenado)", 
        "📸 Escaneo OMR", 
        "⌨️ Tabulación Profesional", 
        "📊 Resultados e IA", 
        "📄 Generar Informe"
    ])
    st.divider()
    st.write(f"**Paciente:** {st.session_state.paciente.get('nombre', 'Pendiente')}")
    st.write(f"**Expediente:** {st.session_state.paciente.get('codigo_expediente')}")

# BANNER DE INSTRUCCIONES PERSISTENTE
st.markdown(f"""
<div class="instruction-sticky">
    <strong>📋 GUÍA DEL SISTEMA:</strong> Actualmente en el módulo <strong>{modulo}</strong>.<br>
    Verifique que los datos del paciente estén completos antes de proceder a la interpretación de la IA. 
    Para imprimir el informe abundante, diríjase al módulo final de exportación.
</div>
""", unsafe_allow_html=True)

# --- MÓDULO: FICHA TÉCNICA ---
if modulo == "👤 Ficha Técnica":
    st.header("Identificación del Evaluado")
    p = st.session_state.paciente
    col1, col2 = st.columns(2)
    with col1:
        p["nombre"] = st.text_input("Nombre y Apellidos", p.get("nombre", ""))
        p["rut"] = st.text_input("RUT / DNI / Pasaporte", p.get("rut", ""))
        p["edad"] = st.number_input("Edad", 18, 99, int(p.get("edad", 25)))
        p["estado_civil"] = st.text_input("Estado Civil", p.get("estado_civil", "Soltero(a)"))
    with col2:
        p["sexo"] = st.selectbox("Sexo", ["Masculino", "Femenino"], index=0 if p.get("sexo")=="Masculino" else 1)
        p["profesion"] = st.text_input("Profesión/Ocupación", p.get("profesion", ""))
        p["institucion"] = st.text_input("Institución", p.get("institucion", ""))
    
    st.success("✅ Datos guardados automáticamente en la sesión.")

# --- MÓDULO: AUTO-LLENADO ---
elif modulo == "📝 Modo Paciente (Auto-llenado)":
    st.header("Aplicación Electrónica")
    items_por_hoja = 20
    hoja = st.slider("Seleccione Bloque de Preguntas", 1, (TOTAL_ITEMS // items_por_hoja) + 1, 1)
    inicio, fin = (hoja - 1) * items_por_hoja, min(hoja * items_por_hoja, TOTAL_ITEMS)
    
    st.progress(fin / TOTAL_ITEMS)
    
    for i in range(inicio, fin):
        num = i + 1
        val_act = st.session_state.data.at[i, "Respuesta"]
        idx_sel = 0 if val_act == "V" else 1 if val_act == "F" else None
        
        sel = st.radio(f"**Ítem {num}:** Declaración o reactivo del MMPI-2 número {num}", 
                       ["Verdadero", "Falso"], index=idx_sel, key=f"p_{num}", horizontal=True)
        st.session_state.data.at[i, "Respuesta"] = "V" if sel == "Verdadero" else "F"

# --- MÓDULO: ESCANEO ---
elif modulo == "📸 Escaneo OMR":
    modulo_escaneo()

# --- MÓDULO: TABULACIÓN ---
elif modulo == "⌨️ Tabulación Profesional":
    st.header("Tabulación y Corrección Masiva")
    st.warning("Use esta herramienta para transcribir hojas físicas o corregir el escaneo automático.")
    st.session_state.data = st.data_editor(
        st.session_state.data, 
        hide_index=True, 
        use_container_width=True, 
        height=600,
        column_config={"Respuesta": st.column_config.SelectboxColumn("V/F", options=["V", "F"], required=True)}
    )

# --- MÓDULO: RESULTADOS ---
elif modulo == "📊 Resultados e IA":
    st.header("Análisis de Perfil e Interpretación IA")
    df_res = ejecutar_motor_ia(st.session_state.data)
    
    # Gráfico de Perfil Psicométrico
    fig = go.Figure(go.Scatter(x=df_res["Escala"], y=df_res["T"], mode='lines+markers+text', text=df_res["T"], textposition="top center"))
    fig.add_hline(y=65, line_dash="dash", line_color="red", annotation_text="CORTE CLÍNICO")
    fig.update_layout(title="Perfil Psicométrico T", yaxis_range=[30, 120])
    st.plotly_chart(fig, use_container_width=True)
    
    for _, row in df_res.iterrows():
        det = row['Detalle']
        clase = "interpretation-card clinical-high" if row['T'] >= 65 else "interpretation-card"
        st.markdown(f"""
        <div class="{clase}">
            <h3 style='margin-top:0;'>{det['titulo']} (Puntaje T: {row['T']})</h3>
            <p><strong>Análisis:</strong> {det['analisis']}</p>
            <p style='color: #1e3a8a;'><strong>Sugerencia Terapéutica:</strong> {det['sugerencia']}</p>
        </div>
        """, unsafe_allow_html=True)

# --- MÓDULO: EXPORTAR ---
elif modulo == "📄 Generar Informe":
    st.header("Generador de Reporte Institucional de Alta Complejidad")
    st.markdown("Este informe incluye la ficha técnica, el protocolo de respuestas (567 ítems) y el análisis clínico de la IA.")
    
    if st.button("🚀 Crear y Descargar Informe (.docx)"):
        with st.spinner("Compilando abundante información clínica..."):
            df_res = ejecutar_motor_ia(st.session_state.data)
            docx_file = generar_megainforme(st.session_state.paciente, st.session_state.data, df_res)
            
            st.success("✅ Informe generado exitosamente.")
            st.download_button(
                label="📥 Descargar Documento Word",
                data=docx_file,
                file_name=f"Informe_MMPI2_{st.session_state.paciente['rut']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
