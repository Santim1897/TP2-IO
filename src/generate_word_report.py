"""
Exportador de Informes a Microsoft Word (.docx) para TP2 Puerto Sur (Grupo 8)
Genera:
1. INFORME_EJECUTIVO_PUERTO_SUR.docx: Informe integral de todo el trabajo práctico.
2. MODELO_CONCEPTUAL_G08.docx: Documento específico del Modelo Conceptual para el buzón de entrega.
"""

import os
import sys
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def format_table(table, header_bg="1F4E79", zebra=True):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for cell in table.rows[0].cells:
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.size = Pt(9.5)
        set_cell_background(cell, header_bg)
        set_cell_margins(cell, 100, 100, 120, 120)
        
    for r_idx, row in enumerate(table.rows[1:], start=1):
        for cell in row.cells:
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(9.0)
            if zebra and r_idx % 2 == 1:
                set_cell_background(cell, "F2F5F9")
            set_cell_margins(cell, 60, 60, 100, 100)

def add_callout(doc, text, title="DIAGNÓSTICO GERENCIAL"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "EBF3FA")
    set_cell_margins(cell, 100, 100, 140, 140)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    r_title = p.add_run(f"📌 {title}: ")
    r_title.bold = True
    r_title.font.size = Pt(9.5)
    r_title.font.color.rgb = RGBColor(31, 78, 121)
    r_text = p.add_run(text)
    r_text.font.size = Pt(9.5)
    r_text.italic = True
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def add_figure_with_caption(doc, image_path, caption_text, width_inches=6.0):
    if os.path.exists(image_path):
        doc.add_picture(image_path, width=Inches(width_inches))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(4)
        p_cap.paragraph_format.space_after = Pt(12)
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.italic = True
        r_cap.font.size = Pt(8.5)
        r_cap.font.color.rgb = RGBColor(80, 80, 80)

# =========================================================================
# GENERADOR 1: MODELO CONCEPTUAL ESPECÍFICO (BUZÓN DE ENTREGA)
# =========================================================================
def build_conceptual_word_doc(output_path="MODELO_CONCEPTUAL_G08.docx"):
    doc = docx.Document()
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)

    COLOR_PRIMARY = RGBColor(31, 78, 121)    # ITBA Navy Blue
    COLOR_SECONDARY = RGBColor(47, 85, 151)  # Slate Blue

    # Portada
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("INSTITUTO TECNOLÓGICO DE BUENOS AIRES (ITBA)\nDEPARTAMENTO DE INGENIERÍA INDUSTRIAL — 2026 2C")
    r_inst.font.bold = True
    r_inst.font.size = Pt(11)
    r_inst.font.color.rgb = COLOR_SECONDARY

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(16)
    p_title.paragraph_format.space_after = Pt(6)
    r_title = p_title.add_run("TRABAJO PRÁCTICO N° 2: INVESTIGACIÓN OPERATIVA (IO51)\nMODELO CONCEPTUAL: TERMINAL PORTUARIA \"PUERTO SUR\"")
    r_title.font.bold = True
    r_title.font.size = Pt(17)
    r_title.font.color.rgb = COLOR_PRIMARY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(16)
    r_sub = p_sub.add_run("Documento Formal de Entrega: Objetivo, Variables, Plan de Análisis, Causalidad, IDEF0, Lógicas y Elementos SimPy")
    r_sub.font.italic = True
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = COLOR_SECONDARY

    t_meta = doc.add_table(rows=6, cols=2)
    meta_info = [
        ("Materia:", "11.51 / IO51 - Investigación Operativa (ITBA)"),
        ("Comisión y Grupo:", "2° Cuatrimestre 2026 — Grupo 08"),
        ("Dataset Asignado:", "data/PuertoSur_escalas_G08.csv (8.852 escalas históricas registradas)"),
        ("Metodología:", "Simulación de Eventos Discretos (DES) & Modelado IDEF0"),
        ("Repositorio Oficial:", "https://github.com/Santim1897/TP2-IO"),
        ("Entregable:", "Buzón de Entrega: Modelo Conceptual (Puntos i a vii)")
    ]
    for idx, (k, v) in enumerate(meta_info):
        t_meta.cell(idx, 0).paragraphs[0].add_run(k).bold = True
        t_meta.cell(idx, 1).paragraphs[0].add_run(v)
    format_table(t_meta, header_bg="1F4E79")

    doc.add_page_break()

    # 1. Objetivo
    h1 = doc.add_heading(level=1)
    h1.add_run("1. Objetivo").font.color.rgb = COLOR_PRIMARY
    
    doc.add_paragraph("1.1. Objetivo del Sistema Portuario (Perspectiva de Negocio):").runs[0].bold = True
    doc.add_paragraph("La Terminal Portuaria Puerto Sur opera como el principal nodo logístico de contenedores de la región patagónica en competencia directa con el puerto de la ciudad capital. El objetivo del sistema real es asegurar el cumplimiento del compromiso contractual de estadía promedio menor o igual a 16 horas (W <= 16 h) con las navieras de servicios regulares (Austral Feeder, Andes Container Line y TransPatagonia Line), a fin de evitar el desvío de buques, maximizar la productividad de transferencia de carga y optimizar la capacidad de sus activos de muelle y patio.")
    
    doc.add_paragraph("1.2. Objetivo del Estudio de Simulación (Perspectiva Metodológica):").runs[0].bold = True
    doc.add_paragraph("Modelar conceptual y computacionalmente el comportamiento estocástico y dinámico del puerto mediante Simulación de Eventos Discretos (DES), cuantificando los tiempos de espera en rada (Wq), maniobras náuticas conjuntas (U(1, 2) h en total), espera de grúas amarrado y faena efectiva en berma; contrastar la operación actual con modelos teóricos de líneas de espera (M/M/c y M/G/c); identificar los cuellos de botella en muelle y patio; y sustentar con evidencia estadística la toma de decisiones estratégicas (adición de una 4ª grúa pórtico STS, políticas de patio y camiones, incorporación de temporada de cruceros y viabilidad de una 4ª berma).")

    # 2. Variables
    h1 = doc.add_heading(level=1)
    h1.add_run("2. Variables de Decisión y de Referencia").font.color.rgb = COLOR_PRIMARY
    
    doc.add_paragraph("• Variables de Decisión (Endógenas / Controlables):").runs[0].bold = True
    doc.add_paragraph("  - B: Bermas asignadas al servicio de carga regular (B in {2, 3, 4}).")
    doc.add_paragraph("  - G: Flota de grúas pórtico STS operativas en muelle (G in {3, 4}).")
    doc.add_paragraph("  - Política de grúas: Asignación de hasta 2 grúas por buque según disponibilidad.")
    doc.add_paragraph("  - Régimen nocturno: Grúa en standby con 15-20 min de alistamiento vs. activa continua.")
    doc.add_paragraph("  - Política de camiones externos: Tolerancia horaria vs. multas por impuntualidad.")
    doc.add_paragraph("  - Política de crucero: Rechazar, aceptar sin reserva, o conceder reserva exclusiva preventiva.")
    doc.add_paragraph("  - Inversión en 4ª berma: Adquisición e instalación de 4ª berma (USD 12M).")

    doc.add_paragraph("• Variables de Referencia / Exógenas (No Controlables / Estocásticas):").runs[0].bold = True
    doc.add_paragraph("  - Arribos de buques: Tiempo entre arribos Delta t (media = 2.968 h, CV = 2.494).")
    doc.add_paragraph("  - Composición de carga: Movimientos Dry, Reefer y OOG por buque.")
    doc.add_paragraph("  - Productividad nominal de grúa: Dry (28 mov/h), Reefer (21 mov/h), OOG (12 mov/h).")
    doc.add_paragraph("  - Factor de interferencia dual: 0.85 de la suma si operan 2 grúas en un buque (factor 1.7x).")
    doc.add_paragraph("  - Maniobras conjuntas de atraque y desatraque: U(1.0, 2.0) horas en conjunto en total (media 1.5 h).")
    doc.add_paragraph("  - Ciclo de turnos: Paradas de 10-15 min cada 8h (00, 08 y 16 h). Reducción nocturna a 1 activa + 1 standby.")
    doc.add_paragraph("  - Patio: Capacidad de 3.000 slots, tiempo de permanencia medio de 72 h, 20-30% camiones tardíos.")
    doc.add_paragraph("  - Escalas de crucero: 2 arribos/semana durante 3 meses, permanencia de 28 a 36 h.")
    doc.add_paragraph("  - Parámetros de costo: Buque inmovilizado (USD 15.000 - 30.000 / día), canon crucero (USD 60.000).")

    doc.add_paragraph("• Variables de Salida / Desempeño (KPIs):").runs[0].bold = True
    doc.add_paragraph("  - W: Estadía promedio total (fondeo + atraque + faena + desatraque). Meta: W <= 16 h.")
    doc.add_paragraph("  - Wq: Tiempo medio de espera en rada. Ws: Tiempo medio en berma.")
    doc.add_paragraph("  - T_esp_grua: Tiempo amarrado esperando grúa STS libre.")
    doc.add_paragraph("  - T_op_grua: Tiempo neto de transferencia efectiva de carga con grúas.")
    doc.add_paragraph("  - % Espera Inactiva: Proporción ((Wq + T_esp_grua) / W) * 100%.")
    doc.add_paragraph("  - L, Lq: Cantidad promedio de buques en el puerto y fondeados en rada.")
    doc.add_paragraph("  - NS_16: Porcentaje de buques despachados con estadía <= 16 horas.")
    doc.add_paragraph("  - Payback y Años-buque de inmovilización evitados al año.")

    # 3. Plan de Análisis
    h1 = doc.add_heading(level=1)
    h1.add_run("3. Plan de Análisis y Visualización de Resultados").font.color.rgb = COLOR_PRIMARY
    doc.add_paragraph("Se estructuró una matriz de experimentación factorial multiescenario: 1) Diagnóstico de línea base física; 2) Barrido de demanda diaria de buques (0.5x a 1.2x) para determinar la capacidad límite bajo 3 vs. 4 grúas; 3) Políticas de ventanas de camiones y zonificación reefer; 4) Impacto de temporada de cruceros con y sin exclusividad; 5) Escenarios del proyecto industrial (+35% y +100%) bajo criterios de decisión bajo incertidumbre (Wald, Savage, Hurwicz, Laplace); 6) Análisis de repago de la 4ª berma.")
    doc.add_paragraph("El protocolo estadístico incluye eliminación del período de calentamiento, réplicas independientes, ANOVA y Test de Comparaciones Múltiples de Tukey HSD (FWER = 0.05).")

    # 4. Relación entre Variables
    h1 = doc.add_heading(level=1)
    h1.add_run("4. Relación entre Variables (Diagrama Causal de Influencias)").font.color.rgb = COLOR_PRIMARY
    add_figure_with_caption(doc, "plots/fig_relacion_variables_causal.png", 
                            "Figura 1: Diagrama de Influencias Causales entre Variables de Decisión, Exógenas, Estado y KPIs", width_inches=6.2)

    # 5. Diagrama IDEF0
    h1 = doc.add_heading(level=1)
    h1.add_run("5. Diagramas IDEF0").font.color.rgb = COLOR_PRIMARY
    add_figure_with_caption(doc, "plots/fig_idef0_a_menos_0.png",
                            "Figura 2: Diagrama de Contexto IDEF0 A-0: Operar Terminal Portuaria Puerto Sur", width_inches=6.2)
    add_figure_with_caption(doc, "plots/fig_idef0_a0_descomposicion.png",
                            "Figura 3: Diagrama de Descomposición Funcional IDEF0 A0 (Actividades A1 a A4)", width_inches=6.2)

    # 6. Lógicas
    h1 = doc.add_heading(level=1)
    h1.add_run("6. Lógicas Operativas del Sistema").font.color.rgb = COLOR_PRIMARY
    add_figure_with_caption(doc, "plots/fig_logica_flujo_buque.png",
                            "Figura 4: Diagrama de Flujo Lógico del Ciclo de Atención de Escalas Portuarias", width_inches=5.8)

    # 7. Elementos del Simulador
    h1 = doc.add_heading(level=1)
    h1.add_run("7. Elementos del Simulador (Arquitectura SimPy)").font.color.rgb = COLOR_PRIMARY
    add_figure_with_caption(doc, "plots/fig_elementos_simulador.png",
                            "Figura 5: Diagrama de Arquitectura de Clases, Recursos y Monitores del Simulador SimPy", width_inches=6.2)

    doc.save(output_path)
    print(f"Documento de Modelo Conceptual guardado exitosamente en: {output_path}")

# =========================================================================
# GENERADOR 2: INFORME EJECUTIVO COMPLETO
# =========================================================================
def build_full_word_doc(output_path="INFORME_EJECUTIVO_PUERTO_SUR.docx"):
    doc = docx.Document()
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)

    COLOR_PRIMARY = RGBColor(31, 78, 121)    # ITBA Navy Blue
    COLOR_SECONDARY = RGBColor(47, 85, 151)  # Slate Blue

    # Portada
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("INSTITUTO TECNOLÓGICO DE BUENOS AIRES (ITBA)\nDEPARTAMENTO DE INGENIERÍA INDUSTRIAL — 2026 2C")
    r_inst.font.bold = True
    r_inst.font.size = Pt(11)
    r_inst.font.color.rgb = COLOR_SECONDARY

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(18)
    p_title.paragraph_format.space_after = Pt(6)
    r_title = p_title.add_run("TRABAJO PRÁCTICO N° 2: INVESTIGACIÓN OPERATIVA (IO51)\nSIMULACIÓN DE EVENTOS DISCRETOS: \"PUERTO SUR\"")
    r_title.font.bold = True
    r_title.font.size = Pt(18)
    r_title.font.color.rgb = COLOR_PRIMARY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(20)
    r_sub = p_sub.add_run("Informe Integral y Autocontenido: Modelo Conceptual, Teoría de Colas, Simulación SimPy, Experimentación y Decisiones Estratégicas")
    r_sub.font.italic = True
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = COLOR_SECONDARY

    t_meta = doc.add_table(rows=6, cols=2)
    meta_info = [
        ("Materia:", "11.51 / IO51 - Investigación Operativa (ITBA)"),
        ("Comisión y Grupo:", "2° Cuatrimestre 2026 — Grupo 08"),
        ("Dataset Asignado:", "data/PuertoSur_escalas_G08.csv (8.852 escalas registradas, ~3 años)"),
        ("Entorno y Lenguaje:", "Python 3.12 / SimPy 4.1.2 / Pandas / SciPy / Statsmodels / Matplotlib"),
        ("Repositorio Oficial:", "https://github.com/Santim1897/TP2-IO"),
        ("Naturaleza del Documento:", "Informe Técnico y Gerencial Autocontenido")
    ]
    for idx, (k, v) in enumerate(meta_info):
        t_meta.cell(idx, 0).paragraphs[0].add_run(k).bold = True
        t_meta.cell(idx, 1).paragraphs[0].add_run(v)
    format_table(t_meta, header_bg="2F5597")

    doc.add_page_break()

    # Resumen Ejecutivo
    h1 = doc.add_heading(level=1)
    h1.add_run("Resumen Ejecutivo y Cuadro Consolidado de Respuestas").font.color.rgb = COLOR_PRIMARY
    doc.add_paragraph("A continuación se presenta la tabla consolidada con las respuestas cuantitativas y recomendaciones estratégicas a cada una de las consignas requeridas por la cátedra para el Grupo 08 (Simulación Física Refactorizada):")

    t_res = doc.add_table(rows=8, cols=4)
    res_data = [
        ["Consigna", "Pregunta Clave de la Cátedra", "Resultado Cuantitativo (Grupo 8)", "Recomendación Estratégica"],
        ["a) Modelo", "Formalización conceptual y operativa del puerto.", "Simulador SimPy con contención física de grúas, maniobras conjuntas de 1.5h y dinámica de patio.", "Verificación formal mediante Ley de Little (L = lambda * W)."],
        ["b) Diagnóstico", "Estadía actual (W), cantidad de buques (L) y desglose espera vs atención.", "W = 15.00 h | L = 5.05 buques | Wq = 7.90 h (52.6%) | Ws = 7.11 h (47.4%). Atención neta grúa: 4.75 h (31.7%). 32.9% excede 16h.", "Reclamo naviero plenamente fundado: 58.3% del tiempo es espera inactiva."],
        ["c) Umbral 16h", "Demanda máx. admisible y beneficio de incorporar una 4ª grúa STS.", "Demanda máx actual: <= 8.09 b/d (32.9% excedido). Con 4ª grúa: W cae a 9.38 h (Wq cae 58.7% a 3.26 h; excedidos caen a 11.8%).", "Aprobar de inmediato la 4ª grúa. Brinda holgura operativa y robustez."],
        ["d) Patio", "Efecto de ventanas horarias de camiones y slots reefer segregados.", "Penalidades bajan camiones tardíos del 25% al 10%, estabilizando el patio por debajo del 75%.", "Aplicar penalidad y segregar slots reefer en temporada de fruta (+57% demanda)."],
        ["e) Cruceros", "Impacto de exclusividad de berma y canon mínimo (USD 60.000 ofrecidos).", "Reserva exclusiva genera +2.31 h/buque de demora a carga (pérdidas de USD 4.26M a 8.52M).", "Rechazar reserva exclusiva. Canon de equilibrio: USD 178k - 355k por escala. Reportar por separado."],
        ["f) Proyecto Ind.", "Decisión bajo incertidumbre ante Base (+35%) y Optimista (+100%).", "Con 3 bermas el puerto colapsa (rho > 1.13). 4ª berma domina bajo Wald, Savage y Laplace.", "Construir 4ª berma de manera urgente. Convicción directiva valida la decisión."],
        ["g) Repago 4ª B.", "Demanda para repago, período de repago y buques-año evitados.", "Ahorro: 2.53 años-buque evitados/año (USD 20.76M/año). Inversión: USD 12M.", "Payback de 0.58 años (~7 meses). Rentabilidad económica sobresaliente."]
    ]
    for r_idx, row in enumerate(res_data):
        for c_idx, val in enumerate(row):
            t_res.cell(r_idx, c_idx).paragraphs[0].add_run(val)
    format_table(t_res, header_bg="1F4E79")

    doc.add_page_break()

    # SECCIÓN 1: MODELO CONCEPTUAL
    h1 = doc.add_heading(level=1)
    h1.add_run("Sección 1: Modelo Conceptual Formal").font.color.rgb = COLOR_PRIMARY
    
    h2 = doc.add_heading(level=2)
    h2.add_run("1.1. Objetivo y Clasificación de Variables").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("El objetivo general es estructurar un modelo DES para Puerto Sur que permita evaluar cuantitativamente la capacidad de sostener una estadía W <= 16 horas con las navieras regulares, identificar cuellos de botella en muelle y patio, y evaluar la viabilidad de la 4ª grúa, la 4ª berma y el impacto de los cruceros.")
    doc.add_paragraph("Se clasificaron rigurosamente las variables de decisión (Bermas B in {2,3,4}, Grúas G in {3,4}, políticas de camiones y cruceros), variables de referencia exógenas (arribos Delta t del Grupo 8, mix de carga, turnos, maniobras conjuntas de 1.5h, paradas de cambio de guardia) y variables de salida/KPIs (W, Wq, Ws, T_esp_grua, T_op_grua, % espera inactiva, L, Lq y Payback).")

    h2 = doc.add_heading(level=2)
    h2.add_run("1.2. Relación Causal entre Variables").font.color.rgb = COLOR_SECONDARY
    add_figure_with_caption(doc, "plots/fig_relacion_variables_causal.png",
                            "Figura 1: Diagrama de Influencias Causales entre Variables del Sistema Portuario", width_inches=6.0)

    h2 = doc.add_heading(level=2)
    h2.add_run("1.3. Diagramas IDEF0 (Contexto y Descomposición Funcional)").font.color.rgb = COLOR_SECONDARY
    add_figure_with_caption(doc, "plots/fig_idef0_a_menos_0.png",
                            "Figura 2: Diagrama de Contexto IDEF0 A-0: Operar Terminal Portuaria Puerto Sur", width_inches=6.0)
    add_figure_with_caption(doc, "plots/fig_idef0_a0_descomposicion.png",
                            "Figura 3: Diagrama de Descomposición Funcional IDEF0 A0 (Actividades A1 a A4)", width_inches=6.0)

    h2 = doc.add_heading(level=2)
    h2.add_run("1.4. Lógicas Operativas y Arquitectura del Simulador").font.color.rgb = COLOR_SECONDARY
    add_figure_with_caption(doc, "plots/fig_logica_flujo_buque.png",
                            "Figura 4: Diagrama de Flujo Lógico Operativo del Ciclo de Atención de Escalas", width_inches=5.8)
    add_figure_with_caption(doc, "plots/fig_elementos_simulador.png",
                            "Figura 5: Diagrama de Arquitectura de Clases, Recursos y Monitores del Simulador SimPy", width_inches=6.0)

    doc.add_page_break()

    # SECCIÓN 2: MODELO DE DATOS Y COLAS
    h1 = doc.add_heading(level=1)
    h1.add_run("Sección 2: Modelo de Datos y Teoría de Colas a Priori").font.color.rgb = COLOR_PRIMARY
    doc.add_paragraph("Del análisis de las 8.852 escalas de data/PuertoSur_escalas_G08.csv se derivaron: lambda = 8.086 buques/día, tiempo entre arribos medio = 2.968 h (CV = 2.494), Austral Feeder (43.8%), Andes Container Line (37.6%), TransPatagonia Line (18.7%).")
    
    t_q = doc.add_table(rows=6, cols=7)
    q_data = [
        ["Modelo Analítico", "Ws Supuesto", "Tasa mu", "Intensidad rho", "Wq (Rada)", "W (Estadía)", "L (Buques)"],
        ["M/M/3 (Ideal 2G)", "5.50 h", "0.1818", "0.618", "1.76 h", "7.26 h", "2.45"],
        ["M/M/3 (Mixto)", "6.50 h", "0.1538", "0.730", "4.34 h", "10.84 h", "3.65"],
        ["M/M/3 (Promedio)", "7.11 h", "0.1406", "0.799", "7.85 h", "14.96 h", "5.04"],
        ["M/G/3 (Allen-Cunneen)", "7.11 h (CV=2.49)", "0.1406", "0.799", "24.81 h", "31.92 h", "10.75"],
        ["Simulación Física G08", "7.11 h (Empírico)", "Dinámico", "~0.79", "7.90 h", "15.00 h", "5.05"]
    ]
    for r_idx, row in enumerate(q_data):
        for c_idx, val in enumerate(row):
            t_q.cell(r_idx, c_idx).paragraphs[0].add_run(val)
    format_table(t_q, header_bg="2F5597")

    add_callout(doc, "Con las maniobras conjuntas de 1.5h corregidas, el modelo M/M/3 analítico con Ws = 7.11h predice Wq = 7.85h y W = 14.96h, coincidiendo de forma casi exacta con la simulación real (Wq = 7.90h, W = 15.00h).", "VALIDACIÓN DE COLAS")

    # SECCIÓN 3: EXPERIMENTACIÓN Y ANÁLISIS
    h1 = doc.add_heading(level=1)
    h1.add_run("Sección 3: Experimentación y Análisis Detallado (Consignas b a g)").font.color.rgb = COLOR_PRIMARY

    # Consigna b
    h2 = doc.add_heading(level=2)
    h2.add_run("Consigna b: Diagnóstico de la Operación Actual vs. Umbral de 16h").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("La operación actual promedia W = 15.00 horas, con Wq = 7.90 horas (52.62% espera en rada) y Ws = 7.11 horas (47.38% en berma). De Ws: 4.75 h son atención efectiva de grúa (31.67%), 0.86 h son espera por grúa libre amarrado (5.73%) y 1.50 h son maniobras náuticas conjuntas (10.00%). La espera total inactiva suma 58.35%.")
    doc.add_paragraph("Aunque el promedio cumple con 15.00h, el 32.91% de las escalas excede las 16 horas (en TransPatagonia Line excede el 45.10%).")
    add_figure_with_caption(doc, "plots/fig2_desglose_estadia.png", "Figura 6: Desglose de Estadía Portuaria: Tiempo en Berma (Ws) vs. Espera en Rada (Wq)", width_inches=5.8)

    # Consigna c
    h2 = doc.add_heading(level=2)
    h2.add_run("Consigna c: Compromiso de 16h y Beneficio de la 4ª Grúa STS").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("Con la 4ª grúa, la estadía total cae a 9.38 horas (reducción de 37.5%). La espera en rada se contrae un 58.7% (de 7.90 h a 3.26 h), y el incumplimiento cae de 32.91% a tan solo 11.85%. A 8.09 buques/día, la 4ª grúa garantiza que el puerto opere con total holgura.")
    add_figure_with_caption(doc, "plots/fig1_capacidad_demanda.png", "Figura 7: Capacidad Operativa y Cumplimiento del Umbral de 16h vs. Demanda Diaria", width_inches=5.8)

    # Consigna d
    h2 = doc.add_heading(level=2)
    h2.add_run("Consigna d: Política de Patio y Camiones").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("Penalizar la impuntualidad de camiones reduce la tasa de tardíos del 25% al 10%, estabilizando el patio por debajo del 75% (>2.250 slots) en momentos pico. La segregación de slots reefer es imprescindible durante octubre a diciembre, donde la demanda de frío sube un +57%.")

    # Consigna e
    h2 = doc.add_heading(level=2)
    h2.add_run("Consigna e: Temporada de Cruceros y Reserva Exclusiva").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("Conceder la reserva exclusiva añade +2.31 horas de demora por buque a la carga, generando demoras de 6.820 h/año con pérdidas de inmovilización de USD 4.26M a USD 8.52M por temporada. El canon compensatorio debería ser de USD 178k a USD 355k por escala (vs USD 60k ofrecidos). Se debe rechazar la exclusividad y reportar los cruceros por separado.")

    # Consigna f
    h2 = doc.add_heading(level=2)
    h2.add_run("Consigna f: Proyecto Industrial y Criterios bajo Incertidumbre").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("Bajo los escenarios Base (+35%) y Optimista (+100%), las 3 bermas colapsan (rho > 1.13). Construir la 4ª berma domina bajo todos los criterios de incertidumbre (Wald: +USD 19.5M vs -USD 1.200M; Savage Regret: USD 0M vs USD 750M). La convicción de la gerencia valida la urgencia de la obra.")

    # Consigna g
    h2 = doc.add_heading(level=2)
    h2.add_run("Consigna g: Análisis de Repago de la 4ª Berma (USD 12M)").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("La 4ª berma ahorra 7.50 horas por buque = 2.53 años-buque de inmovilización evitados al año = USD 20.76 Millones/año de ahorro. El período de repago es de 0.58 años (~6.9 meses).")
    add_figure_with_caption(doc, "plots/fig3_repago_berma.png", "Figura 8: Período de Repago de la Inversión en 4ª Berma (USD 12M) vs. Costo de Inmovilización", width_inches=5.8)

    # SECCIÓN 4: VALIDACIÓN ESTADÍSTICA
    h1 = doc.add_heading(level=1)
    h1.add_run("Sección 4: Validación Estadística con Test de Tukey HSD").font.color.rgb = COLOR_PRIMARY
    doc.add_paragraph("Se certificó la significancia estadística mediante el Test de Tukey HSD (FWER = 0.05):")

    t_tukey = doc.add_table(rows=5, cols=6)
    t_data = [
        ["Comparación de Escenarios", "Diferencia Medias", "p-valor adj.", "IC 95% Inferior", "IC 95% Superior", "¿Significativo?"],
        ["Actual (3G) vs 4 Grúas (4G)", "-4.33 h", "0.000", "-5.11 h", "-3.55 h", "Sí (Rechaza H0)"],
        ["Actual (3G) vs Crucero Exclusivo", "+5.15 h", "0.000", "+4.37 h", "+5.93 h", "Sí (Rechaza H0)"],
        ["Actual (3G) vs Camión Penalizado", "+0.34 h", "0.677", "-0.44 h", "+1.12 h", "No"],
        ["4 Grúas vs Crucero Exclusivo", "+9.48 h", "0.000", "+8.70 h", "+10.26 h", "Sí (Rechaza H0)"]
    ]
    for r_idx, row in enumerate(t_data):
        for c_idx, val in enumerate(row):
            t_tukey.cell(r_idx, c_idx).paragraphs[0].add_run(val)
    format_table(t_tukey, header_bg="1F4E79")

    add_figure_with_caption(doc, "plots/fig4_tukey_hsd.png", "Figura 9: Intervalos de Confianza al 95% del Test de Tukey HSD", width_inches=5.8)

    # SECCIÓN 5: CONCLUSIONES Y LIBRERÍAS
    h1 = doc.add_heading(level=1)
    h1.add_run("Sección 5: Conclusiones Estratégicas y Librerías Utilizadas").font.color.rgb = COLOR_PRIMARY
    doc.add_paragraph("Recomendaciones finales: 1) Incorporar la 4ª grúa de inmediato; 2) Invertir en la 4ª berma (repago en ~7 meses); 3) Rechazar la reserva exclusiva de crucero; 4) Relevo en caliente de turnos y penalización de camiones tardíos.")

    t_lib = doc.add_table(rows=8, cols=3)
    lib_data = [
        ["Librería", "Versión", "Rol Técnico en el Proyecto"],
        ["Python", "3.12", "Lenguaje base para estructuración algorítmica y orquestación."],
        ["SimPy", "4.1.2", "Motor de simulación de eventos discretos (entidades, recursos y procesos)."],
        ["Pandas", "2.2+", "Procesamiento de 8.852 escalas, agregación temporal y exportación."],
        ["NumPy", "1.26+", "Tratamiento matricial y generación estocástica pseudoaleatoria."],
        ["SciPy", "1.13+", "Ajuste de distribuciones y cálculo analítico de Erlang C y Allen-Cunneen."],
        ["Statsmodels", "0.14+", "Ejecución del Test de Comparaciones Múltiples de Tukey HSD y ANOVA."],
        ["Matplotlib", "3.8+", "Generación de gráficos analíticos a 300 DPI insertados en el informe."]
    ]
    for r_idx, row in enumerate(lib_data):
        for c_idx, val in enumerate(row):
            t_lib.cell(r_idx, c_idx).paragraphs[0].add_run(val)
    format_table(t_lib, header_bg="2F5597")

    doc.save(output_path)
    print(f"Documento de Informe Completo guardado exitosamente en: {output_path}")

if __name__ == "__main__":
    try:
        from src.paths import BASE_DIR
        conceptual_out = str(BASE_DIR / "MODELO_CONCEPTUAL_G08.docx")
        full_out = str(BASE_DIR / "INFORME_EJECUTIVO_PUERTO_SUR.docx")
    except Exception:
        conceptual_out = "MODELO_CONCEPTUAL_G08.docx"
        full_out = "INFORME_EJECUTIVO_PUERTO_SUR.docx"
    
    build_conceptual_word_doc(conceptual_out)
    build_full_word_doc(full_out)
