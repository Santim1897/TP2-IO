"""
Generador de Diagramas y Gráficos Formales para el Modelo Conceptual (TP2 Puerto Sur - Grupo 8)
Genera:
1. fig_idef0_a_menos_0.png: Diagrama de Contexto IDEF0 A-0
2. fig_idef0_a0_descomposicion.png: Diagrama de Descomposición IDEF0 A0
3. fig_relacion_variables_causal.png: Diagrama de Influencias Causal (CLD)
4. fig_logica_flujo_buque.png: Diagrama de Flujo Lógico Operativo del Buque
5. fig_elementos_simulador.png: Arquitectura de Componentes del Simulador SimPy
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

out_dir = os.path.join(os.path.dirname(__file__), "..", "plots")
os.makedirs(out_dir, exist_ok=True)

# Configuración general
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 10

# =========================================================================
# 1. DIAGRAMA IDEF0 A-0: CONTEXTO GENERAL
# =========================================================================
def draw_idef0_a0_context():
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 80)
    ax.axis('off')

    # Marco exterior estándar IDEF0
    border = patches.Rectangle((2, 2), 106, 76, fill=False, edgecolor='#1F4E79', linewidth=2)
    ax.add_patch(border)
    
    # Encabezado
    ax.text(5, 75.5, "ITBA - INVESTIGACIÓN OPERATIVA (IO51) | MODELO CONCEPTUAL PUERTO SUR", fontsize=9, fontweight='bold', color='#1F4E79')
    ax.text(85, 75.5, "GRUPO 08 | NODO: A-0", fontsize=9, fontweight='bold', color='#1F4E79')
    ax.plot([2, 108], [74, 74], color='#1F4E79', linewidth=1)

    # Caja Central A-0
    box = patches.Rectangle((35, 26), 40, 26, facecolor='#EBF3FA', edgecolor='#1F4E79', linewidth=2.5, zorder=3)
    ax.add_patch(box)
    ax.text(55, 41, "OPERAR TERMINAL\nPORTUARIA PUERTO SUR", ha='center', va='center', fontsize=12, fontweight='bold', color='#1F4E79', zorder=4)
    ax.text(73, 28, "A-0", ha='right', va='bottom', fontsize=10, fontweight='bold', color='#2F5597', zorder=4)

    # FLECHAS DE CONTROLES (C) - Arriba
    controls = [
        ("C1: Contratos Navieras (Umbral W <= 16 h)", 42, 70),
        ("C2: Régimen de Turnos (8h) y Paradas (10-15m)", 55, 65),
        ("C3: Capacidad de Patio (3.000 slots) y Reglas de Frío", 68, 70)
    ]
    for text, x, y_text in controls:
        ax.annotate('', xy=(x, 52), xytext=(x, y_text),
                    arrowprops=dict(facecolor='#D97706', edgecolor='#D97706', width=1.5, headwidth=7), zorder=2)
        ax.text(x, y_text + 1, text, ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#B45309')

    # FLECHAS DE ENTRADAS (I) - Izquierda
    inputs = [
        ("I1: Buques feeder en rada\n(Arribos históricos G08)", 18, 46),
        ("I2: Carga de importación/exportación\n(Dry, Reefer, OOG)", 18, 38),
        ("I3: Camiones externos de retiro\n(20-30% fuera de ventana)", 18, 30),
        ("I4: Escalas de cruceros\n(Temporada 3 meses, 2/sem)", 18, 22)
    ]
    for text, x_start, y in inputs:
        ax.annotate('', xy=(35, y), xytext=(x_start, y),
                    arrowprops=dict(facecolor='#0275D8', edgecolor='#0275D8', width=1.5, headwidth=7), zorder=2)
        ax.text(x_start - 1, y, text, ha='right', va='center', fontsize=8, color='#0275D8', fontweight='bold')

    # FLECHAS DE SALIDAS (O) - Derecha
    outputs = [
        ("O1: Buques feeder atendidos y despachados", 75, 46, 92),
        ("O2: Métricas de estadía (W, Wq, Ws)", 75, 40, 92),
        ("O3: Nivel de servicio contractual (% <= 16 h)", 75, 34, 92),
        ("O4: Utilización de bermas y grúas pórtico", 75, 28, 92),
        ("O5: Sobrecostos de buques inmovilizados (USD)", 75, 22, 92)
    ]
    for text, x_start, y, x_end in outputs:
        ax.annotate('', xy=(x_end, y), xytext=(x_start, y),
                    arrowprops=dict(facecolor='#059669', edgecolor='#059669', width=1.5, headwidth=7), zorder=2)
        ax.text(x_end + 1, y, text, ha='left', va='center', fontsize=8, color='#059669', fontweight='bold')

    # FLECHAS DE MECANISMOS (M) - Abajo
    mechanisms = [
        ("M1: 3 Bermas de atraque (o 4)", 42, 10),
        ("M2: 3 Grúas STS pórtico (o 4)", 55, 14),
        ("M3: Tractoristas y playa de contenedores", 68, 10)
    ]
    for text, x, y_text in mechanisms:
        ax.annotate('', xy=(x, 26), xytext=(x, y_text),
                    arrowprops=dict(facecolor='#7C3AED', edgecolor='#7C3AED', width=1.5, headwidth=7), zorder=2)
        ax.text(x, y_text - 1, text, ha='center', va='top', fontsize=8.5, fontweight='bold', color='#6D28D9')

    # Título en pie de plano
    ax.text(55, 4, "DIAGRAMA DE CONTEXTO IDEF0 A-0: TERMINAL PORTUARIA PUERTO SUR", ha='center', fontsize=10, fontweight='bold', color='#1F4E79')
    
    plt.tight_layout()
    plt.savefig(f"{out_dir}/fig_idef0_a_menos_0.png", dpi=300)
    plt.close()
    print("Guardado: fig_idef0_a_menos_0.png")

# =========================================================================
# 2. DIAGRAMA IDEF0 A0: DESCOMPOSICIÓN DE PRIMER NIVEL
# =========================================================================
def draw_idef0_a0_decomposition():
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 80)
    ax.axis('off')

    # Marco
    border = patches.Rectangle((2, 2), 116, 76, fill=False, edgecolor='#1F4E79', linewidth=2)
    ax.add_patch(border)
    ax.text(5, 75.5, "ITBA - INVESTIGACIÓN OPERATIVA (IO51) | DESCOMPOSICIÓN FUNCIONAL IDEF0", fontsize=9, fontweight='bold', color='#1F4E79')
    ax.text(95, 75.5, "GRUPO 08 | NODO: A0", fontsize=9, fontweight='bold', color='#1F4E79')
    ax.plot([2, 118], [74, 74], color='#1F4E79', linewidth=1)

    # 4 Actividades escalonadas (A1, A2, A3, A4)
    acts = [
        ("A1: Recepción\ny Fondeo en Rada", 12, 48, 20, 14),
        ("A2: Maniobra de\nEntrada y Atraque", 38, 38, 20, 14),
        ("A3: Operación de Grúas\ny Gestión de Patio", 65, 24, 24, 16),
        ("A4: Desatraque\ny Zarpada", 94, 12, 18, 14)
    ]
    for name, x, y, w, h in acts:
        rect = patches.Rectangle((x, y), w, h, facecolor='#EBF3FA', edgecolor='#1F4E79', linewidth=2, zorder=3)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, name, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1F4E79', zorder=4)

    # Flujo secuencial entre actividades
    # Entrada a A1
    ax.annotate('', xy=(12, 55), xytext=(4, 55), arrowprops=dict(facecolor='#0275D8', edgecolor='#0275D8', width=1.5, headwidth=6))
    ax.text(4, 57, "Arribo buques\nfeeder (G08)", fontsize=7.5, color='#0275D8', fontweight='bold')

    # A1 -> A2 (Buque convocado a muelle)
    ax.plot([32, 35, 35], [55, 55, 45], color='#1F4E79', linewidth=1.5)
    ax.annotate('', xy=(38, 45), xytext=(35, 45), arrowprops=dict(facecolor='#1F4E79', edgecolor='#1F4E79', width=1.5, headwidth=6))
    ax.text(33, 56.5, "Berma libre", fontsize=7.5, color='#1F4E79')

    # A2 -> A3 (Buque amarrado en berma)
    ax.plot([58, 61, 61], [45, 45, 34], color='#1F4E79', linewidth=1.5)
    ax.annotate('', xy=(65, 34), xytext=(61, 34), arrowprops=dict(facecolor='#1F4E79', edgecolor='#1F4E79', width=1.5, headwidth=6))
    ax.text(59, 46.5, "Amarrado\nen berma", fontsize=7.5, color='#1F4E79')

    # A3 -> A4 (Operación de carga completada)
    ax.plot([89, 91, 91], [30, 30, 19], color='#1F4E79', linewidth=1.5)
    ax.annotate('', xy=(94, 19), xytext=(91, 19), arrowprops=dict(facecolor='#1F4E79', edgecolor='#1F4E79', width=1.5, headwidth=6))
    ax.text(88, 31.5, "Carga/descarga\nfinalizada", fontsize=7.5, color='#1F4E79')

    # A4 -> Salida final
    ax.annotate('', xy=(116, 19), xytext=(112, 19), arrowprops=dict(facecolor='#059669', edgecolor='#059669', width=1.5, headwidth=6))
    ax.text(113, 21.5, "Buque zarpado\n(W total)", fontsize=7.5, color='#059669', fontweight='bold')

    # Controles superiores
    ax.annotate('', xy=(22, 62), xytext=(22, 71), arrowprops=dict(facecolor='#D97706', edgecolor='#D97706', width=1.2, headwidth=5))
    ax.text(22, 72, "Cola FIFO / Prioridad", ha='center', fontsize=7.5, color='#B45309', fontweight='bold')

    ax.annotate('', xy=(48, 52), xytext=(48, 71), arrowprops=dict(facecolor='#D97706', edgecolor='#D97706', width=1.2, headwidth=5))
    ax.text(48, 72, "Regla práctico (1-2h)", ha='center', fontsize=7.5, color='#B45309', fontweight='bold')

    ax.annotate('', xy=(77, 40), xytext=(77, 71), arrowprops=dict(facecolor='#D97706', edgecolor='#D97706', width=1.2, headwidth=5))
    ax.text(77, 72, "Turnos / Interferencia 85% / Patio >75%", ha='center', fontsize=7.5, color='#B45309', fontweight='bold')

    # Mecanismos inferiores
    ax.annotate('', xy=(22, 48), xytext=(22, 8), arrowprops=dict(facecolor='#7C3AED', edgecolor='#7C3AED', width=1.2, headwidth=5))
    ax.text(22, 6, "Rada / Fondeo", ha='center', fontsize=7.5, color='#6D28D9', fontweight='bold')

    ax.annotate('', xy=(48, 38), xytext=(48, 8), arrowprops=dict(facecolor='#7C3AED', edgecolor='#7C3AED', width=1.2, headwidth=5))
    ax.text(48, 6, "Prácticos / Remolcadores", ha='center', fontsize=7.5, color='#6D28D9', fontweight='bold')

    ax.annotate('', xy=(77, 24), xytext=(77, 8), arrowprops=dict(facecolor='#7C3AED', edgecolor='#7C3AED', width=1.2, headwidth=5))
    ax.text(77, 6, "3 Grúas STS / 3 Bermas / Patio 3000 slots", ha='center', fontsize=7.5, color='#6D28D9', fontweight='bold')

    ax.annotate('', xy=(103, 12), xytext=(103, 8), arrowprops=dict(facecolor='#7C3AED', edgecolor='#7C3AED', width=1.2, headwidth=5))
    ax.text(103, 6, "Prácticos desatraque", ha='center', fontsize=7.5, color='#6D28D9', fontweight='bold')

    ax.text(60, 3.5, "DESCOMPOSICIÓN A0: CICLO INTEGRAL DE ATENCIÓN DE ESCALAS PORTUARIAS", ha='center', fontsize=10, fontweight='bold', color='#1F4E79')

    plt.tight_layout()
    plt.savefig(f"{out_dir}/fig_idef0_a0_descomposicion.png", dpi=300)
    plt.close()
    print("Guardado: fig_idef0_a0_descomposicion.png")

# =========================================================================
# 3. DIAGRAMA DE INFLUENCIAS CAUSALES (RELACIÓN ENTRE VARIABLES)
# =========================================================================
def draw_causal_influences():
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Título
    ax.text(50, 96, "DIAGRAMA DE RELACIÓN ENTRE VARIABLES Y BUCLES DE RETROALIMENTACIÓN", ha='center', fontsize=12, fontweight='bold', color='#1F4E79')
    ax.text(50, 93, "Terminal Portuaria Puerto Sur — Modelo Conceptual Grupo 08", ha='center', fontsize=9.5, fontstyle='italic', color='#555555')

    # Nodos y Categorías de Variables
    # Cajas con colores temáticos:
    # Azul: Variables de Decisión | Verde: Exógenas/Referencia | Naranja: Estado | Rojo: KPIs / Salida
    def draw_node(x, y, w, h, text, node_type="decision"):
        colors = {
            "decision": ("#DBEAFE", "#1D4ED8", "Decisión"),
            "exogenous": ("#D1FAE5", "#047857", "Exógena / Ref."),
            "state": ("#FEF3C7", "#D97706", "Estado"),
            "kpi": ("#FEE2E2", "#B91C1C", "KPI / Salida")
        }
        bg, border_c, tag = colors[node_type]
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5", facecolor=bg, edgecolor=border_c, linewidth=2, zorder=3)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=8, fontweight='bold', color='#1E293B', zorder=4)

    # 1. Variables de Decisión
    draw_node(5, 75, 18, 9, "Bermas Asignadas\n(B: 2, 3 o 4)", "decision")
    draw_node(5, 55, 18, 9, "Flota Grúas STS\n(G: 3 o 4 grúas)", "decision")
    draw_node(5, 35, 18, 9, "Reserva Exclusiva\nCrucero (Sí/No)", "decision")
    draw_node(5, 15, 18, 9, "Política Camiones\n(Penalidad impuntual)", "decision")

    # 2. Variables Exógenas
    draw_node(30, 80, 18, 9, "Arribos Buques\n(Tasa lambda = 8.09 b/d)", "exogenous")
    draw_node(30, 60, 18, 9, "Mix Contenedores\n(Dry, Reefer, OOG)", "exogenous")
    draw_node(30, 40, 18, 9, "Turnos de Trabajo\n(Día 3G / Noche 1+1G)", "exogenous")
    draw_node(30, 20, 18, 9, "Camiones Tardíos\n(20% - 30% fuera ven.)", "exogenous")

    # 3. Variables de Estado
    draw_node(56, 75, 18, 9, "Cola en Rada\n(Lq buques)", "state")
    draw_node(56, 55, 18, 9, "Productividad Grúa\n(Interferencia 85%)", "state")
    draw_node(56, 35, 18, 9, "Ocupación Patio\n(O_patio vs 3000 slots)", "state")
    draw_node(56, 15, 18, 9, "Bloqueo por Patio\n(Demora si > 75%)", "state")

    # 4. KPIs y Salidas
    draw_node(80, 75, 17, 9, "Espera en Rada\n(Wq horas)", "kpi")
    draw_node(80, 55, 17, 9, "Tiempo en Berma\n(Ws horas)", "kpi")
    draw_node(80, 35, 17, 9, "Estadía Total\n(W = Wq + Ws)", "kpi")
    draw_node(80, 15, 17, 9, "Incumplimiento 16h\n(% buques > 16h)", "kpi")

    # Conexiones con flechas y polaridades
    def draw_arrow(x1, y1, x2, y2, polarity="+", color="#1F4E79", rad=0.0):
        connectionstyle = f"arc3,rad={rad}" if rad != 0.0 else "arc3"
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.8, connectionstyle=connectionstyle), zorder=2)
        mid_x = (x1 + x2)/2
        mid_y = (y1 + y2)/2
        ax.text(mid_x, mid_y, f"({polarity})", fontsize=7.5, fontweight='bold', color=color,
                bbox=dict(boxstyle="circle,pad=0.2", facecolor="white", edgecolor=color, lw=1))

    # Relaciones principales
    draw_arrow(48, 84, 56, 80, "+", "#DC2626") # Arribos -> Cola rada
    draw_arrow(23, 79, 56, 78, "-", "#059669") # Bermas -> Cola rada
    draw_arrow(23, 39, 56, 76, "+", "#DC2626", rad=0.2) # Crucero exclusivo -> resta berma -> Cola rada
    draw_arrow(74, 79, 80, 79, "+", "#DC2626") # Cola rada -> Wq
    
    draw_arrow(23, 59, 56, 60, "+", "#059669") # Flota grúas -> Prod
    draw_arrow(48, 64, 56, 62, "-", "#DC2626") # Mix OOG/Reefer -> reduce tasa
    draw_arrow(48, 44, 56, 57, "-", "#DC2626") # Turno noche -> reduce grúas activas
    draw_arrow(74, 59, 80, 59, "-", "#059669") # Prod -> Reduce Ws
    
    draw_arrow(48, 24, 56, 38, "+", "#DC2626") # Camiones tardíos -> Saturo patio
    draw_arrow(23, 19, 56, 36, "-", "#059669") # Penalidades -> Descongestiona patio
    draw_arrow(65, 35, 65, 24, "+", "#DC2626") # Ocup patio > 75% -> Bloqueo
    draw_arrow(65, 24, 80, 56, "+", "#DC2626", rad=-0.2) # Bloqueo patio -> Alarga Ws
    
    draw_arrow(88, 75, 88, 44, "+", "#DC2626") # Wq -> W
    draw_arrow(88, 55, 88, 44, "+", "#DC2626") # Ws -> W
    draw_arrow(88, 35, 88, 24, "+", "#DC2626") # W -> % > 16h

    # Leyenda
    leg_x = 8
    ax.text(leg_x, 6, "Referencias:", fontweight='bold', fontsize=8.5, color='#1F4E79')
    draw_node(leg_x + 10, 3, 14, 5, "Var. Decisión", "decision")
    draw_node(leg_x + 27, 3, 16, 5, "Var. Exógena", "exogenous")
    draw_node(leg_x + 46, 3, 14, 5, "Var. Estado", "state")
    draw_node(leg_x + 63, 3, 14, 5, "Var. KPI", "kpi")

    plt.tight_layout()
    plt.savefig(f"{out_dir}/fig_relacion_variables_causal.png", dpi=300)
    plt.close()
    print("Guardado: fig_relacion_variables_causal.png")

# =========================================================================
# 4. DIAGRAMA DE FLUJO LÓGICO DE ATENCIÓN DE ESCALAS (LÓGICAS)
# =========================================================================
def draw_logic_flow():
    fig, ax = plt.subplots(figsize=(10, 9), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 120)
    ax.axis('off')

    ax.text(50, 116, "DIAGRAMA DE FLUJO LÓGICO DEL CICLO DE ATENCIÓN DE BUQUES", ha='center', fontsize=12, fontweight='bold', color='#1F4E79')
    ax.text(50, 113, "Lógicas de Rada, Maniobra, Asignación de Grúas, Patio y Desatraque", ha='center', fontsize=9, fontstyle='italic', color='#555555')

    def draw_step(x, y, w, h, text, shape="rect", color="#EBF3FA", border="#1F4E79"):
        if shape == "rect":
            p = patches.Rectangle((x, y), w, h, facecolor=color, edgecolor=border, linewidth=2, zorder=3)
        elif shape == "round":
            p = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.8", facecolor=color, edgecolor=border, linewidth=2, zorder=3)
        elif shape == "diamond":
            p = patches.Polygon([[x + w/2, y], [x + w, y + h/2], [x + w/2, y + h], [x, y + h/2]],
                                facecolor=color, edgecolor=border, linewidth=2, zorder=3)
        ax.add_patch(p)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=8, fontweight='bold', color='#1E293B', zorder=4)

    # 1. Inicio
    draw_step(38, 104, 24, 6, "Arribo Buque a Rada (t_arr)", "round", "#DBEAFE", "#1D4ED8")

    # 2. Decisión Berma
    draw_step(32, 90, 36, 9, "¿Hay Berma Libre?\n(N_amarrados < B y sin reserva crucero)", "diamond", "#FEF3C7", "#D97706")

    # Flecha No (Cola)
    ax.annotate('', xy=(18, 94.5), xytext=(32, 94.5), arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.8))
    ax.text(25, 96, "No", color="#DC2626", fontweight='bold', fontsize=8)
    draw_step(4, 91, 14, 7, "Espera en Rada\n(Acumula Wq)", "rect", "#FEE2E2", "#DC2626")
    ax.plot([11, 11, 40], [91, 84, 84], color="#DC2626", lw=1.5)
    ax.annotate('', xy=(40, 89), xytext=(40, 84), arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.5))

    # Flecha Sí (Atraque)
    ax.annotate('', xy=(50, 77), xytext=(50, 90), arrowprops=dict(arrowstyle="->", color="#059669", lw=1.8))
    ax.text(51.5, 83, "Sí", color="#059669", fontweight='bold', fontsize=8)

    # 3. Maniobra Entrada
    draw_step(35, 71, 30, 6, "Maniobra Atraque: U(1, 2) h\n(Berma ocupada, grúas inactivas)", "rect", "#EBF3FA", "#1F4E79")

    # 4. Asignación Grúas
    draw_step(30, 56, 40, 10, "Evaluar Turno y Grúas Libres:\n• Diurno/Vesp: hasta 2 grúas\n• Nocturno: 1 activa (+1 standby +15m alistamiento)\n• Productividad: Dry 28, Ref 21, OOG 12 | Dual x0.85", "rect", "#E0E7FF", "#4338CA")
    ax.annotate('', xy=(50, 66), xytext=(50, 71), arrowprops=dict(arrowstyle="->", color="#1F4E79", lw=1.8))

    # 5. Verificación de Patio
    draw_step(33, 41, 34, 9, "¿Ocupación Patio > 75%?\n(Slots ocupados > 2.250)", "diamond", "#FEF3C7", "#D97706")
    ax.annotate('', xy=(50, 50), xytext=(50, 56), arrowprops=dict(arrowstyle="->", color="#1F4E79", lw=1.8))

    # Demora Patio
    ax.annotate('', xy=(76, 45.5), xytext=(67, 45.5), arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.8))
    ax.text(70, 47, "Sí", color="#DC2626", fontweight='bold', fontsize=8)
    draw_step(76, 42, 18, 7, "Demora de Grúas\npor falta de slots (+25%)", "rect", "#FEE2E2", "#DC2626")
    ax.plot([85, 85, 60], [42, 33, 33], color="#DC2626", lw=1.5)

    # Operación Grúas
    ax.annotate('', xy=(50, 29), xytext=(50, 41), arrowprops=dict(arrowstyle="->", color="#059669", lw=1.8))
    ax.text(51.5, 36, "No", color="#059669", fontweight='bold', fontsize=8)

    draw_step(30, 23, 40, 6, "Transferencia Carga/Descarga\n(Pausas de 10-15m si hay cambio turno)", "rect", "#EBF3FA", "#1F4E79")

    # Maniobra Salida
    draw_step(35, 12, 30, 6, "Maniobra Desatraque: U(1, 2) h\n(Libera berma al finalizar)", "rect", "#EBF3FA", "#1F4E79")
    ax.annotate('', xy=(50, 18), xytext=(50, 23), arrowprops=dict(arrowstyle="->", color="#1F4E79", lw=1.8))

    # Fin
    draw_step(38, 2, 24, 5, "Zarpada a Mar Abierto\nRegistrar W = Wq + Ws", "round", "#D1FAE5", "#047857")
    ax.annotate('', xy=(50, 7), xytext=(50, 12), arrowprops=dict(arrowstyle="->", color="#047857", lw=1.8))

    plt.tight_layout()
    plt.savefig(f"{out_dir}/fig_logica_flujo_buque.png", dpi=300)
    plt.close()
    print("Guardado: fig_logica_flujo_buque.png")

# =========================================================================
# 5. DIAGRAMA DE ELEMENTOS Y ARQUITECTURA DEL SIMULADOR (SIMPY)
# =========================================================================
def draw_sim_elements():
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 80)
    ax.axis('off')

    ax.text(55, 76, "ARQUITECTURA DE ELEMENTOS DEL SIMULADOR DISCRETO (SIMPY)", ha='center', fontsize=12, fontweight='bold', color='#1F4E79')
    ax.text(55, 73, "Interacción entre Entidades, Recursos, Contenedores y Monitores Estadísticos", ha='center', fontsize=9.5, fontstyle='italic', color='#555555')

    def draw_box(x, y, w, h, title, items, bg="#EBF3FA", border="#1F4E79"):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5", facecolor=bg, edgecolor=border, linewidth=2, zorder=3)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 3, title, ha='center', va='top', fontsize=9.5, fontweight='bold', color=border, zorder=4)
        ax.plot([x + 2, x + w - 2], [y + h - 5, y + h - 5], color=border, lw=1)
        for i, it in enumerate(items):
            ax.text(x + 3, y + h - 8 - (i * 3.8), it, ha='left', va='top', fontsize=8, color='#1E293B', zorder=4)

    # 1. Entidades
    draw_box(4, 34, 30, 36, "ENTIDADES (Processes)", [
        "• Buque Feeder (8.852 escalas)",
        "  - id_escala, servicio",
        "  - t_arribo, mov_dry, mov_reefer, mov_oog",
        "  - Estado: rada -> atraque -> op -> zarpe",
        "",
        "• Crucero Turístico (Opcional)",
        "  - Arribo matutino +- 3 h",
        "  - Ocupación berma: 28 a 36 h",
        "  - Sin uso de grúas STS",
        "",
        "• Lotes Contenedores & Camiones",
        "  - Dwell time medio: 72 horas",
        "  - Ventana camiones: 20-30% tarde"
    ], bg="#DBEAFE", border="#1D4ED8")

    # 2. Recursos SimPy
    draw_box(40, 34, 32, 36, "RECURSOS Y CONTENEDORES", [
        "• Bermas de Atraque",
        "  - simpy.Resource (capacidad 3 o 4)",
        "  - Disciplina de cola: FIFO",
        "",
        "• Grúas Pórtico STS",
        "  - simpy.PriorityResource (G = 3 o 4)",
        "  - Control dinámico por turno:",
        "    * Diurno/Vesp: 3 activas",
        "    * Nocturno: 1 activa + 1 standby",
        "    * Cambio turno: pausa 10-15 min",
        "",
        "• Patio de Almacenamiento",
        "  - simpy.Container (capacidad 3.000)",
        "  - Alerta de cuello de botella: >75%"
    ], bg="#FEF3C7", border="#D97706")

    # 3. Monitor Estadístico
    draw_box(78, 34, 28, 36, "MONITOR ESTADÍSTICO", [
        "• Registro Microsegundo:",
        "  - t_arribo, t_atraque, t_inicio_op",
        "  - t_fin_op, t_zarpada",
        "",
        "• Métricas Vectorizadas:",
        "  - Wq: espera en rada",
        "  - Ws: tiempo en berma",
        "  - W = Wq + Ws: estadía total",
        "  - Indicador binario: excede 16h",
        "",
        "• Exportador DataFrames:",
        "  - Tests de Tukey HSD",
        "  - Verificación Ley de Little (L=lambda*W)"
    ], bg="#D1FAE5", border="#047857")

    # Procesos demonio de soporte (Abajo)
    draw_box(16, 4, 36, 24, "PROCESO DEMONIO: TURNOS", [
        "• Ciclo temporal de 8 horas:",
        "  - 08:00 - 16:00: Diurno pleno",
        "  - 16:00 - 24:00: Vespertino pleno",
        "  - 00:00 - 08:00: Nocturno reducido (1+1)",
        "• Aplica parada de 10-15m por cambio guardia"
    ], bg="#EDE9FE", border="#6D28D9")

    draw_box(58, 4, 36, 24, "PROCESO DEMONIO: PATIO & CAMIONES", [
        "• Monitoreo horario de ocupación",
        "• Generación estocástica de retiros (Poisson)",
        "• Modulador de eficiencia por impuntualidad",
        "• Feedback: activa retraso a grúas si > 75%"
    ], bg="#FCE7F3", border="#BE185D")

    # Flechas de interacción
    ax.annotate('', xy=(40, 52), xytext=(34, 52), arrowprops=dict(arrowstyle="<->", color="#1F4E79", lw=2))
    ax.annotate('', xy=(78, 52), xytext=(72, 52), arrowprops=dict(arrowstyle="->", color="#1F4E79", lw=2))
    ax.annotate('', xy=(56, 34), xytext=(34, 28), arrowprops=dict(arrowstyle="->", color="#6D28D9", lw=1.5))
    ax.annotate('', xy=(56, 34), xytext=(76, 28), arrowprops=dict(arrowstyle="->", color="#BE185D", lw=1.5))

    plt.tight_layout()
    plt.savefig(f"{out_dir}/fig_elementos_simulador.png", dpi=300)
    plt.close()
    print("Guardado: fig_elementos_simulador.png")

if __name__ == "__main__":
    draw_idef0_a0_context()
    draw_idef0_a0_decomposition()
    draw_causal_influences()
    draw_logic_flow()
    draw_sim_elements()
    print("\n¡Todos los diagramas conceptuales fueron generados exitosamente!")
