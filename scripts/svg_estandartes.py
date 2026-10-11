"""
Implementación de referencia (Python) del SVG de los estandartes de las casas
(página Rendimiento de las casas). La medida DAX [Estandartes de las Casas (SVG)]
construye la misma cadena; generar_casos_validacion.py compara ambas.

Cada estandarte muestra datos del contexto de filtro: puesto, puntos netos y
variación contra el período anterior, junto con la identidad fija de la casa
(color, sigilo alquímico de su elemento y rasgos).
"""

from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # consolas Windows en cp1252

ANCHO = 310
ROMANOS = {1: "I", 2: "II", 3: "III", 4: "IV"}
GLIFOS = {
    "Fuego": "M12 3.5L21 19.5H3Z",
    "Agua": "M12 20.5L3 4.5H21Z",
    "Aire": "M12 3.5L21 19.5H3ZM6.6 13.5H17.4",
    "Tierra": "M12 20.5L3 4.5H21ZM6.6 10.5H17.4",
}
DEFS = (
    "<defs>"
    "<linearGradient id='b' x1='0' x2='1'><stop offset='0' stop-color='#4A3A1D'/><stop offset='.3' stop-color='#F3D79B'/>"
    "<stop offset='.55' stop-color='#B08A44'/><stop offset='1' stop-color='#3A2E17'/></linearGradient>"
    "<linearGradient id='t' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#fff' stop-opacity='.18'/>"
    "<stop offset='.5' stop-color='#fff' stop-opacity='0'/><stop offset='1' stop-color='#000' stop-opacity='.4'/></linearGradient>"
    "<path id='p' d='M24 12H76V98L50 84L24 98Z'/>"
    "</defs>"
)


def miles(n: int) -> str:
    return f"{abs(n):,}".replace(",", ".")


def estandarte(c: dict, puesto: int, atenuado: bool, comparacion: str) -> str:
    p = c["puntos"] or 0
    var = c["variacion"]
    if var is None:
        linea_var = "<text x='98' y='86' font-family='Segoe UI,sans-serif' font-size='15' fill='#8F877A'>Sin período previo</text>"
    else:
        flecha, tono = ("▲", "#86CFA4") if var > 0 else (("▼", "#E8978B") if var < 0 else ("=", "#B9B1A0"))
        signo = "+" if var > 0 else ("−" if var < 0 else "")
        linea_var = (f"<text x='98' y='86' font-family='Segoe UI,sans-serif' font-size='15' fill='{tono}'>"
                     f"{flecha} {signo}{miles(var)} <tspan fill='#8F877A'>{comparacion}</tspan></text>")
    return "".join([
        f"<g transform='translate({(c['orden'] - 1) * ANCHO} 0)' opacity='{'.3' if atenuado else '1'}'"
        f" data-casa='{c['clave']}' data-puntos='{p}' data-puesto='{puesto}' data-variacion='{'' if var is None else var}'>",
        "<rect x='14' y='8' width='72' height='4' rx='2' fill='url(#b)'/>",
        "<circle cx='14' cy='10' r='4' fill='#F3D79B'/><circle cx='86' cy='10' r='4' fill='#F3D79B'/>",
        f"<use href='#p' fill='{c['color']}'/><use href='#p' fill='url(#t)'/>",
        "<use href='#p' fill='none' stroke='url(#b)' stroke-width='2'/>",
        "<path d='M30 20H70' stroke='#F3D79B' stroke-opacity='.45'/>",
        f"<g transform='translate(32 34) scale(1.5)'><path d='{GLIFOS[c['elemento']]}' fill='none' stroke='#F6E7BE'"
        " stroke-width='1.6' stroke-linejoin='round'/></g>",
        f"<text x='98' y='36' font-family='Georgia,serif' font-size='24' fill='#EDE6D6'>{c['nombre']}</text>",
        f"<text x='98' y='62' font-family='Segoe UI,sans-serif' font-size='17' fill='#F3D79B'>{ROMANOS[puesto]} · "
        f"<tspan fill='#EDE6D6'>{'—' if c['puntos'] is None else ('−' if p < 0 else '') + miles(p)} puntos</tspan></text>",
        linea_var,
        f"<text x='98' y='106' font-family='Segoe UI,sans-serif' font-size='11' fill='#8F877A'>{c['elemento']} · {c['rasgos']}</text>",
        "</g>",
    ])


def svg(casas: list[dict], seleccion: set[str] | None, comparacion: str) -> str:
    valores = [c["puntos"] or 0 for c in casas]
    cuerpo = "".join(
        estandarte(c, 1 + sum(1 for v in valores if v > (c["puntos"] or 0)),
                   seleccion is not None and c["clave"] not in seleccion, comparacion)
        for c in sorted(casas, key=lambda c: c["orden"])
    )
    contenido = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1240 116'>" + DEFS + cuerpo + "</svg>"
    return "data:image/svg+xml;utf8," + contenido.replace("#", "%23")


if __name__ == "__main__":
    from pathlib import Path
    from urllib.parse import unquote

    ejemplo = [
        {"orden": 1, "clave": "gryffindor", "nombre": "Gryffindor", "color": "#C23634", "elemento": "Fuego", "rasgos": "Valentía · Audacia · Temple", "puntos": 575, "variacion": -295},
        {"orden": 2, "clave": "slytherin", "nombre": "Slytherin", "color": "#33A47D", "elemento": "Agua", "rasgos": "Ambición · Astucia · Determinación", "puntos": 780, "variacion": -35},
        {"orden": 3, "clave": "ravenclaw", "nombre": "Ravenclaw", "color": "#6A8FE0", "elemento": "Aire", "rasgos": "Ingenio · Curiosidad · Sabiduría", "puntos": 670, "variacion": -345},
        {"orden": 4, "clave": "hufflepuff", "nombre": "Hufflepuff", "color": "#BC8C2A", "elemento": "Tierra", "rasgos": "Lealtad · Constancia · Justicia", "puntos": 710, "variacion": 55},
    ]
    uri = svg(ejemplo, None, "vs. Curso IV")
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("estandartes.svg")
    destino.write_text(unquote(uri.split(",", 1)[1]), encoding="utf-8")
    print(f"{len(uri)} caracteres → {destino}")
