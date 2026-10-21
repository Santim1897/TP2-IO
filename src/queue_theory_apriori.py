import numpy as np
import scipy.stats as stats
import math

def erlang_c(c, a):
    # a = lambda / mu
    # P0
    sum_terms = sum([(a**k) / math.factorial(k) for k in range(c)])
    last_term = (a**c) / (math.factorial(c) * (1 - a / c))
    p0 = 1.0 / (sum_terms + last_term)
    # P_queue (Erlang C probability of waiting)
    pc = last_term * p0
    return p0, pc

def mmc_queue(lambd, mu, c):
    rho = lambd / (c * mu)
    if rho >= 1.0:
        return {"status": "unstable", "rho": rho}
    a = lambd / mu
    p0, pc = erlang_c(c, a)
    lq = pc * (rho / (1 - rho))
    wq = lq / lambd
    ws = 1.0 / mu
    w = wq + ws
    l = lambd * w
    pct_waiting = (wq / w) * 100.0
    return {
        "status": "stable",
        "c": c,
        "lambda": lambd,
        "mu": mu,
        "rho": rho,
        "P0": p0,
        "P_wait": pc,
        "Lq": lq,
        "Wq": wq,
        "Ws": ws,
        "W": w,
        "L": l,
        "pct_waiting": pct_waiting
    }

def mgc_allen_cunneen(lambd, mean_s, std_s, c, ca2=1.0):
    # ca2 = variance / mean^2 for arrival process
    mu = 1.0 / mean_s
    rho = lambd / (c * mu)
    if rho >= 1.0:
        return {"status": "unstable", "rho": rho}
    a = lambd / mu
    p0, pc = erlang_c(c, a)
    cs2 = (std_s / mean_s) ** 2
    # Allen-Cunneen approximation
    wq_mmc = (pc * (rho / (1 - rho))) / lambd
    wq = wq_mmc * ((ca2 + cs2) / 2.0)
    lq = lambd * wq
    ws = mean_s
    w = wq + ws
    l = lambd * w
    pct_waiting = (wq / w) * 100.0
    return {
        "status": "stable",
        "c": c,
        "lambda": lambd,
        "mu": mu,
        "rho": rho,
        "Wq": wq,
        "Ws": ws,
        "W": w,
        "Lq": lq,
        "L": l,
        "pct_waiting": pct_waiting
    }

lambd = 0.3369 # ships per hour (from G08 data)

print("=== TEORÍA DE COLAS A PRIORI (c = 3 bermas) ===")
for ws_val in [6.35, 7.0, 7.5, 8.0, 8.69]:
    mu_val = 1.0 / ws_val
    res = mmc_queue(lambd, mu_val, 3)
    if res['status'] == 'stable':
        print(f"Ws = {ws_val:.2f} h | rho = {res['rho']:.3f} | Wq = {res['Wq']:.2f} h | W = {res['W']:.2f} h | L = {res['L']:.2f} | % Espera = {res['pct_waiting']:.1f}%")
    else:
        print(f"Ws = {ws_val:.2f} h | Inestable (rho = {res['rho']:.3f} >= 1)")

print("\n=== M/G/c con Allen-Cunneen (CV llegadas = 2.49) ===")
ca2 = 2.494 ** 2
for ws_val in [6.35, 7.0, 7.5]:
    std_s = ws_val * 0.3
    res_mgc = mgc_allen_cunneen(lambd, ws_val, std_s, 3, ca2=ca2)
    print(f"Ws = {ws_val:.2f} h | Wq_aprox = {res_mgc['Wq']:.2f} h | W_aprox = {res_mgc['W']:.2f} h | % Espera = {res_mgc['pct_waiting']:.1f}%")
