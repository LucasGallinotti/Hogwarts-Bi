"""
Compara los resultados DAX obtenidos en Power BI Desktop con los esperados.

    python powerbi/scripts/comparar_validacion.py

Entradas:  validacion/casos.json (esperados, de generar_casos_validacion.py)
           validacion/resultados_dax.json (reales, de ejecutar_validacion.ps1)
Salida:    validacion/REPORTE_VALIDACION.md y código de salida 1 si algo no coincide.

Reglas de comparación:
- Las columnas se emparejan por nombre sin tabla ni corchetes ("DimCasa[CasaKey]" → "CasaKey").
- Una fila esperada que no aparece en el resultado DAX se compara como vacía
  (SUMMARIZECOLUMNS omite las filas cuyas medidas son todas BLANK).
- Números: tolerancia absoluta del caso (por defecto 0,0005). Textos: igualdad exacta.
- Una fila DAX con algún valor no vacío que no esté entre las esperadas es un error.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # consolas Windows en cp1252

RAIZ = Path(__file__).resolve().parents[1]
CASOS = RAIZ / "validacion" / "casos.json"
RESULTADOS = RAIZ / "validacion" / "resultados_dax.json"
REPORTE = RAIZ / "validacion" / "REPORTE_VALIDACION.md"


def nombre(col: str) -> str:
    m = re.search(r"\[([^\]]+)\]$", col)
    return m.group(1) if m else col


def igual(esperado, real, tol: float) -> bool:
    if esperado is None or real is None:
        return esperado is None and real is None
    if isinstance(esperado, bool) or isinstance(real, bool):
        return bool(esperado) == bool(real)
    if isinstance(esperado, (int, float)) and isinstance(real, (int, float)):
        return abs(float(esperado) - float(real)) <= tol
    return str(esperado) == str(real)


def clave(fila: dict, claves: list[str]):
    return tuple(str(fila.get(k)) for k in claves)


def main() -> int:
    casos = json.loads(CASOS.read_text(encoding="utf-8"))
    resultados = json.loads(RESULTADOS.read_text(encoding="utf-8-sig"))
    lineas = []
    total_valores = 0
    total_fallos = 0
    resumen = []

    for caso in casos:
        res = resultados.get(caso["id"])
        fallos = []
        if res is None:
            fallos.append("No se ejecutó la consulta.")
        elif res.get("error"):
            fallos.append(f"Error DAX: {res['error']}")
        else:
            reales = [{nombre(k): v for k, v in fila.items()} for fila in (res.get("filas") or [])]
            por_clave = {clave(f, caso["claves"]): f for f in reales}
            esperadas = {clave(f, caso["claves"]): f for f in caso["esperado"]}
            for k, esp in esperadas.items():
                real = por_clave.get(k, {}) if caso["claves"] else (reales[0] if reales else {})
                for col, valor in esp.items():
                    if col in caso["claves"]:
                        continue
                    total_valores += 1
                    if not igual(valor, real.get(col), caso["tolerancia"]):
                        obtenido = real.get(col)
                        if isinstance(valor, str) and isinstance(obtenido, str) and max(len(valor), len(obtenido)) > 200:
                            i = next((n for n, (a, b) in enumerate(zip(valor, obtenido)) if a != b), min(len(valor), len(obtenido)))
                            fallos.append(f"{col}: textos distintos desde el carácter {i} (largos {len(valor)} y {len(obtenido)}); "
                                          f"esperado …{valor[max(0, i - 60):i + 60]!r}… DAX …{obtenido[max(0, i - 60):i + 60]!r}…")
                        else:
                            fallos.append(f"{dict(zip(caso['claves'], k))} · {col}: esperado {valor!r}, DAX {obtenido!r}")
            if caso["claves"]:
                columnas = {c for f in caso["esperado"] for c in f if c not in caso["claves"]}
                for k, real in por_clave.items():
                    if k not in esperadas and any(real.get(c) is not None for c in columnas):
                        fallos.append(f"Fila inesperada en DAX: {real}")
        total_fallos += len(fallos)
        estado = "✅" if not fallos else "❌"
        resumen.append(f"| {estado} | `{caso['id']}` | {caso['descripcion']} | {len(caso['esperado'])} |")
        if fallos:
            lineas.append(f"\n### ❌ {caso['id']}\n")
            lineas += [f"- {f}" for f in fallos[:25]]

    ok = total_fallos == 0
    reporte = [
        "# Reporte de validación del modelo",
        "",
        f"Generado: {datetime.now():%Y-%m-%d %H:%M} · Casos: {len(casos)} · Valores comparados: {total_valores} · "
        f"Diferencias: {total_fallos}",
        "",
        "Cada caso ejecuta una consulta DAX contra el modelo abierto en Power BI Desktop (tras una actualización completa) "
        "y la compara con un resultado calculado de forma independiente en Python a partir de los CSV "
        "(`scripts/generar_casos_validacion.py`).",
        "",
        "| | Caso | Qué verifica | Filas esperadas |",
        "|---|---|---|---|",
        *resumen,
    ]
    if lineas:
        reporte += ["", "## Diferencias", *lineas]
    REPORTE.write_text("\n".join(reporte) + "\n", encoding="utf-8")
    print(f"{len(casos)} casos · {total_valores} valores · {total_fallos} diferencias → {REPORTE.relative_to(RAIZ)}")
    if lineas:
        print("\n".join(lineas[:60]))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
