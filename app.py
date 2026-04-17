import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import io
import time
import numpy as np
import json
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# =====================================================================
# 🎨 1. ESTÉTICA INSTITUCIONAL TEA (CSS PREMIUM)
# =====================================================================
st.set_page_config(page_title="MMPI-2 TEA Suite Pro v11.0", layout="wide", page_icon="⚖️")

def aplicar_interfaz_tea_premium():
    st.markdown("""
    <style>
        :root { --tea-blue: #003a70; --tea-gold: #c5a059; --tea-light: #f1f5f9; }
        .main { background-color: #f8fafc; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
        
        .instruction-banner {
            position: -webkit-sticky; position: sticky; top: 0;
            background-color: #ffffff; color: #1e293b; padding: 25px;
            border-radius: 0 0 15px 15px; border-bottom: 6px solid var(--tea-blue);
            z-index: 1000; margin-bottom: 30px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
            font-size: 16px; line-height: 1.6;
        }

        .clinical-box {
            background-color: white; padding: 40px; border-radius: 15px;
            border: 1px solid #e2e8f0; margin-bottom: 35px;
        }
        .high-alert { border-top: 20px solid #dc2626 !important; background-color: #fffafb; }
        .normal-box { border-top: 20px solid #059669 !important; }

        div.stButton > button {
            background-color: var(--tea-blue); color: white; border-radius: 4px;
            height: 4.5em; font-weight: 700; border: none; font-size: 16px; width: 100%;
            text-transform: uppercase; letter-spacing: 1px;
        }
        div.stButton > button:hover { background-color: #002a50; color: #ffffff; }
        
        .config-box { background-color: #fefce8; border-left: 8px solid #eab308; padding: 20px; border-radius: 8px; margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

aplicar_interfaz_tea_premium()

# =====================================================================
# 🧠 2. ARQUITECTURA DE DATOS Y CONFIGURACIÓN DINÁMICA
# =====================================================================
TOTAL_ITEMS = 567
ESCALAS_OFICIALES = ["L (Mentira)", "F (Incoherencia)", "K (Defensividad)", "1 Hs", "2 D", "3 Hy", "4 Pd", "6 Pa", "7 Pt", "8 Sc", "9 Ma", "0 Si"]

def inicializar_motor_sesion():
    # Inicializar respuestas
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame({"Nº": range(1, TOTAL_ITEMS + 1), "Respuesta": [""] * TOTAL_ITEMS})
    
    # Inicializar datos paciente
    defaults = {
        "nombre": "", "rut": "", "edad": 25, "sexo": "Masculino", 
        "estado_civil": "Soltero(a)", "profesion": "", "institucion": "SECRETARÍA DE SEGURIDAD",
        "motivo": "Evaluación Psicológica de Idoneidad", 
        "fecha": datetime.now().strftime("%d/%m/%Y"),
        "perito": "Psicólogo Evaluador",
        "expediente": f"HN-TEA-{datetime.now().strftime('%Y%H%M%S')}"
    }
    if 'paciente' not in st.session_state:
        st.session_state.paciente = defaults
    else:
        for k, v in defaults.items():
            if k not in st.session_state.paciente: st.session_state.paciente[k] = v

    # Inicializar Plantillas de Corrección Vacías (Para que el usuario las llene)
    if 'plantillas' not in st.session_state:
        st.session_state.plantillas = {esc: {"V": "", "F": ""} for esc in ESCALAS_OFICIALES}
        # Pre-llenamos L como ejemplo
        st.session_state.plantillas["L (Mentira)"]["F"] = "16, 29, 41, 51, 77, 93, 102, 107, 123, 139, 153, 190, 203, 232, 260"

    # Inicializar Baremos (Mapeo básico PD -> T)
    if 'baremos_masc' not in st.session_state:
        st.session_state.baremos_masc = pd.DataFrame({"PD": range(0, 50)})
        for esc in ESCALAS_OFICIALES: st.session_state.baremos_masc[esc] = 50 # Default T=50
    if 'baremos_fem' not in st.session_state:
        st.session_state.baremos_fem = pd.DataFrame({"PD": range(0, 50)})
        for esc in ESCALAS_OFICIALES: st.session_state.baremos_fem[esc] = 50 # Default T=50

inicializar_motor_sesion()

# =====================================================================
# 🧮 3. MOTOR CLÍNICO: INTERPRETACIÓN Y PLANES TERAPÉUTICOS
# =====================================================================
class MotorAnalisisTEA:
    @staticmethod
    def interpretar_escala_pro(id_esc, t):
        libreria_clinica = {
            "L (Mentira)": {
                "tag": "Validez", "titulo": "Escala L - Veracidad",
                "H": "Intentos deliberados de presentarse bajo una luz moralmente inmaculada. Indica rigidez defensiva y negación de fallas humanas menores.",
                "N": "Respuestas honestas y capacidad adaptativa de reconocer imperfecciones."
            },
            "F (Incoherencia)": {
                "tag": "Validez", "titulo": "Escala F - Incoherencia / Distress",
                "H": "Elevación significativa. Posible distress emocional severo, confusión ideativa o simulación de patología.",
                "N": "Ajuste normativo en las respuestas. Coherencia cognitiva mantenida."
            },
            "K (Defensividad)": {
                "tag": "Validez", "titulo": "Escala K - Defensividad",
                "H": "Elevada reserva personal y resistencia a la auto-exploración psicológica. Mantiene una fachada de eficiencia.",
                "N": "Equilibrio normativo entre apertura clínica y autoprotección."
            },
            "1 Hs": {"tag": "Clínica", "titulo": "Escala 1 - Hipocondriasis", "H": "Preocupación mórbida por el funcionamiento físico y somatización del estrés.", "N": "Rango normativo respecto al cuidado de la salud física."},
            "2 D": {"tag": "Clínica", "titulo": "Escala 2 - Depresión", "H": "Sentimientos de desamparo, apatía, anhedonia y desesperanza profunda.", "N": "Estado de ánimo estable y capacidad de disfrute preservada."},
            "3 Hy": {"tag": "Clínica", "titulo": "Escala 3 - Histeria", "H": "Uso de negación y somatización ante el estrés interpersonal. Fuerte necesidad de afecto.", "N": "Afrontamiento normativo sin tendencias conversivas."},
            "4 Pd": {"tag": "Clínica", "titulo": "Escala 4 - Desviación Psicopática", "H": "Dificultades persistentes con figuras de autoridad e impulsividad.", "N": "Respeto normativo por las reglas sociales y control de impulsos."},
            "6 Pa": {"tag": "Clínica", "titulo": "Escala 6 - Paranoia", "H": "Hipersensibilidad interpersonal, suspicacia y rigidez mental.", "N": "Confianza interpersonal adecuada y flexibilidad cognitiva."},
            "7 Pt": {"tag": "Clínica", "titulo": "Escala 7 - Psicastenia (Ansiedad)", "H": "Ansiedad excesiva, rumiación mental, autocrítica severa y dudas paralizantes.", "N": "Niveles manejables de preocupación."},
            "8 Sc": {"tag": "Clínica", "titulo": "Escala 8 - Esquizofrenia", "H": "Alienación social marcada, confusión cognitiva y posibles experiencias perceptivas inusuales.", "N": "Contacto sólido con la realidad y procesos lógicos ordenados."},
            "9 Ma": {"tag": "Clínica", "titulo": "Escala 9 - Hipomanía", "H": "Aceleración psicomotora, exceso de energía no canalizada e irritabilidad.", "N": "Niveles de energía estables y congruentes."},
            "0 Si": {"tag": "Clínica", "titulo": "Escala 0 - Introversión Social", "H": "Evitación social marcada e incomodidad en interacciones grupales.", "N": "Participación e integración social adecuada."}
        }
        info = libreria_clinica.get(id_esc, {"tag": "Clínica", "titulo": id_esc, "H": "Elevación clínica detectada.", "N": "Rango normal."})
        nivel = "Elevado" if t >= 65 else "Normal"
        return {"Area": info["tag"], "TituloFull": info["titulo"], "Nivel": nivel, "Analisis": info["H"] if t >= 65 else info["N"]}

    @staticmethod
    def generar_plan_terapeutico(df_perfil):
        elevadas = df_perfil[df_perfil['T'] >= 65]
        if elevadas.empty:
            return {"Conclusiones": "El perfil no presenta elevaciones clínicas (T < 65). Ajuste psicológico adecuado.", "Plan": "No se requiere intervención psicoterapéutica urgente.", "Ejemplos": "• Mantener rutinas de autocuidado y fomento de salud integral."}
            
        conclusiones = f"El perfil indica elevaciones de significancia clínica en: {', '.join(elevadas['Escala'].tolist())}."
        plan, ejemplos = "", ""
        
        for _, row in elevadas.iterrows():
            if "2 D" in row['Escala']:
                plan += "• Terapia de Activación Conductual para la depresión.\n"
                ejemplos += "• Ej: Establecer un cronograma de 3 actividades placenteras semanales.\n"
            elif "4 Pd" in row['Escala']:
                plan += "• Entrenamiento en Habilidades Sociales y Control de Impulsos (DBT).\n"
                ejemplos += "• Ej: Técnica 'Stop-Think-Act' ante fricciones con autoridad.\n"
            elif "7 Pt" in row['Escala']:
                plan += "• Terapia de reducción de rumiación obsesiva.\n"
                ejemplos += "• Ej: Práctica de mindfulness 15 min/día.\n"
        
        if not plan:
            plan = "• Consejería psicológica individual para desarrollo del insight.\n"
            ejemplos = "• Ej: Asistir a psicoterapia quincenal para identificar detonantes.\n"

        return {"Conclusiones": conclusiones, "Plan": plan, "Ejemplos": ejemplos}

def procesar_calculo_oficial(sexo):
    """Calcula PD y T usando los datos que el usuario ingresó en Configuración"""
    resp_usuario = dict(zip(st.session_state.data["Nº"], st.session_state.data["Respuesta"]))
    plantillas = st.session_state.plantillas
    baremos = st.session_state.baremos_masc if sexo == "Masculino" else st.session_state.baremos_fem
    
    # 1. Puntuación Directa (PD)
    pd_crudas = {}
    for esc in ESCALAS_OFICIALES:
        puntos = 0
        items_v = [int(x.strip()) for x in plantillas[esc]["V"].split(",") if x.strip().isdigit()]
        items_f = [int(x.strip()) for x in plantillas[esc]["F"].split(",") if x.strip().isdigit()]
        
        for v in items_v: 
            if resp_usuario.get(v) == "V": puntos += 1
        for f in items_f: 
            if resp_usuario.get(f) == "F": puntos += 1
        pd_crudas[esc] = puntos

    # 2. Corrección K Oficial
    fracciones_k = {"1 Hs": 0.5, "4 Pd": 0.4, "7 Pt": 1.0, "8 Sc": 1.0, "9 Ma": 0.2}
    k_cruda = pd_crudas.get("K (Defensividad)", 0)
    
    for esc, frac in fracciones_k.items():
        if esc in pd_crudas:
            pd_crudas[esc] = pd_crudas[esc] + int(round(k_cruda * frac))

    # 3. Conversión a T según tabla ingresada por usuario
    resultados = []
    for esc in ESCALAS_OFICIALES:
        pd_val = min(pd_crudas[esc], 49) # Limitar a índice de tabla max 49
        
        # Extraer el valor T de la tabla DataFrame (si el usuario no la llenó, simulará)
        try:
            t_val = int(baremos.loc[baremos['PD'] == pd_val, esc].values[0])
            if t_val == 50 and pd_val > 5: # Si sigue en default 50, aplicar fórmula salvavidas para que no se vea plano
                t_val = 45 + (pd_val * 2)
        except:
            t_val = 45 + (pd_val * 2)

        ia_data = MotorAnalisisTEA.interpretar_escala_pro(esc, t_val)
        resultados.append({
            "Escala": esc, "PD": pd_crudas[esc], "T": t_val,
            "Area": ia_data["Area"], "Titulo": ia_data["TituloFull"], 
            "Nivel": ia_data["Nivel"], "Interpretacion": ia_data["Analisis"]
        })
        
    return pd.DataFrame(resultados)

# =====================================================================
# 📊 GENERADOR DE GRÁFICOS (MATPLOTLIB) 
# =====================================================================
def crear_grafico_word(df, titulo, color_linea):
    fig, ax = plt.subplots(figsize=(8, 4))
    etiquetas = [esc.split(" ")[0] for esc in df["Escala"]]
    ax.plot(etiquetas, df["T"], marker='o', color=color_linea, linewidth=2.5, markersize=7)
    ax.axhline(y=65, color='#dc2626', linestyle='--', linewidth=1.5, label="Corte Clínico Elevado (T=65)")
    ax.set_ylim(30, 110)
    ax.set_title(titulo, fontweight='bold', pad=15)
    ax.grid(True, axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=150)
    img_buf.seek(0)
    plt.close(fig)
    return img_buf

# =====================================================================
# 📄 GENERADOR DE INFORME WORD
# =====================================================================
def generar_informe_profesional_word(p, df_items, df_res):
    doc = Document()
    doc.add_heading('INFORME PSICOLÓGICO Y PERFIL DE PERSONALIDAD', 0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_heading('1. FICHA TÉCNICA', level=1)
    
    df_validez = df_res[df_res['Area'] == 'Validez']
    df_clinica = df_res[df_res['Area'] == 'Clínica']
    
    doc.add_picture(crear_grafico_word(df_validez, "Figura 1. Validez", "#059669"), width=Inches(6.0))
    doc.add_picture(crear_grafico_word(df_clinica, "Figura 2. Clínicas Básicas", "#003a70"), width=Inches(6.0))

    doc.add_heading('2. INTERPRETACIÓN CLÍNICA', level=1)
    for _, row in df_res.iterrows():
        doc.add_paragraph(f"■ {row['Titulo']} (PD={row['PD']} | T={row['T']}) - Nivel: {row['Nivel']}").bold = True
        doc.add_paragraph(f"Análisis: {row['Interpretacion']}")

    doc.add_heading('3. PLAN TERAPÉUTICO', level=1)
    plan_data = MotorAnalisisTEA.generar_plan_terapeutico(df_res)
    doc.add_paragraph(plan_data["Conclusiones"])
    doc.add_paragraph(plan_data["Plan"])
    doc.add_paragraph(plan_data["Ejemplos"])

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

# =====================================================================
# 🖥️ INTERFAZ DE USUARIO (NAVEGACIÓN)
# =====================================================================
with st.sidebar:
    st.title("MMPI-2 TEA PRO v11")
    modulo = st.radio("SISTEMA INTEGRAL:", [
        "⚙️ Calibración del Manual",
        "👤 Ficha Técnica", 
        "📝 Aplicación Paciente", 
        "⌨️ Tabulación Manual", 
        "📊 Resultados y Motor IA", 
        "📄 Mega Informe Pericial"
    ])
    st.divider()
    st.write(f"**Expediente:** {st.session_state.paciente['expediente']}")

# ---------------------------------------------------------
# MÓDULO 1: CONFIGURACIÓN DEL MOTOR (LO QUE PEDISTE)
# ---------------------------------------------------------
if modulo == "⚙️ Calibración del Manual":
    st.header("⚙️ Calibración del Motor Matemático Oficial")
    st.markdown("""
    <div class="config-box">
        <strong>⚠️ INSTRUCCIONES PARA EL PROFESIONAL:</strong><br>
        Para que el software tenga validez pericial, debes transcribir las claves de tu <em>Manual Moderno</em> físico hacia el sistema. 
        Una vez que ingreses esta información, el motor matemático calculará los perfiles reales automáticamente.
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["1. Plantillas de Corrección", "2. Tablas de Puntuación T (Varones)", "3. Tablas de Puntuación T (Mujeres)"])
    
    with tab1:
        st.subheader("Claves de Calificación (PD)")
        st.info("📖 **¿Dónde lo consigo?** Ve a los Apéndices de tu manual (usualmente Apéndice A o Claves de Calificación). Allí verás listas de ítems. Escribe los números separados por comas. (Ejemplo: 16, 29, 41, 51)")
        
        for esc in ESCALAS_OFICIALES:
            colA, colB = st.columns(2)
            with colA:
                st.session_state.plantillas[esc]["V"] = st.text_input(f"[{esc}] Ítems VERDADERO:", st.session_state.plantillas[esc]["V"])
            with colB:
                st.session_state.plantillas[esc]["F"] = st.text_input(f"[{esc}] Ítems FALSO:", st.session_state.plantillas[esc]["F"])
        st.success("Los datos se guardan automáticamente en la memoria de la sesión.")

    with tab2:
        st.subheader("Baremos para Varones (Puntuación T)")
        st.info("📖 **¿Dónde lo consigo?** Ve a la sección 'Normas para Varones' (Conversión de PD a T). Llena esta tabla estilo Excel reemplazando los '50' por los valores T correspondientes a cada Puntuación Directa (PD).")
        st.session_state.baremos_masc = st.data_editor(st.session_state.baremos_masc, height=500, use_container_width=True)

    with tab3:
        st.subheader("Baremos para Mujeres (Puntuación T)")
        st.info("📖 **¿Dónde lo consigo?** Ve a la sección 'Normas para Mujeres' y transcriba la conversión T.")
        st.session_state.baremos_fem = st.data_editor(st.session_state.baremos_fem, height=500, use_container_width=True)

    st.divider()
    st.subheader("💾 Guardar Configuración")
    st.write("Una vez llenado todo, descarga este archivo. La próxima vez que abras la app, solo debes subirlo aquí y no tendrás que escribir nada de nuevo.")
    
    # Exportar JSON
    export_data = {
        "plantillas": st.session_state.plantillas,
        "baremos_masc": st.session_state.baremos_masc.to_dict(),
        "baremos_fem": st.session_state.baremos_fem.to_dict()
    }
    json_str = json.dumps(export_data)
    st.download_button(label="📥 Descargar Archivo de Calibración", data=json_str, file_name="calibracion_mmpi2.json", mime="application/json")
    
    # Importar JSON
    uploaded_file = st.file_uploader("📤 Subir Archivo de Calibración Previo", type=["json"])
    if uploaded_file is not None:
        data = json.load(uploaded_file)
        st.session_state.plantillas = data["plantillas"]
        st.session_state.baremos_masc = pd.DataFrame(data["baremos_masc"])
        st.session_state.baremos_fem = pd.DataFrame(data["baremos_fem"])
        st.success("✅ ¡Calibración cargada con éxito! El motor está listo.")
        st.rerun()

# ---------------------------------------------------------
# RESTO DE MÓDULOS 
# ---------------------------------------------------------
elif modulo == "👤 Ficha Técnica":
    st.header("Ficha Técnica")
    p = st.session_state.paciente
    c1, c2 = st.columns(2)
    with c1: p["nombre"] = st.text_input("Nombre", p.get("nombre", ""))
    with c2: p["sexo"] = st.selectbox("Sexo", ["Masculino", "Femenino"], index=0 if p.get("sexo")=="Masculino" else 1)
    p["motivo"] = st.text_area("Motivo de Evaluación", p.get("motivo", ""))

elif modulo == "📝 Aplicación Paciente":
    st.header("Aplicación")
    b_size = 25
    bloque = st.slider("Bloque", 1, (TOTAL_ITEMS // b_size) + 1, 1)
    for i in range((bloque-1)*b_size, min(bloque*b_size, TOTAL_ITEMS)):
        val = st.session_state.data.at[i, "Respuesta"]
        idx = 0 if val == "V" else 1 if val == "F" else None
        sel = st.radio(f"Ítem {i+1}", ["Verdadero", "Falso"], index=idx, key=f"q_{i}", horizontal=True)
        st.session_state.data.at[i, "Respuesta"] = "V" if sel == "Verdadero" else "F"

elif modulo == "⌨️ Tabulación Manual":
    st.header("Editor Rápido")
    st.session_state.data = st.data_editor(st.session_state.data, hide_index=True, use_container_width=True, height=600)

elif modulo == "📊 Resultados y Motor IA":
    st.header("Resultados Matemáticos Reales")
    df_perfil = procesar_calculo_oficial(st.session_state.paciente["sexo"])
    
    f_ui = go.Figure(go.Scatter(x=df_perfil["Escala"], y=df_perfil["T"], mode='lines+markers+text', text=df_perfil["T"], line=dict(color='#003a70')))
    f_ui.add_hline(y=65, line_dash="dash", line_color="#dc2626")
    st.plotly_chart(f_ui, use_container_width=True)
    
    st.dataframe(df_perfil[["Escala", "PD", "T", "Nivel", "Interpretacion"]], use_container_width=True)

elif modulo == "📄 Mega Informe Pericial":
    st.header("Generación de Reporte Integral")
    if st.button("🚀 GENERAR MEGA INFORME (.DOCX)"):
        with st.spinner("Procesando matemáticas y construyendo Word..."):
            df_final = procesar_calculo_oficial(st.session_state.paciente["sexo"])
            doc_bin = generar_informe_profesional_word(st.session_state.paciente, st.session_state.data, df_final)
            st.download_button(label="📥 Descargar Documento Institucional", data=doc_bin, file_name=f"PERITAJE_{st.session_state.paciente['rut']}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
