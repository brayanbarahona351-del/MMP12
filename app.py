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

# =====================================================================
# 🛑 ZONA 1: ÍTEMS DEL CUESTIONARIO
# =====================================================================
PREGUNTAS = [
    "Me gustan las revistas de mecánica.", 
    "Tengo buen apetito.", 
    "Me despierto fresco y descansado casi todas las mañanas.",
    "Creo que me gustaría el trabajo de bibliotecario.",
    "El ruido me despierta fácilmente."
]
# Relleno temporal para que no colapse hasta que pegues tu manual real
while len(PREGUNTAS) < 567:
    PREGUNTAS.append(f"Ítem {len(PREGUNTAS) + 1} del cuadernillo oficial.")

# =====================================================================
# 🛑 ZONA 2: CLAVES DE CORRECCIÓN (Copiar del Word)
# =====================================================================
CLAVES = {
    "L (Mentira)": {"V": [], "F": [16, 29, 41, 51, 77, 93, 102, 107, 123, 139, 153, 183, 203, 232, 260]},
    "F (Incoherencia)": {"V": [18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 84, 96, 114, 138, 144, 150, 156, 162, 168, 180, 198, 216, 228, 234, 240, 246, 252, 258, 264, 270, 282, 288, 294, 300, 306, 312, 324, 336, 349, 355, 361], "F": [6, 12, 78, 90, 102, 108, 120, 126, 132, 174, 186, 192, 204, 210, 222, 276, 318, 330, 343]},
    "K (Defensividad)": {"V": [83], "F": [29, 37, 58, 76, 110, 116, 122, 127, 130, 136, 148, 157, 158, 167, 171, 196, 213, 238, 240, 257, 258, 267, 281, 290, 300, 316, 319, 332, 338, 346]},
    "1 Hs (Hipocondriasis)": {"V": [11, 18, 28, 39, 59], "F": [2, 3, 9, 10, 20]}, # Completar con el manual
    "2 D (Depresión)": {"V": [], "F": []},       
    "3 Hy (Histeria)": {"V": [], "F": []},
    "4 Pd (Desv. Psicopática)": {"V": [], "F": []},
    "5 Mf (Masc-Fem)": {"V": [], "F": []}, 
    "6 Pa (Paranoia)": {"V": [], "F": []},
    "7 Pt (Psicastenia)": {"V": [11, 16, 23, 31, 38, 56, 65, 73, 82, 89, 94, 130, 147, 170, 175, 196, 218, 242, 273, 275, 277, 285, 289, 301, 302, 304, 308, 309, 310, 313, 316, 317, 320, 325, 326, 327, 328, 329, 331], "F": [3, 9, 33, 109, 140, 165, 174, 293, 321]},
    "8 Sc (Esquizofrenia)": {"V": [], "F": []},
    "9 Ma (Hipomanía)": {"V": [], "F": []},
    "0 Si (Intr. Social)": {"V": [], "F": []}
}

# =====================================================================
# 🛑 ZONA 3: BAREMOS Y MOTOR DE INTERPRETACIÓN CLÍNICA 
# =====================================================================
def obtener_t(sexo, escala, puntaje):
    # Simulador seguro de T (Reemplazar con tablas de Excel luego)
    try:
        return min(puntaje * 2 + 30, 120) 
    except:
        return 50

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
    "K (Defensividad)": {
        "causa": "Mecanismo de defensa clínico para ocultar deficiencias personales.",
        "razon": "Refleja una actitud cerrada al proceso de evaluación y resistencia al cambio.",
        "plan": "Disminuir resistencias mediante validación emocional y reducción de la crítica percibida."
    },
    "1 Hs (Hipocondriasis)": {
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
    "5 Mf (Masc-Fem)": {
        "causa": "Identificación de intereses y roles no tradicionales.",
        "razon": "Patrón atípico de intereses respecto al rol de género tradicional.",
        "plan": "Exploración de la identidad personal libre de juicios normativos."
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

# =====================================================================
# INTERFAZ Y LÓGICA DE LA APLICACIÓN
# =====================================================================
with st.sidebar:
    st.header("📋 Instrucciones")
    st.markdown("""
    **Guía de Aplicación:**
    - **Verdadero:** Aplica a usted.
    - **Falso:** No aplica a usted.
    - **Blanco:** Solo si es imposible decidir.
    
    *Evite dejar más de 30 ítems en blanco.*
    """)
    st.divider()
    nombre = st.text_input("Nombre Completo")
    edad = st.number_input("Edad", 18, 99, 25)
    sexo = st.selectbox("Sexo para Baremos", ["Varón", "Mujer"])
    modo_llenado = st.radio("Modo de Interfaz", ["Llenado Paciente", "Captura Rápida (Psicólogo)"])
    st.divider()
    progreso = sum(1 for r in st.session_state.respuestas.values() if r is not None and r != "") / 567
    st.progress(progreso)
    st.write(f"Avance: {int(progreso * 100)}%")
    if st.button("🗑️ Reiniciar Evaluación"): reset_form()

st.title(f"Sistema MMPI-2 Profesional - {nombre}")

ITEMS_PAG = 100 if modo_llenado == "Captura Rápida (Psicólogo)" else 50
total_pags = math.ceil(567 / ITEMS_PAG)
inicio = st.session_state.pagina_actual * ITEMS_PAG
fin = min(inicio + ITEMS_PAG, 567)

if modo_llenado == "Captura Rápida (Psicólogo)":
    st.info("⚡ **MODO RÁPIDO:** Usa 'Tab' para avanzar y 'V' o 'F' en tu teclado.")
    cols = st.columns(5)
    for i in range(inicio + 1, fin + 1):
        with cols[(i-1)%5]:
            val_actual = ""
            if st.session_state.respuestas[i] == "Verdadero": val_actual = "V"
            elif st.session_state.respuestas[i] == "Falso": val_actual = "F"
            seleccion = st.selectbox(f"Ítem {i}", ["", "V", "F"], index=["", "V", "F"].index(val_actual) if val_actual else 0, key=f"q_{i}")
            if seleccion == "V": st.session_state.respuestas[i] = "Verdadero"
            elif seleccion == "F": st.session_state.respuestas[i] = "Falso"
            else: st.session_state.respuestas[i] = None
else:
    for i in range(inicio + 1, fin + 1):
        st.session_state.respuestas[i] = st.radio(f"**{i}. {PREGUNTAS[i-1]}**", ["Verdadero", "Falso", "No sé (Blanco)"], horizontal=True, index=["Verdadero", "Falso", "No sé (Blanco)"].index(st.session_state.respuestas[i]) if st.session_state.respuestas[i] else None, key=f"q_{i}")

st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.session_state.pagina_actual > 0:
        if st.button("⬅️ Anterior"): st.session_state.pagina_actual -= 1; st.rerun()
with col3:
    if st.session_state.pagina_actual < total_pags - 1:
        if st.button("Siguiente ➡️"): st.session_state.pagina_actual += 1; st.rerun()
    else:
        if st.button("📈 GENERAR DIAGNÓSTICO CLÍNICO"):
            blancos = [str(k) for k, v in st.session_state.respuestas.items() if v is None or v == "No sé (Blanco)" or v == ""]
            
            if len(blancos) > 30:
                st.error(f"❌ **TEST INVÁLIDO:** Faltan {len(blancos)} preguntas (Límite: 30).")
                st.warning(f"**Ítems por completar:** {', '.join(blancos)}")
            else:
                if len(blancos) > 0:
                    st.warning(f"⚠️ **Se calculará con {len(blancos)} ítems omitidos:** {', '.join(blancos)}")

                # 1. CÁLCULO PD
                resultados = {}
                for escala, claves in CLAVES.items():
                    pd_val = 0
                    for item in claves.get("V", []):
                        if st.session_state.respuestas.get(item) == "Verdadero": pd_val += 1
                    for item in claves.get("F", []):
                        if st.session_state.respuestas.get(item) == "Falso": pd_val += 1
                    resultados[escala] = {"PD": pd_val, "PD_K": pd_val, "T": 0}

                # 2. CORRECCIÓN K
                valor_k = resultados.get("K (Defensividad)", {}).get("PD", 0)
                if "1 Hs (Hipocondriasis)" in resultados: resultados["1 Hs (Hipocondriasis)"]["PD_K"] = round(resultados["1 Hs (Hipocondriasis)"]["PD"] + (0.5 * valor_k))
                if "4 Pd (Desv. Psicopática)" in resultados: resultados["4 Pd (Desv. Psicopática)"]["PD_K"] = round(resultados["4 Pd (Desv. Psicopática)"]["PD"] + (0.4 * valor_k))
                if "7 Pt (Psicastenia)" in resultados: resultados["7 Pt (Psicastenia)"]["PD_K"] = round(resultados["7 Pt (Psicastenia)"]["PD"] + (1.0 * valor_k))
                if "8 Sc (Esquizofrenia)" in resultados: resultados["8 Sc (Esquizofrenia)"]["PD_K"] = round(resultados["8 Sc (Esquizofrenia)"]["PD"] + (1.0 * valor_k))
                if "9 Ma (Hipomanía)" in resultados: resultados["9 Ma (Hipomanía)"]["PD_K"] = round(resultados["9 Ma (Hipomanía)"]["PD"] + (0.2 * valor_k))

                # 3. INTERPRETACIÓN ESTRUCTURADA
                lista_datos = []
                for k, v in resultados.items():
                    t_score = obtener_t(sexo, k, v["PD_K"])
                    info = INTERPRETACIONES.get(k, {"causa": "", "razon": "", "plan": ""})
                    
                    status = "🚨 Elevación Clínica" if t_score >= 65 else "🙂 Rango Normal" if t_score >= 45 else "📉 Rango Bajo"
                    emoji = "🚨" if t_score >= 65 else "🙂" if t_score >= 45 else "📉"
                    
                    lista_datos.append({
                        "Escala": k, "PD": v["PD"], "PD+K": v["PD_K"], "Puntuación T": t_score,
                        "Emoji": emoji, "Status": status, "Causas": info["causa"], "Razon": info["razon"], "Plan": info["plan"]
                    })

                df = pd.DataFrame(lista_datos)

                # --- VISUALIZACIÓN ---
                st.success("✅ Perfil Generado Exitosamente")
                
                fig, ax = plt.subplots(figsize=(12, 5))
                ax.plot(df['Escala'], df['Puntuación T'], marker='o', color='darkblue', linewidth=2)
                ax.axhline(y=65, color='red', linestyle='--', label='Umbral Clínico (T=65)')
                ax.axhline(y=50, color='gray', linestyle='-', alpha=0.5)
                ax.fill_between(df['Escala'], 65, 120, color='red', alpha=0.1)
                ax.set_ylim(20, 120)
                plt.xticks(rotation=45, ha='right')
                st.pyplot(fig)

                st.header("Análisis Diagnóstico")
                for item in lista_datos:
                    with st.expander(f"{item['Emoji']} {item['Escala']} (T={item['Puntuación T']}) - {item['Status']}"):
                        st.write(f"**Análisis de Causas:** {item['Causas']}")
                        st.write(f"**Razón Clínica:** {item['Razon']}")
                        st.write(f"**Plan Terapéutico:** {item['Plan']}")

                # --- REPORTE WORD ---
                doc = Document()
                sec = doc.sections[0]
                sec.top_margin = sec.bottom_margin = Inches(0.5)

                doc.add_heading('INFORME CLÍNICO MMPI-2 Y PLAN DE TRATAMIENTO', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
                doc.add_paragraph(f"Paciente: {nombre}\nEdad: {edad} años\nSexo: {sexo}\nÍtems Omitidos: {len(blancos)}").bold = True
                
                img_b = BytesIO()
                plt.savefig(img_b, format='png', bbox_inches='tight')
                doc.add_picture(img_b, width=Inches(6.5))
                
                # Tabla
                doc.add_heading('1. Tabla de Puntuaciones', level=1)
                t_word = doc.add_table(rows=1, cols=4)
                t_word.style = 'Table Grid'
                hdr = t_word.rows[0].cells
                hdr[0].text, hdr[1].text, hdr[2].text, hdr[3].text = 'Escala', 'PD', 'PD+K', 'T'
                for _, row in df.iterrows():
                    row_cells = t_word.add_row().cells
                    row_cells[0].text = str(row['Escala'])
                    row_cells[1].text = str(row['PD'])
                    row_cells[2].text = str(row['PD+K'])
                    row_cells[3].text = str(row['Puntuación T'])

                # Interpretación
                doc.add_page_break()
                doc.add_heading('2. Interpretación Detallada', level=1)
                for item in lista_datos:
                    if item['Puntuación T'] >= 65:
                        p = doc.add_paragraph()
                        p.add_run(f"■ {item['Escala']} (T: {item['Puntuación T']}): ").bold = True
                        p.add_run(f"{item['Razon']} {item['Causas']} Sugerencia Terapéutica: {item['Plan']}")

                # PLAN ADAPTADO A HONDURAS
                doc.add_heading('3. Plan de Intervención Maestro (Adaptación Sociocultural)', level=1)
                
                doc.add_heading('Fase 1: Estabilización, Psicoeducación y Desmitificación', level=2)
                doc.add_paragraph("Objetivo: Reducir los síntomas agudos (los 'nervios' o el estrés severo) y romper el estigma cultural sobre la salud mental, validando el sufrimiento del paciente en su contexto actual (presión económica, inseguridad o problemas familiares).")
                p1 = doc.add_paragraph(style='List Bullet')
                p1.add_run("Actividad Terapéutica - 'El Anclaje Hondureño': ").bold = True
                p1.add_run("Ante crisis de ansiedad, usar técnicas de grounding (TCC) adaptadas a lo cotidiano. Pedirle al paciente que se enfoque en olores familiares (ej. hacer una taza de café de palo y olerla profundamente) o estímulos táctiles para aterrizar en el 'aquí y el ahora', combinándolo con respiración diafragmática (4-7-8).")
                
                doc.add_heading('Fase 2: Reestructuración Cognitiva y Activación Conductual', level=2)
                doc.add_paragraph("Objetivo: Modificar pensamientos fatalistas ('es la voluntad de Dios', 'no hay salida') hacia un enfoque de afrontamiento activo y resiliencia.")
                p2 = doc.add_paragraph(style='List Bullet')
                p2.add_run("Actividad Terapéutica - 'Registro de Pensamientos y Fe Activa': ").bold = True
                p2.add_run("Enseñar al paciente a identificar distorsiones cognitivas usando un diario emocional sencillo. En pacientes con fuertes creencias espirituales, usar la reestructuración adaptada (ej. 'Dios nos dio libre albedrío y herramientas para cuidarnos').")
                p3 = doc.add_paragraph(style='List Bullet')
                p3.add_run("Actividad Terapéutica - 'Activación Conductual Segura': ").bold = True
                p3.add_run("Para cuadros depresivos o de aislamiento, programar tareas graduales de bajo costo y seguras en su entorno. Ejemplos: ir a la pulpería a platicar 5 minutos con el vecino, salir al patio/corredor a recibir sol en la mañana, o asistir a reuniones de su congregación religiosa o patronato.")

                doc.add_heading('Fase 3: Control de Impulsos y Resolución de Conflictos', level=2)
                doc.add_paragraph("Objetivo: Disminuir la reactividad (violencia intrafamiliar, impulsividad) mediante estrategias de inteligencia emocional aplicables al entorno.")
                p4 = doc.add_paragraph(style='List Bullet')
                p4.add_run("Actividad Terapéutica - 'Técnica del Semáforo y Tiempo Fuera': ").bold = True
                p4.add_run("Entrenar al paciente para reconocer las señales físicas del enojo (calor en la cara, tensión). Acordar con la familia una 'palabra de seguridad' para que el paciente pueda retirarse de la habitación a calmarse antes de que el conflicto escale a violencia verbal o física.")

                doc.add_heading('Fase 4: Redes de Apoyo y Prevención de Recaídas', level=2)
                doc.add_paragraph("Objetivo: Consolidar el alta terapéutica integrando los pilares culturales del paciente: la familia extensa (familismo) y la comunidad.")
                p5 = doc.add_paragraph(style='List Bullet')
                p5.add_run("Actividad Terapéutica - 'Mapeo de Aliados': ").bold = True
                p5.add_run("Dibujar un círculo con el paciente identificando a quién acudir en caso de recaída. Incluir familiares de confianza (tíos, abuelos), líderes comunitarios o guías espirituales (pastores/sacerdotes), educando a un familiar como 'co-terapeuta' para que detecte señales de alarma de forma temprana.")

                w_buf = BytesIO()
                doc.save(w_buf)
                st.download_button("📥 DESCARGAR INFORME CLÍNICO Y PLAN DE INTERVENCIÓN (WORD)", w_buf.getvalue(), f"MMPI_{nombre}.docx")
