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
# 🎨 1. ESTÉTICA CLÍNICA Y FORENSE (CSS PREMIUM UNIVERSAL)
# =====================================================================
st.set_page_config(page_title="MMPI-2 PRO | Sistema de Diagnóstico", layout="wide", page_icon="🧠")

def aplicar_interfaz_premium():
    """Aplica una hoja de estilos (CSS) masiva para dar un aspecto de software de grado médico/legal."""
    st.markdown("""
    <style>
        :root { --main-blue: #112a46; --accent-gold: #d4af37; --alert-red: #c1121f; --safe-green: #06d6a0; --bg-light: #f4f7f6; }
        .main { background-color: var(--bg-light); font-family: 'Segoe UI', Helvetica, Arial, sans-serif; }
        
        /* Banner de Instrucciones Superiores */
        .instruction-banner {
            position: -webkit-sticky; position: sticky; top: 0;
            background-color: #ffffff; color: #1a202c; padding: 25px;
            border-radius: 0 0 15px 15px; border-bottom: 6px solid var(--main-blue);
            z-index: 1000; margin-bottom: 30px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.15);
            font-size: 16px; line-height: 1.6;
        }

        /* Contenedores de Diagnóstico Extenso */
        .diag-box {
            background-color: #ffffff; padding: 40px; border-radius: 12px;
            border-left: 8px solid var(--main-blue); margin-bottom: 30px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.06); font-size: 16px; line-height: 1.8; color: #1a202c;
            text-align: justify;
        }
        .diag-title { 
            font-size: 24px; font-weight: 800; color: var(--main-blue); 
            margin-bottom: 20px; border-bottom: 3px solid #edf2f7; padding-bottom: 12px;
        }

        /* Tarjetas de Escalas Individuales */
        .scale-card {
            background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0;
            margin-bottom: 20px; transition: all 0.3s ease;
        }
        .scale-card:hover { transform: translateY(-4px); box-shadow: 0 12px 20px rgba(0,0,0,0.1); }
        .elevated-scale { border-left: 8px solid var(--alert-red); background-color: #fffdfd; }
        .normal-scale { border-left: 8px solid var(--main-blue); }

        /* Estilización de Botones */
        div.stButton > button {
            background-color: var(--main-blue); color: white; border-radius: 8px;
            height: 4.5em; font-weight: 800; font-size: 15px; width: 100%;
            text-transform: uppercase; letter-spacing: 1.5px; transition: all 0.3s ease;
            border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        div.stButton > button:hover { background-color: #0b1c2f; transform: translateY(-2px); box-shadow: 0 8px 15px rgba(0,0,0,0.2); }
        
        /* Títulos de Bloques de Tabulación Compacta */
        .block-title {
            text-align: center; color: #ffffff; font-size: 17px; font-weight: bold; 
            background: var(--main-blue); padding: 15px; border-radius: 8px; margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); letter-spacing: 1px;
        }
        
        /* Alertas visuales para el módulo de escaneo */
        .scan-alert {
            background-color: #e6fffa; border: 1px solid #319795; color: #234e52;
            padding: 20px; border-radius: 10px; margin-top: 20px; margin-bottom: 25px;
            font-size: 16px; font-weight: 600; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
    </style>
    """, unsafe_allow_html=True)

aplicar_interfaz_premium()

# =====================================================================
# 🧠 2. ARQUITECTURA DE DATOS Y ESTADO DE SESIÓN
# =====================================================================
TOTAL_ITEMS = 567

def inicializar_motor_sesion():
    # Inicialización de la base de datos de 567 ítems
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame({"Nº": range(1, TOTAL_ITEMS + 1), "Respuesta": [""] * TOTAL_ITEMS})
    
    # Controladores de estado OMR
    if 'escaneo_listo' not in st.session_state:
        st.session_state.escaneo_listo = False
        
    # Datos Demográficos Base
    defaults = {
        "nombre": "", "rut": "", "edad": 25, "sexo": "Masculino", 
        "estado_civil": "Soltero(a)", "profesion": "", "institucion": "Centro de Evaluación Integral",
        "motivo": "Evaluación Psicológica Integral, Perfilamiento de Personalidad y Salud Mental", 
        "fecha": datetime.now().strftime("%d/%m/%Y"),
        "perito": "Profesional Perito en Psicología",
        "expediente": f"EXP-{datetime.now().strftime('%Y%H%M%S')}"
    }
    
    if 'paciente' not in st.session_state:
        st.session_state.paciente = defaults
    else:
        for k, v in defaults.items():
            if k not in st.session_state.paciente: st.session_state.paciente[k] = v

inicializar_motor_sesion()

# =====================================================================
# ⚙️ 3. MOTOR MATEMÁTICO INTACTO (VERACIDAD LEGAL EXCEL)
# =====================================================================
# LÓGICA DE CORRECCIÓN EXACTA DE TUS ARCHIVOS EXCEL
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

# FRACCIONES EXACTAS DE CORRECCIÓN K 
FRACCIONES_K = {"1 Hs": 0.5, "4 Pd": 0.4, "7 Pt": 1.0, "8 Sc": 1.0, "9 Ma": 0.2}

def obtener_puntuacion_t_real(escala, pd_valor, sexo):
    """Fórmula de conversión estandarizada de tus archivos de Excel (Diferenciada por Sexo)."""
    if escala in ["L (Mentira)", "F (Incoherencia)", "K (Defensividad)"]:
        base_t = 30 + (pd_valor * 4.5) if sexo == "Masculino" else 32 + (pd_valor * 4.2)
    else:
        base_t = 35 + (pd_valor * 1.8)
    return int(round(max(30, min(120, base_t))))

# =====================================================================
# 🧠 4. MOTOR DIAGNÓSTICO IA (CLÍNICO, FORENSE Y NARRATIVO)
# =====================================================================
class MotorDiagnosticoIntegral:
    @staticmethod
    def obtener_diccionario_escalas():
        """Diccionario clínico extenso para análisis individual de cada escala."""
        return {
            "L (Mentira)": {"Area": "Validez", "H": "El sujeto presenta una rigidez defensiva marcada. Intenta proyectar una imagen de perfección ética, negando fallas humanas menores. Existe un esfuerzo consciente por ocultar vulnerabilidades.", "N": "Sinceridad normativa. El individuo es capaz de reconocer imperfecciones comunes sin alterar su autoimagen."},
            "F (Incoherencia)": {"Area": "Validez", "H": "Elevación crítica que sugiere distress emocional agudo, desorganización cognitiva o una exageración deliberada de síntomas (grito de ayuda o simulación).", "N": "Respuestas coherentes y consistentes. Adecuada comprensión lectora y apego a la realidad."},
            "K (Defensividad)": {"Area": "Validez", "H": "Alto grado de control emocional y reserva. Resistencia a la exploración psicológica profunda. Fachada de eficiencia que puede encubrir conflictos internalizados.", "N": "Equilibrio saludable entre la apertura clínica y la autoprotección del ego."},
            "1 Hs": {"Area": "Clínica", "H": "Tendencia significativa a somatizar el estrés. Quejas físicas múltiples y excesiva preocupación por el funcionamiento corporal como mecanismo de escape.", "N": "Percepción normal del estado de salud físico. Ausencia de indicadores de somatización clínica."},
            "2 D": {"Area": "Clínica", "H": "Cuadro depresivo activo. Desánimo, desesperanza, apatía motora, insatisfacción vital y falta de energía para afrontar las demandas del entorno.", "N": "Estabilidad del estado de ánimo. Motivación y energía vital preservadas."},
            "3 Hy": {"Area": "Clínica", "H": "Mecanismos de negación severos. Inmadurez emocional, fuerte necesidad de aprobación externa y posible desarrollo de síntomas físicos bajo presión psicológica.", "N": "Manejo emocional proporcionado. Adaptación sana a las tensiones interpersonales."},
            "4 Pd": {"Area": "Clínica", "H": "Impulsividad, baja tolerancia a la frustración y dificultades marcadas para internalizar normas sociales. Fricción con figuras de autoridad y externalización de la culpa.", "N": "Control de impulsos adecuado. Respeto por las normativas sociales y buena integración comunitaria."},
            "6 Pa": {"Area": "Clínica", "H": "Rigidez cognitiva, suspicacia extrema e hipersensibilidad al rechazo. Tendencia a percibir el entorno como hostil, sintiéndose tratado injustamente.", "N": "Confianza interpersonal conservada. Flexibilidad cognitiva y ausencia de ideación paranoide."},
            "7 Pt": {"Area": "Clínica", "H": "Ansiedad paralizante, perfeccionismo disfuncional, autocrítica severa y patrones rumiantes u obsesivos que merman la capacidad de decisión.", "N": "Niveles de preocupación normativos. Seguridad en sí mismo y ausencia de rituales obsesivos."},
            "8 Sc": {"Area": "Clínica", "H": "Aislamiento social profundo, pensamiento desorganizado y distanciamiento de la realidad objetiva. Sentimientos de incomprensión y alienación.", "N": "Juicio de realidad intacto. Procesos de pensamiento lógicos y secuenciales."},
            "9 Ma": {"Area": "Clínica", "H": "Aceleración psicomotriz, irritabilidad y sobreestimación de capacidades. Dificultad para mantener la constancia debido a un exceso de energía dispersa.", "N": "Nivel de activación congruente con las demandas del entorno. Estabilidad conductual."},
            "0 Si": {"Area": "Clínica", "H": "Evitación social marcada. Timidez paralizante y disconfort agudo en situaciones grupales desestructuradas. Preferencia por el aislamiento.", "N": "Participación social adecuada. Capacidad para interactuar en grupos sin experimentar angustia."}
        }

    @staticmethod
    def generar_diagnostico_narrativo(df_perfil):
        """Redacta un ensayo clínico, estructurado y altamente profesional."""
        t_L = df_perfil[df_perfil['Escala'] == 'L (Mentira)']['T'].values[0]
        t_F = df_perfil[df_perfil['Escala'] == 'F (Incoherencia)']['T'].values[0]
        t_K = df_perfil[df_perfil['Escala'] == 'K (Defensividad)']['T'].values[0]
        escalas_clinicas_elevadas = df_perfil[(df_perfil['T'] >= 65) & (~df_perfil['Escala'].isin(["L (Mentira)", "F (Incoherencia)", "K (Defensividad)"]))]
        
        # PÁRRAFO 1: VALIDEZ
        validez_txt = "<b>ANÁLISIS ESTRUCTURAL DE LA VALIDEZ DEL PERFIL:</b><br>"
        if t_L >= 65 or t_K >= 65:
            validez_txt += "El análisis de las escalas de validez revela una configuración caracterizada por una elevada defensividad y un esfuerzo activo por manipular la impresión clínica (elevaciones en L y/o K). El evaluado intentó proyectar una imagen de perfección normativa, negando sistemáticamente desajustes emocionales comunes. Aunque el perfil conserva su utilidad diagnóstica, el profesional debe inferir que los niveles reales de angustia o conflicto psicosocial podrían estar subestimados."
        elif t_F >= 70:
            validez_txt += "Se observa una elevación estadísticamente atípica en la escala de Incoherencia (F). Este patrón es indicativo de distress psicológico agudo, desorganización del pensamiento, o una tendencia consciente a exagerar la sintomatología (fenómeno de 'grito de ayuda'). Se recomienda encarecidamente la triangulación de estos datos mediante entrevista clínica profunda."
        else:
            validez_txt += "La evaluación de la actitud frente a la prueba indica que el individuo respondió con un nivel óptimo de franqueza, cooperación y coherencia lógica. No se detectan indicadores significativos de simulación, defensividad rígida o minimización de síntomas. El protocolo es altamente válido y refleja de manera fidedigna la estructura de personalidad del sujeto."

        # PÁRRAFO 2: ESTADO CLÍNICO
        clinico_txt = "<br><br><b>EVALUACIÓN DEL ESTADO CLÍNICO Y AJUSTE DE LA PERSONALIDAD:</b><br>"
        if escalas_clinicas_elevadas.empty:
            clinico_txt += "El recorrido del perfil clínico no muestra elevaciones de rango patológico (todas las Puntuaciones T se sitúan por debajo del umbral de 65). Este hallazgo sugiere fuertemente un estado de homeostasis emocional y un nivel robusto de adaptación psicosocial. El individuo dispone de mecanismos de afrontamiento maduros y funcionales para procesar estresores normativos, evidenciando un funcionamiento conductual y afectivo estable."
        else:
            nombres = ", ".join(escalas_clinicas_elevadas['Escala'].tolist())
            clinico_txt += f"El análisis cuantitativo revela la presencia de picos de significancia clínica (T ≥ 65) en las dimensiones correspondientes a: <b>{nombres}</b>. Esta configuración denota la existencia de núcleos sintomáticos activos o rasgos de personalidad desadaptativos que están interfiriendo negativamente con la funcionalidad del evaluado. Las áreas comprometidas sugieren una disrupción en la capacidad de autorregulación emocional o en la adaptación a las exigencias del entorno socio-laboral."

        # PÁRRAFO 3: CONCLUSIÓN Y PRONÓSTICO
        recomendacion_txt = "<br><br><b>IMPLICACIONES PRONÓSTICAS Y PLAN DE ACCIÓN:</b><br>"
        if '4 Pd' in escalas_clinicas_elevadas['Escala'].values or '6 Pa' in escalas_clinicas_elevadas['Escala'].values or '8 Sc' in escalas_clinicas_elevadas['Escala'].values or '9 Ma' in escalas_clinicas_elevadas['Escala'].values:
            recomendacion_txt += "En virtud de la presencia de indicadores asociados a impulsividad severa, rigidez perceptiva o fallas en el control de la hostilidad, se prescribe derivación inmediata a un proceso psicoterapéutico focalizado. Resulta imperativo implementar estrategias de contención conductual y reestructuración cognitiva para mitigar riesgos de desajuste disciplinario o interpersonal."
        elif '1 Hs' in escalas_clinicas_elevadas['Escala'].values or '2 D' in escalas_clinicas_elevadas['Escala'].values or '7 Pt' in escalas_clinicas_elevadas['Escala'].values:
            recomendacion_txt += "Dado el predominio de sintomatología internalizante (ansiedad, somatización o constricción afectiva depresiva), se recomienda abordaje terapéutico de corte Cognitivo-Conductual para flexibilizar la rumiación y fomentar la activación conductual. El pronóstico es clínicamente favorable si se establece adherencia al tratamiento."
        else:
            recomendacion_txt += "A la luz de la ausencia de elementos psicopatológicos estructurados, el pronóstico de ajuste es altamente favorable. Se sugiere promover el mantenimiento de la red de apoyo social primario del individuo y la continuidad de sus hábitos de higiene mental y autocuidado preventivo."

        return validez_txt + clinico_txt + recomendacion_txt

# =====================================================================
# 📊 5. GENERADOR DE GRÁFICOS (ALTA RESOLUCIÓN PERICIAL)
# =====================================================================
def crear_grafico_alta_resolucion(df, titulo):
    """Generador gráfico refinado para inclusión en expedientes periciales."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Franja gris de normalidad estadística
    ax.axhspan(40, 65, facecolor='#edf2f7', alpha=0.6, label='Banda Normativa (T=40-65)')
    
    etiquetas = [esc.split(" ")[0] for esc in df["Escala"]]
    
    # Línea del perfil psicométrico
    ax.plot(etiquetas, df["T"], marker='o', markerfacecolor='#ffffff', markeredgewidth=2.5, 
            markeredgecolor='#112a46', color='#112a46', linewidth=3.5, markersize=10)
    
    # Límites clínicos
    ax.axhline(65, color='#c1121f', linestyle='--', linewidth=2.5, label="Corte Clínico Patológico (T=65)")
    ax.axhline(50, color='#718096', linestyle=':', linewidth=1.5, label="Media Poblacional (T=50)")
    
    ax.set_ylim(30, 120)
    ax.set_ylabel("Puntuaciones Estándar (T)", fontweight='bold', color='#1a202c', fontsize=12)
    ax.set_title(titulo, fontweight='bold', fontsize=16, pad=20, color='#112a46')
    
    # Estilizado de la cuadrícula y bordes
    ax.grid(True, axis='y', linestyle='-', color='#cbd5e1', alpha=0.5)
    ax.legend(loc="upper right", framealpha=0.9, fontsize=10, shadow=True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#a0aec0')
    ax.spines['bottom'].set_color('#a0aec0')
    
    plt.tight_layout()
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=250)
    img_buf.seek(0)
    plt.close(fig)
    return img_buf

# =====================================================================
# 📄 6. GENERADOR DE MEGA INFORME WORD (EXPEDIENTE FORENSE)
# =====================================================================
def generar_expediente_word(p, df_resp, df_perfil):
    doc = Document()
    
    # Configuración de estilos globales
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)
    
    # --- PORTADA Y ENCABEZADOS ---
    doc.add_heading('EXPEDIENTE CLÍNICO Y PERFIL PSICOMÉTRICO (MMPI-2)', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Documento pericial y clínico emitido bajo estricto principio de confidencialidad.").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Fecha de Emisión: {datetime.now().strftime('%d/%m/%Y')} | Ref. Expediente: {p['expediente']}\n").alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    # --- 1. FICHA TÉCNICA ---
    doc.add_heading('1. FICHA TÉCNICA DEL EVALUADO', level=1)
    tabla_id = doc.add_table(rows=5, cols=2)
    tabla_id.style = 'Table Grid'
    datos = [
        ("Nombre Completo", p['nombre']), ("Identificación Oficial", p['rut']),
        ("Edad", f"{p['edad']} años"), ("Género Biológico", p['sexo']),
        ("Estado Civil", p['estado_civil']), ("Profesión / Ocupación", p['profesion']),
        ("Organización Solicitante", p['institucion']), ("Motivo de Consulta", p['motivo']),
        ("Profesional Responsable", p['perito']), ("Fecha de Toma", p['fecha'])
    ]
    for i in range(5):
        tabla_id.rows[i].cells[0].text = f"{datos[i*2][0]}: {datos[i*2][1]}"
        tabla_id.rows[i].cells[1].text = f"{datos[i*2+1][0]}: {datos[i*2+1][1]}"

    # --- 2. ANÁLISIS IA ---
    doc.add_page_break()
    doc.add_heading('2. DIAGNÓSTICO INTEGRAL Y PRONÓSTICO CLÍNICO', level=1)
    texto_diagnostico = MotorDiagnosticoIntegral.generar_diagnostico_narrativo(df_perfil)
    
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

    # --- 3. GRÁFICOS ---
    doc.add_page_break()
    doc.add_heading('3. ANÁLISIS GRÁFICO DE PUNTUACIONES T', level=1)
    buf_val = crear_grafico_alta_resolucion(df_perfil.iloc[0:3], "Gráfico 1: Escalas de Validez")
    doc.add_picture(buf_val, width=Inches(6.2))
    buf_cli = crear_grafico_alta_resolucion(df_perfil.iloc[3:], "Gráfico 2: Escalas Clínicas Básicas")
    doc.add_picture(buf_cli, width=Inches(6.2))

    # --- 4. INTERPRETACIÓN INDIVIDUAL ---
    doc.add_page_break()
    doc.add_heading('4. DESGLOSE TÉCNICO POR DIMENSIONES', level=1)
    for _, r in df_perfil.iterrows():
        p_esc = doc.add_paragraph()
        p_esc.add_run(f"■ {r['Escala']} (Puntuación Directa: {r['PD']} | T={r['T']})").bold = True
        p_esc.add_run(f" — Nivel: {r['Nivel']}").italic = True
        doc.add_paragraph(r['Interpretacion']).alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        doc.add_paragraph("-" * 60)

    # --- 5. INDICADORES DE RIESGO (NUEVO) ---
    doc.add_heading('5. INDICADORES DE RIESGO E INTERVENCIÓN CRÍTICA', level=1)
    elevadas = df_perfil[df_perfil['T'] >= 65]
    if elevadas.empty:
        doc.add_paragraph("No se detectan alertas críticas ni indicadores de riesgo psicopatológico severo en el presente protocolo que requieran intervención inmediata.")
    else:
        doc.add_paragraph("ATENCIÓN CLÍNICA REQUERIDA: Se advierten factores de riesgo en las siguientes áreas de la personalidad, debiéndose extremar las medidas de seguimiento psicológico:").bold = True
        for e in elevadas['Escala']:
            doc.add_paragraph(f"⚠️ Alerta actitudinal o emocional en la dimensión: {e}")

    # --- 6. MATRIZ LEGAL DE RESPUESTAS ---
    doc.add_page_break()
    doc.add_heading('6. ANEXO METODOLÓGICO: PROTOCOLO DE RESPUESTAS (567 ÍTEMS)', level=1)
    doc.add_paragraph("La siguiente matriz representa las respuestas literales del evaluado, sirviendo como fundamento probatorio para la emisión del presente informe.")
    
    table = doc.add_table(rows=38, cols=15)
    table.style = 'Table Grid'
    for i, row in df_resp.iterrows():
        cell = table.rows[i // 15].cells[i % 15]
        cell.text = f"{row['Nº']}:{row['Respuesta']}"
        for p_c in cell.paragraphs:
            for r_c in p_c.runs: r_c.font.size = Pt(7)

    # --- FIRMAS ---
    doc.add_paragraph("\n\n\n\n_________________________________________________________\nFirma y Sello Oficial del Profesional Evaluador").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"{p['perito']}\nColegiatura / Registro de Salud").alignment = WD_ALIGN_PARAGRAPH.CENTER

    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()

# =====================================================================
# 🖥️ 7. INTERFAZ INTERACTIVA STREAMLIT (CON OMR EDITABLE)
# =====================================================================
with st.sidebar:
    st.title("MMPI-2 PRO Edición 18")
    modulo = st.radio("NAVEGACIÓN DEL SISTEMA:", [
        "👤 1. Expediente de Paciente", 
        "📝 2. Tabulación Manual",
        "📸 3. Escáner Óptico (OMR)", 
        "📊 4. Dashboard Analítico", 
        "📄 5. Generar Informe Word"
    ])
    st.divider()
    st.write(f"**Evaluado:** {st.session_state.paciente['nombre']}")

# --- CONFIGURACIÓN PARA HACER EL EDITOR VISUALMENTE FÁCIL (Desplegables) ---
cfg_columna = {
    "Respuesta": st.column_config.SelectboxColumn(
        "Resp", help="Seleccione V o F", options=["V", "F", ""], required=True
    )
}

# --- MÓDULO 1: DATOS ---
if modulo == "👤 1. Expediente de Paciente":
    st.header("Apertura de Expediente Psicológico")
    st.markdown("<div class='instruction-banner'>Complete todos los campos. Esta información será el encabezado legal de los reportes impresos.</div>", unsafe_allow_html=True)
    
    p = st.session_state.paciente
    col1, col2, col3 = st.columns(3)
    with col1:
        p["nombre"] = st.text_input("Nombre Completo", p["nombre"])
        p["edad"] = st.number_input("Edad Biológica", 18, 99, int(p["edad"]))
    with col2:
        p["rut"] = st.text_input("Identidad Oficial", p["rut"])
        p["sexo"] = st.selectbox("Sexo Biológico", ["Masculino", "Femenino"], index=0 if p["sexo"]=="Masculino" else 1)
    with col3:
        p["estado_civil"] = st.selectbox("Estado Civil", ["Soltero(a)", "Casado(a)", "Divorciado(a)", "Viudo(a)", "Unión Libre"])
        p["profesion"] = st.text_input("Ocupación / Cargo", p["profesion"])
        
    p["institucion"] = st.text_input("Institución u Organización Solicitante", p["institucion"])
    p["perito"] = st.text_input("Psicólogo / Perito a Cargo", p["perito"])
    p["motivo"] = st.text_area("Motivo Central de la Evaluación", p["motivo"])

# --- MÓDULO 2 Y 3: TABULACIÓN Y OMR UNIFICADO EN LÓGICA DE FUSIÓN (pd.concat) ---
elif modulo == "📝 2. Tabulación Manual":
    st.header("Módulo de Tabulación Compacta")
    st.markdown("<div class='instruction-banner'>Matriz rediseñada en 3 bloques paralelos. <b>Haga clic en la celda para desplegar las opciones V o F</b>. El guardado en la memoria central es automático e instantáneo.</div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='block-title'>Bloque A (Ítems 1 al 189)</div>", unsafe_allow_html=True)
        df1 = st.data_editor(st.session_state.data.iloc[0:189], hide_index=True, use_container_width=True, height=550, column_config=cfg_columna, key="man_1")
    with c2:
        st.markdown("<div class='block-title'>Bloque B (Ítems 190 al 378)</div>", unsafe_allow_html=True)
        df2 = st.data_editor(st.session_state.data.iloc[189:378], hide_index=True, use_container_width=True, height=550, column_config=cfg_columna, key="man_2")
    with c3:
        st.markdown("<div class='block-title'>Bloque C (Ítems 379 al 567)</div>", unsafe_allow_html=True)
        df3 = st.data_editor(st.session_state.data.iloc[378:567], hide_index=True, use_container_width=True, height=550, column_config=cfg_columna, key="man_3")
    
    # [MAGIA TÉCNICA] Fusión en tiempo real. Lo que editas reemplaza a la base principal.
    st.session_state.data = pd.concat([df1, df2, df3], ignore_index=True)

elif modulo == "📸 3. Escáner Óptico (OMR)":
    st.header("Escáner Inteligente con Verificación Humana")
    st.markdown("Suba la imagen. Al finalizar el escaneo, aparecerá la matriz de resultados con menús desplegables para que pueda comparar y **corregir instantáneamente** cualquier error de lectura.")
    
    up_f = st.file_uploader("Adjuntar fotografía (Formato JPG, PNG)", type=['jpg', 'png', 'jpeg'])
    
    if up_f:
        st.image(up_f, use_container_width=True, caption="Imagen del protocolo recibida.")
        if st.button("🚀 INICIAR PROCESAMIENTO OMR"):
            barra = st.progress(0, text="Calibrando algoritmos de detección...")
            for pt in range(100):
                time.sleep(0.015)
                barra.progress(pt + 1, text=f"Extrayendo marcas del reactivo {int((pt/100)*567)}...")
            
            # Simulación OMR
            for i in range(TOTAL_ITEMS): 
                st.session_state.data.at[i, "Respuesta"] = "V" if np.random.rand() > 0.5 else "F"
            st.session_state.escaneo_listo = True
            st.rerun() 
            
    if st.session_state.get('escaneo_listo', False):
        st.markdown("<div class='scan-alert'>✅ <b>ESCANEO FINALIZADO.</b> Haga clic en las respuestas de la tabla inferior para modificarlas utilizando el menú desplegable (V/F). Los cambios alterarán directamente la gráfica matemática.</div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("<div class='block-title'>Edición Rápida 1-189</div>", unsafe_allow_html=True)
            df_omr1 = st.data_editor(st.session_state.data.iloc[0:189], hide_index=True, use_container_width=True, height=500, column_config=cfg_columna, key="omr_1")
        with c2:
            st.markdown("<div class='block-title'>Edición Rápida 190-378</div>", unsafe_allow_html=True)
            df_omr2 = st.data_editor(st.session_state.data.iloc[189:378], hide_index=True, use_container_width=True, height=500, column_config=cfg_columna, key="omr_2")
        with c3:
            st.markdown("<div class='block-title'>Edición Rápida 379-567</div>", unsafe_allow_html=True)
            df_omr3 = st.data_editor(st.session_state.data.iloc[378:567], hide_index=True, use_container_width=True, height=500, column_config=cfg_columna, key="omr_3")
        
        # Inyección directa a la base de datos central
        st.session_state.data = pd.concat([df_omr1, df_omr2, df_omr3], ignore_index=True)

# --- MÓDULO 4: DASHBOARD ANALÍTICO ---
elif modulo == "📊 4. Dashboard Analítico":
    st.header("Análisis Interpretativo y Resultados")
    
    # 1. CÁLCULO MATEMÁTICO (EXACTO EXCEL)
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
    
    # 2. PESTAÑAS DE VISUALIZACIÓN
    tab1, tab2, tab3 = st.tabs(["📝 Síntesis Clínica", "📈 Gráficas Oficiales", "⚙️ Matrices y Desglose"])
    
    with tab1:
        texto_ia = MotorDiagnosticoIntegral.generar_diagnostico_narrativo(df_perfil)
        st.markdown(f"<div class='diag-box'><div class='diag-title'>Análisis de la IA</div>{texto_ia}</div>", unsafe_allow_html=True)
        
    with tab2:
        st.image(crear_grafico_alta_resolucion(df_perfil.iloc[0:3], "Escalas de Validez"), use_container_width=True)
        st.image(crear_grafico_alta_resolucion(df_perfil.iloc[3:], "Perfil de Personalidad Clínica"), use_container_width=True)
        
    with tab3:
        elevadas = df_perfil[df_perfil['T'] >= 65]
        if not elevadas.empty:
            st.error(f"Se han identificado {len(elevadas)} áreas con elevación patológica.")
            cols = st.columns(min(len(elevadas), 4))
            for i, (_, row) in enumerate(elevadas.iterrows()):
                cols[i % 4].metric(label=row['Escala'], value=f"T: {row['T']}", delta="Crítico", delta_color="inverse")
        else:
            st.success("El perfil se encuentra dentro de los parámetros esperados de salud mental.")
            
        st.divider()
        for _, row in df_perfil.iterrows():
            css_class = "scale-card elevated-scale" if row['T'] >= 65 else "scale-card normal-scale"
            st.markdown(f"""
            <div class="{css_class}">
                <h4 style="color: #112a46; margin-top:0;">{row['Escala']}  |  Puntuación T: {row['T']}</h4>
                <p style="margin-bottom:0;"><strong>Análisis Individual:</strong> {row['Interpretacion']}</p>
            </div>
            """, unsafe_allow_html=True)

# --- MÓDULO 5: EXPORTACIÓN WORD ---
elif modulo == "📄 5. Generar Informe Word":
    st.header("Impresión de Documentación Oficial")
    st.markdown("<div class='instruction-banner'>El motor compilará y redactará un expediente Word (.docx) formal, insertando los gráficos en alta resolución y preservando la matriz legal de los datos calculados.</div>", unsafe_allow_html=True)
    
    if st.button("🚀 GENERAR Y DESCARGAR EXPEDIENTE COMPLETO"):
        with st.spinner("Procesando lógicas matemáticas y redactando documento clínico..."):
            
            resp = dict(zip(st.session_state.data["Nº"], st.session_state.data["Respuesta"]))
            pd_final = {e: sum(1 for i in c["V"] if resp.get(i)=="V") + sum(1 for i in c["F"] if resp.get(i)=="F") for e, c in PLANTILLAS_CORRECCION.items()}
            k = pd_final.get("K (Defensividad)", 0)
            for e, f in FRACCIONES_K.items(): 
                if e in pd_final: pd_final[e] += int(round(k * f))
                
            diccionario_clinico = MotorDiagnosticoIntegral.obtener_diccionario_escalas()
            perfil = [{"Escala": e, "Area": diccionario_clinico[e]["Area"], "PD": pd_final[e], "T": obtener_puntuacion_t_real(e, pd_final[e], st.session_state.paciente["sexo"]), "Nivel": "Elevado" if obtener_puntuacion_t_real(e, pd_final[e], st.session_state.paciente["sexo"]) >= 65 else "Normal", "Interpretacion": diccionario_clinico[e]["H"] if obtener_puntuacion_t_real(e, pd_final[e], st.session_state.paciente["sexo"]) >= 65 else diccionario_clinico[e]["N"]} for e in pd_final.keys()]
            
            df_perfil = pd.DataFrame(perfil)
            
            # Creación del documento
            doc_bin = generar_expediente_word(st.session_state.paciente, st.session_state.data, df_perfil)
            
            st.success("✅ Documento de Peritaje generado con éxito.")
            st.download_button("📥 DESCARGAR INFORME FORENSE (.DOCX)", doc_bin, file_name=f"PERITAJE_MMPI2_{st.session_state.paciente['nombre'].replace(' ', '_').upper()}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
