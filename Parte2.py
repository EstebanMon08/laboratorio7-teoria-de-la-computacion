import argparse
import csv
import math
import os
import statistics
import sys
import time

TAMANOS = [1, 10, 100, 1000, 10000, 100000, 1000000]
SALIDA = open(os.devnull, "w")


# Algoritmo a
def algoritmo_a(n):
    counter = 0
    i = n // 2
    while i <= n:
        j = 1
        while j + n // 2 <= n:
            k = 1
            while k <= n:
                counter += 1
                k = k * 2
            j += 1
        i += 1
    return counter


def algoritmo_a_contado(n):
    ops = 0
    counter = 0; ops += 1                 # counter = 0
    i = n // 2; ops += 1                  # i = n/2
    while True:
        ops += 1                          # i <= n
        if not i <= n:
            break
        j = 1; ops += 1                   # j = 1
        while True:
            ops += 1                      # j + n/2 <= n
            if not j + n // 2 <= n:
                break
            k = 1; ops += 1               # k = 1
            while True:
                ops += 1                  # k <= n
                if not k <= n:
                    break
                counter += 1; ops += 1    # counter++
                k = k * 2; ops += 1       # k = k*2
            j += 1; ops += 1              # j++
        i += 1; ops += 1                  # i++
    return ops


def formula_a(n):
    A = n - n // 2 + 1                    # iteraciones de i
    B = n - n // 2                        # iteraciones de j  (= ceil(n/2))
    C = n.bit_length()                    # iteraciones de k  (= floor(log2 n) + 1)
    return 3 + 4 * A + 4 * A * B + 3 * A * B * C


# Algoritmo b
def algoritmo_b(n):
    if n <= 1:
        return
    i = 1
    while i <= n:
        j = 1
        while j <= n:
            print("Sequence", file=SALIDA)
            break
        i += 1


def algoritmo_b_contado(n):
    ops = 0
    ops += 1                              # n <= 1
    if n <= 1:
        return ops
    i = 1; ops += 1                       # i = 1
    while True:
        ops += 1                          # i <= n
        if not i <= n:
            break
        j = 1; ops += 1                   # j = 1
        while True:
            ops += 1                      # j <= n
            if not j <= n:
                break
            print("Sequence", file=SALIDA); ops += 1   # printf
            ops += 1                      # break
            break
        i += 1; ops += 1                  # i++
    return ops


def formula_b(n):
    return 1 if n <= 1 else 6 * n + 3


# Algoritmo c
def algoritmo_c(n):
    i = 1
    while i <= n // 3:
        j = 1
        while j <= n:
            print("Sequence", file=SALIDA)
            j += 4
        i += 1


def algoritmo_c_contado(n):
    ops = 0
    i = 1; ops += 1                       # i = 1
    while True:
        ops += 1                          # i <= n/3
        if not i <= n // 3:
            break
        j = 1; ops += 1                   # j = 1
        while True:
            ops += 1                      # j <= n
            if not j <= n:
                break
            print("Sequence", file=SALIDA); ops += 1   # printf
            j += 4; ops += 1              # j += 4
        i += 1; ops += 1                  # i++
    return ops


def formula_c(n):
    A = n // 3                            # iteraciones de i
    B = (n + 3) // 4                      # iteraciones de j  (= ceil(n/4))
    return 2 + 4 * A + 3 * A * B


ALGORITMOS = {
    "a": (algoritmo_a, algoritmo_a_contado, formula_a, "O(n² log n)"),
    "b": (algoritmo_b, algoritmo_b_contado, formula_b, "O(n)"),
    "c": (algoritmo_c, algoritmo_c_contado, formula_c, "O(n²)"),
}


# ----------------------------------------------------------------------------
# Medición de tiempo
# ----------------------------------------------------------------------------
def medir_tiempo(funcion, n, repeticiones=5, minimo_total=0.2):
    """Devuelve la mediana del tiempo (s) de una ejecución de funcion(n).

    Para n pequeños una sola ejecución dura microsegundos, así que se repite
    la llamada en un lote hasta acumular al menos `minimo_total` segundos y se
    divide entre el número de llamadas. Luego se toma la mediana de varios
    lotes para reducir el ruido del sistema operativo.
    """
    # Calibrar cuántas llamadas caben en un lote
    llamadas = 1
    while True:
        t0 = time.perf_counter()
        for _ in range(llamadas):
            funcion(n)
        dt = time.perf_counter() - t0
        if dt >= minimo_total or llamadas >= 1_000_000:
            break
        llamadas *= 10 if dt < minimo_total / 10 else 2

    muestras = [dt / llamadas]
    if dt < 5:  # corridas largas: una sola muestra basta
        for _ in range(repeticiones - 1):
            t0 = time.perf_counter()
            for _ in range(llamadas):
                funcion(n)
            muestras.append((time.perf_counter() - t0) / llamadas)
    return statistics.median(muestras)


# Programa principal
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limite", type=float, default=3e9,
                        help="máximo de operaciones para medir realmente el tiempo de una corrida")
    parser.add_argument("--limite-conteo", type=float, default=1e8,
                        help="máximo de operaciones para ejecutar la versión instrumentada")
    args = parser.parse_args()

    filas = []
    for nombre, (pura, contada, formula, clase) in ALGORITMOS.items():
        print(f"\n=== Algoritmo {nombre}  {clase} ===")
        ops_por_seg = None
        for n in TAMANOS:
            ops_teoricas = formula(n)
            if ops_teoricas <= args.limite:
                if ops_teoricas <= args.limite_conteo:
                    ops = contada(n)
                    assert ops == ops_teoricas, f"el contador ({ops}) no coincide con T(n) ({ops_teoricas})"
                else:
                    ops = ops_teoricas  # fórmula ya verificada con el contador en n menores
                t = medir_tiempo(pura, n)
                if n >= 100:
                    ops_por_seg = ops / t
                modo = "medido"
            else:
                ops = ops_teoricas
                t = ops / ops_por_seg
                modo = "estimado"
            filas.append({"algoritmo": nombre, "n": n, "operaciones": ops,
                          "tiempo_s": t, "modo": modo})
            print(f"n={n:>8}  ops={ops:>22,}  tiempo={formatear_tiempo(t):>14}  ({modo})")

    with open("resultados_lab7.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=filas[0].keys())
        w.writeheader()
        w.writerows(filas)

    graficar(filas)
    print("\nListo: resultados_lab7.csv y grafica_algoritmo_{a,b,c}.png")


def formatear_tiempo(t):
    if t < 1e-3:
        return f"{t * 1e6:.2f} µs"
    if t < 1:
        return f"{t * 1e3:.2f} ms"
    if t < 3600:
        return f"{t:.2f} s"
    if t < 86400 * 2:
        return f"{t / 3600:.1f} h"
    if t < 86400 * 365:
        return f"{t / 86400:.1f} días"
    return f"{t / (86400 * 365):.1f} años"


def graficar(filas):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    AZUL, NARANJA = "#2a78d6", "#eb6834"
    TINTA, TINTA2, REJILLA = "#0b0b0b", "#52514e", "#e4e3df"

    for nombre, (_, _, _, clase) in ALGORITMOS.items():
        datos = [f for f in filas if f["algoritmo"] == nombre]
        fig, ejes = plt.subplots(1, 2, figsize=(11, 4.2))
        fig.patch.set_facecolor("#fcfcfb")
        paneles = [
            (ejes[0], "tiempo_s", "Tiempo real (s)", AZUL),
            (ejes[1], "operaciones", "Conteo de operaciones", NARANJA),
        ]
        for ax, clave, titulo, color in paneles:
            ax.set_facecolor("#fcfcfb")
            ns = [f["n"] for f in datos]
            ys = [f[clave] for f in datos]
            ax.plot(ns, ys, color=color, linewidth=2, zorder=2)
            med = [(f["n"], f[clave]) for f in datos if f["modo"] == "medido"]
            est = [(f["n"], f[clave]) for f in datos if f["modo"] == "estimado"]
            if med:
                ax.scatter(*zip(*med), s=45, color=color, edgecolor="#fcfcfb",
                           linewidth=2, zorder=3, label="medido")
            if est:
                ax.scatter(*zip(*est), s=45, facecolor="#fcfcfb", edgecolor=color,
                           linewidth=2, zorder=3, label="estimado")
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_xlabel("Tamaño de entrada n", color=TINTA2)
            ax.set_title(titulo, loc="left", color=TINTA, fontsize=11)
            ax.grid(True, which="major", color=REJILLA, linewidth=0.8)
            ax.tick_params(colors=TINTA2, labelsize=9)
            for s in ("top", "right"):
                ax.spines[s].set_visible(False)
            for s in ("left", "bottom"):
                ax.spines[s].set_color(REJILLA)
            if est:
                ax.legend(frameon=False, fontsize=9, labelcolor=TINTA2)
        fig.suptitle(f"Algoritmo {nombre}  —  {clase}", x=0.06, ha="left",
                     color=TINTA, fontsize=13, fontweight="bold")
        fig.tight_layout()
        fig.savefig(f"grafica_algoritmo_{nombre}.png", dpi=150)
        plt.close(fig)


if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    main()