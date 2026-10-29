"""Dibuja la estructura del random forest elegido. Lo usa la notebook 03."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def coma(numero):
    return f"{numero:.2f}".replace(".", ",")


def dibujar_estructura(modelo, filas, columnas, pesos, archivo):
    arbol = modelo.estimators_[0]
    n_arboles = int(modelo.n_estimators)
    profundidad = int(modelo.max_depth)
    hoja = int(modelo.min_samples_leaf)
    corte = int(arbol.max_features_)
    muestra = (
        "Muestra con reposición"
        if modelo.bootstrap
        else "Usa todas las filas"
    )
    izquierda = [
        f"{filas} filas, {columnas} columnas",
        muestra,
        f"Cada corte mira {corte} columnas",
        f"Profundidad {profundidad}, hoja de {hoja} hechos",
        f"Peso: leve {coma(pesos['LEVE'])}, grave {coma(pesos['GRAVE'])}, mortal {coma(pesos['MORTAL'])}",
    ]
    derecha = [
        f"{n_arboles} árboles, armados así",
        f"El hecho recorre los {n_arboles}",
        "Cada uno da leve, grave y mortal",
        f"Se promedian las {n_arboles}",
        "Gana la proporción más alta",
    ]

    figura, eje = plt.subplots(figsize=(11.4, 6.2))
    eje.set_xlim(0, 100)
    eje.set_ylim(0, 100)
    eje.axis("off")
    figura.patch.set_facecolor("white")

    def panel(x, titulo):
        eje.add_patch(
            FancyBboxPatch(
                (x, 3),
                46,
                94,
                boxstyle="round,pad=0.4,rounding_size=1.2",
                facecolor="#e6e6e6",
                edgecolor="#8a8a8a",
                linewidth=1,
            )
        )
        eje.text(x + 23, 90, titulo, ha="center", va="center", fontsize=12, color="#1f1f1f")

    def columna(x, textos):
        ancho = 38
        alto = 12
        izquierda_caja = x + 4
        bases = [72, 56, 40, 24, 8]
        for base, texto in zip(bases, textos):
            eje.add_patch(
                FancyBboxPatch(
                    (izquierda_caja, base),
                    ancho,
                    alto,
                    boxstyle="round,pad=0.3,rounding_size=0.8",
                    facecolor="#f7f7f7",
                    edgecolor="#8a8a8a",
                    linewidth=1,
                )
            )
            eje.text(
                izquierda_caja + ancho / 2,
                base + alto / 2,
                texto,
                ha="center",
                va="center",
                fontsize=10,
                color="#1f1f1f",
                wrap=True,
            )
        for origen, destino in zip(bases, bases[1:]):
            eje.annotate(
                "",
                xy=(izquierda_caja + ancho / 2, destino + alto + 0.4),
                xytext=(izquierda_caja + ancho / 2, origen - 0.2),
                arrowprops=dict(arrowstyle="-|>", color="#1f1f1f", lw=1.05),
            )
        return izquierda_caja, ancho, bases, alto

    panel(2, "Cómo se arma cada árbol")
    panel(52, "Cómo predice el bosque")
    ix, ancho, bases, alto = columna(2, izquierda)
    dx, _, bases_d, _ = columna(52, derecha)
    eje.annotate(
        "",
        xy=(dx, bases_d[0] + alto / 2),
        xytext=(ix + ancho, bases[-1] + alto / 2),
        arrowprops=dict(arrowstyle="-|>", color="#1f1f1f", lw=1.05),
    )
    archivo = Path(archivo)
    archivo.parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(archivo, dpi=140, bbox_inches="tight", facecolor="white")
    return {
        "arboles": n_arboles,
        "profundidad": profundidad,
        "hoja": hoja,
        "columnas_por_corte": corte,
        "filas": int(filas),
        "columnas": int(columnas),
        "bootstrap": bool(modelo.bootstrap),
        "archivo": str(archivo),
    }
