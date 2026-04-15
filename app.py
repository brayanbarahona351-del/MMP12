import streamlit as st
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import matplotlib.pyplot as plt
import math

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema Clínico MMPI-2", layout="wide")

# --- CONTROL DE SESIÓN ---
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
# 🛑 ZONA 1: ÍTEMS DEL CUESTIONARIO (Opcional si usas Captura Rápida)
# =====================================================================
PREGUNTAS = [
    "Me gustan las revistas de mecánica.", 
    "Tengo buen apetito.", 
    "Me despierto fresco y descansado casi todas las mañanas.",
    "Creo que me gustaría el trabajo de bibliotecario.",
    "El ruido me despierta fácilmente."
]
while len(PREGUNTAS) < 567:
    PREGUNTAS.append(f"Ítem {len(PREGUNTAS) + 1} del manual.")

# =====================================================================
# 🛑 ZONA 2: CLAVES DE CORRECCIÓN
# =====================================================================
CLAVES = {
    "L (Mentira)": {"V": [], "F": [16, 29, 41, 51, 77, 93, 102, 107, 123, 139, 153, 183, 203, 232, 260]},
    "F (Incoherencia)": {"V": [18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 84, 96, 114, 138, 144, 150, 156, 162, 168, 180, 198, 216, 228, 234, 240, 246, 252, 258, 264, 270, 282, 288, 294, 300, 306, 312, 324, 336, 349, 355, 361], "F": [6, 12, 78, 90, 102, 108, 120, 126, 132, 174, 186, 192, 204, 210, 222, 276, 318, 330, 343]},
    "K (Defensividad)": {"V": [83], "F": [29, 37, 58, 76, 110, 116, 122, 127, 130, 136, 148, 157, 158, 167, 171, 196, 213, 238, 240, 257, 258, 267, 281, 290, 300, 316, 319, 332, 338, 346]},
    "1 Hs (Hipocondriasis)": {"V": [11, 18, 28, 39, 59], "F": [2, 3, 9, 10, 20]}, # LLENAR RESTO
    "2 D (Depresión)": {"V": [], "F": []},       
    "3 Hy (Histeria)": {"V": [], "F": []},
    "4 Pd (Desviación Psicopática)": {"V": [], "F": []},
    "5 Mf (Masculinidad-Feminidad)": {"V": [], "F": []}, 
    "6 Pa (Paranoia)": {"V": [], "F": []},
    "7 Pt (Psicastenia)": {"V": [11, 16, 23, 31, 38, 56, 65, 73, 82, 89, 94, 130, 147, 170, 175, 196, 218, 242, 273, 275, 277, 285, 289, 301, 302, 304, 308, 309, 310, 313, 316, 317, 320, 325, 326, 327, 328, 329, 331], "F": [3, 9, 33, 109, 140, 165, 174, 293, 321]},
    "8 Sc (Esquizofrenia)": {"V": [], "F": []},
    "9 Ma (Hipomanía)": {"V": [], "F": []},
    "0 Si (Introversión Social)": {"V": [], "F": []}
}

# =====================================================================
# 🛑 ZONA 3: BAREMOS T Y DESCRIPCIONES CLINICAS 
# =====================================================================
def obtener_t(sexo, escala, puntaje):
    # Simulador seguro de T (Reemplazar con tablas reales luego)
    try:
        return min(puntaje * 2 + 30, 120) 
    except:
        return 50

def obtener_interpretacion(escala, t_score):
    if t_score >= 65:
        return "Elevación clínica significativa. Requiere atención según manual MMPI-2."
    return "Dentro de los límites normativos."

# =====================================================================
# INTERFAZ Y LÓGICA
# =====================================================================
with st.sidebar:
    st.header("📋 Datos y Configuración")
    nombre = st.text_input("Nombre Completo")
    edad = st.number_input("Edad", 18, 99, 25)
    sexo = st.selectbox("Sexo Biológico", ["Varón", "Mujer"])
    st.divider()
    
    # NUEVO: Selector de Modo de Llenado
    modo_llenado = st.radio("MODO DE VISUALIZACIÓN", ["Paciente (Texto Completo)", "Psicólogo (Captura Rápida)"])
    st.divider()
    
    progreso = sum(1 for r in st.session_state.respuestas.values() if r is not None and r != "") / 567
    st.progress(progreso)
    st.write(f"Avance: {int(progreso * 100)}%")
    
    if st.button("🗑️ Reiniciar Evaluación"): reset_form()

st.title("MMPI-2: Inventario Multifásico de Personalidad")

# --- SISTEMA DE VISUALIZACIÓN ---
if modo_llenado == "Psicólogo (Captura Rápida)":
    st.info("⚡ **MODO CAPTURA RÁPIDA:** Usa la tecla 'Tab' para saltar de casilla y 'V' o 'F' para llenar rápido desde tu hoja impresa.")
    ITEMS_POR_PAGINA = 100
else:
    st.info("Responda Verdadero o Falso a cada afirmación.")
    ITEMS_POR_PAGINA = 50

total_paginas = math.ceil(567 / ITEMS_POR_PAGINA)
inicio = st.session_state.pagina_actual * ITEMS_POR_PAGINA
fin = min(inicio + ITEMS_POR_PAGINA, 567)

# --- RENDERIZADO DE PREGUNTAS ---
if modo_llenado == "Psicólogo (Captura Rápida)":
    # Cuadrícula compacta de 5 columnas
    cols = st.columns(5)
    for i in range(inicio + 1, fin + 1):
        col_idx = (i - 1) % 5
        with cols[col_idx]:
            # Guardamos "V" o "F" internamente
            val_actual = ""
            if st.session_state.respuestas[i] == "Verdadero": val_actual = "V"
            elif st.session_state.respuestas[i] == "Falso": val_actual = "F"
            
            seleccion = st.selectbox(
                f"Ítem {i}", 
                ["", "V", "F"], 
                index=["", "V", "F"].index(val_actual) if val_actual else 0,
                key=f"q_{i}"
            )
            # Traducir V/F al sistema interno
            if seleccion == "V": st.session_state.respuestas[i] = "Verdadero"
            elif seleccion == "F": st.session_state.respuestas[i] = "Falso"
            else: st.session_state.respuestas[i] = None

else:
    # Modo tradicional con texto
    for i in range(inicio + 1, fin + 1):
        st.session_state.respuestas[i] = st.radio(
            f"**{i}. {PREGUNTAS[i-1]}**", 
            ["Verdadero", "Falso", "No sé (Blanco)"], 
            horizontal=True, 
            index=["Verdadero", "Falso", "No sé (Blanco)"].index(st.session_state.respuestas[i]) if st.session_state.respuestas[i] else None,
            key=f"q_{i}"
        )

st.divider()

# --- NAVEGACIÓN Y CÁLCULO ---
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.session_state.pagina_actual > 0:
        if st.button("⬅️ Anterior"):
            st.session_state.pagina_actual -= 1
            st.rerun()
with col3:
    if st.session_state.pagina_actual < total_paginas - 1:
        if st.button("Siguiente ➡️"):
            st.session_state.pagina_actual += 1
            st.rerun()
    else:
        if st.button("📈 CALCULAR PERFIL"):
            # NUEVO: RASTREADOR DE ÍTEMS EN BLANCO
            blancos = [str(k) for k, v in st.session_state.respuestas.items() if v is None or v == "No sé (Blanco)" or v == ""]
            
            if len(blancos) > 30:
                st.error(f"❌ **TEST INVÁLIDO:** Faltan {len(blancos)} preguntas (Límite: 30).")
                st.warning(f"**Por favor llene los siguientes ítems:** {', '.join(blancos)}")
            else:
                if len(blancos) > 0:
                    st.warning(f"⚠️ **Atención:** Se calculará con {len(blancos)} ítems omitidos: {', '.join(blancos)}")

                # 1. CÁLCULO PD SEGURO
                resultados = {}
                for escala, claves in CLAVES.items():
                    pd_val = 0
                    for item in claves.get("V", []):
                        if st.session_state.respuestas.get(item) == "Verdadero": pd_val += 1
                    for item in claves.get("F", []):
                        if st.session_state.respuestas.get(item) == "Falso": pd_val += 1
                    resultados[escala] = {"PD": pd_val, "PD_K": pd_val, "T": 0, "Interp": ""}

                # 2. MOTOR CORRECCIÓN K BLINDADO
                valor_k = resultados.get("K (Defensividad)", {}).get("PD", 0)
                
                if "1 Hs (Hipocondriasis)" in resultados:
                    resultados["1 Hs (Hipocondriasis)"]["PD_K"] = round(resultados["1 Hs (Hipocondriasis)"]["PD"] + (0.5 * valor_k))
                if "4 Pd (Desviación Psicopática)" in resultados:
                    resultados["4 Pd (Desviación Psicopática)"]["PD_K"] = round(resultados["4 Pd (Desviación Psicopática)"]["PD"] + (0.4 * valor_k))
                if "7 Pt (Psicastenia)" in resultados:
                    resultados["7 Pt (Psicastenia)"]["PD_K"] = round(resultados["7 Pt (Psicastenia)"]["PD"] + (1.0 * valor_k))
                if "8 Sc (Esquizofrenia)" in resultados:
                    resultados["8 Sc (Esquizofrenia)"]["PD_K"] = round(resultados["8 Sc (Esquizofrenia)"]["PD"] + (1.0 * valor_k))
                if "9 Ma (Hipomanía)" in resultados:
                    resultados["9 Ma (Hipomanía)"]["PD_K"] = round(resultados["9 Ma (Hipomanía)"]["PD"] + (0.2 * valor_k))

                # 3. CONSTRUCCIÓN DE DATAFRAME SEGURA
                lista_datos = []
                for k, v in resultados.items():
                    t_score = obtener_t(sexo, k, v["PD_K"])
                    interp = obtener_interpretacion(k, t_score)
                    
                    lista_datos.append({
                        "Escala": k,
                        "PD": v["PD"],
                        "PD+K": v["PD_K"],
                        "Puntuación T": t_score,
                        "Interpretación": interp
                    })

                df = pd.DataFrame(lista_datos) # <- AQUÍ SE SOLUCIONÓ EL ERROR

                # --- VISUALIZACIÓN ---
                st.success("✅ Perfil Generado Exitosamente")
                
                # Gráfico
                fig, ax = plt.subplots(figsize=(12, 5))
                ax.plot(df['Escala'], df['Puntuación T'], marker='o', color='darkblue')
                ax.axhline(y=65, color='red', linestyle='--', label='Corte Clínico (T=65)')
                ax.axhline(y=50, color='gray', linestyle='-', alpha=0.5)
                ax.set_ylim(20, 120)
                plt.xticks(rotation=45, ha='right')
                st.pyplot(fig)

                st.table(df[['Escala', 'PD', 'PD+K', 'Puntuación T']])

                # --- WORD ---
                doc = Document()
                doc.add_heading('PERFIL MMPI-2', 0)
                doc.add_paragraph(f"Paciente: {nombre}\nEdad: {edad}\nÍtems Omitidos: {len(blancos)}")
                if blancos:
                    doc.add_paragraph(f"Ítems específicos omitidos: {', '.join(blancos)}")

                img_b = BytesIO()
                plt.savefig(img_b, format='png', bbox_inches='tight')
                doc.add_picture(img_b, width=Inches(6))

                w_buf = BytesIO()
                doc.save(w_buf)
                st.download_button("📥 DESCARGAR REPORTE WORD", w_buf.getvalue(), f"MMPI_{nombre}.docx")
