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
import os

out_dir = "C:/Users/ASUS/.gemini/antigravity/scratch/TP2-IO/plots"
os.makedirs(out_dir, exist_ok=True)

# Paleta formal ITBA / Corporativa
COLOR_NAVY = "#1F4E79"
COLOR_STEEL = "#2F5597"
COLOR_LIGHT_BG = "#F8FAFC"
COLOR_BLUE_BOX = "#EBF3FA"
COLOR_BLUE_BORDER = "#1F4E79"
COLOR_DECISION_BG = "#FEF3C7"
COLOR_DECISION_BORDER = "#D97706"
COLOR_PROCESS_BG = "#E0E7FF"
COLOR_PROCESS_BORDER = "#4338CA"
COLOR_SUCCESS_BG = "#D1FAE5"
COLOR_SUCCESS_BORDER = "#059669"
COLOR_ALERT_BG = "#FEE2E2"
COLOR_ALERT_BORDER = "#DC2626"
COLOR_PURPLE_BG = "#EDE9FE"
COLOR_PURPLE_BORDER = "#6D28D9"

# Configuración general
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 9.5
plt.rcParams['axes.edgecolor'] = '#CCCCCC'


# =========================================================================
# 1. DIAGRAMA IDEF0 A-0: CONTEXTO GENERAL
# =========================================================================
def draw_idef0_a0_context():
    fig, ax = plt.subplots(figsize=(11.5, 7.8), dpi=300)
    ax.set_xlim(0, 115)
    ax.set_ylim(0, 82)
    ax.axis('off')

    # Marco exterior estándar IDEF0
    border = patches.Rectangle((2, 2), 111, 78, fill=False, edgecolor=COLOR_NAVY, linewidth=2)
    ax.add_patch(border)
    
    # Encabezado formal IDEF0
    ax.text(5, 77.2, "ITBA - INVESTIGACIÓN OPERATIVA (IO51) | MODELO CONCEPTUAL PUERTO SUR", fontsize=9, fontweight='bold', color=COLOR_NAVY)
    ax.text(90, 77.2, "GRUPO 08 | NODO: A-0", fontsize=9, fontweight='bold', color=COLOR_NAVY)
    ax.plot([2, 113], [75.5, 75.5], color=COLOR_NAVY, linewidth=1)

    # Caja Central A-0
    box = patches.Rectangle((37, 26), 42, 27, facecolor='#EDF4FB', edgecolor=COLOR_NAVY, linewidth=2.5, zorder=3)
    ax.add_patch(box)
    ax.text(58, 41.5, "OPERAR TERMINAL\nPORTUARIA PUERTO SUR", ha='center', va='center', fontsize=12, fontweight='bold', color=COLOR_NAVY, zorder=4)
    ax.text(77, 28, "A-0", ha='right', va='bottom', fontsize=10, fontweight='bold', color=COLOR_STEEL, zorder=4)

    # FLECHAS DE CONTROLES (C) - Arriba
    controls = [
        ("C1: Contratos Navieras\n(Umbral W <= 16 h)", 42, 70),
        ("C2: Régimen de Turnos (8h)\ny Relevos (10-15m)", 54, 65),
        ("C3: Maniobra Práctico/Remolque\n(1 a 2 h en conjunto total)", 66, 71),
        ("C4: Capacidad Patio (3.000 slots)\ny Reglas Reefer/OOG", 78, 65)
    ]
    for text, x, y_text in controls:
        ax.annotate('', xy=(x, 53), xytext=(x, y_text),
                    arrowprops=dict(facecolor='#D97706', edgecolor='#D97706', width=1.5, headwidth=6), zorder=2)
        ax.text(x, y_text + 0.8, text, ha='center', va='bottom', fontsize=7.5, fontweight='bold', color='#B45309')

    # FLECHAS DE ENTRADAS (I) - Izquierda
    inputs = [
        ("I1: Buques feeder en rada\n(Historico G08, lambda=8.09 b/d)", 20, 48),
        ("I2: Carga impo/expo\n(Mix Dry, Reefer, OOG)", 20, 40),
        ("I3: Camiones de retiro\n(20-30% fuera de ventana)", 20, 32),
        ("I4: Escalas cruceros\n(Temporada 3 meses, 2/sem)", 20, 24)
    ]
    for text, x_start, y in inputs:
        ax.annotate('', xy=(37, y), xytext=(x_start, y),
                    arrowprops=dict(facecolor='#0275D8', edgecolor='#0275D8', width=1.5, headwidth=6), zorder=2)
        ax.text(x_start - 1, y, text, ha='right', va='center', fontsize=7.5, color='#0275D8', fontweight='bold')

    # FLECHAS DE SALIDAS (O) - Derecha
    outputs = [
        ("O1: Buques feeder atendidos y despachados", 79, 48, 96),
        ("O2: Métricas de estadía (W, Wq, Ws, T_esp_grua)", 79, 42, 96),
        ("O3: Nivel de servicio contractual (% W <= 16 h)", 79, 36, 96),
        ("O4: Utilización de bermas y grúas pórtico STS", 79, 30, 96),
        ("O5: Sobrecostos de inmovilización naviera (USD)", 79, 24, 96)
    ]
    for text, x_start, y, x_end in outputs:
        ax.annotate('', xy=(x_end, y), xytext=(x_start, y),
                    arrowprops=dict(facecolor='#059669', edgecolor='#059669', width=1.5, headwidth=6), zorder=2)
        ax.text(x_end + 1, y, text, ha='left', va='center', fontsize=7.5, color='#059669', fontweight='bold')

    # FLECHAS DE MECANISMOS (M) - Abajo
    mechanisms = [
        ("M1: 3 Bermas de atraque (o 4)\n(Línea continua de muelle)", 45, 12),
        ("M2: 3 Grúas STS pórtico (o 4)\n(Contención física de asignación)", 58, 16),
        ("M3: Tractoristas, RTG y patio\n+ Prácticos y remolcadores", 71, 12)
    ]
    for text, x, y_text in mechanisms:
        ax.annotate('', xy=(x, 26), xytext=(x, y_text),
                    arrowprops=dict(facecolor='#7C3AED', edgecolor='#7C3AED', width=1.5, headwidth=6), zorder=2)
        ax.text(x, y_text - 1, text, ha='center', va='top', fontsize=7.5, fontweight='bold', color='#6D28D9')

    # Pie de plano
    ax.text(58, 4, "DIAGRAMA DE CONTEXTO IDEF0 A-0: TERMINAL PORTUARIA PUERTO SUR", ha='center', fontsize=10, fontweight='bold', color=COLOR_NAVY)
    
    plt.tight_layout()
    plt.savefig(f"{out_dir}/fig_idef0_a_menos_0.png", dpi=300)
    plt.close()
    print("Guardado exitoso: fig_idef0_a_menos_0.png")


# =========================================================================
# 2. DIAGRAMA IDEF0 A0: DESCOMPOSICIÓN DE PRIMER NIVEL
# =========================================================================
def draw_idef0_a0_decomposition():
    fig, ax = plt.subplots(figsize=(12.5, 8.2), dpi=300)
    ax.set_xlim(0, 125)
    ax.set_ylim(0, 84)
    ax.axis('off')

    # Marco
    border = patches.Rectangle((2, 2), 121, 80, fill=False, edgecolor=COLOR_NAVY, linewidth=2)
    ax.add_patch(border)
    ax.text(5, 79, "ITBA - INVESTIGACIÓN OPERATIVA (IO51) | DESCOMPOSICIÓN FUNCIONAL IDEF0", fontsize=9, fontweight='bold', color=COLOR_NAVY)
    ax.text(98, 79, "GRUPO 08 | NODO: A0", fontsize=9, fontweight='bold', color=COLOR_NAVY)
    ax.plot([2, 123], [77, 77], color=COLOR_NAVY, linewidth=1)

    # 4 Actividades escalonadas (A1, A2, A3, A4)
    acts = [
        ("A1: Recepción\ny Fondeo en Rada", 12, 50, 21, 14),
        ("A2: Maniobra de\nEntrada y Atraque", 40, 39, 21, 14),
        ("A3: Operación de Grúas\ny Manejo de Carga", 69, 24, 25, 16),
        ("A4: Desatraque\ny Zarpada", 100, 11, 19, 14)
    ]
    for name, x, y, w, h in acts:
        rect = patches.Rectangle((x, y), w, h, facecolor='#EDF4FB', edgecolor=COLOR_NAVY, linewidth=2, zorder=3)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, name, ha='center', va='center', fontsize=8.5, fontweight='bold', color=COLOR_NAVY, zorder=4)

    # Flujo secuencial entre actividades (I -> O)
    # Entrada a A1
    ax.annotate('', xy=(12, 57), xytext=(4, 57), arrowprops=dict(facecolor='#0275D8', edgecolor='#0275D8', width=1.5, headwidth=6))
    ax.text(3.5, 59, "Arribo buques\nfeeder (G08)", fontsize=7.5, color='#0275D8', fontweight='bold')

    # A1 -> A2 (Berma asignada)
    ax.plot([33, 36, 36], [57, 57, 46], color=COLOR_NAVY, linewidth=1.5)
    ax.annotate('', xy=(40, 46), xytext=(36, 46), arrowprops=dict(facecolor=COLOR_NAVY, edgecolor=COLOR_NAVY, width=1.5, headwidth=6))
    ax.text(34, 58.5, "Berma libre\nasignada", fontsize=7.2, color=COLOR_NAVY, fontweight='bold')

    # A2 -> A3 (Buque amarrado en berma)
    ax.plot([61, 65, 65], [46, 46, 34], color=COLOR_NAVY, linewidth=1.5)
    ax.annotate('', xy=(69, 34), xytext=(65, 34), arrowprops=dict(facecolor=COLOR_NAVY, edgecolor=COLOR_NAVY, width=1.5, headwidth=6))
    ax.text(62, 47.5, "Buque amarrado\n(berma ocupada)", fontsize=7.2, color=COLOR_NAVY, fontweight='bold')

    # A3 -> A4 (Carga finalizada, solicita desatraque)
    ax.plot([94, 97, 97], [30, 30, 18], color=COLOR_NAVY, linewidth=1.5)
    ax.annotate('', xy=(100, 18), xytext=(97, 18), arrowprops=dict(facecolor=COLOR_NAVY, edgecolor=COLOR_NAVY, width=1.5, headwidth=6))
    ax.text(93, 31.5, "Carga/descarga\nfinalizada", fontsize=7.2, color=COLOR_NAVY, fontweight='bold')

    # A4 -> Salida final
    ax.annotate('', xy=(121, 18), xytext=(119, 18), arrowprops=dict(facecolor='#059669', edgecolor='#059669', width=1.5, headwidth=6))
    ax.text(118.5, 20.5, "Buque zarpado\n(W total, berma libre)", fontsize=7.2, color='#059669', fontweight='bold')

    # CONTROLES SUPERIORES (C)
    # Control A1: Disciplina FIFO
    ax.annotate('', xy=(22, 64), xytext=(22, 73), arrowprops=dict(facecolor='#D97706', edgecolor='#D97706', width=1.2, headwidth=5))
    ax.text(22, 74, "Disciplina FIFO / Rada", ha='center', fontsize=7.2, color='#B45309', fontweight='bold')

    # Control conjunto de maniobras para A2 y A4 (1-2h en conjunto total)
    ax.plot([50, 50, 109, 109], [53, 73, 73, 25], color='#D97706', linewidth=1.2, linestyle='--')
    ax.annotate('', xy=(50, 53), xytext=(50, 56), arrowprops=dict(facecolor='#D97706', edgecolor='#D97706', width=1.2, headwidth=5))
    ax.annotate('', xy=(109, 25), xytext=(109, 28), arrowprops=dict(facecolor='#D97706', edgecolor='#D97706', width=1.2, headwidth=5))
    ax.text(79.5, 74, "Regla Práctico y Remolcador: 1 a 2 h en conjunto total\n(Entrada: ~0.5-1.0 h | Salida: ~0.5-1.0 h | Grúas inactivas)",
            ha='center', fontsize=7.2, color='#B45309', fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#FEF3C7", edgecolor="#D97706", lw=0.8))

    # Control A3: Turnos y Patio
    ax.annotate('', xy=(81, 40), xytext=(81, 68), arrowprops=dict(facecolor='#D97706', edgecolor='#D97706', width=1.2, headwidth=5))
    ax.text(81, 69, "Turnos (Día 3G, Noche 1+1G) / Interf. 85% / Patio >75%", ha='center', fontsize=7.2, color='#B45309', fontweight='bold')

    # MECANISMOS INFERIORES (M)
    ax.annotate('', xy=(22, 50), xytext=(22, 9), arrowprops=dict(facecolor='#7C3AED', edgecolor='#7C3AED', width=1.2, headwidth=5))
    ax.text(22, 7, "Zona de Rada\n(Aguas profundas)", ha='center', fontsize=7.2, color='#6D28D9', fontweight='bold')

    ax.annotate('', xy=(50, 39), xytext=(50, 9), arrowprops=dict(facecolor='#7C3AED', edgecolor='#7C3AED', width=1.2, headwidth=5))
    ax.text(50, 7, "Prácticos y Remolcadores\n(Maniobra entrada)", ha='center', fontsize=7.2, color='#6D28D9', fontweight='bold')

    ax.annotate('', xy=(81, 24), xytext=(81, 9), arrowprops=dict(facecolor='#7C3AED', edgecolor='#7C3AED', width=1.2, headwidth=5))
    ax.text(81, 7, "3 Bermas + 3 Grúas STS\n+ Patio 3.000 slots", ha='center', fontsize=7.2, color='#6D28D9', fontweight='bold')

    ax.annotate('', xy=(109, 11), xytext=(109, 9), arrowprops=dict(facecolor='#7C3AED', edgecolor='#7C3AED', width=1.2, headwidth=5))
    ax.text(109, 6, "Prácticos y Remolcadores\n(Maniobra salida)", ha='center', fontsize=7.2, color='#6D28D9', fontweight='bold')

    ax.text(62, 3.5, "DESCOMPOSICIÓN A0: CICLO INTEGRAL DE ATENCIÓN DE ESCALAS PORTUARIAS", ha='center', fontsize=10, fontweight='bold', color=COLOR_NAVY)

    plt.tight_layout()
    plt.savefig(f"{out_dir}/fig_idef0_a0_descomposicion.png", dpi=300)
    plt.close()
    print("Guardado exitoso: fig_idef0_a0_descomposicion.png")


# =========================================================================
# 3. DIAGRAMA DE INFLUENCIAS CAUSALES (RELACIÓN ENTRE VARIABLES)
# =========================================================================
def draw_causal_influences():
    fig, ax = plt.subplots(figsize=(11.5, 7.8), dpi=300)
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Título formal
    ax.text(52.5, 96.5, "DIAGRAMA DE RELACIÓN ENTRE VARIABLES Y BUCLES DE RETROALIMENTACIÓN", ha='center', fontsize=12, fontweight='bold', color=COLOR_NAVY)
    ax.text(52.5, 93.5, "Terminal Portuaria Puerto Sur — Modelo Conceptual Grupo 08", ha='center', fontsize=9, fontstyle='italic', color='#555555')

    def draw_node(x, y, w, h, text, node_type="decision"):
        colors = {
            "decision": ("#DBEAFE", "#1D4ED8", "Decisión"),
            "exogenous": ("#D1FAE5", "#047857", "Exógena / Ref."),
            "state": ("#FEF3C7", "#D97706", "Estado"),
            "kpi": ("#FEE2E2", "#B91C1C", "KPI / Salida")
        }
        bg, border_c, tag = colors[node_type]
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5", facecolor=bg, edgecolor=border_c, linewidth=1.8, zorder=3)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=7.8, fontweight='bold', color='#1E293B', zorder=4)

    # 1. Variables de Decisión
    draw_node(4, 76, 18, 9, "Bermas Asignadas\n(B: 2, 3 o 4)", "decision")
    draw_node(4, 56, 18, 9, "Flota Grúas STS\n(G: 3 o 4 grúas)", "decision")
    draw_node(4, 36, 18, 9, "Reserva Berma\nCrucero (Sí/No)", "decision")
    draw_node(4, 16, 18, 9, "Tarifa / Ventana\nCamiones", "decision")

    # 2. Variables Exógenas / Referencia
    draw_node(28, 80, 20, 9, "Arribos Buques Feeder\n(lambda = 8.09 b/d, G08)", "exogenous")
    draw_node(28, 62, 20, 9, "Turnos y Dotación\n(Día 3G / Noche 1+1G)", "exogenous")
    draw_node(28, 44, 20, 9, "Maniobras Náuticas\n(1 a 2 h en conjunto total)", "exogenous")
    draw_node(28, 26, 20, 9, "Mix Carga & Dwell Time\n(Dry/Ref/OOG, Camiones)", "exogenous")

    # 3. Variables de Estado
    draw_node(54, 76, 19, 9, "Cola en Rada\n(Lq buques en espera)", "state")
    draw_node(54, 56, 19, 9, "Contención Grúas\n(Espera amarrado T_esp)", "state")
    draw_node(54, 36, 19, 9, "Ocupación Patio\n(O_patio vs 3.000 slots)", "state")
    draw_node(54, 16, 19, 9, "Bloqueo Grúas Patio\n(+25% demora si > 75%)", "state")

    # 4. KPIs y Salidas
    draw_node(81, 76, 19, 9, "Espera en Rada\n(Wq horas)", "kpi")
    draw_node(81, 56, 19, 9, "Tiempo en Berma\n(Ws = Man + Esp + Op)", "kpi")
    draw_node(81, 36, 19, 9, "Estadía Total\n(W = Wq + Ws)", "kpi")
    draw_node(81, 16, 19, 9, "Incumplimiento 16h\n(% buques > 16h / USD)", "kpi")

    # Conexiones causales
    def draw_arrow(x1, y1, x2, y2, polarity="+", color="#1F4E79", rad=0.0):
        connectionstyle = f"arc3,rad={rad}" if rad != 0.0 else "arc3"
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.6, connectionstyle=connectionstyle), zorder=2)
        mid_x = (x1 + x2)/2
        mid_y = (y1 + y2)/2
        ax.text(mid_x, mid_y, f"({polarity})", fontsize=7.2, fontweight='bold', color=color,
                bbox=dict(boxstyle="circle,pad=0.15", facecolor="white", edgecolor=color, lw=0.8), zorder=5)

    # Relaciones de rada
    draw_arrow(48, 84, 54, 81, "+", "#DC2626") # Arribos -> Cola rada
    draw_arrow(22, 80, 54, 79, "-", "#059669") # Bermas -> reduce cola rada
    draw_arrow(22, 40, 54, 76, "+", "#DC2626", rad=0.18) # Reserva crucero -> quita berma -> sube cola
    draw_arrow(73, 80, 81, 80, "+", "#DC2626") # Cola rada -> Wq

    # Relaciones de grúas y berma
    draw_arrow(22, 60, 54, 60, "-", "#059669") # Flota grúas -> reduce contención grúa
    draw_arrow(48, 66, 54, 62, "-", "#059669") # Turnos plenos -> reduce contención
    draw_arrow(48, 48, 81, 60, "+", "#DC2626") # Maniobras conjuntas 1-2h -> suman a Ws
    draw_arrow(73, 60, 81, 61, "+", "#DC2626") # Contención grúas -> sube Ws

    # Relaciones de patio
    draw_arrow(48, 30, 54, 39, "+", "#DC2626") # Mix / dwell time -> satura patio
    draw_arrow(22, 20, 54, 37, "-", "#059669") # Políticas camiones -> descongestiona patio
    draw_arrow(63.5, 36, 63.5, 25, "+", "#DC2626") # Ocup patio > 75% -> genera bloqueo
    draw_arrow(73, 20, 81, 57, "+", "#DC2626", rad=-0.2) # Bloqueo patio -> alarga Ws

    # Agregación a estadía total W y penalidad contractual
    draw_arrow(90.5, 76, 90.5, 45, "+", "#DC2626") # Wq -> W
    draw_arrow(90.5, 56, 90.5, 45, "+", "#DC2626") # Ws -> W
    draw_arrow(90.5, 36, 90.5, 25, "+", "#DC2626") # W -> % > 16h

    # Leyenda
    leg_x = 10
    ax.text(leg_x, 6, "Referencias de Variables:", fontweight='bold', fontsize=8, color=COLOR_NAVY)
    draw_node(leg_x + 19, 3, 14, 5, "Decisión", "decision")
    draw_node(leg_x + 35, 3, 16, 5, "Exógena / Ref.", "exogenous")
    draw_node(leg_x + 53, 3, 14, 5, "Estado", "state")
    draw_node(leg_x + 69, 3, 14, 5, "KPI / Salida", "kpi")

    plt.tight_layout()
    plt.savefig(f"{out_dir}/fig_relacion_variables_causal.png", dpi=300)
    plt.close()
    print("Guardado exitoso: fig_relacion_variables_causal.png")


# =========================================================================
# 4. DIAGRAMA DE FLUJO LÓGICO DE ATENCIÓN DE ESCALAS (LÓGICAS)
# =========================================================================
def draw_logic_flow():
    fig, ax = plt.subplots(figsize=(10.5, 9.8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 126)
    ax.axis('off')

    ax.text(50, 122.5, "DIAGRAMA DE FLUJO LÓGICO DEL CICLO DE ATENCIÓN DE BUQUES", ha='center', fontsize=12, fontweight='bold', color=COLOR_NAVY)
    ax.text(50, 119.5, "Lógicas de Rada, Maniobra Conjunta (1-2h total), Grúas STS, Patio y Desatraque", ha='center', fontsize=8.8, fontstyle='italic', color='#555555')

    def draw_step(x, y, w, h, text, shape="rect", color="#EDF4FB", border=COLOR_NAVY, fontsize=7.8):
        if shape == "rect":
            p = patches.Rectangle((x, y), w, h, facecolor=color, edgecolor=border, linewidth=1.8, zorder=3)
        elif shape == "round":
            p = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6", facecolor=color, edgecolor=border, linewidth=1.8, zorder=3)
        elif shape == "diamond":
            p = patches.Polygon([[x + w/2, y], [x + w, y + h/2], [x + w/2, y + h], [x, y + h/2]],
                                facecolor=color, edgecolor=border, linewidth=1.8, zorder=3)
        ax.add_patch(p)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fontsize, fontweight='bold', color='#1E293B', zorder=4)

    # 1. Inicio: Arribo
    draw_step(36, 110, 28, 6.5, "Arribo de Buque a Rada (t_arribo)\nGenerador Poisson G08 (lambda = 8.09 b/d)", "round", "#DBEAFE", "#1D4ED8")

    # 2. Decisión Berma
    draw_step(31, 95, 38, 9.5, "¿Hay Berma de Atraque Libre?\n(N_amarrados < B y sin reserva preventiva de crucero)", "diamond", COLOR_DECISION_BG, COLOR_DECISION_BORDER)
    ax.annotate('', xy=(50, 104.5), xytext=(50, 110), arrowprops=dict(arrowstyle="->", color=COLOR_NAVY, lw=1.6))

    # Flecha No (Cola en Rada)
    ax.annotate('', xy=(19, 99.7), xytext=(31, 99.7), arrowprops=dict(arrowstyle="->", color=COLOR_ALERT_BORDER, lw=1.6))
    ax.text(24, 101.2, "No", color=COLOR_ALERT_BORDER, fontweight='bold', fontsize=8)
    draw_step(4, 96, 15, 7.5, "Espera en Fondeo (Rada)\n(Acumula Wq en cola FIFO)", "rect", COLOR_ALERT_BG, COLOR_ALERT_BORDER)
    ax.plot([11.5, 11.5, 38], [96, 88.5, 88.5], color=COLOR_ALERT_BORDER, lw=1.4)
    ax.annotate('', xy=(38, 95), xytext=(38, 88.5), arrowprops=dict(arrowstyle="->", color=COLOR_ALERT_BORDER, lw=1.4))

    # Flecha Sí (Asignar Berma)
    ax.annotate('', xy=(50, 83), xytext=(50, 95), arrowprops=dict(arrowstyle="->", color=COLOR_SUCCESS_BORDER, lw=1.6))
    ax.text(51.5, 89, "Sí", color=COLOR_SUCCESS_BORDER, fontweight='bold', fontsize=8)

    # 3. Maniobra Entrada (CORREGIDO A FRACCIÓN DE 1-2H TOTAL)
    draw_step(27, 75, 46, 7.5, "Maniobra de Entrada y Atraque (Práctico y Remolcador)\nT_man_in ~ U(0.5, 1.0) h  [Media: 0.75 h]\n(Parte de 1 a 2 h en conjunto total | Berma ocupada, grúas inactivas)", "rect", "#EDF4FB", COLOR_NAVY)

    # 4. Asignación y Espera de Grúas STS (Contención Física)
    draw_step(25, 59, 50, 10.5, "Asignación de Grúas Pórtico STS según Turno:\n• Diurno / Vesp: hasta 2 grúas | Nocturno: 1 activa (+1 standby +15m)\n¿Hay grúas libres?  Si NO -> buque espera amarrado (acumula T_esp_grua)\n• Rendimiento dual: factor de interferencia 0.85 (Dry: 28, Ref: 21, OOG: 12 m/h)", "rect", COLOR_PROCESS_BG, COLOR_PROCESS_BORDER)
    ax.annotate('', xy=(50, 69.5), xytext=(50, 75), arrowprops=dict(arrowstyle="->", color=COLOR_NAVY, lw=1.6))

    # 5. Verificación de Cuello de Botella de Patio
    draw_step(31, 44, 38, 9.5, "¿Ocupación de Patio > 75%?\n(Slots ocupados > 2.250 TEU)", "diamond", COLOR_DECISION_BG, COLOR_DECISION_BORDER)
    ax.annotate('', xy=(50, 53.5), xytext=(50, 59), arrowprops=dict(arrowstyle="->", color=COLOR_NAVY, lw=1.6))

    # Demora Patio
    ax.annotate('', xy=(78, 48.7), xytext=(69, 48.7), arrowprops=dict(arrowstyle="->", color=COLOR_ALERT_BORDER, lw=1.6))
    ax.text(72.5, 50.2, "Sí", color=COLOR_ALERT_BORDER, fontweight='bold', fontsize=8)
    draw_step(78, 45, 19, 7.5, "Demora de Grúas por Patio\n(+25% tiempo de transferencia)", "rect", COLOR_ALERT_BG, COLOR_ALERT_BORDER)
    ax.plot([87.5, 87.5, 62], [45, 36, 36], color=COLOR_ALERT_BORDER, lw=1.4)

    # No congestión patio -> Operación Grúas
    ax.annotate('', xy=(50, 32), xytext=(50, 44), arrowprops=dict(arrowstyle="->", color=COLOR_SUCCESS_BORDER, lw=1.6))
    ax.text(51.5, 38, "No", color=COLOR_SUCCESS_BORDER, fontweight='bold', fontsize=8)

    # 6. Transferencia de Carga
    draw_step(27, 25, 46, 7, "Transferencia Efectiva de Carga / Descarga\n(Aplica pausas de 10-15m por cambio de guardia | Acumula T_op_grua)\nAl terminar: LIBERA GRÚAS STS INMEDIATAMENTE", "rect", "#EDF4FB", COLOR_NAVY)

    # 7. Maniobra Desatraque (CORREGIDO A FRACCIÓN DE 1-2H TOTAL)
    draw_step(27, 12, 46, 7.5, "Maniobra de Desatraque y Salida (Práctico y Remolcador)\nT_man_out = T_man_total - T_man_in ~ U(0.5, 1.0) h  [Media: 0.75 h]\n[Suma total maniobras: T_man_in + T_man_out = U(1, 2) h en conjunto]\n(Berma ocupada hasta el final de la maniobra)", "rect", "#EDF4FB", COLOR_NAVY)
    ax.annotate('', xy=(50, 19.5), xytext=(50, 25), arrowprops=dict(arrowstyle="->", color=COLOR_NAVY, lw=1.6))

    # 8. Fin y Registro
    draw_step(32, 2, 36, 5.5, "Zarpada a Mar Abierto — Libera Berma\nRegistrar W = Wq + Ws, T_esp_grua, T_op | ¿W <= 16 h?", "round", COLOR_SUCCESS_BG, COLOR_SUCCESS_BORDER)
    ax.annotate('', xy=(50, 7.5), xytext=(50, 12), arrowprops=dict(arrowstyle="->", color=COLOR_SUCCESS_BORDER, lw=1.6))

    plt.tight_layout()
    plt.savefig(f"{out_dir}/fig_logica_flujo_buque.png", dpi=300)
    plt.close()
    print("Guardado exitoso: fig_logica_flujo_buque.png")


# =========================================================================
# 5. DIAGRAMA DE ELEMENTOS Y ARQUITECTURA DEL SIMULADOR (SIMPY)
# =========================================================================
def draw_sim_elements():
    fig, ax = plt.subplots(figsize=(11.5, 7.8), dpi=300)
    ax.set_xlim(0, 114)
    ax.set_ylim(0, 82)
    ax.axis('off')

    ax.text(57, 78, "ARQUITECTURA DE ELEMENTOS DEL SIMULADOR DISCRETO (SIMPY)", ha='center', fontsize=12, fontweight='bold', color=COLOR_NAVY)
    ax.text(57, 75, "Interacción entre Entidades, Recursos de Muelle, Contenedores y Monitores Estadísticos", ha='center', fontsize=9, fontstyle='italic', color='#555555')

    def draw_box(x, y, w, h, title, items, bg="#EDF4FB", border=COLOR_NAVY):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5", facecolor=bg, edgecolor=border, linewidth=1.8, zorder=3)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h - 2.8, title, ha='center', va='top', fontsize=9, fontweight='bold', color=border, zorder=4)
        ax.plot([x + 2, x + w - 2], [y + h - 4.5, y + h - 4.5], color=border, lw=1)
        for i, it in enumerate(items):
            ax.text(x + 2.5, y + h - 7 - (i * 3.3), it, ha='left', va='top', fontsize=7.6, color='#1E293B', zorder=4)

    # 1. Entidades
    draw_box(4, 32, 33, 39, "ENTIDADES (Processes)", [
        "• Buque Feeder (8.852 escalas G08)",
        "  - id_escala, t_arribo, tipo servicio",
        "  - Demanda: TEUs Dry, Reefer, OOG",
        "  - Maniobras náuticas: U(1, 2) h en conjunto",
        "    (Atraque: ~0.75h + Desatraque: ~0.75h)",
        "  - Ciclo: Rada -> Atraque -> Op -> Zarpe",
        "",
        "• Crucero Turístico (Escenario Cruceros)",
        "  - Arribo semanal matutino +-3h",
        "  - Ocupa berma 28 a 36 h (sin grúas)",
        "  - Reserva preventiva de berma",
        "",
        "• Camiones y Lotes de Patio",
        "  - Dwell time medio: 72 horas",
        "  - Ventanas de entrega (20-30% impuntual)"
    ], bg="#DBEAFE", border="#1D4ED8")

    # 2. Recursos SimPy
    draw_box(40, 32, 34, 39, "RECURSOS Y CONTENEDORES", [
        "• Bermas de Atraque",
        "  - simpy.Resource (capacidad B = 3 o 4)",
        "  - Disciplina de atraque: FIFO",
        "",
        "• Grúas Pórtico STS (G = 3 o 4)",
        "  - simpy.Resource con contención explícita",
        "  - Asignación dinámica: 1 a 2 por buque",
        "  - Control dinámico por turnos:",
        "    * Diurno/Vesp: hasta 2 grúas/buque",
        "    * Nocturno: 1 activa (+1 standby +15m)",
        "    * Relevos: pausa 10-15m cada 8 horas",
        "",
        "• Patio de Contenedores",
        "  - simpy.Container (capacidad 3.000 slots)",
        "  - Alerta de cuello de botella: >75%"
    ], bg="#FEF3C7", border="#D97706")

    # 3. Monitor Estadístico
    draw_box(77, 32, 33, 39, "MONITOR ESTADÍSTICO", [
        "• Marcas de Tiempo por Escala:",
        "  - t_llegada_rada, t_inicio_maniobra",
        "  - t_amarrado, t_inicio_faena, t_fin_faena",
        "  - t_inicio_desatraque, t_zarpada",
        "",
        "• Métricas Desglosadas Vectorizadas:",
        "  - Wq: Espera en rada",
        "  - T_esp_grua: Espera amarrado por grúa",
        "  - T_op_grua: Faena efectiva de grúas",
        "  - Ws: Tiempo en berma (Man + Esp + Op)",
        "  - W = Wq + Ws: Estadía total",
        "  - Indicador contractual: I(W <= 16 h)",
        "",
        "• Verificación Analítica:",
        "  - Ley de Little: L = lambda * W"
    ], bg="#D1FAE5", border="#047857")

    # Procesos demonio de soporte (Abajo)
    draw_box(16, 4, 38, 24, "PROCESO DEMONIO: TURNOS", [
        "• Ciclo temporal de 8 horas:",
        "  - 08:00 - 16:00: Diurno pleno (3 grúas)",
        "  - 16:00 - 24:00: Vespertino pleno (3 grúas)",
        "  - 00:00 - 08:00: Nocturno reducido (1+1)",
        "• Aplica interrupción estocástica de relevo:",
        "  10 a 15 min por cambio de guardia"
    ], bg="#EDE9FE", border="#6D28D9")

    draw_box(59, 4, 38, 24, "PROCESO DEMONIO: PATIO & CAMIONES", [
        "• Monitoreo horario continuo de ocupación",
        "• Retiros de importación con dwell time medio 72h",
        "• Modulador de ventanas y tardanzas de camiones",
        "• Bucle de realimentación: si slots > 2.250 (>75%),",
        "  penaliza productividad de grúas con +25% demora"
    ], bg="#FCE7F3", border="#BE185D")

    # Flechas de interacción
    ax.annotate('', xy=(40, 51.5), xytext=(37, 51.5), arrowprops=dict(arrowstyle="<->", color=COLOR_NAVY, lw=1.8))
    ax.annotate('', xy=(77, 51.5), xytext=(74, 51.5), arrowprops=dict(arrowstyle="->", color=COLOR_NAVY, lw=1.8))
    ax.annotate('', xy=(57, 32), xytext=(35, 28), arrowprops=dict(arrowstyle="->", color="#6D28D9", lw=1.4))
    ax.annotate('', xy=(57, 32), xytext=(78, 28), arrowprops=dict(arrowstyle="->", color="#BE185D", lw=1.4))

    plt.tight_layout()
    plt.savefig(f"{out_dir}/fig_elementos_simulador.png", dpi=300)
    plt.close()
    print("Guardado exitoso: fig_elementos_simulador.png")


if __name__ == "__main__":
    draw_idef0_a0_context()
    draw_idef0_a0_decomposition()
    draw_causal_influences()
    draw_logic_flow()
    draw_sim_elements()
    print("\n¡Todos los diagramas conceptuales fueron generados exitosamente!")
