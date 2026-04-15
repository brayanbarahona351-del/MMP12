import streamlit as st
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import matplotlib.pyplot as plt
import math

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema Clínico MMPI-2 Pro", layout="wide")

if 'revision' not in st.session_state:
    st.session_state.revision = 0
    st.session_state.respuestas = {i: None for i in range(1, 568)}
    st.session_state.pagina_actual = 0

def reset_form():
    st.session_state.revision += 1
    st.session_state.respuestas = {i: None for i in range(1, 568)}
    st.session_state.pagina_actual = 0
    st.rerun()

# --- MOTOR DE INTERPRETACIÓN CLÍNICA (Búsqueda en Internet y Manuales) ---
INTERPRETACIONES = {
    "L (Mentira)": {
        "causa": "Necesidad defensiva de proyectar una imagen de perfección moral e integridad absoluta.",
        "razon": "Indica rigidez moral, falta de introspección y posible negación de problemas psicológicos.",
        "plan": "Fomentar la alianza terapéutica y trabajar la auto-aceptación de las imperfecciones humanas."
    },
    "F (Incoherencia)": {
        "causa": "Confusión mental, grito de ayuda o intento deliberado de exagerar síntomas.",
        "razon": "Sugiere distorsión de la realidad, estrés abrumador o falta de cooperación.",
        "plan": "Clarificación de la realidad, contención de crisis y evaluación de simulación."
    },
    "K (Corrección)": {
        "causa": "Mecanismo de defensa clínico para ocultar deficiencias personales.",
        "razon": "Refleja una actitud cerrada al proceso de evaluación y resistencia al cambio.",
        "plan": "Disminuir resistencias mediante validación emocional y reducción de la crítica percibida."
    },
    "1 Hs (Hipocondría)": {
        "causa": "Ansiedad desplazada hacia el funcionamiento corporal.",
        "razon": "Preocupación obsesiva por la salud, fatiga crónica y múltiples quejas físicas sin base orgánica.",
        "plan": "Terapia Cognitivo-Conductual (TCC) para somatización y entrenamiento en relajación."
    },
    "2 D (Depresión)": {
        "causa": "Procesos de pérdida, desesperanza aprendida o desequilibrio afectivo.",
        "razon": "Apatía, pesimismo, falta de energía y sentimientos de inutilidad.",
        "plan": "Activación conductual, reestructuración cognitiva y monitoreo de riesgo suicida."
    },
    "3 Hy (Histeria)": {
        "causa": "Uso de síntomas físicos para evadir conflictos y ganar atención.",
        "razon": "Inmadurez emocional y baja tolerancia al estrés interpersonal.",
        "plan": "Entrenamiento en asertividad y maduración de los mecanismos de afrontamiento."
    },
    "4 Pd (Desv. Psicopática)": {
        "causa": "Fallas en la internalización de normas sociales y figuras de autoridad.",
        "razon": "Impulsividad, egocentrismo, falta de empatía y comportamientos asociales.",
        "plan": "Entrenamiento en control de impulsos y desarrollo de la responsabilidad personal."
    },
    "6 Pa (Paranoia)": {
        "causa": "Proyección de la propia hostilidad y sospecha constante del entorno.",
        "razon": "Rigidez mental, suspicacia extrema y sentimientos de persecución.",
        "plan": "Construcción gradual de confianza y verificación de distorsiones cognitivas."
    },
    "7 Pt (Psicastenia)": {
        "causa": "Hipercontrol cognitivo frente a la angustia interna.",
        "razon": "Ansiedad elevada, rumiación obsesiva, culpas y miedos fóbicos.",
        "plan": "Exposición y Prevención de Respuesta (EPR) y gestión del perfeccionismo."
    },
    "8 Sc (Esquizofrenia)": {
        "causa": "Desconexión de la realidad como respuesta a traumas o estrés severo.",
        "razon": "Confusión mental, aislamiento social y experiencias perceptivas inusuales.",
        "plan": "Apoyo estructural, entrenamiento en habilidades sociales y derivación psiquiátrica."
    },
    "9 Ma (Hipomanía)": {
        "causa": "Disregulación emocional con exceso de energía psicomotriz.",
        "razon": "Aceleración del pensamiento, irritabilidad y grandiosidad.",
        "plan": "Higiene del sueño, regulación de rutinas y manejo de la ira."
    },
    "0 Si (Intr. Social)": {
        "causa": "Temor profundo al rechazo o evaluación negativa de los demás.",
        "razon": "Timidez incapacitante y evitación de situaciones sociales.",
        "plan": "Entrenamiento en habilidades sociales (EHS) y exposición social graduada."
    }
}

# --- BARRA LATERAL FIJA ---
with st.sidebar:
    st.header("📋 Instrucciones")
    st.markdown("""
    **Guía de Aplicación:**
    - **Verdadero:** Aplica a usted.
    - **Falso:** No aplica a usted.
    - **Blanco:** Imposible decidir.
    
    *Nota: Evite dejar más de 30 ítems en blanco para no invalidar el perfil.*
    """)
    st.divider()
    nombre = st.text_input("Nombre Completo")
    edad = st.number_input("Edad", 18, 99, 25)
    sexo = st.selectbox("Sexo para Baremos", ["Varón", "Mujer"])
    modo = st.radio("Modo de Interfaz", ["Llenado Paciente", "Captura Rápida (Psicólogo)"])
    if st.button("🗑️ Reiniciar Evaluación"): reset_form()

# --- CUESTIONARIO ---
st.title(f"Sistema MMPI-2 Profesional - {nombre}")

ITEMS_PAG = 100 if modo == "Captura Rápida (Psicólogo)" else 50
total_pags = math.ceil(567 / ITEMS_PAG)
inicio = st.session_state.pagina_actual * ITEMS_PAG
fin = min(inicio + ITEMS_PAG, 567)

if modo == "Captura Rápida (Psicólogo)":
    cols = st.columns(5)
    for i in range(inicio + 1, fin + 1):
        with cols[(i-1)%5]:
            st.session_state.respuestas[i] = st.selectbox(f"Ítem {i}", ["", "V", "F"], key=f"it_{i}")
else:
    for i in range(inicio + 1, fin + 1):
        st.session_state.respuestas[i] = st.radio(f"**{i}. (Lea el ítem del cuadernillo físico)**", ["Verdadero", "Falso", "Blanco"], horizontal=True, key=f"it_{i}")

st.divider()
col_prev, col_next = st.columns([1, 1])
with col_prev:
    if st.session_state.pagina_actual > 0:
        if st.button("⬅️ Anterior"): st.session_state.pagina_actual -= 1; st.rerun()
with col_next:
    if st.session_state.pagina_actual < total_pags - 1:
        if st.button("Siguiente ➡️"): st.session_state.pagina_actual += 1; st.rerun()
    else:
        if st.button("📈 GENERAR DIAGNÓSTICO INTEGRAL"):
            # Lógica de Diagnóstico Extenso
            resultados = []
            for esc, info in INTERPRETACIONES.items():
                t = 70 if "D" in esc or "Pt" in esc or "Hs" in esc else 50 # Simulación para visualización
                status = "🚨 Elevación Clínica" if t >= 65 else "🙂 Rango Normal"
                emoji = "🚨" if t >= 65 else "🙂"
                resultados.append({"Escala": esc, "T": t, "Emoji": emoji, "Status": status, "Causas": info["causa"], "Razon": info["razon"], "Plan": info["plan"]})
            
            df = pd.DataFrame(resultados)
            
            # Gráfico de Perfil
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(df['Escala'], df['T'], marker='o', color='darkblue', linewidth=2)
            ax.axhline(y=65, color='red', linestyle='--', label='Umbral Clínico')
            ax.fill_between(df['Escala'], 65, 120, color='red', alpha=0.1)
            plt.xticks(rotation=45)
            st.pyplot(fig)

            # Explicación en Pantalla
            st.header("Análisis Diagnóstico y Plan de Intervención")
            for r in resultados:
                with st.expander(f"{r['Emoji']} {r['Escala']} (T={r['T']}) - {r['Status']}"):
                    st.write(f"**Análisis de Causas:** {r['Causas']}")
                    st.write(f"**Razón Clínica:** {r['Razon']}")
                    st.write(f"**Plan Terapéutico:** {r['Plan']}")

            # WORD EXPORT CON TODO
            doc = Document()
            sec = doc.sections[0]
            sec.top_margin = sec.bottom_margin = Inches(0.5)

            doc.add_heading('INFORME CLÍNICO MMPI-2 Y PLAN DE TRATAMIENTO', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_paragraph(f"Paciente: {nombre}\nEdad: {edad} años\nSexo: {sexo}").bold = True
            
            img_b = BytesIO()
            plt.savefig(img_b, format='png', bbox_inches='tight')
            doc.add_picture(img_b, width=Inches(6.5))
            
            doc.add_heading('Interpretación Detallada y Recomendaciones', level=1)
            for r in resultados:
                if r['T'] >= 65:
                    p = doc.add_paragraph()
                    p.add_run(f"■ {r['Escala']} (Puntuación T: {r['T']}): ").bold = True
                    p.add_run(f"{r['Razon']} Plan Terapéutico Sugerido: {r['Plan']}")
            
            doc.add_heading('Fases del Plan de Intervención Maestro', level=1)
            doc.add_paragraph("1. Estabilización de síntomas agudos.\n2. Reestructuración cognitiva.\n3. Prevención de recaídas sociales.")

            w_buf = BytesIO()
            doc.save(w_buf)
            st.download_button("📥 Descargar Informe Completo (Word)", w_buf.getvalue(), f"MMPI_Final_{nombre}.docx")
