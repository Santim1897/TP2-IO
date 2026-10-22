"""
Exportador de Informe a Microsoft Word (.docx) para TP2 Puerto Sur (Grupo 8)
Asignatura: 11.51 / IO51 - Investigación Operativa (ITBA) - 2026 2C
"""

import os
import sys
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
    # Encabezados
    for cell in table.rows[0].cells:
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.size = Pt(9.5)
        set_cell_background(cell, header_bg)
        set_cell_margins(cell, 100, 100, 120, 120)
        
    # Filas de datos
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

def build_word_report(output_path="INFORME_EJECUTIVO_PUERTO_SUR.docx"):
    doc = docx.Document()
    
    # Configuración de página
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)
        
    COLOR_PRIMARY = RGBColor(31, 78, 121)    # ITBA Navy Blue
    COLOR_SECONDARY = RGBColor(47, 85, 151)  # Slate Blue
    COLOR_DARK = RGBColor(40, 40, 40)
    
    # -------------------------------------------------------------
    # PORTADA Y METADATOS
    # -------------------------------------------------------------
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
    r_sub = p_sub.add_run("Evaluación de Capacidad, Teoría de Colas, Cuellos de Botella y Decisiones Estratégicas de Inversión")
    r_sub.font.italic = True
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = COLOR_SECONDARY

    # Tabla de Metadatos
    t_meta = doc.add_table(rows=6, cols=2)
    t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_info = [
        ("Materia:", "11.51 / IO51 - Investigación Operativa (ITBA)"),
        ("Comisión y Grupo:", "2° Cuatrimestre 2026 — Grupo 08"),
        ("Dataset Asignado:", "PuertoSur_escalas_G08.csv (8.852 escalas registradas, ~3 años)"),
        ("Entorno y Lenguaje:", "Python 3.12 / SimPy 4.1.2 / Pandas / SciPy / Statsmodels / Matplotlib"),
        ("Repositorio Oficial:", "https://github.com/Santim1897/TP2-IO"),
        ("Naturaleza del Documento:", "Informe Técnico y Gerencial Autocontenido")
    ]
    for idx, (k, v) in enumerate(meta_info):
        t_meta.cell(idx, 0).paragraphs[0].add_run(k).bold = True
        t_meta.cell(idx, 1).paragraphs[0].add_run(v)
    format_table(t_meta, header_bg="2F5597")
    
    doc.add_page_break()

    # -------------------------------------------------------------
    # RESUMEN EJECUTIVO Y TABLA CONSOLIDADA
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    r = h1.add_run("Resumen Ejecutivo y Cuadro Consolidado de Respuestas")
    r.font.color.rgb = COLOR_PRIMARY
    
    p = doc.add_paragraph("El presente informe documenta el desarrollo conceptual, la formulación analítica de líneas de espera, la implementación en SimPy y la experimentación estadística del sistema portuario de Puerto Sur para el Grupo 08. La siguiente tabla consolida las respuestas técnicas y recomendaciones estratégicas a cada una de las consignas requeridas por la cátedra:")
    p.paragraph_format.space_after = Pt(10)
    
    t_res = doc.add_table(rows=8, cols=4)
    res_data = [
        ["Consigna", "Pregunta Clave de la Cátedra", "Resultado Cuantitativo (Grupo 8)", "Recomendación Estratégica"],
        ["a) Modelo", "Formalización conceptual y operativa del puerto.", "Simulador SimPy verificado formalmente mediante Ley de Little (L = lambda * W).", "Arquitectura modular y reproducible."],
        ["b) Diagnóstico", "Estadía actual (W), cantidad de buques (L) y desglose espera vs atención.", "W = 24.25 h | L = 8.15 buques | Wq = 16.32 h (67.3%) | Ws = 7.92 h (32.7%). 58.1% excede 16h.", "Reclamo naviero plenamente fundado: 2 de cada 3 horas son espera en rada."],
        ["c) Umbral 16h", "Demanda máx. admisible y beneficio de incorporar una 4ª grúa STS.", "Demanda máx actual: <= 7.4 b/d. Con 4ª grúa: W cae a 16.46 h (espera en rada se reduce en 44.5%).", "Aprobar de inmediato la 4ª grúa. Permite atender la demanda actual (8.09 b/d)."],
        ["d) Patio", "Efecto de ventanas horarias de camiones y slots reefer segregados.", "Penalidades bajan camiones tardíos del 25% al 10%, evitando superar el 75% del patio.", "Aplicar penalidad y segregar slots reefer en temporada de fruta (+57% demanda)."],
        ["e) Cruceros", "Impacto de exclusividad de berma y canon mínimo (USD 60.000 ofrecidos).", "Reserva exclusiva genera +12.88 h/buque de demora a carga (pérdidas de USD 23.8M a 47.5M).", "Rechazar reserva exclusiva. Canon de equilibrio: USD 990k - 1.98M por escala. Reportar por separado."],
        ["f) Proyecto Ind.", "Decisión bajo incertidumbre ante Base (+35%) y Optimista (+100%).", "Con 3 bermas el puerto colapsa (rho > 1.13). 4ª berma domina bajo Wald, Savage y Laplace.", "Construir 4ª berma de manera urgente. Convicción directiva valida la decisión."],
        ["g) Repago 4ª B.", "Demanda para repago, período de repago y buques-año evitados.", "Ahorro: 5.97 años-buque evitados/año (USD 49.0M/año). Inversión: USD 12M.", "Payback de 0.24 años (~3 meses). Rentabilidad económica sobresaliente."]
    ]
    for r_idx, row in enumerate(res_data):
        for c_idx, val in enumerate(row):
            t_res.cell(r_idx, c_idx).paragraphs[0].add_run(val)
    format_table(t_res, header_bg="1F4E79")
    
    doc.add_page_break()

    # -------------------------------------------------------------
    # SECCIÓN 1: MODELO CONCEPTUAL
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    r = h1.add_run("Sección 1: Modelo Conceptual")
    r.font.color.rgb = COLOR_PRIMARY
    
    # 1.1 Objetivo
    h2 = doc.add_heading(level=2)
    h2.add_run("1.1. Objetivo General y Específicos").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("El objetivo general es estructurar un modelo de simulación de eventos discretos que capture la dinámica operativa, logística y de capacidad de la Terminal Portuaria Puerto Sur, a fin de evaluar cuantitativamente el cumplimiento del compromiso de estadía promedio contractual (W <= 16 horas), detectar cuellos de botella en muelle y patio, y evaluar la viabilidad de alternativas de expansión de capacidad (4ª grúa y 4ª berma) y convenios comerciales (temporada de cruceros y proyecto industrial).")

    # 1.2 Variables
    h2 = doc.add_heading(level=2)
    h2.add_run("1.2. Variables de Decisión y de Referencia").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("Las variables del sistema se clasifican rigurosamente:")
    doc.add_paragraph("• Variables de Decisión (Controlables): Cantidad de bermas comerciales asignadas (B in {2, 3, 4}), dotación de grúas pórtico STS (G in {3, 4}), políticas de despacho de grúas (máximo 2 grúas simultáneas con factor de interferencia de 85%), régimen nocturno de grúas (standby con 15-20 min de alistamiento vs activa continua), políticas de tolerancia horaria para camiones y régimen de exclusividad para cruceros.")
    doc.add_paragraph("• Variables de Referencia (Exógenas): Arribos de buques feeders (Delta t histórico Grupo 8), composición de carga (movimientos Dry, Reefer, OOG), rendimientos de grúa (Dry: 28 mov/h, Reefer: 21 mov/h, OOG: 12 mov/h), tiempos de maniobra (1 a 2 horas al entrar y al salir), paradas de cambio de turno (10 a 15 min), permanencia de contenedores en patio (media 72 h), impuntualidad de camiones (20% a 30% tardíos) y costos de inmovilización de buques (USD 15.000 a 30.000 / día).")
    doc.add_paragraph("• Variables de Salida (KPIs): Estadía promedio total W, espera media en rada Wq, tiempo en berma Ws, porcentaje del tiempo en espera (Wq/W), cantidad promedio de buques en el puerto L y en rada Lq, nivel de servicio (% buques <= 16h), y período de repago de inversiones.")

    # 1.3 Plan de Análisis
    h2 = doc.add_heading(level=2)
    h2.add_run("1.3. Plan de Análisis y Visualización de Resultados").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("El plan experimental comprende 6 fases: 1) Análisis exploratorio y ajuste de distribuciones del Grupo 8; 2) Modelo analítico de colas a priori; 3) Simulación de línea base; 4) Barridos de capacidad límite y evaluación de 4ª grúa; 5) Análisis de cruceros y proyecto industrial; 6) Verificación estadística mediante ANOVA y Test de Tukey HSD (FWER = 0.05).")

    # 1.4 Relación Causal
    h2 = doc.add_heading(level=2)
    h2.add_run("1.4. Relación entre Variables (Mecanismos Causal)").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("Existe un fuerte acoplamiento causal en la terminal: Los buques que arriban ingresan a rada. Si las bermas están ocupadas, se acumula cola. Una vez amarrado, la atención depende del mix de contenedores y de las grúas disponibles. La asignación dual rinde 1.7 veces la tasa individual (85% de productividad combinada). En el turno noche, la capacidad se reduce drásticamente. Además, la descarga alimenta el patio de 3.000 slots; si la ocupación supera el 75% (>2.250 slots), las grúas sufren bloqueos obligados esperando slots libres. Toda demora en berma retiene el recurso y eleva la cola en rada, disparando W.")

    # 1.5 Diagrama IDEF0
    h2 = doc.add_heading(level=2)
    h2.add_run("1.5. Diagrama IDEF0").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("• A-0 (Contexto): Entradas: buques en rada, contenedores y camiones. Controles: umbral de 16h, turnos y reglas de patio. Mecanismos: bermas, grúas STS, tractores y simulador SimPy. Salidas: buques despachados, estadía W y costos de inmovilización.")
    doc.add_paragraph("• Descomposición A0: A1: Recepción en rada (FIFO) -> A2: Maniobra de atraque (1-2 h, grúas inactivas) -> A3: Operación de grúas y patio -> A4: Desatraque y zarpada (1-2 h).")

    # 1.6 Lógicas
    h2 = doc.add_heading(level=2)
    h2.add_run("1.6. Lógicas del Sistema").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("Se implementaron formalmente: 1) Lógica de asignación de berma por disponibilidad; 2) Lógica de practicaje y remolque independiente de grúas; 3) Lógica de grúas según turnos y afectación por congestión de patio (>75%); 4) Lógica de camiones externos y retiro de contenedores; 5) Lógica de cruceros con y sin reserva exclusiva.")

    # 1.7 Elementos del Simulador
    h2 = doc.add_heading(level=2)
    h2.add_run("1.7. Elementos del Simulador (SimPy)").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("Entidades: EntidadBuque, EntidadCrucero, Contenedor, Camion. Recursos: bermas (Resource cap=3 o 4), gruas (PriorityResource dinámico), patio (Container cap=3000). Procesos: buque, crucero, turnos (temporizador de 8h con pausas de 10-15 min) y camiones. Monitor: colector de microdatos para contrastes estadísticos.")

    doc.add_page_break()

    # -------------------------------------------------------------
    # SECCIÓN 2: MODELO DE DATOS Y COLAS A PRIORI
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    h1.add_run("Sección 2: Modelo de Datos y Teoría de Colas a Priori").font.color.rgb = COLOR_PRIMARY
    
    doc.add_paragraph("Del análisis de las 8.852 escalas históricas de PuertoSur_escalas_G08.csv se obtuvieron los parámetros empíricos maestros:")
    doc.add_paragraph("• Tasa media de llegadas: lambda = 8.086 buques/día (0.3369 buques/hora).")
    doc.add_paragraph("• Tiempo entre llegadas: media = 2.968 h, desvío = 7.404 h, Coeficiente de Variación CV = 2.494 (arribos agrupados).")
    doc.add_paragraph("• Servicios regulares: Austral Feeder (43.8%, 98.3 mov/buque, 3.87 h grúa), Andes Container Line (37.6%, 154.2 mov/buque, 6.17 h grúa), TransPatagonia Line (18.7%, 222.7 mov/buque, 9.01 h grúa).")
    doc.add_paragraph("• Tiempo medio en berma: Ws = 6.35 h (con 2 grúas) a 8.69 h (con 1 grúa).")
    
    h2 = doc.add_heading(level=2)
    h2.add_run("Contraste Analítico: Teoría de Colas vs. Simulación").font.color.rgb = COLOR_SECONDARY
    
    t_q = doc.add_table(rows=7, cols=7)
    q_data = [
        ["Modelo Analítico", "Ws Supuesto", "Tasa mu", "Intensidad rho", "Wq (Rada)", "W (Estadía)", "L (Buques)"],
        ["M/M/3 (Dual 2G)", "6.35 h", "0.1575", "0.713", "3.78 h", "10.13 h", "3.41"],
        ["M/M/3 (Mixto)", "7.00 h", "0.1429", "0.786", "6.81 h", "13.81 h", "4.65"],
        ["M/M/3 (Promedio)", "7.50 h", "0.1333", "0.842", "11.37 h", "18.87 h", "6.36"],
        ["M/G/3 (Allen-Cunneen)", "7.00 h (CV=2.49)", "0.1429", "0.786", "21.50 h", "28.50 h", "9.60"],
        ["M/G/3 (Allen-Cunneen)", "7.50 h (CV=2.49)", "0.1333", "0.842", "35.86 h", "43.36 h", "14.61"],
        ["Simulación Real G08", "7.92 h (Empírico)", "Dinámico", "~0.81", "16.32 h", "24.25 h", "8.15"]
    ]
    for r_idx, row in enumerate(q_data):
        for c_idx, val in enumerate(row):
            t_q.cell(r_idx, c_idx).paragraphs[0].add_run(val)
    format_table(t_q, header_bg="2F5597")
    
    add_callout(doc, "El resultado de la simulación (W = 24.25 h) se ubica coherentemente entre el modelo M/M/3 con llegadas sin memoria (W = 18.87 h) y el modelo conservador de Allen-Cunneen (W = 28.50 a 43.36 h), validando que las restricciones operativas reales (turnos nocturnos y paradas) explican con precisión la congestión.", "VALIDACIÓN TEÓRICA DE COLAS")

    # -------------------------------------------------------------
    # SECCIÓN 3: EXPERIMENTACIÓN Y ANÁLISIS DE CONSIGNAS
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    h1.add_run("Sección 3: Experimentación y Análisis Detallado").font.color.rgb = COLOR_PRIMARY

    # Consigna b
    h2 = doc.add_heading(level=2)
    h2.add_run("Consigna b: Diagnóstico de la Operación Actual vs. Umbral de 16h").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("La simulación de las 8.852 escalas históricas demuestra que la terminal incumple severamente el umbral contractual:")
    doc.add_paragraph("• Estadía promedio total W = 24.25 horas (desvío 18.02 h).")
    doc.add_paragraph("• Tiempo promedio de espera en rada Wq = 16.32 horas (67.33% del tiempo total).")
    doc.add_paragraph("• Tiempo promedio en berma Ws = 7.92 horas (32.67% del tiempo total).")
    doc.add_paragraph("• Cantidad promedio de buques en el sistema L = 8.15 buques (5.49 en rada y 2.66 amarrados).")
    doc.add_paragraph("• El 58.10% de los buques supera las 16 horas. En TransPatagonia Line (buques grandes), el 68.5% excede el umbral.")
    
    # Imagen Fig 2
    if os.path.exists("plots/fig2_desglose_estadia.png"):
        doc.add_picture("plots/fig2_desglose_estadia.png", width=Inches(5.8))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("Figura 1: Desglose de Estadía Portuaria: Tiempo en Berma (Ws) vs. Espera en Rada (Wq)")
        r_cap.font.italic = True
        r_cap.font.size = Pt(8.5)

    # Consigna c
    h2 = doc.add_heading(level=2)
    h2.add_run("Consigna c: Compromiso de 16h y Capacidad Máxima (Actual vs. 4ª Grúa)").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("Se ejecutó un barrido de demanda diaria para determinar el punto de quiebre donde la terminal cumple W <= 16 horas:")
    doc.add_paragraph("• Con 3 Grúas (Actual): La demanda diaria máxima que soporta la terminal para cumplir W <= 16h es de aproximadamente 7.40 buques/día (~1.140 contenedores/día). La demanda actual (8.09 buques/día) supera esta cota y empuja al sistema a la zona hiperbólica de colas (W = 24.25 h).")
    doc.add_paragraph("• Con 4 Grúas STS: La capacidad se eleva y soporta la demanda actual de 8.09 buques/día con W = 16.46 horas (la espera en rada se reduce un 44.5%, de 16.32 h a 9.06 h).")
    
    # Imagen Fig 1
    if os.path.exists("plots/fig1_capacidad_demanda.png"):
        doc.add_picture("plots/fig1_capacidad_demanda.png", width=Inches(5.8))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("Figura 2: Capacidad Operativa y Cumplimiento del Umbral de 16h vs. Demanda Diaria")
        r_cap.font.italic = True
        r_cap.font.size = Pt(8.5)
        
    add_callout(doc, "Recomendación: Aprobar la compra e instalación de la 4ª grúa pórtico. Como medidas operativas complementarias sin inversión de capital, se recomienda implementar el relevo de turnos 'en caliente' (eliminando la detención de 10-15 min) y mantener la 2ª grúa nocturna precalentada y operativa de forma continua (eliminando la espera de 15-20 min de alistamiento).", "DECISIÓN 4ª GRÚA")

    # Consigna d
    h2 = doc.add_heading(level=2)
    h2.add_run("Consigna d: Política de Ventanas Horarias de Camiones y Slots Reefer").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("• Ventanas de Camiones: La penalización económica por arribo tardío reduce la proporción de camiones fuera de ventana del 25% al 10%. Esto estabiliza la ocupación del patio por debajo de los 2.000 slots y elimina los cuellos de botella donde la ocupación supera el 75% (>2.250 slots). Por el contrario, ampliar la ventana aumenta la variabilidad de llegadas y congestiona la playa de estacionamiento.")
    doc.add_paragraph("• Segregación de Slots Reefer: El análisis de datos demostró que en los meses 10 a 12 (octubre a diciembre) la demanda de contenedores refrigerados se dispara un +57% (de 29.2 a 45.9 reefer/buque) por la cosecha de frutas. Reservar slots electrificados dedicados exclusivamente a reefer evita maniobras de remoción interna (re-handling) y agiliza las conexiones de frío.")

    # Consigna e
    h2 = doc.add_heading(level=2)
    h2.add_run("Consigna e: Temporada de Cruceros y Reserva Exclusiva de Berma").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("• Impacto Operativo: Cada crucero ocupa una berma completa entre 28 y 36 horas sin usar grúas pórtico. Con 2 escalas por semana durante 3 meses (24 escalas), conceder la reserva exclusiva reduce transitoriamente las bermas disponibles para carga de 3 a 2. Esto dispara la estadía de los buques feeder en +12.88 horas por buque.")
    doc.add_paragraph("• Análisis Económico: Las demoras adicionales a la flota de carga totalizan 38.012 horas-buque al año. Valuando el costo de inmovilización entre USD 15.000 y 30.000 / día (USD 625 a 1.250 / h), el costo económico trasladado a las navieras de carga asciende a USD 23.757.490 - USD 47.514.980 por temporada. El consorcio planea percibir USD 60.000 por escala (USD 1.440.000 en total).")
    doc.add_paragraph("• Canon Compensatorio: Para no perder dinero frente a los daños a las navieras de carga, el canon de crucero debería fijarse entre USD 989.895 y USD 1.979.791 por escala (entre 16 y 33 veces lo ofrecido).")
    doc.add_paragraph("• Tratamiento Estadístico: Las escalas de cruceros DEBEN reportarse por separado de las estadísticas de los feeders. Los cruceros permanecen 32h por excursiones turísticas; mezclar sus horas con buques portacontenedores distorsionaría las métricas contractuales e induciría el desvío de líneas regulares al puerto capital.")

    # Consigna f
    h2 = doc.add_heading(level=2)
    h2.add_run("Consigna f: Proyecto Industrial y Criterios de Decisión bajo Incertidumbre").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("El proyecto industrial prevé dos escenarios: Base (+35% demanda, 10.92 buques/día) y Optimista (+100% demanda, 16.17 buques/día). Dado que la capacidad física de 3 bermas es de ~9.6 buques/día, ante cualquiera de los dos escenarios la infraestructura actual COLAPSA con colas infinitas (rho > 1.13).")
    doc.add_paragraph("Se aplicaron los criterios de decisión bajo incertidumbre pura para evaluar si invertir en la 4ª berma:")
    doc.add_paragraph("• Wald (Maximin / Pesimista): La peor consecuencia de Mantener 3 Bermas es el colapso masivo (-USD 1.200M), mientras que para Construir 4ª Berma es un beneficio neto de +USD 47.8M. Decisión: Construir 4ª Berma.")
    doc.add_paragraph("• Savage (Minimax Regret): El arrepentimiento máximo de no invertir si se materializa el proyecto industrial es de USD 850M a USD 1.200M. El arrepentimiento de invertir es USD 0M (estrategia dominante). Decisión: Construir 4ª Berma.")
    doc.add_paragraph("• Hurwicz (alfa = 0.5) y Laplace (Equiprobable): Construir 4ª Berma arroja valores esperados de +USD 248.9M y +USD 282.6M, frente a pérdidas de -USD 600M y -USD 567M de no invertir.")
    add_callout(doc, "La convicción del directorio respecto a que el escenario base se materializará es formalmente irrelevante en criterios de incertidumbre no probabilística, pero ratifica plenamente la conveniencia de invertir en la 4ª berma, la cual es una alternativa estrictamente dominante en todas las condiciones posibles.", "CRITERIO DE DECISIÓN FORMAL")

    # Consigna g
    h2 = doc.add_heading(level=2)
    h2.add_run("Consigna g: Análisis de Repago de la 4ª Berma (USD 12M)").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("• Inversión: USD 12.000.000 (Vida útil: 20 años). Costo de inmovilización: USD 15.000 a USD 30.000 / día (media USD 22.500/día).")
    doc.add_paragraph("• Demora evitada: Incorporar la 4ª berma reduce la estadía en 17.71 horas por buque. Para los 2.951 buques/año actuales, representa un ahorro de 52.260 horas-buque/año = 5.97 años-buque de inmovilización evitados al año.")
    doc.add_paragraph("• Ahorro económico anual: USD 48.99 Millones/año (rango: USD 32.7M a 65.3M/año).")
    doc.add_paragraph("• Período de Repago (Payback): Payback = USD 12M / USD 48.99M/año = 0.24 años (~2.9 meses). Rango: 2.2 a 4.4 meses.")
    
    # Imagen Fig 3
    if os.path.exists("plots/fig3_repago_berma.png"):
        doc.add_picture("plots/fig3_repago_berma.png", width=Inches(5.8))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("Figura 3: Período de Repago de la Inversión en 4ª Berma (USD 12M) vs. Costo de Inmovilización")
        r_cap.font.italic = True
        r_cap.font.size = Pt(8.5)

    doc.add_page_break()

    # -------------------------------------------------------------
    # SECCIÓN 4: VALIDACIÓN ESTADÍSTICA (TUKEY HSD)
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    h1.add_run("Sección 4: Validación Estadística con Test de Tukey HSD").font.color.rgb = COLOR_PRIMARY
    
    doc.add_paragraph("Para certificar con rigor científico que las diferencias observadas entre configuraciones no son artefactos del azar muestral, se realizó un Test de Comparaciones Múltiples de Tukey HSD (FWER = 0.05) sobre 1.500 réplicas por escenario:")
    
    t_tukey = doc.add_table(rows=5, cols=6)
    t_data = [
        ["Comparación de Escenarios", "Diferencia Medias", "p-valor adj.", "IC 95% Inferior", "IC 95% Superior", "¿Significativo?"],
        ["Actual (3G) vs 4 Grúas (4G)", "-8.30 h", "0.000", "-9.72 h", "-6.88 h", "Sí (Rechaza H0)"],
        ["Actual (3G) vs Crucero Exclusivo", "+24.08 h", "0.000", "+22.66 h", "+25.50 h", "Sí (Rechaza H0)"],
        ["Actual (3G) vs Camión Penalizado", "-1.05 h", "0.228", "-2.47 h", "+0.37 h", "No"],
        ["4 Grúas vs Crucero Exclusivo", "+32.38 h", "0.000", "+30.96 h", "+33.79 h", "Sí (Rechaza H0)"]
    ]
    for r_idx, row in enumerate(t_data):
        for c_idx, val in enumerate(row):
            t_tukey.cell(r_idx, c_idx).paragraphs[0].add_run(val)
    format_table(t_tukey, header_bg="1F4E79")
    
    # Imagen Fig 4
    if os.path.exists("plots/fig4_tukey_hsd.png"):
        doc.add_picture("plots/fig4_tukey_hsd.png", width=Inches(5.8))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("Figura 4: Diagrama de Intervalos de Confianza al 95% del Test de Tukey HSD")
        r_cap.font.italic = True
        r_cap.font.size = Pt(8.5)

    # -------------------------------------------------------------
    # SECCIÓN 5: CONCLUSIONES Y LIBRERÍAS
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    h1.add_run("Sección 5: Conclusiones Estratégicas y Librerías Utilizadas").font.color.rgb = COLOR_PRIMARY
    
    doc.add_paragraph("Hoja de Ruta Recomendada a la Dirección del Consorcio:")
    doc.add_paragraph("1. Corto Plazo: Adquirir la 4ª grúa pórtico STS para normalizar la estadía en torno a 16.46 h y neutralizar la amenaza de éxodo de las navieras al puerto capital.")
    doc.add_paragraph("2. Inversión en Infraestructura: Ejecutar inmediatamente la construcción de la 4ª berma (USD 12M). Su período de repago de menos de 3 meses y el ahorro de 5.97 años-buque anuales la convierten en una inversión con retorno excepcional que protege al puerto ante el proyecto industrial.")
    doc.add_paragraph("3. Política Comercial de Cruceros: Rechazar la cláusula de reserva exclusiva. Ofrecer atraque condicional a disponibilidad de berma o condicionar la exclusividad a la entrada en operaciones de la 4ª berma.")
    doc.add_paragraph("4. Gestión de Turnos: Eliminar las paradas de guardia de 15 min mediante relevos de personal 'en caliente' y eliminar el alistamiento de la 2ª grúa nocturna.")

    h2 = doc.add_heading(level=2)
    h2.add_run("Librerías Utilizadas").font.color.rgb = COLOR_SECONDARY
    
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
    print(f"Documento Word guardado exitosamente en: {output_path}")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else str(__import__("src.paths", fromlist=["BASE_DIR"]).BASE_DIR / "INFORME_EJECUTIVO_PUERTO_SUR.docx")
    build_word_report(out)
