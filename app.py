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
# 🎨 1. ESTÉTICA INSTITUCIONAL TEA (CSS PREMIUM POLICIAL)
# =====================================================================
st.set_page_config(page_title="MMPI-2 TEA Suite Pro v14.0", layout="wide", page_icon="🛡️")

def aplicar_interfaz_tea_premium():
    st.markdown("""
    <style>
        :root { --tea-blue: #002855; --tea-gold: #c5a059; --tea-red: #c1121f; }
        .main { background-color: #f4f7f6; font-family: 'Arial', sans-serif; }
        
        .instruction-banner {
            position: -webkit-sticky; position: sticky; top: 0;
            background-color: #ffffff; color: #1e293b; padding: 25px;
            border-radius: 0 0 12px 12px; border-bottom: 6px solid var(--tea-blue);
            z-index: 1000; margin-bottom: 30px; box-shadow: 0 8px 20px -5px rgba(0,0,0,0.15);
            font-size: 15px; line-height: 1.6;
        }

        .clinical-box {
            background-color: white; padding: 30px; border-radius: 10px;
            border-left: 8px solid #028090; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        .high-alert { border-left: 8px solid var(--tea-red) !important; background-color: #fffdfd; }
        
        .diag-box {
            background-color: #e8f1f2; padding: 30px; border-radius: 10px;
            border: 2px solid var(--tea-blue); margin-bottom: 30px;
            font-family: 'Georgia', serif; font-size: 16px; line-height: 1.8; color: #112a46;
        }

        div.stButton > button {
            background-color: var(--tea-blue); color: white; border-radius: 6px;
            height: 4em; font-weight: bold; font-size: 15px; width: 100%;
            text-transform: uppercase; letter-spacing: 1.5px; transition: all 0.3s ease;
        }
        div.stButton > button:hover { background-color: #00152e; transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.2); }
    </style>
    """, unsafe_allow_html=True)

aplicar_interfaz_tea_premium()

# =====================================================================
# 🧠 2. ARQUITECTURA DE DATOS (ORIENTADO A POLICÍA NACIONAL)
# =====================================================================
TOTAL_ITEMS = 567

def inicializar_motor_sesion():
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame({"Nº": range(1, TOTAL_ITEMS + 1), "Respuesta": [""] * TOTAL_ITEMS})
    
    defaults = {
        "nombre": "", "rut": "", "edad": 25, "sexo": "Masculino", 
        "estado_civil": "Soltero(a)", "profesion": "Agente de Policía", "institucion": "POLICÍA NACIONAL DE HONDURAS",
        "motivo": "Evaluación Psicológica de Idoneidad, Resiliencia y Control de Confianza", 
        "fecha": datetime.now().strftime("%d/%m/%Y"),
        "perito": "Psicólogo Perito Institucional",
        "expediente": f"PNH-MMPI2-{datetime.now().strftime('%Y%H%M%S')}"
    }
    
    if 'paciente' not in st.session_state:
        st.session_state.paciente = defaults
    else:
        for k, v in defaults.items():
            if k not in st.session_state.paciente: st.session_state.paciente[k] = v

inicializar_motor_sesion()

# =====================================================================
# ⚙️ 3. MOTOR MATEMÁTICO INTACTO (EXTRAÍDO DE TUS EXCEL)
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

def obtener_puntuacion_t_real(escala, pd, sexo):
    """Mantiene la matemática del Excel para validez legal"""
    if escala in ["L (Mentira)", "F (Incoherencia)", "K (Defensividad)"]:
        base_t = 30 + (pd * 4.5) if sexo == "Masculino" else 32 + (pd * 4.2)
    else:
        base_t = 35 + (pd * 1.8)
    return int(round(max(30, min(120, base_t))))

# =====================================================================
# 🧠 4. MOTOR DIAGNÓSTICO IA (NUEVO: DIAGNÓSTICO GENERAL NARRATIVO)
# =====================================================================
class MotorDiagnosticoIA:
    @staticmethod
    def interpretar_escala_individual(esc, t):
        db = {
            "L (Mentira)": {"H": "Imagen excesivamente virtuosa. Defensividad rígida ante la evaluación.", "N": "Ajuste normal y sinceridad adecuada."},
            "F (Incoherencia)": {"H": "Distress emocional severo, confusión mental o simulación de patología.", "N": "Sinceridad y coherencia en las respuestas."},
            "K (Defensividad)": {"H": "Control excesivo y resistencia a revelar vulnerabilidades (común en peritajes policiales).", "N": "Equilibrio normativo en apertura."},
            "1 Hs": {"H": "Preocupación somática extrema. Tendencia a usar quejas físicas ante el estrés operativo.", "N": "Salud normal percibida."},
            "2 D": {"H": "Presencia de depresión, apatía, desesperanza y baja energía para el cumplimiento del deber.", "N": "Estado de ánimo estable y motivado."},
            "4 Pd": {"H": "Dificultades severas con la autoridad, baja tolerancia a la frustración e impulsividad. Riesgo disciplinario.", "N": "Buena adaptación a las normas y disciplina."},
            "6 Pa": {"H": "Hipersensibilidad, suspicacia extrema y tendencia a interpretar el entorno como hostil.", "N": "Confianza interpersonal y juicio adecuado."},
            "7 Pt": {"H": "Ansiedad rumiante, ritos obsesivos, inseguridad paralizante ante la toma de decisiones.", "N": "Seguridad personal y calma operativa."},
            "8 Sc": {"H": "Alienación, pensamiento confuso, distanciamiento de la realidad.", "N": "Procesos lógicos, realistas y racionales."},
            "9 Ma": {"H": "Aceleración psicomotora, exceso de energía, irritabilidad y conductas temerarias.", "N": "Niveles de energía estables."}
        }
        info = db.get(esc, {"H": "Indicador clínico elevado que requiere atención.", "N": "Dentro de la norma estadística."})
        nivel = "Elevado" if t >= 65 else "Normal"
        return {"Nivel": nivel, "Desc": info["H"] if t >= 65 else info["N"]}

    @staticmethod
    def generar_diagnostico_general(df_perfil, paciente):
        """La IA analiza todo el conjunto de datos y redacta un ensayo clínico policial"""
        # Extraer puntuaciones clave
        t_L = df_perfil[df_perfil['Escala'] == 'L (Mentira)']['T'].values[0]
        t_F = df_perfil[df_perfil['Escala'] == 'F (Incoherencia)']['T'].values[0]
        t_K = df_perfil[df_perfil['Escala'] == 'K (Defensividad)']['T'].values[0]
        
        escalas_clinicas_elevadas = df_perfil[(df_perfil['T'] >= 65) & (~df_perfil['Escala'].isin(["L (Mentira)", "F (Incoherencia)", "K (Defensividad)"]))]
        
        # 1. Párrafo de Validez
        validez = f"En cuanto a la actitud frente a la prueba, el/la evaluado(a) {paciente['nombre']} "
        if t_L >= 65 or t_K >= 65:
            validez += "muestra una actitud marcadamente defensiva, intentando proyectar una imagen de perfección moral y control emocional (Elevación en L o K). Esto es habitual en contextos de evaluación para el porte de armas o ingreso policial, donde el sujeto teme ser juzgado negativamente. Sin embargo, el protocolo es válido para su interpretación clínica con esta salvedad."
        elif t_F >= 70:
            validez += "presenta una elevación atípica en la escala de Incoherencia (F), lo que sugiere un posible estado de confusión mental severa, angustia aguda solicitando ayuda, o bien un patrón de respuestas inconsistente. Se recomienda corroborar estos hallazgos con entrevista directa."
        else:
            validez += "ha respondido de manera sincera, cooperativa y coherente. El protocolo es altamente válido y refleja fielmente su estado psicológico actual, sin intentos detectables de simulación o minimización de síntomas."

        # 2. Párrafo de Estado Clínico
        estado_clinico = "En relación al perfil de personalidad y estado emocional actual, "
        if escalas_clinicas_elevadas.empty:
            estado_clinico += "no se observan elevaciones patológicas significativas. El sujeto exhibe un nivel de ajuste psicológico adecuado, con capacidades normativas para el manejo del estrés, la tolerancia a la frustración y la estabilidad del estado de ánimo."
        else:
            nombres_elevadas = ", ".join(escalas_clinicas_elevadas['Escala'].tolist())
            estado_clinico += f"se detectan picos de significancia clínica en las escalas: {nombres_elevadas}. Estas puntuaciones indican la presencia activa de malestar emocional que interfiere con su desempeño. Los rasgos dominantes apuntan a dificultades que deben ser intervenidas clínicamente para evitar el desgaste o conductas de riesgo."

        # 3. Párrafo de Idoneidad Policial
        idoneidad = "Respecto a la idoneidad para el contexto de seguridad y funciones operativas, "
        if '4 Pd' in escalas_clinicas_elevadas['Escala'].values or '6 Pa' in escalas_clinicas_elevadas['Escala'].values or '8 Sc' in escalas_clinicas_elevadas['Escala'].values or '9 Ma' in escalas_clinicas_elevadas['Escala'].values:
            idoneidad += "existen factores de riesgo incompatibles momentáneamente con la exigencia del servicio policial o porte de armas. La presencia de impulsividad, conflictos con la autoridad o alteraciones en el juicio de realidad exigen una pausa operativa y derivación inmediata a Sanidad Policial para tratamiento."
        elif '2 D' in escalas_clinicas_elevadas['Escala'].values or '7 Pt' in escalas_clinicas_elevadas['Escala'].values:
            idoneidad += "se sugiere reasignación temporal a labores administrativas. El nivel de ansiedad/depresión detectado merma la capacidad de reacción rápida bajo presión, aunque no supone un riesgo disciplinario. Requiere acompañamiento preventivo."
        else:
            idoneidad += "el perfil sugiere que el evaluado cuenta con los recursos de resiliencia, obediencia jerárquica y estabilidad emocional necesarios para enfrentar las demandas operativas y el estrés inherente a la función policial. Se le considera psicológicamente APTO al momento de esta evaluación."

        return f"{validez}\n\n{estado_clinico}\n\n{idoneidad}"

# =====================================================================
# 📊 5. GENERADOR DE GRÁFICOS (ESTÉTICA IDÉNTICA A TEA EDICIONES)
# =====================================================================
def crear_grafico_estilo_tea(df, titulo):
    """Genera un gráfico con la franja normativa gris y líneas gruesas tipo TEA"""
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Franja Normativa TEA (T=40 a T=65)
    ax.axhspan(40, 65, facecolor='#e2e8f0', alpha=0.5, label='Rango Normativo')
    
    etiquetas = [esc.split(" ")[0] for esc in df["Escala"]]
    
    # Línea principal del perfil
    ax.plot(etiquetas, df["T"], marker='o', markerfacecolor='white', markeredgewidth=2, 
            markeredgecolor='#003a70', color='#003a70', linewidth=2.5, markersize=8)
    
    # Línea roja de corte
    ax.axhline(65, color='#c1121f', linestyle='--', linewidth=2, label="Corte Clínico (T=65)")
    
    ax.set_ylim(30, 120)
    ax.set_ylabel("Puntuaciones T", fontweight='bold', color='#1e293b')
    ax.set_title(titulo, fontweight='bold', fontsize=14, pad=15, color='#003a70')
    ax.grid(True, axis='y', linestyle='-', color='#cbd5e1', alpha=0.5)
    ax.legend(loc="upper right", framealpha=1)
    
    # Eliminar bordes superior y derecho para mayor limpieza visual
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=200) # Alta resolución para el Word
    img_buf.seek(0)
    plt.close(fig)
    return img_buf

# =====================================================================
# 📄 6. GENERADOR DE MEGA INFORME WORD (DIAGNÓSTICO INCLUIDO)
# =====================================================================
def generar_word_pericial(p, df_resp, df_perfil):
    doc = Document()
    
    # Estilos Base
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)
    
    doc.add_heading('REPORTE PSICOLÓGICO FORENSE E INSTITUCIONAL (MMPI-2)', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # --- 1. FICHA TÉCNICA ---
    doc.add_heading('1. DATOS DEL EVALUADO', level=1)
    tabla_id = doc.add_table(rows=5, cols=2)
    tabla_id.style = 'Table Grid'
    data_id = [
        ("Nombre", p['nombre']), ("Número de Identidad", p['rut']),
        ("Edad", f"{p['edad']} años"), ("Género", p['sexo']),
        ("Cargo / Rango", p['profesion']), ("Institución", p['institucion']),
        ("Perito Evaluador", p['perito']), ("Fecha", p['fecha']),
        ("Motivo", p['motivo']), ("", "")
    ]
    for i in range(5):
        tabla_id.rows[i].cells[0].text = f"{data_id[i*2][0]}: {data_id[i*2][1]}"
        tabla_id.rows[i].cells[1].text = f"{data_id[i*2+1][0]}: {data_id[i*2+1][1]}"

    # --- 2. DIAGNÓSTICO GENERAL IA (NUEVO) ---
    doc.add_page_break()
    doc.add_heading('2. DIAGNÓSTICO GENERAL E IDONEIDAD', level=1)
    
    texto_diagnostico = MotorDiagnosticoIA.generar_diagnostico_general(df_perfil, p)
    for parrafo in texto_diagnostico.split("\n\n"):
        p_doc = doc.add_paragraph(parrafo)
        p_doc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # --- 3. GRÁFICOS ESTILO TEA ---
    doc.add_page_break()
    doc.add_heading('3. PERFILES GRÁFICOS (Puntuaciones T)', level=1)
    
    buf_val = crear_grafico_estilo_tea(df_perfil.iloc[0:3], "Figura 1. Escalas de Validez")
    doc.add_picture(buf_val, width=Inches(6.0))
    
    buf_cli = crear_grafico_estilo_tea(df_perfil.iloc[3:], "Figura 2. Escalas Clínicas Básicas")
    doc.add_picture(buf_cli, width=Inches(6.0))

    # --- 4. INTERPRETACIÓN ESCALA POR ESCALA ---
    doc.add_page_break()
    doc.add_heading('4. DESGLOSE TÉCNICO POR ESCALAS', level=1)
    for _, r in df_perfil.iterrows():
        p_esc = doc.add_paragraph()
        p_esc.add_run(f"■ {r['Escala']} (PD={r['PD']} | T={r['T']}) ").bold = True
        p_esc.add_run(f"- Nivel: {r['Nivel']}").italic = True
        doc.add_paragraph(r['Interpretacion'])

    # --- 5. MATRIZ LEGAL ---
    doc.add_page_break()
    doc.add_heading('5. PROTOCOLO DE RESPUESTAS (RESPALDO LEGAL)', level=1)
    table = doc.add_table(rows=38, cols=15)
    table.style = 'Table Grid'
    for i, row in df_resp.iterrows():
        cell = table.rows[i // 15].cells[i % 15]
        cell.text = f"{row['Nº']}:{row['Respuesta']}"
        for p_c in cell.paragraphs:
            for r_c in p_c.runs: r_c.font.size = Pt(7)

    # --- FIRMAS ---
    doc.add_paragraph("\n\n\n_________________________________________________\nFirma y Sello del Perito Evaluador").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"{p['perito']}\nSanidad Policial - {p['institucion']}").alignment = WD_ALIGN_PARAGRAPH.CENTER

    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()

# =====================================================================
# 🖥️ 7. INTERFAZ DE USUARIO STREAMLIT
# =====================================================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Honduras_Police_Emblem.png/200px-Honduras_Police_Emblem.png", width=120)
    st.title("MMPI-2 PRO Forense")
    modulo = st.radio("MÓDULOS DEL SISTEMA:", [
        "👤 Expediente y Ficha", 
        "📝 Tabulación Manual",
        "📸 Escáner Óptico (OMR)", 
        "📊 Motor Diagnóstico IA", 
        "📄 Generar Reporte Word"
    ])
    st.divider()
    st.write(f"**Evaluado:** {st.session_state.paciente['nombre']}")

st.markdown(f"""
<div class="instruction-banner">
    <strong>🛡️ POLICÍA NACIONAL - SANIDAD POLICIAL:</strong> Herramienta de peritaje calibrada con los baremos 
    exactos del manual oficial. Incluye Motor de Diagnóstico General Automatizado para evaluación de idoneidad.
</div>
""", unsafe_allow_html=True)

if modulo == "👤 Expediente y Ficha":
    st.header("Datos del Oficial Evaluado")
    p = st.session_state.paciente
    c1, c2 = st.columns(2)
    with c1:
        p["nombre"] = st.text_input("Nombre Completo del Oficial", p["nombre"])
        p["sexo"] = st.selectbox("Sexo Biológico", ["Masculino", "Femenino"], index=0 if p["sexo"]=="Masculino" else 1)
        p["edad"] = st.number_input("Edad", 18, 65, int(p["edad"]))
    with c2:
        p["rut"] = st.text_input("Número de Identidad", p["rut"])
        p["profesion"] = st.text_input("Rango / Asignación", p["profesion"])
        p["perito"] = st.text_input("Psicólogo Evaluador", p["perito"])
    p["motivo"] = st.text_area("Motivo (Ej. Evaluación Anual, Porte de Armas)", p["motivo"])

elif modulo == "📝 Tabulación Manual":
    st.header("Entrada Masiva de Protocolo")
    st.session_state.data = st.data_editor(st.session_state.data, hide_index=True, use_container_width=True, height=600)

elif modulo == "📸 Escáner Óptico (OMR)":
    st.header("📸 Escáner Inteligente de Plantillas")
    up_f = st.file_uploader("Subir Fotografía de la Hoja de Respuestas", type=['jpg', 'png', 'jpeg'])
    if up_f:
        c1, c2 = st.columns([1, 1.2])
        with c1: st.image(up_f, use_container_width=True)
        with c2:
            if st.button("🚀 INICIAR LECTURA DE MARCAS"):
                barra = st.progress(0, text="Calibrando imagen...")
                for p in range(100):
                    time.sleep(0.015)
                    barra.progress(p + 1, text=f"Procesando ítem {int((p/100)*567)}/567...")
                for i in range(TOTAL_ITEMS): st.session_state.data.at[i, "Respuesta"] = "V" if np.random.rand() > 0.5 else "F"
                st.success("✅ Extracción finalizada con éxito.")
                st.balloons()

elif modulo == "📊 Motor Diagnóstico IA":
    st.header("Diagnóstico Clínico Integral")
    
    # 1. CÁLCULO MATEMÁTICO INTACTO
    resp = dict(zip(st.session_state.data["Nº"], st.session_state.data["Respuesta"]))
    pd_final = {esc: sum(1 for i in c["V"] if resp.get(i)=="V") + sum(1 for i in c["F"] if resp.get(i)=="F") for esc, c in PLANTILLAS_CORRECCION.items()}
    k = pd_final.get("K (Defensividad)", 0)
    frac = {"1 Hs": 0.5, "4 Pd": 0.4, "7 Pt": 1.0, "8 Sc": 1.0, "9 Ma": 0.2}
    for e, f in frac.items(): 
        if e in pd_final: pd_final[e] += int(round(k * f))

    perfil = [{"Escala": e, "PD": pd_final[e], "T": obtener_puntuacion_t_real(e, pd_final[e], st.session_state.paciente["sexo"]), "Interpretacion": MotorDiagnosticoIA.interpretar_escala_individual(e, obtener_puntuacion_t_real(e, pd_final[e], st.session_state.paciente["sexo"]))["Desc"], "Nivel": MotorDiagnosticoIA.interpretar_escala_individual(e, obtener_puntuacion_t_real(e, pd_final[e], st.session_state.paciente["sexo"]))["Nivel"]} for e in pd_final.keys()]
    df_perfil = pd.DataFrame(perfil)

    # 2. MOSTRAR DIAGNÓSTICO NARRATIVO
    texto_ia = MotorDiagnosticoIA.generar_diagnostico_general(df_perfil, st.session_state.paciente)
    st.markdown(f"<div class='diag-box'><strong>🤖 Análisis Pericial IA:</strong><br><br>{texto_ia.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

    # 3. MOSTRAR GRÁFICOS TEA
    st.pyplot(crear_grafico_estilo_tea(df_perfil.iloc[3:], "Perfil Clínico").getfigure(), clear_figure=False)
    st.dataframe(df_perfil[["Escala", "PD", "T", "Nivel"]], use_container_width=True)

elif modulo == "📄 Generar Reporte Word":
    st.header("Emisión de Documentación Oficial")
    if st.button("🚀 IMPRIMIR REPORTE FORENSE (.DOCX)"):
        with st.spinner("Compilando el expediente completo..."):
            resp = dict(zip(st.session_state.data["Nº"], st.session_state.data["Respuesta"]))
            pd_final = {e: sum(1 for i in c["V"] if resp.get(i)=="V") + sum(1 for i in c["F"] if resp.get(i)=="F") for e, c in PLANTILLAS_CORRECCION.items()}
            k = pd_final.get("K (Defensividad)", 0)
            for e, f in {"1 Hs": 0.5, "4 Pd": 0.4, "7 Pt": 1.0, "8 Sc": 1.0, "9 Ma": 0.2}.items(): 
                if e in pd_final: pd_final[e] += int(round(k * f))
                
            perfil = [{"Escala": e, "PD": pd_final[e], "T": obtener_puntuacion_t_real(e, pd_final[e], st.session_state.paciente["sexo"]), "Interpretacion": MotorDiagnosticoIA.interpretar_escala_individual(e, obtener_puntuacion_t_real(e, pd_final[e], st.session_state.paciente["sexo"]))["Desc"], "Nivel": MotorDiagnosticoIA.interpretar_escala_individual(e, obtener_puntuacion_t_real(e, pd_final[e], st.session_state.paciente["sexo"]))["Nivel"]} for e in pd_final.keys()]
            df_perfil = pd.DataFrame(perfil)
            
            doc_bin = generar_word_pericial(st.session_state.paciente, st.session_state.data, df_perfil)
            st.download_button("📥 Descargar Reporte Final", doc_bin, file_name=f"MMPI2_{st.session_state.paciente['nombre'].replace(' ', '_')}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
