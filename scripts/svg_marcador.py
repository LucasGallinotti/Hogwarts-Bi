"""
Implementación de referencia (Python) del SVG del marcador de Quidditch
(página Quidditch y Hechizos). La medida DAX [Marcador de Quidditch (SVG)]
construye la misma cadena; generar_casos_validacion.py compara ambas.

Contenido, todo calculado con medidas existentes en el contexto de filtro:
- Resumen: [Partidos], [Partidos Decididos por la Snitch], [Puntos por Partido].
- Jugadores destacados: los tres máximos goleadores del contexto ([Goles] por estudiante).
- Una fila por casa, ordenada por [Posición Copa Quidditch]: partidos jugados,
  victorias, derrotas, puntos a favor y en contra, diferencia y Snitches.
- Casa sin partidos en el período: fila con "—" al final. Sin partidos en
  absoluto: aviso explícito. Con el segmentador de casa, las demás se atenúan.
"""

from __future__ import annotations

import sys
from decimal import ROUND_HALF_UP, Decimal

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # consolas Windows en cp1252

ROMANOS = {1: "I", 2: "II", 3: "III", 4: "IV"}
GLIFOS = {
    "Fuego": "M12 3.5L21 19.5H3Z",
    "Agua": "M12 20.5L3 4.5H21Z",
    "Aire": "M12 3.5L21 19.5H3ZM6.6 13.5H17.4",
    "Tierra": "M12 20.5L3 4.5H21ZM6.6 10.5H17.4",
}
# Fondo: marco de latón y líneas tenues de un campo de juego (óvalo, círculo central y aros).
FONDO = (
    "<defs><linearGradient id='b' x1='0' x2='1'><stop offset='0' stop-color='#4A3A1D'/><stop offset='.3' stop-color='#F3D79B'/>"
    "<stop offset='.55' stop-color='#B08A44'/><stop offset='1' stop-color='#3A2E17'/></linearGradient>"
    "<radialGradient id='w' cx='.5' cy='.5' r='.6'><stop offset='0' stop-color='#1C2A3C'/><stop offset='1' stop-color='#0E1322'/></radialGradient></defs>"
    "<rect x='2' y='2' width='596' height='242' rx='12' fill='url(#w)' stroke='url(#b)' stroke-width='2'/>"
    "<rect x='8' y='8' width='584' height='230' rx='9' fill='none' stroke='#5E4A25' stroke-width='.8'/>"
    "<g fill='none' stroke='#F3D79B' stroke-opacity='.07' stroke-width='1.5'>"
    "<ellipse cx='300' cy='124' rx='280' ry='88'/><circle cx='300' cy='124' r='22'/><path d='M300 40V234'/>"
    "<circle cx='34' cy='96' r='7'/><circle cx='26' cy='118' r='9'/><circle cx='34' cy='140' r='7'/>"
    "<circle cx='566' cy='96' r='7'/><circle cx='574' cy='118' r='9'/><circle cx='566' cy='140' r='7'/></g>"
    # Esfera alada (emblema) junto al título.
    "<g transform='translate(30 27)'><path d='M-4 0C-9-7-16-7-20-4C-15-3-13-1-12 1C-9 1-6 1-4 0ZM4 0C9-7 16-7 20-4C15-3 13-1 12 1C9 1 6 1 4 0Z'"
    " fill='#EDE2C4' fill-opacity='.9'/><circle r='4.5' fill='#E2BC6A'/></g>"
    "<text x='56' y='31' font-family='Georgia,serif' font-size='13' letter-spacing='2.5' fill='#F3D79B'>MARCADOR · COPA DE QUIDDITCH</text>"
    "<g font-family='Segoe UI,sans-serif' font-size='10' letter-spacing='1' fill='#A8843F'>"
    "<text x='28' y='60'>#</text><text x='72' y='60'>CASA</text><text x='262' y='60' text-anchor='end'>PJ</text>"
    "<text x='300' y='60' text-anchor='end'>G</text><text x='338' y='60' text-anchor='end'>P</text>"
    "<text x='408' y='60' text-anchor='end'>A FAVOR</text><text x='482' y='60' text-anchor='end'>EN CONTRA</text>"
    "<text x='532' y='60' text-anchor='end'>DIF.</text><text x='578' y='60' text-anchor='end'>SNITCH</text></g>"
    "<path d='M22 67H578' stroke='#5E4A25' stroke-width='1'/>"
)


def miles(n: int) -> str:
    return f"{abs(n):,}".replace(",", ".")


def con_signo(n: int) -> str:
    return ("+" if n > 0 else "−" if n < 0 else "") + miles(n)


def decimal(x: float) -> str:
    """FORMAT ( x, "#,0.0" ) con cultura es-ES (redondeo de la mitad hacia arriba, como DAX)."""
    redondeado = Decimal(repr(x)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    entero, dec = f"{redondeado:,.1f}".split(".")
    return entero.replace(",", ".") + "," + dec


def fila(c: dict, indice: int, atenuado: bool) -> str:
    y = 92 + indice * 30
    jugo = c["jugados"] is not None
    lider = c["puesto"] == 1
    v = lambda x: miles(x) if jugo else "—"  # noqa: E731
    return "".join([
        f"<g opacity='{'.3' if atenuado else '1'}' data-casa='{c['clave']}' data-puesto='{c['puesto'] if c['puesto'] else ''}'"
        f" data-victorias='{c['victorias'] if jugo else ''}' data-favor='{c['favor'] if jugo else ''}'>",
        f"<rect x='18' y='{y - 19}' width='564' height='26' rx='5' fill='#D9B66F' fill-opacity='.12'/>" if lider and jugo else "",
        f"<rect x='18' y='{y - 19}' width='4' height='26' rx='2' fill='{c['color']}'/>",
        f"<circle cx='34' cy='{y - 6}' r='10' fill='#0E121C' stroke='#A8843F' stroke-width='1.2'/>",
        f"<text x='34' y='{y - 2}' text-anchor='middle' font-family='Georgia,serif' font-size='11' fill='#F3D79B'>"
        f"{ROMANOS[c['puesto']] if c['puesto'] else '—'}</text>",
        f"<g transform='translate(52 {y - 15}) scale(.75)'><path d='{GLIFOS[c['elemento']]}' fill='none' stroke='{c['color']}'"
        " stroke-width='2.6' stroke-linejoin='round'/></g>",
        f"<text x='72' y='{y}' font-family='Georgia,serif' font-size='16' fill='#EDE6D6'>{c['nombre']}</text>",
        f"<g font-family='Segoe UI,sans-serif' font-size='16' fill='#EDE6D6' text-anchor='end'>",
        f"<text x='262' y='{y}'>{v(c['jugados'])}</text>",
        f"<text x='300' y='{y}' fill='#86CFA4'>{v(c['victorias'])}</text>",
        f"<text x='338' y='{y}' fill='#E8978B'>{v(c['derrotas'])}</text>",
        f"<text x='408' y='{y}' font-weight='600'>{v(c['favor'])}</text>",
        f"<text x='482' y='{y}' fill='#B9B1A0'>{v(c['contra'])}</text>",
        f"<text x='532' y='{y}' fill='#B9B1A0'>{con_signo(c['favor'] - c['contra']) if jugo else '—'}</text>",
        f"<text x='578' y='{y}' fill='#F3D79B'>{v(c['snitches'])}</text>",
        "</g></g>",
    ])


def svg(casas: list[dict], seleccion: set[str] | None, partidos: int, decididos: int, promedio: float | None,
        goleadores: list[dict]) -> str:
    """casas: [{orden, clave, nombre, color, elemento, jugados, victorias, derrotas, favor, contra, snitches, puesto}].
    goleadores: [{nombre, color, goles}] de todos los jugadores con goles en el contexto; se muestran los 3 primeros
    (más goles; desempata el nombre)."""
    ordenadas = sorted(casas, key=lambda c: (c["puesto"] or 9, c["orden"]))
    if partidos:
        resumen = (f"<path d='M22 192H578' stroke='#5E4A25' stroke-width='.8'/>"
                   f"<text x='300' y='210' text-anchor='middle' font-family='Segoe UI,sans-serif' font-size='12' fill='#B9B1A0'>"
                   f"{partidos} {'partido' if partidos == 1 else 'partidos'} · <tspan fill='#F3D79B'>{decididos}</tspan> "
                   f"{'decidido' if decididos == 1 else 'decididos'} por la Snitch · "
                   f"{decimal(promedio)} pts por partido</text>")
    else:
        resumen = ("<path d='M22 192H578' stroke='#5E4A25' stroke-width='.8'/>"
                   "<text x='300' y='210' text-anchor='middle' font-family='Segoe UI,sans-serif' font-size='12' fill='#B9B1A0'>"
                   "Sin partidos en el período seleccionado</text>")
    top = sorted(goleadores, key=lambda g: (-g["goles"], g["nombre"]))[:3]
    resumen += ("<text x='300' y='234' text-anchor='middle' font-family='Segoe UI,sans-serif' font-size='12' fill='#EDE6D6'>"
                "<tspan fill='#A8843F' font-size='10' letter-spacing='1'>MÁXIMOS GOLEADORES</tspan> "
                + (" · ".join(f"<tspan fill='{g['color']}'>●</tspan> {g['nombre']} <tspan fill='#F3D79B'>{miles(g['goles'])}</tspan>"
                             for g in top) or "<tspan fill='#B9B1A0'>sin goles en el período</tspan>")
                + "</text>")
    cuerpo = "".join(fila(c, i, seleccion is not None and c["clave"] not in seleccion) for i, c in enumerate(ordenadas))
    contenido = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 246'>" + FONDO + resumen + cuerpo + "</svg>"
    return "data:image/svg+xml;utf8," + contenido.replace("#", "%23")



def descripcion(casas: list[dict]) -> str:
    """Texto alternativo: [Marcador de Quidditch (descripción)]."""
    jugaron = sorted((c for c in casas if c["jugados"] is not None), key=lambda c: (c["puesto"], c["orden"]))
    if not jugaron:
        return "Marcador de la Copa de Quidditch: sin partidos en el período seleccionado"
    return "Marcador de la Copa de Quidditch: " + "; ".join(
        f"{c['puesto']}.º {c['nombre']}, {miles(c['victorias'])} victorias de {miles(c['jugados'])}, "
        f"{miles(c['favor'])} puntos a favor" for c in jugaron)

if __name__ == "__main__":
    from pathlib import Path
    from urllib.parse import unquote

    base = {"gryffindor": ("Gryffindor", "#C23634", "Fuego", 1), "slytherin": ("Slytherin", "#33A47D", "Agua", 2),
            "ravenclaw": ("Ravenclaw", "#6A8FE0", "Aire", 3), "hufflepuff": ("Hufflepuff", "#BC8C2A", "Tierra", 4)}
    datos = {"gryffindor": (3, 2, 1, 540, 350, 2, 1), "slytherin": (3, 2, 1, 460, 360, 2, 2),
             "ravenclaw": (3, 0, 3, 250, 630, 0, 4), "hufflepuff": (3, 2, 1, 420, 330, 2, 3)}
    casas = [{"clave": k, "nombre": n, "color": col, "elemento": e, "orden": o, "jugados": d[0], "victorias": d[1],
              "derrotas": d[2], "favor": d[3], "contra": d[4], "snitches": d[5], "puesto": d[6]}
             for k, (n, col, e, o) in base.items() for d in [datos[k]]]
    goleadores = [{"nombre": "Tobias Ashcombe", "color": "#C23634", "goles": 11}, {"nombre": "Arlo Fenwick", "color": "#6A8FE0", "goles": 10},
                  {"nombre": "Odalys Ferro", "color": "#33A47D", "goles": 9}, {"nombre": "Elara Brightwater", "color": "#C23634", "goles": 7}]
    uri = svg(casas, None, 6, 3, 278.333, goleadores)
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("marcador.svg")
    destino.write_text(unquote(uri.split(",", 1)[1]), encoding="utf-8")
    print(f"{len(uri)} caracteres → {destino}")
