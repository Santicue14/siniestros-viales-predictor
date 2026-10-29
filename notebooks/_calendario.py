# -*- coding: utf-8 -*-
"""Cruza los hechos con feriados nacionales y con el fin de semana.

La API https://api.argentinadatos.com/v1/feriados/{anio} publica 2021 en adelante.
2019 y 2020 responden 404. Esos dos años se arman con la misma regla de
traslado que la API usa en 2021-2025, más los feriados puente de los decretos
del período. La regla se contrasta contra el JSON de la API antes de usarla.
"""
import json
from datetime import date, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DATA = RAIZ / "data"
FIG = RAIZ / "docs" / "figuras"

PUENTES = {
    2019: [date(2019, 7, 8), date(2019, 8, 19), date(2019, 10, 14)],
    2020: [date(2020, 3, 23), date(2020, 7, 10), date(2020, 12, 7)],
}


def pascua(anio):
    a = anio % 19
    b, c = divmod(anio, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes, dia = divmod(h + l - 7 * m + 114, 31)
    return date(anio, mes, dia + 1)


def trasladar(dia):
    # Martes o miércoles: al lunes anterior. Jueves o viernes: al lunes siguiente.
    if dia.weekday() in (1, 2):
        return dia - timedelta(days=dia.weekday())
    if dia.weekday() in (3, 4):
        return dia + timedelta(days=7 - dia.weekday())
    return dia


def feriados_por_regla(anio):
    domingo = pascua(anio)
    fijos = [
        (date(anio, 1, 1), "inamovible", "Año nuevo"),
        (domingo - timedelta(days=48), "inamovible", "Carnaval"),
        (domingo - timedelta(days=47), "inamovible", "Carnaval"),
        (date(anio, 3, 24), "inamovible", "Día Nacional de la Memoria por la Verdad y la Justicia"),
        (date(anio, 4, 2), "inamovible", "Día del Veterano y de los Caídos en la Guerra de Malvinas"),
        (domingo - timedelta(days=2), "inamovible", "Viernes Santo"),
        (date(anio, 5, 1), "inamovible", "Día del Trabajador"),
        (date(anio, 5, 25), "inamovible", "Día de la Revolución de Mayo"),
        (trasladar(date(anio, 6, 17)), "trasladable", "Paso a la Inmortalidad del General Martín Güemes"),
        (date(anio, 6, 20), "inamovible", "Paso a la Inmortalidad del General Manuel Belgrano"),
        (date(anio, 7, 9), "inamovible", "Día de la Independencia"),
        (trasladar(date(anio, 8, 17)), "trasladable", "Paso a la Inmortalidad del Gral. José de San Martín"),
        (trasladar(date(anio, 10, 12)), "trasladable", "Día del Respeto a la Diversidad Cultural"),
        (trasladar(date(anio, 11, 20)), "trasladable", "Día de la Soberanía Nacional"),
        (date(anio, 12, 8), "inamovible", "Día de la Inmaculada Concepción de María"),
        (date(anio, 12, 25), "inamovible", "Navidad"),
    ]
    filas = [{"fecha": d.isoformat(), "tipo": t, "nombre": n, "anio": anio, "origen": "regla"} for d, t, n in fijos]
    for d in PUENTES.get(anio, []):
        filas.append({"fecha": d.isoformat(), "tipo": "puente", "nombre": "Puente turístico no laborable", "anio": anio, "origen": "decreto"})
    return filas


def cargar_api(anio):
    ruta = DATA / f"feriados_{anio}.json"
    payload = json.loads(ruta.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        raise SystemExit(f"{ruta.name} no es la lista de la API: {payload}")
    return payload


def contrastar():
    """La regla de traslado tiene que caer dentro de las fechas que publica la API."""
    for anio in range(2021, 2026):
        api = {item["fecha"] for item in cargar_api(anio)}
        regla = {item["fecha"] for item in feriados_por_regla(anio) if item["tipo"] != "puente"}
        faltan = sorted(regla - api)
        if faltan:
            raise SystemExit(f"{anio}: la regla arma fechas que la API no tiene: {faltan}")
        print(anio, "la regla entra en la API")


def calendario(anio_min, anio_max):
    filas = []
    for anio in range(anio_min, anio_max + 1):
        if anio >= 2021:
            for item in cargar_api(anio):
                filas.append({**item, "anio": anio, "origen": "api.argentinadatos.com"})
        else:
            filas.extend(feriados_por_regla(anio))
    feriados = pd.DataFrame(filas)
    feriados["fecha"] = pd.to_datetime(feriados["fecha"])
    return feriados


def main():
    contrastar()
    hechos = pd.read_csv(DATA / "siniestros_hechos_limpio.csv", sep=";", encoding="utf-8-sig")
    hechos["fecha"] = pd.to_datetime(hechos["fecha_siniestro"])
    anio_min = int(hechos["fecha"].dt.year.min())
    anio_max = int(hechos["fecha"].dt.year.max())
    feriados = calendario(anio_min, anio_max)
    feriados.to_csv(DATA / "feriados_nacionales_2019-2025.csv", index=False, encoding="utf-8-sig")

    fechas = set(feriados["fecha"])
    dias = pd.DataFrame({"fecha": pd.date_range(f"{anio_min}-01-01", f"{anio_max}-12-31")})
    dias["anio"] = dias["fecha"].dt.year
    dias["es_feriado"] = dias["fecha"].isin(fechas)
    dias["es_finde"] = dias["fecha"].dt.day_of_week >= 5
    dias["tipo_dia"] = "dia_de_semana"
    dias.loc[dias["es_finde"], "tipo_dia"] = "fin_de_semana"
    dias.loc[dias["es_feriado"], "tipo_dia"] = "feriado"

    hechos["es_feriado"] = hechos["fecha"].isin(fechas)
    hechos["anio"] = hechos["fecha"].dt.year
    hechos["es_finde"] = hechos["fecha"].dt.day_of_week >= 5
    hechos["tipo_dia"] = "dia_de_semana"
    hechos.loc[hechos["es_finde"], "tipo_dia"] = "fin_de_semana"
    hechos.loc[hechos["es_feriado"], "tipo_dia"] = "feriado"
    hechos["mortal"] = hechos["gravedad_siniestro"].eq("MORTAL")

    orden = ["dia_de_semana", "fin_de_semana", "feriado"]
    nombres = {"dia_de_semana": "Día de semana", "fin_de_semana": "Fin de semana", "feriado": "Feriado"}

    base = dias.groupby(["anio", "tipo_dia"]).size().rename("dias")
    agg = hechos.groupby(["anio", "tipo_dia"]).agg(hechos=("id_siniestro", "size"), mortales=("mortal", "sum"))
    tabla = agg.join(base).reset_index()
    tabla["hechos_por_dia"] = tabla["hechos"] / tabla["dias"]
    tabla["tasa_mortal"] = tabla["mortales"] / tabla["hechos"]
    tabla["tipo"] = tabla["tipo_dia"].map(nombres)
    tabla.to_csv(DATA / "calendario_por_anio.csv", index=False, encoding="utf-8-sig")

    print("\nPor año, hechos por día")
    piv = tabla.pivot(index="anio", columns="tipo_dia", values="hechos_por_dia").reindex(columns=orden)
    print(piv.round(2).to_string())
    print("\nTasa mortal")
    print(tabla.pivot(index="anio", columns="tipo_dia", values="tasa_mortal").reindex(columns=orden).mul(100).round(2).to_string())
    print("\nTotal")
    total_h = hechos.groupby("tipo_dia").agg(hechos=("id_siniestro", "size"), mortales=("mortal", "sum"))
    total_d = dias.groupby("tipo_dia").size().rename("dias")
    total = total_h.join(total_d)
    total["por_dia"] = total["hechos"] / total["dias"]
    total["tasa"] = total["mortales"] / total["hechos"]
    print(total.reindex(orden).round(3).to_string())

    # Corte que pidió: feriado contra día normal, y finde contra semana, sin excluir el cruce.
    hechos["corte_feriado"] = hechos["es_feriado"].map({True: "Feriado", False: "Día normal"})
    hechos["corte_semana"] = hechos["es_finde"].map({True: "Fin de semana", False: "Día de semana"})
    dias["corte_feriado"] = dias["es_feriado"].map({True: "Feriado", False: "Día normal"})
    dias["corte_semana"] = dias["es_finde"].map({True: "Fin de semana", False: "Día de semana"})

    def corte(col):
        h = hechos.groupby(["anio", col]).agg(hechos=("id_siniestro", "size"), mortales=("mortal", "sum"))
        d = dias.groupby(["anio", col]).size().rename("dias")
        t = h.join(d).reset_index()
        t["hechos_por_dia"] = t["hechos"] / t["dias"]
        t["tasa_mortal"] = t["mortales"] / t["hechos"]
        return t

    fer = corte("corte_feriado")
    sem = corte("corte_semana")
    print("\nFeriado vs normal, hechos por día")
    print(fer.pivot(index="anio", columns="corte_feriado", values="hechos_por_dia").round(2).to_string())
    print("\nFinde vs semana, hechos por día")
    print(sem.pivot(index="anio", columns="corte_semana", values="hechos_por_dia").round(2).to_string())

    colores = {"dia_de_semana": "#4C78A8", "fin_de_semana": "#F2C14E", "feriado": "#E45756"}
    fig, ejes = plt.subplots(1, 2, figsize=(11.2, 4.4))
    anios = sorted(tabla["anio"].unique())
    ancho = 0.25
    import numpy as np
    x = np.arange(len(anios))
    for eje, valor, titulo, ylabel in (
        (ejes[0], "hechos_por_dia", "Hechos por día", "Hechos por día"),
        (ejes[1], "tasa_mortal", "Tasa de hechos mortales", "Tasa"),
    ):
        for i, tipo in enumerate(orden):
            serie = tabla.loc[tabla["tipo_dia"].eq(tipo)].set_index("anio").reindex(anios)[valor]
            eje.bar(x + (i - 1) * ancho, serie.values, width=ancho, label=nombres[tipo], color=colores[tipo])
        eje.set_xticks(x)
        eje.set_xticklabels(anios)
        eje.set_title(titulo)
        eje.set_ylabel(ylabel)
        if valor == "tasa_mortal":
            eje.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _p: f"{100 * v:.1f} %"))
    ejes[0].legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "07_calendario.png", dpi=140, bbox_inches="tight")
    print("figura", FIG / "07_calendario.png")
    por_nombre(hechos, feriados)


def nombre_corto(nombre, tipo):
    n = str(nombre).lower()
    if tipo == "puente" or "puente" in n:
        return "Puente turístico"
    if "carnaval" in n:
        return "Carnaval"
    if "memoria" in n:
        return "Memoria, Verdad y Justicia"
    if "malvinas" in n:
        return "Malvinas"
    if "santo" in n:
        return "Viernes Santo"
    if "trabajador" in n:
        return "Día del Trabajador"
    if "mayo" in n:
        return "Revolución de Mayo"
    if "güemes" in n or "guemes" in n:
        return "Güemes"
    if "belgrano" in n:
        return "Belgrano"
    if "independencia" in n:
        return "Independencia"
    if "san mart" in n:
        return "San Martín"
    if "diversidad" in n:
        return "Diversidad cultural"
    if "soberan" in n:
        return "Soberanía Nacional"
    if "inmaculada" in n:
        return "Inmaculada"
    if "navidad" in n:
        return "Navidad"
    if "año nuevo" in n or "ano nuevo" in n:
        return "Año Nuevo"
    if "censo" in n:
        return "Censo nacional"
    if "decreto" in n:
        return "Feriado por decreto"
    return str(nombre)


def por_nombre(hechos, feriados):
    """Tasa y volumen de cada feriado. Un día entra una sola vez."""
    tabla_feriados = feriados.copy()
    tabla_feriados["feriado"] = [
        nombre_corto(nombre, tipo)
        for nombre, tipo in zip(tabla_feriados["nombre"], tabla_feriados["tipo"])
    ]
    cruce = hechos.merge(tabla_feriados[["fecha", "feriado"]], on="fecha", how="inner")
    resumen = (
        cruce.groupby("feriado")
        .agg(dias=("fecha", "nunique"), hechos=("id_siniestro", "size"), mortales=("mortal", "sum"))
        .reset_index()
    )
    resumen["hechos_por_dia"] = resumen["hechos"] / resumen["dias"]
    resumen["tasa_mortal"] = resumen["mortales"] / resumen["hechos"]
    resumen = resumen.sort_values(["tasa_mortal", "mortales"], ascending=False)
    resumen.to_csv(DATA / "feriados_por_nombre.csv", index=False, encoding="utf-8-sig")

    tasa_semana = 484 / 50481
    grafico = resumen.loc[resumen["dias"] >= 6].sort_values("tasa_mortal", ascending=True)
    colores = ["#E45756" if tasa > tasa_semana else "#4C78A8" for tasa in grafico["tasa_mortal"]]
    fig, ejes = plt.subplots(1, 2, figsize=(11.2, 6.2), sharey=True)
    ejes[0].barh(grafico["feriado"], grafico["tasa_mortal"], color=colores)
    ejes[0].axvline(tasa_semana, color="#333333", linewidth=1, linestyle="--")
    ejes[0].set_title("Tasa de hechos mortales")
    ejes[0].set_xlim(0, 0.072)
    ejes[0].set_xlabel("Muertes cada 100 hechos. La línea es el día de semana, 0,96 %.")
    ejes[0].xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _p: f"{100 * v:.0f} %"))
    for feriado, tasa, muertes in zip(grafico["feriado"], grafico["tasa_mortal"], grafico["mortales"]):
        ejes[0].text(tasa + 0.001, feriado, f"{int(muertes)} muertes", va="center", fontsize=8)
    ejes[1].barh(grafico["feriado"], grafico["hechos_por_dia"], color="#4C78A8")
    ejes[1].set_title("Hechos por día")
    ejes[1].set_xlabel("Hechos por día de ese feriado")
    fig.tight_layout()
    fig.savefig(FIG / "08_feriados_tasa.png", dpi=140, bbox_inches="tight")
    print(resumen.round(4).to_string(index=False))
    print("figura", FIG / "08_feriados_tasa.png")


if __name__ == "__main__":
    main()
