import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# =====================================================================
# 🛠️ CONFIGURACIÓN DE PÁGINA Y CSS PERSONALIZADO
# =====================================================================
st.set_page_config(page_title="MMPI-2 Pro Suite", layout="wide", page_icon="🧠")

# CSS para mejorar la estética de los botones, métricas y fondo
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        border: 1px solid #1f77b4;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #1f77b4;
        color: white;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        font-weight: 700;
        margin-bottom: 0;
    }
    .sub-header {
        color: #7f8c8d;
        font-size: 1.2rem;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 🧠 INICIALIZACIÓN DE DATOS GLOBALES (SESSION STATE)
# =====================================================================
TOTAL_ITEMS = 567

if 'paciente' not in st.session_state:
    st.session_state.paciente = {"nombre": "", "edad": 25, "sexo": "Masculino", "fecha": datetime.today().strftime('%Y-%m-%d')}

if 'respuestas_df' not in st.session_state:
    # Generamos los 567 ítems (agregando algunos reales de ejemplo para contexto)
    preguntas_ejemplo = [
        "Me gustan las revistas de mecánica.", "Tengo buen apetito.", 
        "Me despierto fresco y descansado casi todas las mañanas.", 
        "Creo que me gustaría el trabajo de bibliotecario.", "El ruido me despierta fácilmente."
    ]
    textos = preguntas_ejemplo + [f"Ítem del cuadernillo número {i}" for i in range(6, TOTAL_ITEMS + 1)]
    
    st.session_state.respuestas_df = pd.DataFrame({
        "Ítem": range(1, TOTAL_ITEMS + 1),
        "Pregunta": textos,
        "Respuesta": [""] * TOTAL_ITEMS
    })

if 'pagina_paciente' not in st.session_state:
    st.session_state.pagina_paciente = 0

# =====================================================================
# 🧮 LÓGICA DE CORRECCIÓN CLÍNICA (MOTOR CENTRAL)
# =====================================================================
def calcular_perfil_clinico(df):
    resp_dict = dict(zip(df["Ítem"], df["Respuesta"]))
    
    # Estadísticas base
    omitidas = sum(1 for r in resp_dict.values() if r == "")
    total_v = sum(1 for r in resp_dict.values() if r == "V")
    total_f = sum(1 for r in resp_dict.values() if r == "F")
    
    # Claves (Simuladas para estructura, debes poner las reales del manual)
    claves = {
        "L (Mentira)": {"V": [15], "F": [16, 29, 41, 51, 77, 93, 102, 107, 123]},
        "F (Incoherencia)": {"V": [14, 23, 31, 38, 48, 56], "F": [174, 192, 210]}, 
        "K (Defensividad)": {"V": [83, 96, 122, 127], "F": [29, 37, 58, 76]},
        "1 Hs (Hipocondriasis)": {"V": [11, 18, 28, 39], "F": [2, 3, 9, 10]},
        "2 D (Depresión)": {"V": [5, 15, 18, 25], "F": [2, 8, 9, 10]},
        "3 Hy (Histeria)": {"V": [10, 23, 32, 41], "F": [15, 18, 19, 26]},
        "4 Pd (Desv. Psicopática)": {"V": [17, 21, 22, 31], "F": [9, 12, 34]},
        "5 Mf (Masc/Fem)": {"V": [4, 69, 70], "F": [1, 78, 80]},
        "6 Pa (Paranoia)": {"V": [16, 24, 27], "F": [280, 290]},
        "7 Pt (Psicastenia)": {"V": [11, 16, 23, 31], "F": [3, 9, 33]},
        "8 Sc (Esquizofrenia)": {"V": [16, 17, 21, 22], "F": [6, 9, 12]},
        "9 Ma (Hipomanía)": {"V": [13, 15, 23, 24], "F": [107, 153]},
        "0 Si (Introversión)": {"V": [31, 56, 73], "F": [21, 54]}
    }
    
    resultados = []
    k_valor = 0
    
    for escala, items in claves.items():
        pd_val = sum(1 for i in items["V"] if resp_dict.get(i) == "V")
        pd_val += sum(1 for i in items["F"] if resp_dict.get(i) == "F")
        if escala.startswith("K"): k_valor = pd_val
        resultados.append({"Escala": escala, "PD": pd_val, "PD_K": pd_val, "T": 0})
        
    df_res = pd.DataFrame(resultados).set_index("Escala")

    # Fracciones de K
    if k_valor > 0:
        if "1 Hs (Hipocondriasis)" in df_res.index: df_res.at["1 Hs (Hipocondriasis)", "PD_K"] += round(0.5 * k_valor)
        if "4 Pd (Desv. Psicopática)" in df_res.index: df_res.at["4 Pd (Desv. Psicopática)", "PD_K"] += round(0.4 * k_valor)
        if "7 Pt (Psicastenia)" in df_res.index: df_res.at["7 Pt (Psicastenia)", "PD_K"] += round(1.0 * k_valor)
        if "8 Sc (Esquizofrenia)" in df_res.index: df_res.at["8 Sc (Esquizofrenia)", "PD_K"] += round(1.0 * k_valor)
        if "9 Ma (Hipomanía)" in df_res.index: df_res.at["9 Ma (Hipomanía)", "PD_K"] += round(0.2 * k_valor)

    # Conversión a T (Fórmula lineal para demo, requiere CSV de baremos en producción)
    for index, row in df_res.iterrows():
        df_res.at[index, "T"] = min(max(round((row["PD_K"] * 2.2) + 40), 30), 120)

    return df_res.reset_index(), omitidas, total_v, total_f

# =====================================================================
# 🖥️ ESTRUCTURA DE NAVEGACIÓN (SIDEBAR)
# =====================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2906/2906274.png", width=100)
    st.markdown("<h2 style='text-align: center; color: #2c3e50;'>MMPI-2 Pro</h2>", unsafe_allow_html=True)
    st.divider()
    
    menu = st.radio("Navegación", [
        "👤 1. Ficha del Paciente", 
        "💻 2. Auto-llenado (Paciente)", 
        "⚡ 3. Captura Cuadrícula (Clínico)", 
        "📈 4. Dashboard Clínico",
        "📄 5. Generar Informe Word"
    ])
    
    st.divider()
    st.caption("Progreso de Evaluación")
    respondidas = TOTAL_ITEMS - st.session_state.respuestas_df['Respuesta'].eq("").sum()
    st.progress(respondidas / TOTAL_ITEMS)
    st.write(f"**{respondidas} / {TOTAL_ITEMS} ítems** completados.")

# =====================================================================
# VISTA 1: FICHA DEL PACIENTE
# =====================================================================
if menu == "👤 1. Ficha del Paciente":
    st.markdown("<h1 class='main-header'>Ficha de Identificación</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Ingrese los datos demográficos para el cálculo de baremos.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.paciente["nombre"] = st.text_input("Nombre Completo / Código", st.session_state.paciente["nombre"])
        st.session_state.paciente["edad"] = st.number_input("Edad", 18, 99, st.session_state.paciente["edad"])
    with col2:
        st.session_state.paciente["sexo"] = st.selectbox("Sexo Biológico (Baremos)", ["Masculino", "Femenino"], index=0 if st.session_state.paciente["sexo"]=="Masculino" else 1)
        st.session_state.paciente["fecha"] = st.date_input("Fecha de Evaluación", datetime.strptime(st.session_state.paciente["fecha"], '%Y-%m-%d')).strftime('%Y-%m-%d')
    
    st.success("Datos actualizados correctamente en la memoria del sistema.")

# =====================================================================
# VISTA 2: AUTO-LLENADO (PACIENTE)
# =====================================================================
elif menu == "💻 2. Auto-llenado (Paciente)":
    st.markdown("<h1 class='main-header'>Evaluación Psicológica</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Lea cada afirmación y seleccione la opción que mejor le describa.</p>", unsafe_allow_html=True)
    
    ITEMS_PAG = 50
    inicio = st.session_state.pagina_paciente * ITEMS_PAG
    fin = min(inicio + ITEMS_PAG, TOTAL_ITEMS)
    
    for i in range(inicio, fin):
        num_item = st.session_state.respuestas_df.at[i, "Ítem"]
        pregunta = st.session_state.respuestas_df.at[i, "Pregunta"]
        resp_actual = st.session_state.respuestas_df.at[i, "Respuesta"]
        
        idx = 0 if resp_actual == "V" else 1 if resp_actual == "F" else None
        
        # Tarjeta visual para cada pregunta
        with st.container():
            st.markdown(f"**{num_item}. {pregunta}**")
            seleccion = st.radio(
                "Opciones", ["Verdadero", "Falso"], index=idx, key=f"q_{num_item}", horizontal=True, label_visibility="collapsed"
            )
            st.divider()
            
            if seleccion == "Verdadero": st.session_state.respuestas_df.at[i, "Respuesta"] = "V"
            elif seleccion == "Falso": st.session_state.respuestas_df.at[i, "Respuesta"] = "F"

    # Controles de navegación
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.session_state.pagina_paciente > 0:
            if st.button("⬅️ Página Anterior"): st.session_state.pagina_paciente -= 1; st.rerun()
    with c2:
        st.markdown(f"<p style='text-align: center; color: gray;'>Página {st.session_state.pagina_paciente + 1} de {(TOTAL_ITEMS // ITEMS_PAG) + 1}</p>", unsafe_allow_html=True)
    with c3:
        if fin < TOTAL_ITEMS:
            if st.button("Siguiente Página ➡️"): st.session_state.pagina_paciente += 1; st.rerun()
        else:
            st.success("Cuestionario Finalizado")

# =====================================================================
# VISTA 3: CAPTURA EN CUADRÍCULA (CLÍNICO)
# =====================================================================
elif menu == "⚡ 3. Captura Cuadrícula (Clínico)":
    st.markdown("<h1 class='main-header'>Transcriptor Rápido</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Herramienta para tabulación masiva desde cuadernillos impresos.</p>", unsafe_allow_html=True)
    
    st.info("💡 **Tip Profesional:** Haz clic en la primera celda de 'Respuesta', presiona 'V' o 'F' en tu teclado y usa la flecha ⬇️ para bajar rápidamente.")
    
    df_editado = st.data_editor(
        st.session_state.respuestas_df,
        column_config={
            "Ítem": st.column_config.NumberColumn("Nº", disabled=True, width="small"),
            "Pregunta": st.column_config.TextColumn("Contenido del Ítem", disabled=True, width="large"),
            "Respuesta": st.column_config.SelectboxColumn("Respuesta", options=["V", "F", ""], required=False, width="medium")
        },
        hide_index=True, height=600, use_container_width=True
    )
    st.session_state.respuestas_df = df_editado

# =====================================================================
# VISTA 4: DASHBOARD CLÍNICO Y ESTADÍSTICAS
# =====================================================================
elif menu == "📈 4. Dashboard Clínico":
    st.markdown(f"<h1 class='main-header'>Perfil Oficial de {st.session_state.paciente['nombre']}</h1>", unsafe_allow_html=True)
    
    df_resultados, omitidas, tv, tf = calcular_perfil_clinico(st.session_state.respuestas_df)
    
    # 1. TARJETAS DE VALIDEZ
    st.markdown("### Indicadores de Validez de la Prueba")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        color = "red" if omitidas > 30 else "green"
        st.markdown(f"<div class='metric-card'><h3 style='color:{color}'>{omitidas}</h3><p>? (Omitidas)</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><h3>{tv}</h3><p>Verdaderos (VRIN/TRIN base)</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'><h3>{tf}</h3><p>Falsos</p></div>", unsafe_allow_html=True)
    with c4:
        estado = "VÁLIDA" if omitidas <= 30 else "INVÁLIDA"
        color_est = "green" if estado == "VÁLIDA" else "red"
        st.markdown(f"<div class='metric-card'><h3 style='color:{color_est}'>{estado}</h3><p>Estatus Clínico</p></div>", unsafe_allow_html=True)

    if omitidas > 30:
        st.error("🚨 CRÍTICO: La prueba carece de validez clínica. El paciente ha omitido demasiados ítems.")
        st.stop()

    st.divider()

    # 2. GRÁFICO PROFESIONAL CON PLOTLY
    st.markdown("### Perfil de Puntuaciones T (Validez y Clínicas)")
    
    validez_escalas = df_resultados.iloc[:3]
    clinicas_escalas = df_resultados.iloc[3:]

    fig = go.Figure()
    
    # Escalas de Validez (Gris/Negro)
    fig.add_trace(go.Scatter(x=validez_escalas['Escala'], y=validez_escalas['T'], 
                             mode='lines+markers+text', name='Validez',
                             line=dict(color='gray', width=3),
                             marker=dict(size=10, color='black'),
                             text=validez_escalas['T'], textposition="top center"))

    # Escalas Clínicas (Azul)
    fig.add_trace(go.Scatter(x=clinicas_escalas['Escala'], y=clinicas_escalas['T'], 
                             mode='lines+markers+text', name='Clínicas',
                             line=dict(color='#1f77b4', width=3),
                             marker=dict(size=10, color='#1f77b4'),
                             text=clinicas_escalas['T'], textposition="top center"))

    # Líneas de corte clínico
    fig.add_shape(type="line", x0=0, y0=65, x1=1, y1=65, xref='paper', yref='y', line=dict(color="red", width=2, dash="dash"))
    fig.add_shape(type="line", x0=0, y0=50, x1=1, y1=50, xref='paper', yref='y', line=dict(color="green", width=1, dash="dot"))
    
    # Sombreado de área clínica (T > 65)
    fig.add_hrect(y0=65, y1=120, line_width=0, fillcolor="red", opacity=0.1, annotation_text="Elevación Clínica", annotation_position="top left")

    fig.update_layout(
        height=500, title_text="Perfil Psicométrico MMPI-2", 
        yaxis=dict(title="Puntuación T (Media 50, DE 10)", range=[30, 120], dtick=10),
        xaxis=dict(tickangle=-45),
        plot_bgcolor='white', hovermode="x unified", margin=dict(b=100)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

    st.plotly_chart(fig, use_container_width=True)

    # 3. TABLA DE DATOS
    st.markdown("### Tabla Desglosada de Resultados")
    st.dataframe(df_resultados.style.applymap(lambda x: "background-color: #ffcccc" if isinstance(x, (int, float)) and x >= 65 else "", subset=['T']), use_container_width=True)

# =====================================================================
# VISTA 5: GENERADOR DE INFORMES (WORD)
# =====================================================================
elif menu == "📄 5. Generar Informe Word":
    st.markdown("<h1 class='main-header'>Motor de Informes</h1>", unsafe_allow_html=True)
    st.write("Genera un informe editable en Microsoft Word (.docx) con gráficos y tablas pre-formateadas.")
    
    if st.button("🚀 Crear Informe Oficial"):
        df_resultados, omit, tv, tf = calcular_perfil_clinico(st.session_state.respuestas_df)
        pac = st.session_state.paciente
        
        doc = Document()
        
        # Título
        t = doc.add_heading('INFORME PSICOLÓGICO MMPI-2', level=0)
        t.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Datos
        doc.add_heading('1. Datos de Identificación', level=1)
        p = doc.add_paragraph()
        p.add_run(f"Paciente: {pac['nombre']}\nEdad: {pac['edad']} años\nSexo: {pac['sexo']}\nFecha de Evaluación: {pac['fecha']}").bold = True
        
        # Validez
        doc.add_heading('2. Validez de la Prueba', level=1)
        doc.add_paragraph(f"Ítems Omitidos (?): {omit} (Se considera válido por debajo de 30).")
        doc.add_paragraph(f"Porcentaje de respuestas Verdaderas: {int((tv/TOTAL_ITEMS)*100)}%")
        doc.add_paragraph(f"Porcentaje de respuestas Falsas: {int((tf/TOTAL_ITEMS)*100)}%")
        
        # Tabla
        doc.add_heading('3. Tabla de Puntuaciones', level=1)
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text, hdr_cells[1].text, hdr_cells[2].text, hdr_cells[3].text = 'Escala', 'PD', 'PD+K', 'T'
        
        for _, row in df_resultados.iterrows():
            row_cells = table.add_row().cells
            row_cells[0].text = str(row['Escala'])
            row_cells[1].text = str(row['PD'])
            row_cells[2].text = str(row['PD_K'])
            row_cells[3].text = str(row['T'])

        # Interpretación básica
        doc.add_heading('4. Notas Clínicas (Picos > T65)', level=1)
        elevaciones = df_resultados[df_resultados['T'] >= 65]
        if not elevaciones.empty:
            for _, row in elevaciones.iterrows():
                doc.add_paragraph(f"Elevación significativa en {row['Escala']} (T = {row['T']}).", style='List Bullet')
        else:
            doc.add_paragraph("No se observan elevaciones clínicas significativas por encima de T=65.")

        # Guardar en memoria
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        st.success("✅ Informe generado con éxito.")
        st.download_button(
            label="📥 Descargar Documento Word (.docx)",
            data=buffer,
            file_name=f"MMPI_2_Reporte_{pac['nombre'].replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
