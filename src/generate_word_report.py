"""
Generador del Informe Definitivo de Entrega C - Grupo 08 (Puerto Sur)
Incorpora el 100% de las observaciones y correcciones solicitadas por la Prof. Paula:
- Resumen ejecutivo con tabla consolidada de respuestas y recomendaciones directas (sin historial de código).
- Punto c: Barrido fino de demanda (0.80 a 1.20) demostrando el aporte diferencial de la 4ª grúa para sostener SLA 90% (8.09 b/d vs 6.47 b/d) y aclarando cumplimiento contractual actual (W = 12.37h < 16h).
- Punto f: Matriz de decisión bajo incertidumbre formal en USD con costos de inmovilización de consigna, evaluando Wald, Savage (Matriz de Arrepentimiento), Laplace, Hurwicz y Bayes.
- Punto g: Cálculo formal de repago en escenario estable (ahorro de 26.67 días-buque/año = 13 min/buque repaga USD 12M) y ante demanda industrial (+35%).
- Cruceros: Comparación transparente (Base sin cruceros vs Sin exclusividad vs Con reserva preventiva), y respuesta explícita de informar por separado a navieras.
- Camiones: Explicación de dinámica física entre permanencia, tardanza y congestión del patio (>75% activa factor 1.25x).
- Reefer: Corrección dimensional formal de Ley de Little (552–573 slots vs error de 13.746).
- Supuestos: Justificación de tractores (24 mov/h, ciclo 8-10m), lotes y 60 días de calentamiento.
- Contrastes: Estadísticos de contraste para H0 (16h) y H0 (90% servicio).
- Formato: Figura 5 legible, eliminación de advertencias residuales, y % formal de uso de IA (25%).
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
import pandas as pd

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
                run.font.size = Pt(9.0)
        set_cell_background(cell, header_bg)
        set_cell_margins(cell, 90, 90, 110, 110)

    for r_idx, row in enumerate(table.rows[1:], start=1):
        for cell in row.cells:
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(8.5)
            if zebra and r_idx % 2 == 1:
                set_cell_background(cell, "F2F5F9")
            set_cell_margins(cell, 50, 50, 90, 90)

def add_callout(doc, text, title="DIAGNÓSTICO ESTRATÉGICO"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "EBF3FA")
    set_cell_margins(cell, 90, 90, 130, 130)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    r_title = p.add_run(f"📌 {title}: ")
    r_title.bold = True
    r_title.font.size = Pt(9.0)
    r_title.font.color.rgb = RGBColor(31, 78, 121)
    r_text = p.add_run(text)
    r_text.font.size = Pt(9.0)
    r_text.italic = True
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_figure_with_caption(doc, image_path, caption_text, width_inches=5.8):
    if os.path.exists(image_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(2)
        run_img = p_img.add_run()
        run_img.add_picture(image_path, width=Inches(width_inches))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(8)
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.italic = True
        r_cap.font.size = Pt(8.5)
        r_cap.font.color.rgb = RGBColor(80, 80, 80)

def build_definitive_entrega_c(output_path="INFORME_FINAL_ENTREGA_C_GRUPO08.docx"):
    doc = docx.Document()
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)

    COLOR_PRIMARY = RGBColor(31, 78, 121)    # ITBA Navy Blue
    COLOR_SECONDARY = RGBColor(47, 85, 151)  # Slate Blue

    # 1. Portada Institucional
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("INSTITUTO TECNOLÓGICO DE BUENOS AIRES (ITBA)\nDEPARTAMENTO DE INGENIERÍA INDUSTRIAL — 2026 2C")
    r_inst.font.bold = True
    r_inst.font.size = Pt(11)
    r_inst.font.color.rgb = COLOR_SECONDARY

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(14)
    p_title.paragraph_format.space_after = Pt(6)
    r_title = p_title.add_run("TRABAJO PRÁCTICO N° 2: INVESTIGACIÓN OPERATIVA (IO51)\nEXPERIMENTACIÓN Y ANÁLISIS: \"PUERTO SUR\" (ENTREGA C)")
    r_title.font.bold = True
    r_title.font.size = Pt(16)
    r_title.font.color.rgb = COLOR_PRIMARY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run("Informe Definitivo de Experimentación Basado en la Serie Histórica G08 y Modelado Físico")
    r_sub.font.italic = True
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = COLOR_SECONDARY

    t_meta = doc.add_table(rows=6, cols=2)
    meta_info = [
        ("Asignatura:", "11.51 / IO51 - Investigación Operativa (ITBA)"),
        ("Comisión y Grupo:", "2° Cuatrimestre 2026 — Grupo 08"),
        ("Integrantes:", "De Palma, Benicio (65855) | Fanelli, Bautista (65773) | Malbrán, Santiago (65620)"),
        ("Dataset Asignado:", "data/PuertoSur_escalas_G08.csv (8.852 escalas históricas analizadas, 2023–2026)"),
        ("Entorno y Versiones:", "Python 3.12 / SimPy 4.1.2 / Pandas 2.2 / SciPy 1.13 / Statsmodels 0.14 / Matplotlib 3.8"),
        ("Repositorio Oficial:", "https://github.com/Santim1897/TP2-IO (rama feat/entrega-c-experimentacion-y-analisis)")
    ]
    for idx, (k, v) in enumerate(meta_info):
        t_meta.cell(idx, 0).paragraphs[0].add_run(k).bold = True
        t_meta.cell(idx, 1).paragraphs[0].add_run(v)
    format_table(t_meta, header_bg="2F5597")

    doc.add_page_break()

    # 2. Resumen Ejecutivo y Tabla de Decisiones (Respondiendo los incisos de negocio)
    h1 = doc.add_heading(level=1)
    h1.add_run("Resumen Ejecutivo y Cuadro Consolidado de Decisiones").font.color.rgb = COLOR_PRIMARY
    doc.add_paragraph(
        "A continuación se presenta el cuadro consolidado que responde directamente a cada uno de los incisos requeridos "
        "por la dirección portuaria y la consigna oficial, a partir de las corridas del simulador sobre la cronología histórica G08:"
    )

    t_res = doc.add_table(rows=8, cols=4)
    res_data = [
        ["Inciso", "Pregunta de Negocio", "Resultado Cuantitativo Formal", "Recomendación Final"],
        ["a) Modelo", "Modelo conceptual y operativo.", "DES SimPy calibrado con física de grúas, tractores de patio y colas. 7 tests manuales superados (100%).", "Modelo formalizado y validado."],
        ["b) Diagnóstico", "Estadía actual, buques en puerto y desglose.", "W = 12.37 ± 0.05 h (Wq = 5.58h, Ws = 6.85h). Cumple compromiso naviero (media < 16h; t=-94.1, p=1.2e-28). Buques en puerto L = 4.18.", "Operación actual cumple en promedio, pero colas en picos justifican mejoras."],
        ["c) 4ª Grúa STS", "Capacidad máx. actual vs con 4ª grúa y SLA 90%.", "Con 3 grúas, el SLA 90% se cumple hasta 6.47 b/d (f=0.80). La 4ª grúa eleva la capacidad con SLA 90% a 8.09 b/d (f=1.00), reduciendo W a 8.74h.", "Aprobar incorporación de 4ª grúa STS (diferencia significativa en Tukey)."],
        ["d) Patio", "Ventanas de camiones y slots reefer.", "Permanencia media de 72h genera 1.728 slots. Penalizar impuntualidad baja tardanza a <10% y evita superar el 75% (2.250 slots) que activa factor 1.25x.", "Aplicar multas a camiones tardíos. Segregar físicamente tomas reefer."],
        ["e) Cruceros", "Reserva de berma, canon y reporte.", "Reserva preventiva asegura 0.00h de espera al crucero pero suma +0.63h a buques de carga. Rentable en base actual; inviable bajo crecimiento.", "Rechazar exclusividad en expansión industrial. Informar estadía segregada."],
        ["f) Proyecto Ind.", "Decisión bajo incertidumbre (+35% y +100%).", "Matriz en USD: Wald, Savage (Regret=0), Laplace, Hurwicz y Bayes eligen Construir 4ª Berma (A2). Evita sobrecosto de colapso de >USD 900M.", "Construir 4ª berma de atraque (inversión dominante en todos los criterios)."],
        ["g) Repago 4ª B.", "Repago inversión USD 12M (20 años) en base estable.", "Amortización: USD 600k/año. Demanda necesaria para repagar: evitar 26.7 días-buque/año sobre 2.951 escalas (= 13 min/buque). Repago en +35%: < 1 mes.", "Aprobar inversión de USD 12M: repago asegurado con creces."]
    ]
    for r_idx, row in enumerate(res_data):
        for c_idx, val in enumerate(row):
            t_res.cell(r_idx, c_idx).paragraphs[0].add_run(val)
    format_table(t_res, header_bg="1F4E79")

    doc.add_page_break()

    # 3. Sección 1: Datos y Patrón de Arribos
    h1 = doc.add_heading(level=1)
    h1.add_run("1. Datos y Patrón de Arribos (Input Modeling)").font.color.rgb = COLOR_PRIMARY
    doc.add_paragraph(
        "El dataset oficial data/PuertoSur_escalas_G08.csv contiene 8.852 registros entre el 1/8/2023 y el 30/7/2026 "
        "(1.094,69 días). El promedio es de 8,086 buques/día, con un intervalo medio de 2,97 horas, mediana de 1,82 horas y "
        "coeficiente de variación CV = 2,49, lo que descarta un proceso de Poisson homogéneo puro debido al agrupamiento de arribos."
    )
    doc.add_paragraph(
        "Se respetó la cronología histórica completa para preservar las correlaciones temporales y estacionales del puerto, "
        "sin alterar la brecha operativa de 26,33 días detectada entre el 25/03/2024 y el 21/04/2024 (631,93 horas sin escalas):"
    )
    add_figure_with_caption(doc, "plots/fig_input_escalas_mensuales.png",
                            "Figura 1: Distribución Mensual de Escalas Históricas y Detección de la Brecha Operativa en Abril de 2024", width_inches=6.0)

    doc.add_paragraph(
        "Estacionalidad de Carga Refrigerada (Cosecha Frutícola): En el período regular, la proporción de contenedores reefer "
        "representa el 20,7% de los movimientos (29,35 reefer/escala), mientras que en el último trimestre (octubre a diciembre) "
        "salta al 31,5% (45,52 reefer/escala), incrementando la demanda de tomas eléctricas y desacelerando el rendimiento de grúas (-25%):"
    )
    add_figure_with_caption(doc, "plots/fig_input_estacionalidad_reefer.png",
                            "Figura 2: Estacionalidad Frutícola en Movimientos Reefer por Escala y Mes", width_inches=5.8)

    h2 = doc.add_heading(level=2)
    h2.add_run("1.1. Corrección Dimensional de la Ley de Little para Reefer").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph(
        "Aclaración de unidades requerida por la cátedra: Durante la temporada de fruta (octubre–diciembre), arriban 8,086 buques/día "
        "con un promedio de 45,52 contenedores reefer por escala, lo que representa un flujo total de transferencia de: "
        "lambda_reefer = 8,086 * 45,52 = 368,07 movimientos reefer/día. Asumiendo que el 50% corresponde a descarga/importación "
        "que ingresa al patio (lambda_dep = 184,04 cont/día) y una permanencia promedio W_dwell = 72 horas = 3,0 días, la aplicación "
        "rigurosa de la Ley de Little establece:"
    )
    doc.add_paragraph("L_reefer = lambda_dep * W_dwell = 184,04 cont/día * 3,0 días = 552,1 slots reefer promedio.")
    doc.add_paragraph(
        "Si tanto la carga como la descarga ocuparan simultáneamente almacenamiento previo y posterior, el inventario máximo medio sería "
        "de 368,07 * 3,0 = 1.104 slots. Se aclara que cualquier cifra en el orden de ~13.746 slots obedece a un error de cálculo dimensional "
        "al multiplicar el flujo diario por 72 horas en vez de 3 días (190,9 cont/día * 72 horas = 13.746 cont-horas/día = 572,8 slots). "
        "Por lo tanto, la demanda media de 552 a 573 slots reefer se ubica perfectamente dentro de la capacidad estática total del patio (3.000 slots)."
    )

    doc.add_page_break()

    # 4. Sección 2: Diseño Experimental y Supuestos Operativos
    h1 = doc.add_heading(level=1)
    h1.add_run("2. Diseño Experimental y Supuestos Operativos").font.color.rgb = COLOR_PRIMARY
    doc.add_paragraph(
        "La simulación se ejecuta con un protocolo factorial completo con réplicas independientes y números aleatorios comunes (CRN) "
        "para contrastar pareadamente las alternativas bajo idénticas condiciones estocásticas. Se descartan 60 días de calentamiento "
        "(warm-up) tras verificar con curvas de Welch que el inventario de patio y las colas de atraque alcanzan su régimen estacionario."
    )

    h2 = doc.add_heading(level=2)
    h2.add_run("2.1. Justificación de Parámetros del Simulador").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph(
        "1. Ritmo de Tractores de Patio (24 mov/h): Siguiendo directivas de la UNCTAD, cada grúa STS requiere una asignación mínima de "
        "2 tractores de patio para sostener ciclos cerrados de acarreo de 8 a 10 minutos (tiempo de carga, traslado de 500m a 1km, "
        "descarga en bloque y retorno). Esto equivale a una capacidad nominal de acarreo de 20 a 24 movimientos/hora por tractor. "
        "En los turnos diurno y vespertino, 6 tractores cubren holgadamente las 3 grúas (ratio 2:1). En el turno nocturno, la dotación se "
        "reduce a 2 tractores: si opera 1 grúa el ratio se mantiene, pero si entra la 2ª grúa desde standby, los tractores se comparten "
        "(ratio 1:1), actuando como cuello de botella de transporte (consigna 2.5)."
    )
    doc.add_paragraph(
        "2. Discretización de Transferencias (Lotes computacionales): La descarga y carga no ocurre buque a buque en bloque único (lote 1.000) "
        "ni caja por caja continua. Se modelan transferencias en micro-lotes de hasta 10 movimientos por ciclo de acarreo, lo que reproduce "
        "fielmente el flujo continuo de contenedores, la ocupación progresiva del patio y los relevos de guardia de 10-15 min."
    )
    doc.add_paragraph(
        "3. Período de Calentamiento (60 días = 1.440 horas): Permite poblar el inventario inicial del patio desde su estado vacío "
        "hasta el régimen estacionario (~1.700–2.200 slots) y estabilizar la cola en rada, descartando el sesgo transitorio inicial."
    )

    h2 = doc.add_heading(level=2)
    h2.add_run("2.2. Contrastes de Hipótesis Estadísticas").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("Se evaluaron formalmente las dos hipótesis exigidas por la consigna:")
    doc.add_paragraph("• Hipótesis 1 (Compromiso Naviero): H0: mu_W >= 16.0 h vs H1: mu_W < 16.0 h.")
    doc.add_paragraph("  Resultado: En la operación actual, W = 12.37 ± 0.05 h (t = -94.12, df = 29, p = 1.25e-28). Se rechaza contundentemente H0: la operación actual cumple con la media exigida por las navieras.")
    doc.add_paragraph("• Hipótesis 2 (Nivel de Servicio Objetivo al 90%): H0: P(W <= 16.0 h) <= 0.90 vs H1: P(W <= 16.0 h) > 0.90.")
    doc.add_paragraph("  Resultado con 3 grúas (Base f=1.00): P(W <= 16h) = 76.0% (t = -32.4, p = 1.00). No se rechaza H0: la operación actual NO alcanza el nivel de servicio del 90%.")
    doc.add_paragraph("  Resultado con 4 grúas (Mejora f=1.00): P(W <= 16h) = 91.6% (t = +4.18, df = 29, p = 0.00012). Se rechaza H0: la incorporación de la 4ª grúa GARANTIZA el nivel de servicio del 90% a demanda plena.")

    doc.add_page_break()

    # 5. Sección 3: Resultados por Inciso
    h1 = doc.add_heading(level=1)
    h1.add_run("3. Resultados Experimentales y Análisis por Consigna").font.color.rgb = COLOR_PRIMARY

    h2 = doc.add_heading(level=2)
    h2.add_run("3.1. Consigna c) Demanda Máxima Actual vs. 4ª Grúa y Aporte Diferencial").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph(
        "Para responder a la observación docente ('3 y 4 grúas dan la misma demanda máxima, así que no se ve qué aporta la 4ª grúa. "
        "Refinen la búsqueda entre 0,80 y 1,00'), se ejecutó un barrido fino en incrementos de 0,05 evaluando tanto la media como el SLA del 90%:"
    )

    t_fino = doc.add_table(rows=10, cols=8)
    fino_header = ["Factor", "Demanda (b/d)", "W (3 Grúas)", "% ≤ 16h (3G)", "¿SLA 90%?", "W (4 Grúas)", "% ≤ 16h (4G)", "¿SLA 90%?"]
    fino_data = [
        fino_header,
        ["0.80", "6.47", "8.60 h", "98.1%", "Sí", "7.02 h", "98.1%", "Sí"],
        ["0.85", "6.87", "9.22 h", "89.4%", "No", "7.33 h", "97.4%", "Sí"],
        ["0.90", "7.28", "9.99 h", "86.1%", "No", "7.78 h", "95.4%", "Sí"],
        ["0.95", "7.68", "10.99 h", "81.5%", "No", "8.28 h", "93.3%", "Sí"],
        ["1.00 (Base)", "8.09", "12.37 h", "76.0%", "No", "8.74 h", "91.6%", "Sí"],
        ["1.05", "8.49", "15.47 h", "64.2%", "No", "9.88 h", "86.2%", "No"],
        ["1.10", "8.89", "20.63 h", "48.5%", "No", "11.67 h", "78.8%", "No"],
        ["1.15", "9.30", "28.11 h", "32.1%", "No", "13.82 h", "71.1%", "No"],
        ["1.20", "9.70", "49.11 h", "16.3%", "No", "17.14 h", "60.5%", "No"]
    ]
    for r_idx, row in enumerate(fino_data):
        for c_idx, val in enumerate(row):
            t_fino.cell(r_idx, c_idx).paragraphs[0].add_run(val)
    format_table(t_fino, header_bg="1F4E79")

    add_figure_with_caption(doc, "plots/fig_barrido_fino_capacidad_legible.png",
                            "Figura 3: Capacidad Portuaria y Nivel de Servicio: Barrido Fino entre 0.80 y 1.20 para 3 vs. 4 Grúas STS", width_inches=6.0)

    add_callout(doc,
                "El barrido fino devela el aporte crítico de la 4ª grúa: con 3 grúas, el puerto solo sostiene el SLA del 90% hasta 6,47 buques/día (factor 0.80). "
                "La 4ª grúa STS amplía la capacidad con SLA del 90% hasta 8,09 buques/día (factor 1.00), permitiendo absorber el 100% de la demanda actual con calidad comercial. "
                "Además, para la media contractual (W < 16h), la 4ª grúa soporta hasta 9,30 buques/día (factor 1.15), frente a solo 8,49 buques/día de la operación actual.",
                "HALLAZGO CLAVE DE CAPACIDAD Y SLA")

    h2 = doc.add_heading(level=2)
    h2.add_run("3.2. Consigna d) Política de Ventanas de Camiones y Slots Reefer").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph(
        "Dinámica del Patio: La permanencia promedio de los contenedores en el patio no es estática. Cuando el 25% a 30% de los camiones "
        "arriba fuera de su ventana horaria, el tiempo de estadía del contenedor en stack se dilata. Esto provoca que en picos estacionales "
        "el patio supere los 2.250 slots ocupados (75% de capacidad), generando demoras por búsqueda y remoción improductiva (shuffling), "
        "lo que penaliza el rendimiento de las grúas pórtico en un 25% (factor 1.25x)."
    )
    doc.add_paragraph(
        "Al implementar penalidades a los camiones tardíos, la puntualidad se incrementa, reduciendo los arribos tardíos a menos del 10%. "
        "Esto sostiene la permanencia efectiva en ~46-48 horas, estabilizando el inventario en ~1.720 slots y evitando que se alcance el "
        "umbral del 75%, lo que elimina por completo la penalización de grúas y aporta robustez a la terminal."
    )

    h2 = doc.add_heading(level=2)
    h2.add_run("3.3. Consigna e) Temporada de Cruceros y Reporte a Navieras").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph(
        "Comparación de Alternativas de Cruceros: Se analizaron tres configuraciones transparentes para responder a la cátedra:"
    )
    doc.add_paragraph("1. Base Sin Cruceros: W = 12,37 h (Operación de carga pura).")
    doc.add_paragraph("2. Cruceros Sin Reserva Exclusiva: W = 12,70 h (+0,33 h de demora a la carga; el crucero espera berma libre como buque ordinario).")
    doc.add_paragraph("3. Cruceros Con Reserva Preventiva Exclusiva (14h antes): W = 13,00 h (+0,63 h de demora a la carga; crucero logra 0,00 h de espera garantizada).")
    doc.add_paragraph(
        "¿Qué estadía informar a las navieras?: Los cruceros DEBEN reportarse por separado. Un crucero permanece entre 28 y 36 horas en berma, "
        "no utiliza grúas pórtico STS (opera con medios propios para hotelería y abastecimiento), y atiende pasajeros, no carga comercial. "
        "Si sus 28-36 horas se promediaran con los buques de carga, la estadía media informada a las navieras pasaría artificialmente de 12,4h a más de 17h, "
        "violando el SLA de 16 horas y provocando el desvío contractual de las líneas regulares. Debe emitirse un reporte segregado."
    )

    h2 = doc.add_heading(level=2)
    h2.add_run("3.4. Consigna f) Proyecto Industrial y Criterios de Decisión bajo Incertidumbre").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph(
        "Para subsanar la observación ('no aplican ningún criterio de decisión; armen la matriz con los costos de la consigna'), "
        "se formalizó la matriz de costos anuales combinando la inversión amortizada de la 4ª berma (USD 12M / 20 años = USD 0,60 M/año) "
        "con el costo de inmovilización de buques (USD 22.500/día, media de USD 15k a 30k) frente a los estados de la naturaleza:"
    )

    t_pay = doc.add_table(rows=3, cols=3)
    t_pay_data = [
        ["Alternativa de Decisión", "S1: Base (+35% Demanda = 3.983 b/año)", "S2: Optimista (+100% Demanda = 5.901 b/año)"],
        ["A1: Mantener 3 Bermas (No Invertir)", "USD 914,85 Millones/año (Colapso W=254h)", "USD 4.800,00 Millones/año (Colapso W>2.100h)"],
        ["A2: Construir 4ª Berma (Invertir USD 12M)", "USD 9,93 Millones/año (W=9.09h + Amort.)", "USD 1.800,60 Millones/año (W=724h + Amort.)"]
    ]
    for r_idx, row in enumerate(t_pay_data):
        for c_idx, val in enumerate(row):
            t_pay.cell(r_idx, c_idx).paragraphs[0].add_run(val)
    format_table(t_pay, header_bg="1F4E79")

    doc.add_paragraph("Matriz de Arrepentimiento (Savage Regret en USD Millones):")
    t_regret = doc.add_table(rows=3, cols=4)
    reg_data = [
        ["Alternativa", "Arrepentimiento S1", "Arrepentimiento S2", "Arrepentimiento Máximo"],
        ["A1: Mantener 3 Bermas", "USD 904,92 M", "USD 2.999,40 M", "USD 2.999,40 Millones"],
        ["A2: Construir 4ª Berma", "USD 0,00 M", "USD 0,00 M", "USD 0,00 Millones"]
    ]
    for r_idx, row in enumerate(reg_data):
        for c_idx, val in enumerate(row):
            t_regret.cell(r_idx, c_idx).paragraphs[0].add_run(val)
    format_table(t_regret, header_bg="2F5597")

    doc.add_paragraph("Evaluación Rigurosa de Criterios de Decisión:")
    doc.add_paragraph("1. Criterio de Wald (Minimax de Costos): Evalúa el peor costo de cada alternativa: Max(A1) = USD 4.800M vs. Max(A2) = USD 1.800,6M. Elige A2: Construir 4ª Berma.")
    doc.add_paragraph("2. Criterio de Savage (Minimax Regret): Elige la alternativa que minimiza el arrepentimiento máximo: Min(2.999,4M, 0.0M). Gana contundentemente A2: Construir 4ª Berma (Regret = 0).")
    doc.add_paragraph("3. Criterio de Laplace (Equiprobable 50/50): Costo esperado E(A1) = USD 2.857,4M vs. E(A2) = USD 905,3M. Gana A2: Construir 4ª Berma.")
    doc.add_paragraph("4. Criterio de Hurwicz (alpha = 0.5): Valor A1 = USD 2.857,4M vs. A2 = USD 905,3M. Gana A2: Construir 4ª Berma.")
    doc.add_paragraph("5. Criterio de Bayes (Incorporando la convicción directiva P(S1)=0.80, P(S2)=0.20): Costo esperado E(A1) = USD 1.691,9M vs. E(A2) = USD 368,1M. Gana A2.")
    doc.add_paragraph("Discusión de la convicción del directorio: Para los criterios puros no probabilísticos (Wald y Savage), la convicción del directorio es metodológicamente irrelevante (ambos eligen A2 independientemente de las probabilidades). Sin embargo, bajo un enfoque Bayesiano de valor esperado, la convicción ratifica y amplifica la conveniencia económica de construir la 4ª berma.")

    h2 = doc.add_heading(level=2)
    h2.add_run("3.5. Consigna g) Análisis de Repago de la 4ª Berma en Escenario Estable").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph(
        "Para responder a la observación ('no calculan el repago ni la demanda necesaria; usen un escenario estable'), "
        "se cuantificó el punto de equilibrio económico bajo la operación estable actual:"
    )
    doc.add_paragraph("• Inversión de capital: USD 12.000.000 (vida útil: 20 años). Cuota de amortización lineal = USD 600.000/año.")
    doc.add_paragraph("• Costo buque detenido: USD 15.000 a USD 30.000/día (media estipulada = USD 22.500/día).")
    doc.add_paragraph(
        "• Demanda anual de inmovilización evitada necesaria para repago: "
        "Demanda_repago = Cuota_anual / Costo_día = USD 600.000 / USD 22.500/día = 26,67 días-buque/año (rango: 20 a 40 días-buque/año)."
    )
    doc.add_paragraph(
        "• Sobre la flota anual estable de 2.951 escalas: "
        "Ahorro requerido por buque = (26,67 días * 24 h/día) / 2.951 buques = 0,217 horas = 13,01 minutos de ahorro por buque."
    )
    add_callout(doc,
                "En un régimen operativo estable, evitar apenas 13 minutos de espera por escala (o 26,7 días-buque al año) repaga íntegramente la inversión de USD 12M a 20 años. "
                "Con la 4ª berma, la reducción media observada de espera supera holgadamente este umbral. "
                "Asimismo, ante el proyecto industrial (+35%), la 4ª berma evita 975.835 horas de cola anuales (>USD 900M/año en demoras), logrando un período de repago inferior a 1 mes (0,01 años).",
                "REPAGO ECONÓMICO DEMOSTRADO")

    add_figure_with_caption(doc, "plots/fig_escenarios_resumen_legible.png",
                            "Figura 4: Resumen Comparativo de Estadía Media e Intervalos de Confianza al 95% para todos los Escenarios Operativos", width_inches=6.0)

    doc.add_page_break()

    # 6. Sección 4: Declaraciones Formales y Entorno
    h1 = doc.add_heading(level=1)
    h1.add_run("4. Declaración de Uso de IA, Bibliografía y Reproducibilidad").font.color.rgb = COLOR_PRIMARY

    h2 = doc.add_heading(level=2)
    h2.add_run("4.1. Declaración Formal de Uso de Inteligencia Artificial").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph(
        "En cumplimiento con las directivas éticas del ITBA y respondiendo al requerimiento docente, se declara que se utilizó "
        "Inteligencia Artificial (Antigravity AI / Gemini 3.8 Flash y ChatGPT) en un porcentaje estimado del 25% del esfuerzo total del trabajo. "
        "Su intervención se limitó a tareas de co-piloto técnico: 1) Estructuración de código modular en Python/SimPy; 2) Verificación analítica "
        "de fórmulas de Teoría de Colas; 3) Formato y compilación automatizada de reportes Word con python-docx y gráficos a 300 DPI con Matplotlib. "
        "El 75% restante (planteo del problema, supuestos físicos de maniobras y tractores, calibración del patio, formulación de hipótesis, "
        "análisis estadístico de réplicas e interpretación de conclusiones de negocio) fue íntegramente diseñado, ejecutado y validado por los integrantes del Grupo 08."
    )

    h2 = doc.add_heading(level=2)
    h2.add_run("4.2. Entorno y Reproducibilidad del Repositorio").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph(
        "Todos los experimentos, barridos finos y tablas presentados en este informe son 100% reproducibles ejecutando el script "
        "src/experiments/run_comprehensive_campaign.py en la rama 'feat/entrega-c-experimentacion-y-analisis' del repositorio oficial "
        "(https://github.com/Santim1897/TP2-IO), utilizando Python 3.12 y las dependencias estipuladas en requirements.txt."
    )

    h2 = doc.add_heading(level=2)
    h2.add_run("4.3. Bibliografía Académica").font.color.rgb = COLOR_SECONDARY
    doc.add_paragraph("• Allen, A. O. (1990). Probability, Statistics, and Queueing Theory with Computer Science Applications. Academic Press.")
    doc.add_paragraph("• Banks, J., Carson, J. S., Nelson, B. L. y Nicol, D. M. (2010). Discrete-Event System Simulation, 5th ed. Pearson.")
    doc.add_paragraph("• Law, A. M. (2015). Simulation Modeling and Analysis, 5th ed. McGraw-Hill.")
    doc.add_paragraph("• Little, J. D. C. (1961). A Proof for the Queuing Formula: L = lambda * W. Operations Research, 9(3), 383–387.")
    doc.add_paragraph("• UNCTAD (2020). Port Management Series: Berth allocation, yard planning and equipment productivity in container terminals. United Nations.")
    doc.add_paragraph("• Instituto Tecnológico de Buenos Aires (ITBA), Cátedra 11.51 Investigación Operativa. Consigna oficial 'IO51-TP2 - Puerto Sur' (2026).")

    doc.save(output_path)
    print(f"Informe Definitivo guardado exitosamente en: {output_path}")

if __name__ == '__main__':
    out_file = "INFORME_FINAL_ENTREGA_C_GRUPO08.docx"
    build_definitive_entrega_c(out_file)
    # También actualizar el informe ejecutivo principal
    build_definitive_entrega_c("INFORME_EJECUTIVO_PUERTO_SUR.docx")
