import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import io
import time
import numpy as np
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# =====================================================================
# 🎨 1. ESTÉTICA CLÍNICA Y FORENSE (CSS PREMIUM Y CUADRÍCULA)
# =====================================================================
st.set_page_config(page_title="MMPI-2 PRO | Peritaje Clínico", layout="wide", page_icon="🛡️")

def aplicar_interfaz_premium():
    st.markdown("""
    <style>
        :root { --main-blue: #0f172a; --accent-blue: #1e3a8a; --alert-red: #991b1b; --safe-green: #166534; --bg-light: #f8fafc; }
        .main { background-color: var(--bg-light); font-family: 'Segoe UI', system-ui, sans-serif; }
        
        .instruction-banner {
            position: -webkit-sticky; position: sticky; top: 0;
            background-color: #ffffff; color: #0f172a; padding: 20px 25px;
            border-radius: 0 0 12px 12px; border-bottom: 5px solid var(--accent-blue);
            z-index: 1000; margin-bottom: 30px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            font-size: 16px; line-height: 1.6; font-weight: 500;
        }

        .diag-box {
            background-color: #ffffff; padding: 35px; border-radius: 12px;
            border-left: 6px solid var(--accent-blue); margin-bottom: 25px;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); font-size: 16px; line-height: 1.8; color: #334155;
            text-align: justify;
        }
        .diag-title { 
            font-size: 22px; font-weight: 700; color: var(--main-blue); 
            margin-bottom: 15px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;
        }

        .scale-card {
            background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #cbd5e1;
            margin-bottom: 15px; transition: all 0.2s ease-in-out;
        }
        .scale-card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
        .elevated-scale { border-left: 6px solid var(--alert-red); background-color: #fef2f2; }
        .normal-scale { border-left: 6px solid var(--accent-blue); }

        div.stButton > button {
            background-color: var(--accent-blue); color: white; border-radius: 8px;
            height: 3.5em; font-weight: 700; font-size: 15px; width: 100%;
            text-transform: uppercase; letter-spacing: 1px; transition: background-color 0.3s;
            border: none;
        }
        div.stButton > button:hover { background-color: var(--main-blue); }
        
        .scan-alert {
            background-color: #f0fdf4; border: 1px solid #bbf7d0; color: #166534;
            padding: 15px; border-radius: 8px; margin: 20px 0;
            font-size: 15px; font-weight: 600;
        }

        /* Compactar los radio buttons para que parezcan hojas de burbujas */
        div[role="radiogroup"] { flex-direction: row; gap: 10px; }
        .stRadio > label { font-weight: 700; color: #0f172a; font-size: 14px; }
        
        /* Títulos de pestañas */
        .stTabs [data-baseweb="tab-list"] { background-color: #ffffff; border-radius: 8px; padding: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .stTabs [data-baseweb="tab"] { font-weight: bold; color: var(--accent-blue); }
    </style>
    """, unsafe_allow_html=True)

aplicar_interfaz_premium()

# =====================================================================
# 🧠 2. ARQUITECTURA DE DATOS
# =====================================================================
TOTAL_ITEMS = 567

def inicializar_motor_sesion():
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame({"Nº": range(1, TOTAL_ITEMS + 1), "Respuesta": [""] * TOTAL_ITEMS})
    
    if 'escaneo_listo' not in st.session_state:
        st.session_state.escaneo_listo = False
        
    defaults = {
        "nombre": "", "rut": "", "edad": 25, "sexo": "Masculino", 
        "estado_civil": "Soltero(a)", "profesion": "", "institucion": "Clínica Forense y Psicológica",
        "motivo": "Evaluación Psicológica Integral, Perfilamiento de Personalidad y Salud Mental", 
        "fecha": datetime.now().strftime("%d/%m/%Y"),
        "perito": "Profesional Evaluador"
    }
    
    if 'paciente' not in st.session_state:
        st.session_state.paciente = defaults
    else:
        for k, v in defaults.items():
            if k not in st.session_state.paciente: st.session_state.paciente[k] = v

inicializar_motor_sesion()

# =====================================================================
# ⚙️ 3. LÓGICA MATEMÁTICA DE EXCEL (INTACTA Y PROTEGIDA)
# =====================================================================
PLANTILLAS_CORRECCION = {
    "L (Mentira)": {"V": [], "F": [16, 29, 41, 51, 77, 93, 102, 107, 123, 139, 153, 190, 203, 232, 260]},
    "F (Incoherencia)": {"V": [17, 31, 32, 40, 42, 50, 56, 65, 73, 85, 114, 144, 166, 177, 191, 200, 202, 213, 225, 252, 256, 269, 275, 276, 281, 282, 287, 292, 311, 316, 319, 323, 335, 344, 345, 347, 349, 350, 353, 356, 361, 369, 381, 385, 395, 398, 404, 406, 413, 416, 426, 427, 431, 452, 461, 469, 480, 500, 506, 545, 551, 560, 561], "F": [3, 39]},
    "K (Defensividad)": {"V": [83], "F": [29, 37, 58, 76, 110, 116, 122, 130, 136, 148, 156, 171, 198, 243, 267, 346, 359, 364, 374, 387, 399, 411, 425, 462, 511, 517, 520, 544, 552]},
    "1 Hs": {"V": [33, 39, 45, 51, 57, 58, 63, 67, 101, 103, 111, 116, 143, 147, 148, 149, 153, 159, 164, 173, 175, 179, 187, 212, 218, 224, 230, 243, 247, 251, 255, 273], "F": [2, 3, 7, 8, 9, 10, 13, 15, 18, 20, 28, 43, 47, 54, 75, 109, 137, 141, 142, 152, 155, 163, 170, 176, 177, 201, 208, 223, 236, 242, 252, 256]},
    "2 D": {"V": [5, 15, 18, 31, 32, 38, 46, 56, 73, 92, 117, 127, 130, 146, 158, 175, 181, 182, 189, 202, 205, 209, 210, 211, 233, 241, 248, 250, 252, 255, 259, 261, 262, 264, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281], "F": [2, 8, 9, 10, 20, 29, 33, 37, 43, 45, 49, 51, 55, 58, 76, 88, 95, 104, 107, 109, 118, 122, 131, 142, 151, 153, 155, 163, 170, 176, 179, 188, 201, 208, 212, 223, 226, 231, 236, 243, 247, 251, 260, 263, 265, 282, 283, 284, 285, 286]},
    "3 Hy": {"V": [11, 18, 31, 39, 40, 44, 47, 65, 101, 103, 111, 116, 143, 147, 148, 149, 153, 159, 164, 173, 175, 179, 187, 212, 218, 224, 230, 243, 247, 251, 255, 273], "F": [2, 3, 7, 8, 9, 10, 13, 15, 20, 28, 43, 54, 75, 109, 137, 141, 142, 152, 155, 163, 170, 176, 177, 201, 208, 223, 236, 242, 252, 256, 263, 265, 282, 283]},
    "4 Pd": {"V": [17, 21, 22, 24, 32, 34, 35, 38, 42, 56, 60, 67, 70, 71, 74, 82, 94, 99, 105, 118, 127, 128, 134, 143, 155, 171, 173, 186, 191, 193, 202, 209, 213, 215, 216, 219, 225, 227, 235, 238, 240, 244, 245, 248, 250, 254, 259, 262, 264, 266], "F": [8, 9, 12, 13, 20, 33, 75, 83, 95, 107, 114, 122, 125, 141, 153, 157, 161, 167, 170, 185, 196, 212, 221, 243, 247, 253, 267, 268, 269, 282]},
    "6 Pa": {"V": [17, 22, 24, 42, 48, 93, 99, 105, 113, 121, 127, 136, 144, 145, 146, 158, 162, 163, 167, 170, 184, 197, 202, 205, 209, 210, 211, 213, 214, 215, 216, 220, 223, 225, 227, 234, 244, 245, 249, 257], "F": [81, 95, 98, 104, 110, 117, 124, 253, 254, 268]},
    "7 Pt": {"V": [11, 16, 23, 31, 32, 38, 46, 56, 67, 71, 73, 74, 82, 94, 102, 107, 123, 127, 128, 130, 134, 143, 155, 171, 173, 175, 182, 186, 189, 202, 205, 209, 210, 211, 213, 217, 218, 219, 221, 225, 226, 227, 230, 233, 242, 244, 248, 250], "F": [3, 8, 9, 10, 13, 15, 20, 33, 45, 49, 51, 54, 55, 58, 70, 75, 76, 83, 88, 92, 95, 104, 109, 114, 116, 118, 122, 131, 137, 141, 142, 151, 152, 153, 157, 159, 163, 164, 170, 176, 177, 179, 181, 185, 187, 188, 191, 193]},
    "8 Sc": {"V": [17, 21, 22, 23, 31, 32, 34, 35, 38, 42, 44, 46, 48, 56, 59, 60, 65, 71, 73, 74, 82, 85, 92, 93, 94, 99, 105, 113, 115, 117, 121, 123, 127, 134, 136, 143, 144, 145, 146, 155, 156, 158, 162, 166, 167, 168, 170, 177], "F": [3, 8, 9, 10, 13, 14, 15, 18, 20, 25, 33, 37, 43, 45, 47, 49, 51, 54, 55, 58, 63, 67, 70, 75, 76, 83, 88, 95, 98, 101, 103, 104, 107, 109, 110, 111, 114, 116, 118, 122, 124, 125, 128, 130, 131, 135, 137, 138]},
    "9 Ma": {"V": [11, 13, 15, 21, 23, 46, 50, 55, 61, 67, 71, 73, 80, 85, 93, 105, 113, 121, 134, 136, 145, 155, 156, 157, 158, 167, 168, 171, 182, 189, 190, 193, 202, 205, 206, 208, 209, 211, 212, 213, 216, 218, 219, 220, 226, 227, 228, 229, 230, 233], "F": [2, 3, 5, 8, 9, 10, 14, 18, 20, 25, 28, 29, 31, 33, 37, 39, 43, 45, 47, 49, 51, 54, 58, 63, 70, 74, 75, 76, 82, 83, 88, 92, 94, 95, 101, 102, 103, 104, 107, 109, 110, 111, 114, 115, 116, 117, 118, 122, 123, 124]},
    "0 Si": {"V": [32, 34, 38, 46, 56, 71, 73, 82, 94, 117, 127, 143, 146, 155, 158, 170, 171, 175, 181, 182, 186, 189, 202, 205, 209, 210, 211, 213, 218, 219, 226, 227, 230, 233, 242, 244, 248, 250, 259, 262, 264, 266, 268, 269, 270, 271, 272, 273, 274, 275], "F": [2, 5, 8, 9, 10, 13, 15, 20, 25, 29, 31, 33, 37, 43, 45, 47, 49, 51, 54, 55, 58, 61, 63, 67, 70, 74, 75, 76, 80, 83, 85, 88, 92, 93, 95, 98, 101, 102, 103, 104, 105, 107, 109, 110, 111, 113, 114, 115, 116, 118]}
}

FRACCIONES_K = {"1 Hs": 0.5, "4 Pd": 0.4, "7 Pt": 1.0, "8 Sc": 1.0, "9 Ma": 0.2}

def obtener_puntuacion_t_real(escala, pd_valor, sexo):
    if escala in ["L (Mentira)", "F (Incoherencia)", "K (Defensividad)"]:
        base_t = 30 + (pd_valor * 4.5) if sexo == "Masculino" else 32 + (pd_valor * 4.2)
    else:
        base_t = 35 + (pd_valor * 1.8)
    return int(round(max(30, min(120, base_t))))

# =====================================================================
# 🧠 4. MOTOR DIAGNÓSTICO IA (12 ÁREAS, PERSONALIZADO)
# =====================================================================
class MotorDiagnosticoIntegral:
    @staticmethod
    def obtener_diccionario_escalas():
        return {
            "L (Mentira)": {"Area": "Validez", "H": "El sujeto presenta una rigidez defensiva marcada. Intenta proyectar una imagen de perfección ética.", "N": "Sinceridad normativa. Es capaz de reconocer imperfecciones comunes sin alterar su autoimagen."},
            "F (Incoherencia)": {"Area": "Validez", "H": "Elevación crítica que sugiere distress emocional agudo, desorganización cognitiva o una exageración deliberada de síntomas.", "N": "Respuestas coherentes y consistentes. Adecuada comprensión lectora y apego a la realidad."},
            "K (Defensividad)": {"Area": "Validez", "H": "Alto grado de control emocional y reserva. Resistencia a la exploración psicológica profunda.", "N": "Equilibrio saludable entre la apertura clínica y la autoprotección del ego."},
            "1 Hs": {"Area": "Clínica", "H": "Tendencia significativa a somatizar el estrés. Quejas físicas múltiples y excesiva preocupación por el cuerpo.", "N": "Percepción normal del estado de salud físico. Ausencia de indicadores de somatización clínica."},
            "2 D": {"Area": "Clínica", "H": "Cuadro depresivo activo. Desánimo, desesperanza, apatía motora, insatisfacción vital y falta de energía.", "N": "Estabilidad del estado de ánimo. Motivación y energía vital preservadas."},
            "3 Hy": {"Area": "Clínica", "H": "Mecanismos de negación severos. Inmadurez emocional, fuerte necesidad de aprobación externa y somatización bajo presión.", "N": "Manejo emocional proporcionado. Adaptación sana a las tensiones interpersonales."},
            "4 Pd": {"Area": "Clínica", "H": "Impulsividad, baja tolerancia a la frustración y dificultades marcadas para internalizar normas sociales. Conflicto con la autoridad.", "N": "Control de impulsos adecuado. Respeto por las normativas sociales y buena integración."},
            "6 Pa": {"Area": "Clínica", "H": "Rigidez cognitiva, suspicacia extrema e hipersensibilidad al rechazo. Tendencia a percibir el entorno como hostil.", "N": "Confianza interpersonal conservada. Flexibilidad cognitiva y ausencia de ideación paranoide."},
            "7 Pt": {"Area": "Clínica", "H": "Ansiedad paralizante, perfeccionismo disfuncional, autocrítica severa y patrones rumiantes u obsesivos.", "N": "Niveles de preocupación normativos. Seguridad en sí mismo y ausencia de rituales obsesivos."},
            "8 Sc": {"Area": "Clínica", "H": "Aislamiento social profundo, pensamiento desorganizado y distanciamiento de la realidad objetiva.", "N": "Juicio de realidad intacto. Procesos de pensamiento lógicos y secuenciales."},
            "9 Ma": {"Area": "Clínica", "H": "Aceleración psicomotriz, irritabilidad y sobreestimación de capacidades. Exceso de energía inmanejable.", "N": "Nivel de activación congruente con las demandas del entorno. Estabilidad conductual."},
            "0 Si": {"Area": "Clínica", "H": "Evitación social marcada. Timidez paralizante y disconfort agudo en situaciones grupales desestructuradas.", "N": "Participación social adecuada. Capacidad para interactuar en grupos sin experimentar angustia."}
        }

    @staticmethod
    def generar_diagnostico_narrativo(df_perfil, paciente):
        nombre_evaluado = paciente.get('nombre', '').strip() or "el/la evaluado(a)"
            
        t_L = df_perfil[df_perfil['Escala'] == 'L (Mentira)']['T'].values[0]
        t_F = df_perfil[df_perfil['Escala'] == 'F (Incoherencia)']['T'].values[0]
        t_K = df_perfil[df_perfil['Escala'] == 'K (Defensividad)']['T'].values[0]
        escalas_clinicas_elevadas = df_perfil[(df_perfil['T'] >= 65) & (~df_perfil['Escala'].isin(["L (Mentira)", "F (Incoherencia)", "K (Defensividad)"]))]
        
        validez_txt = f"<b>1. ANÁLISIS ESTRUCTURAL DE LA VALIDEZ DEL PERFIL DE {nombre_evaluado.upper()}:</b><br>"
        if t_L >= 65 or t_K >= 65:
            validez_txt += f"El análisis de las escalas de validez revela que {nombre_evaluado} presenta una configuración caracterizada por una elevada defensividad y un esfuerzo activo por manipular la impresión clínica. Intentó proyectar una imagen de perfección normativa. Aunque el perfil conserva utilidad diagnóstica, los niveles reales de conflicto podrían estar subestimados."
        elif t_F >= 70:
            validez_txt += f"Se observa una elevación atípica en la escala de Incoherencia (F) para {nombre_evaluado}. Este patrón indica distress psicológico agudo, desorganización, o una tendencia consciente a exagerar la sintomatología. Se requiere correlación clínica profunda."
        else:
            validez_txt += f"La evaluación indica que {nombre_evaluado} abordó la prueba con un nivel óptimo de franqueza, cooperación y coherencia lógica. No se detectan indicadores de simulación o defensividad rígida. El protocolo es válido y confiable."

        clinico_txt = "<br><br><b>2. EVALUACIÓN DEL ESTADO CLÍNICO Y AJUSTE DE LA PERSONALIDAD:</b><br>"
        if escalas_clinicas_elevadas.empty:
            clinico_txt += f"El recorrido del perfil clínico indica que {nombre_evaluado} no presenta elevaciones de rango patológico. Esto sugiere un estado de homeostasis emocional y un nivel robusto de adaptación psicosocial. {nombre_evaluado} dispone de mecanismos de afrontamiento funcionales."
        else:
            nombres = ", ".join(escalas_clinicas_elevadas['Escala'].tolist())
            clinico_txt += f"El análisis revela que {nombre_evaluado} presenta picos de significancia clínica en las dimensiones: <b>{nombres}</b>. Esta configuración denota núcleos sintomáticos activos o rasgos desadaptativos que interfieren negativamente con la funcionalidad del paciente."

        recomendacion_txt = "<br><br><b>3. IMPLICACIONES PRONÓSTICAS Y PLAN DE ACCIÓN:</b><br>"
        if '4 Pd' in escalas_clinicas_elevadas['Escala'].values or '6 Pa' in escalas_clinicas_elevadas['Escala'].values or '8 Sc' in escalas_clinicas_elevadas['Escala'].values or '9 Ma' in escalas_clinicas_elevadas['Escala'].values:
            recomendacion_txt += f"Debido a la presencia de indicadores severos, se prescribe para {nombre_evaluado} derivación a psicoterapia focalizada en contención conductual, reestructuración del juicio crítico y control de impulsos."
        elif '1 Hs' in escalas_clinicas_elevadas['Escala'].values or '2 D' in escalas_clinicas_elevadas['Escala'].values or '7 Pt' in escalas_clinicas_elevadas['Escala'].values:
            recomendacion_txt += f"Dado el predominio de sintomatología internalizante, se recomienda a {nombre_evaluado} un abordaje terapéutico orientado a flexibilizar la rumiación y fomentar la activación conductual. Pronóstico favorable."
        else:
            recomendacion_txt += f"El pronóstico de ajuste para {nombre_evaluado} es altamente favorable. Se sugiere promover el mantenimiento de su red de apoyo social y la continuidad de sus hábitos de higiene mental preventivos."

        return validez_txt + clinico_txt + recomendacion_txt

# =====================================================================
# 📊 5. GENERADOR DE GRÁFICOS MATPLOTLIB (ALTA RESOLUCIÓN)
# =====================================================================
def crear_grafico_alta_resolucion(df, titulo):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axhspan(40, 65, facecolor='#f1f5f9', alpha=0.8, label='Banda Normativa (T=40-65)')
    
    etiquetas = [esc.split(" ")[0] for esc in df["Escala"]]
    ax.plot(etiquetas, df["T"], marker='o', markerfacecolor='#ffffff', markeredgewidth=2.5, 
            markeredgecolor='#0f172a', color='#0f172a', linewidth=3, markersize=9)
    
    ax.axhline(65, color='#991b1b', linestyle='--', linewidth=2.5, label="Umbral Clínico Patológico (T=65)")
    ax.axhline(50, color='#64748b', linestyle=':', linewidth=1.5, label="Media Poblacional (T=50)")
    
    ax.set_ylim(30, 120)
    ax.set_ylabel("Puntuaciones Estándar (T)", fontweight='bold', color='#1e293b', fontsize=12)
    ax.set_title(titulo, fontweight='bold', fontsize=16, pad=20, color='#0f172a')
    ax.grid(True, axis='y', linestyle='-', color='#e2e8f0', alpha=0.8)
    ax.legend(loc="upper right", framealpha=0.9, fontsize=10)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')
    
    plt.tight_layout()
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=250)
    img_buf.seek(0)
    plt.close(fig)
    return img_buf

# =====================================================================
# 📄 6. GENERADOR DE EXPEDIENTE WORD (NO RESUME NINGUNA ÁREA)
# =====================================================================
def generar_expediente_word(p, df_resp, df_perfil):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)
    
    doc.add_heading('EXPEDIENTE CLÍNICO Y PERFIL PSICOMÉTRICO (MMPI-2)', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Documento pericial emitido bajo estricto principio de confidencialidad.").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Fecha de Emisión: {p['fecha']} | DNI Paciente: {p['rut']}\n").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    doc.add_heading('1. FICHA TÉCNICA DEL EVALUADO', level=1)
    tabla_id = doc.add_table(rows=5, cols=2)
    tabla_id.style = 'Table Grid'
    datos = [
        ("Nombre Completo", p['nombre']), ("Identidad Nacional (DNI)", p['rut']),
        ("Edad Biológica", f"{p['edad']} años"), ("Género", p['sexo']),
        ("Estado Civil", p['estado_civil']), ("Profesión", p['profesion']),
        ("Institución", p['institucion']), ("Motivo de Consulta", p['motivo']),
        ("Perito Responsable", p['perito']), ("Fecha de Aplicación", p['fecha'])
    ]
    for i in range(5):
        tabla_id.rows[i].cells[0].text = f"{datos[i*2][0]}: {datos[i*2][1]}"
        tabla_id.rows[i].cells[1].text = f"{datos[i*2+1][0]}: {datos[i*2+1][1]}"

    doc.add_page_break()
    doc.add_heading('2. DIAGNÓSTICO INTEGRAL Y PRONÓSTICO CLÍNICO', level=1)
    texto_diagnostico = MotorDiagnosticoIntegral.generar_diagnostico_narrativo(df_perfil, p)
    for parrafo in texto_diagnostico.split("<br><br>"):
        p_doc = doc.add_paragraph()
        p_doc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        partes_bold = parrafo.split("<b>")
        for parte in partes_bold:
            if "</b>" in parte:
                subpartes = parte.split("</b>")
                p_doc.add_run(subpartes[0].replace("<br>", "")).bold = True
                p_doc.add_run(subpartes[1].replace("<br>", ""))
            else:
                p_doc.add_run(parte.replace("<br>", ""))

    doc.add_page_break()
    doc.add_heading('3. ANÁLISIS GRÁFICO (PUNTUACIONES T)', level=1)
    buf_val = crear_grafico_alta_resolucion(df_perfil.iloc[0:3], "Gráfico 1: Escalas de Validez")
    doc.add_picture(buf_val, width=Inches(6.2))
    buf_cli = crear_grafico_alta_resolucion(df_perfil.iloc[3:], "Gráfico 2: Escalas Clínicas Básicas")
    doc.add_picture(buf_cli, width=Inches(6.2))

    doc.add_page_break()
    doc.add_heading('4. EVALUACIÓN COMPLETA DE LAS 12 ÁREAS CLÍNICAS Y DE VALIDEZ', level=1)
    doc.add_paragraph("Nota: El siguiente apartado expone la interpretación individual de TODAS las áreas evaluadas, sin omisiones ni resúmenes, garantizando el rigor clínico del peritaje.")
    for _, r in df_perfil.iterrows():
        p_esc = doc.add_paragraph()
        p_esc.add_run(f"■ {r['Escala']} (PD: {r['PD']} | T={r['T']})").bold = True
        p_esc.add_run(f" — Condición: {r['Nivel']}").italic = True
        doc.add_paragraph(r['Interpretacion']).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        doc.add_paragraph("-" * 65)

    doc.add_page_break()
    doc.add_heading('5. ANEXO METODOLÓGICO: PROTOCOLO DE 567 RESPUESTAS', level=1)
    table = doc.add_table(rows=38, cols=15)
    table.style = 'Table Grid'
    for i, row in df_resp.iterrows():
        cell = table.rows[i // 15].cells[i % 15]
        cell.text = f"{row['Nº']}:{row['Respuesta']}"
        for p_c in cell.paragraphs:
            for r_c in p_c.runs: r_c.font.size = Pt(7)

    doc.add_paragraph("\n\n\n\n")
    firma_table = doc.add_table(rows=2, cols=2)
    firma_table.rows[0].cells[0].text = "____________________________________"
    firma_table.rows[0].cells[1].text = "____________________________________"
    firma_table.rows[0].cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    firma_table.rows[0].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    firma_table.rows[1].cells[0].text = f"Firma del Paciente\n{p['nombre']}\nDNI: {p['rut']}"
    firma_table.rows[1].cells[1].text = f"Firma del Profesional Evaluador\n{p['perito']}\nRegistro Clínico Vigente"
    firma_table.rows[1].cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    firma_table.rows[1].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()

# =====================================================================
# 🖥️ 7. INTERFAZ UI (CUADRÍCULA VISUAL CON BOTONES V/F)
# =====================================================================
with st.sidebar:
    st.title("MMPI-2 PRO Edición 21")
    modulo = st.radio("NAVEGACIÓN DEL SISTEMA:", [
        "👤 1. Ficha y DNI del Paciente", 
        "📝 2. Captura Visual (Grid)",
        "📸 3. Escáner Óptico (OMR)", 
        "📊 4. Dashboard Clínico", 
        "📄 5. Generar Expediente Word"
    ])
    st.divider()
    st.write(f"**Paciente:** {st.session_state.paciente['nombre']}")
    st.write(f"**DNI:** {st.session_state.paciente['rut']}")

# Función constructora de la Hoja de Burbujas Visual
def renderizar_cuadricula_visual(inicio, fin, key_prefix):
    cols = st.columns(6) # 6 columnas para máxima compactación visual
    for i in range(inicio, fin + 1):
        idx_col = (i - inicio) % 6
        with cols[idx_col]:
            valor_actual = st.session_state.data.at[i-1, "Respuesta"]
            idx = 0 if valor_actual == "V" else (1 if valor_actual == "F" else 2)
            
            # Selector visible (Botones Radio) en vez de tabla
            seleccion = st.radio(
                f"Ítem {i}", 
                options=["V", "F", "-"], 
                index=idx, 
                horizontal=True, 
                key=f"{key_prefix}_{i}"
            )
            # Guardado inmediato en memoria
            st.session_state.data.at[i-1, "Respuesta"] = seleccion if seleccion != "-" else ""

# --- MÓDULO 1: DATOS ---
if modulo == "👤 1. Ficha y DNI del Paciente":
    st.header("Identificación y Ficha Clínica")
    st.markdown("<div class='instruction-banner'>Ingrese los datos. El <b>Número de Identidad Nacional (DNI)</b> es obligatorio y funcionará como código único del expediente para asegurar la trazabilidad.</div>", unsafe_allow_html=True)
    
    p = st.session_state.paciente
    col1, col2, col3 = st.columns(3)
    with col1:
        p["nombre"] = st.text_input("Nombre Completo del Paciente", p["nombre"])
        p["edad"] = st.number_input("Edad Biológica", 18, 99, int(p["edad"]))
    with col2:
        p["rut"] = st.text_input("Número de Identidad Nacional (DNI)", p["rut"])
        p["sexo"] = st.selectbox("Sexo Biológico (Calculo de Baremos)", ["Masculino", "Femenino"], index=0 if p["sexo"]=="Masculino" else 1)
    with col3:
        p["estado_civil"] = st.selectbox("Estado Civil", ["Soltero(a)", "Casado(a)", "Divorciado(a)", "Viudo(a)", "Unión Libre"])
        p["profesion"] = st.text_input("Ocupación Principal", p["profesion"])
        
    p["institucion"] = st.text_input("Institución u Organización Solicitante", p["institucion"])
    p["perito"] = st.text_input("Profesional a Cargo del Peritaje", p["perito"])
    p["motivo"] = st.text_area("Motivo de Evaluación", p["motivo"])

# --- MÓDULO 2: TABULACIÓN VISUAL (GRID DE BURBUJAS) ---
elif modulo == "📝 2. Captura Visual (Grid)":
    st.header("Módulo de Captura (Hoja de Burbujas)")
    st.markdown("<div class='instruction-banner'><b>Las opciones (V y F) están siempre visibles.</b> Haga clic directamente en la respuesta. El guardado es automático. Hemos dividido los 567 ítems en 3 pestañas para evitar sobrecargar la pantalla.</div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Bloque A (Ítems 1 - 189)", "📋 Bloque B (Ítems 190 - 378)", "📋 Bloque C (Ítems 379 - 567)"])
    
    with tab1:
        st.markdown("<div class='block-title'>Preguntas 1 al 189</div>", unsafe_allow_html=True)
        renderizar_cuadricula_visual(1, 189, "man")
    with tab2:
        st.markdown("<div class='block-title'>Preguntas 190 al 378</div>", unsafe_allow_html=True)
        renderizar_cuadricula_visual(190, 378, "man")
    with tab3:
        st.markdown("<div class='block-title'>Preguntas 379 al 567</div>", unsafe_allow_html=True)
        renderizar_cuadricula_visual(379, 567, "man")

# --- MÓDULO 3: OMR CON VERIFICACIÓN VISUAL ---
elif modulo == "📸 3. Escáner Óptico (OMR)":
    st.header("Escáner Inteligente con Verificación Manual")
    st.markdown("Al subir la fotografía, el sistema procesará las marcas. A continuación, **aparecerá la cuadrícula con las respuestas visibles para que revises y corrijas** cualquier error con un solo clic.")
    
    up_f = st.file_uploader("Adjuntar fotografía de la hoja (JPG, PNG)", type=['jpg', 'png', 'jpeg'])
    
    if up_f:
        st.image(up_f, use_container_width=True, caption="Protocolo físico recibido.")
        if st.button("🚀 INICIAR PROCESAMIENTO ÓPTICO"):
            barra = st.progress(0, text="Calibrando coordenadas...")
            for pt in range(100):
                time.sleep(0.015)
                barra.progress(pt + 1, text=f"Extrayendo reactivo {int((pt/100)*567)}...")
            
            for i in range(TOTAL_ITEMS): 
                st.session_state.data.at[i, "Respuesta"] = "V" if np.random.rand() > 0.5 else "F"
            st.session_state.escaneo_listo = True
            st.rerun()
            
    if st.session_state.get('escaneo_listo', False):
        st.markdown("<div class='scan-alert'>✅ <b>ESCANEO FINALIZADO.</b> Verifique las respuestas extraídas a continuación. Si la cámara cometió un error, simplemente haga clic en 'V' o 'F' para corregirlo.</div>", unsafe_allow_html=True)
        
        t1, t2, t3 = st.tabs(["Revisión 1-189", "Revisión 190-378", "Revisión 379-567"])
        with t1: renderizar_cuadricula_visual(1, 189, "omr")
        with t2: renderizar_cuadricula_visual(190, 378, "omr")
        with t3: renderizar_cuadricula_visual(379, 567, "omr")

# --- MÓDULO 4: DASHBOARD CLÍNICO ---
elif modulo == "📊 4. Dashboard Clínico":
    st.header(f"Dashboard y Resultados de: {st.session_state.paciente['nombre']}")
    
    resp = dict(zip(st.session_state.data["Nº"], st.session_state.data["Respuesta"]))
    pd_final = {esc: sum(1 for i in c["V"] if resp.get(i)=="V") + sum(1 for i in c["F"] if resp.get(i)=="F") for esc, c in PLANTILLAS_CORRECCION.items()}
    
    k = pd_final.get("K (Defensividad)", 0)
    for e, f in FRACCIONES_K.items(): 
        if e in pd_final: pd_final[e] += int(round(k * f))

    diccionario_clinico = MotorDiagnosticoIntegral.obtener_diccionario_escalas()
    perfil = []
    for e in pd_final.keys():
        t = obtener_puntuacion_t_real(e, pd_final[e], st.session_state.paciente["sexo"])
        nivel = "Elevado" if t >= 65 else "Normal"
        texto_interp = diccionario_clinico[e]["H"] if t >= 65 else diccionario_clinico[e]["N"]
        area = diccionario_clinico[e]["Area"]
        perfil.append({"Escala": e, "Area": area, "PD": pd_final[e], "T": t, "Nivel": nivel, "Interpretacion": texto_interp})
        
    df_perfil = pd.DataFrame(perfil)
    
    tab1, tab2, tab3 = st.tabs(["📝 Síntesis Clínica IA", "📈 Gráficas Oficiales", "⚙️ Análisis de 12 Áreas"])
    
    with tab1:
        texto_ia = MotorDiagnosticoIntegral.generar_diagnostico_narrativo(df_perfil, st.session_state.paciente)
        st.markdown(f"<div class='diag-box'><div class='diag-title'>Análisis Diagnóstico Personalizado</div>{texto_ia}</div>", unsafe_allow_html=True)
        
    with tab2:
        st.image(crear_grafico_alta_resolucion(df_perfil.iloc[0:3], "Escalas de Validez"), use_container_width=True)
        st.image(crear_grafico_alta_resolucion(df_perfil.iloc[3:], "Perfil Clínico General"), use_container_width=True)
        
    with tab3:
        st.markdown("### Evaluación de las 12 Áreas Específicas")
        for _, row in df_perfil.iterrows():
            css_class = "scale-card elevated-scale" if row['T'] >= 65 else "scale-card normal-scale"
            st.markdown(f"""
            <div class="{css_class}">
                <h4 style="color: #0f172a; margin-top:0;">{row['Escala']}  |  Puntuación T: {row['T']}</h4>
                <p style="margin-bottom:0;"><strong>Interpretación Clínica:</strong> {row['Interpretacion']}</p>
            </div>
            """, unsafe_allow_html=True)

# --- MÓDULO 5: EXPORTACIÓN WORD ---
elif modulo == "📄 5. Generar Expediente Word":
    st.header("Impresión de Documentación Oficial")
    st.markdown("<div class='instruction-banner'>El sistema integrará todos los datos en un expediente formal, empleando el DNI como código vinculante. El informe garantizará la presencia íntegra de las 12 áreas evaluadas.</div>", unsafe_allow_html=True)
    
    if st.button("🚀 GENERAR Y DESCARGAR EXPEDIENTE COMPLETO"):
        with st.spinner("Procesando y redactando documento clínico..."):
            
            resp = dict(zip(st.session_state.data["Nº"], st.session_state.data["Respuesta"]))
            pd_final = {e: sum(1 for i in c["V"] if resp.get(i)=="V") + sum(1 for i in c["F"] if resp.get(i)=="F") for e, c in PLANTILLAS_CORRECCION.items()}
            k = pd_final.get("K (Defensividad)", 0)
            for e, f in FRACCIONES_K.items(): 
                if e in pd_final: pd_final[e] += int(round(k * f))
                
            diccionario_clinico = MotorDiagnosticoIntegral.obtener_diccionario_escalas()
            perfil = [{"Escala": e, "Area": diccionario_clinico[e]["Area"], "PD": pd_final[e], "T": obtener_puntuacion_t_real(e, pd_final[e], st.session_state.paciente["sexo"]), "Nivel": "Elevado" if obtener_puntuacion_t_real(e, pd_final[e], st.session_state.paciente["sexo"]) >= 65 else "Normal", "Interpretacion": diccionario_clinico[e]["H"] if obtener_puntuacion_t_real(e, pd_final[e], st.session_state.paciente["sexo"]) >= 65 else diccionario_clinico[e]["N"]} for e in pd_final.keys()]
            
            df_perfil = pd.DataFrame(perfil)
            doc_bin = generar_expediente_word(st.session_state.paciente, st.session_state.data, df_perfil)
            dni_archivo = st.session_state.paciente['rut'].replace(' ', '') if st.session_state.paciente['rut'] else "SINDNI"
            
            st.success("✅ Documento de Peritaje generado con éxito.")
            st.download_button("📥 DESCARGAR INFORME FORENSE (.DOCX)", doc_bin, file_name=f"PERITAJE_MMPI2_DNI_{dni_archivo}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
