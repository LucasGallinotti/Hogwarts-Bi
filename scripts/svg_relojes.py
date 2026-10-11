"""
Implementación de referencia (Python) del SVG de los relojes de arena.

La medida DAX [Relojes de Arena (SVG)] construye exactamente la misma cadena.
Este módulo cumple dos funciones:
  1. Diseño: generar el SVG para un conjunto de puntos y verlo en un navegador.
  2. Prueba: generar_casos_validacion.py compara la salida DAX con esta función
     para varios contextos de filtro (mismos niveles de arena, mismas cifras).

Reglas de representación (idénticas en DAX):
- Nivel de arena (cámara inferior) = 92 px × max(puntos, 0) / máximo positivo
  entre las cuatro casas. Las cámaras son cilíndricas en el tramo medido, así
  que la altura es proporcional a los puntos.
- La cámara superior queda vacía a propósito: una sola codificación (la arena
  caída) evita que el lector compare dos escalas distintas.
- Sin máximo positivo (todas en 0, vacías o negativas): escala 1, sin división por cero,
  sin niveles negativos (los puntos negativos se dibujan como 0 y se rotulan "Saldo negativo").
- Las alturas se redondean a píxeles enteros (error máximo 0,5 px de 92).
"""

from __future__ import annotations

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # consolas Windows en cp1252

ANCHO_CELDA = 260
ROMANOS = {1: 'I', 2: 'II', 3: 'III', 4: 'IV'}
GLIFOS = {
    "Fuego": "M12 3.5L21 19.5H3Z",
    "Agua": "M12 20.5L3 4.5H21Z",
    "Aire": "M12 3.5L21 19.5H3ZM6.6 13.5H17.4",
    "Tierra": "M12 20.5L3 4.5H21ZM6.6 10.5H17.4",
}
ALTO_INFERIOR = 92   # tramo recto medible de la cámara inferior (y 206 → 298)
BASE_INFERIOR = 298

DEFS = (
    "<defs>"
    "<linearGradient id='b' x1='0' x2='1'><stop offset='0' stop-color='#4A3A1D'/><stop offset='.3' stop-color='#F3D79B'/>"
    "<stop offset='.55' stop-color='#B08A44'/><stop offset='1' stop-color='#3A2E17'/></linearGradient>"
    "<linearGradient id='s' x1='0' x2='1'><stop offset='0' stop-opacity='.45'/><stop offset='.35' stop-opacity='0'/>"
    "<stop offset='.75' stop-opacity='.08'/><stop offset='1' stop-opacity='.5'/></linearGradient>"
    "<radialGradient id='l'><stop offset='0' stop-color='#F3D79B' stop-opacity='.26'/><stop offset='1' stop-color='#F3D79B' stop-opacity='0'/></radialGradient>"
    "<pattern id='g' width='7' height='6' patternUnits='userSpaceOnUse'><circle cx='1.5' cy='1.5' r='.9' fill='#fff' fill-opacity='.38'/>"
    "<circle cx='5' cy='4.2' r='.7' fill='#000' fill-opacity='.3'/></pattern>"
    # Armazón: cresta ojival con medallón, pináculos, columnas con anillos, placas y patas.
    "<g id='r'>"
    "<path d='M94 24 C100 2 160 2 166 24' fill='none' stroke='url(#b)' stroke-width='3'/>"
    "<path d='M50 22 L56 3 L62 22 Z M198 22 L204 3 L210 22 Z' fill='url(#b)'/>"
    "<circle cx='56' cy='3' r='2.6' fill='#F3D79B'/><circle cx='204' cy='3' r='2.6' fill='#F3D79B'/>"
    "<rect x='46' y='22' width='168' height='14' rx='6' fill='url(#b)'/><rect x='56' y='36' width='148' height='4' fill='#2E2412'/>"
    "<rect x='59' y='40' width='8' height='258' rx='3' fill='url(#b)'/><rect x='193' y='40' width='8' height='258' rx='3' fill='url(#b)'/>"
    "<path d='M56 98h14v6H56zM190 98h14v6h-14zM56 166h14v6H56zM190 166h14v6h-14zM56 234h14v6H56zM190 234h14v6h-14z' fill='#E9CB8A'/>"
    "<rect x='56' y='298' width='148' height='4' fill='#2E2412'/><rect x='46' y='302' width='168' height='14' rx='6' fill='url(#b)'/>"
    "<path d='M56 316h22l-4 9H60zM182 316h22l-4 9h-14z' fill='url(#b)'/>"
    "<path d='M67 54Q67 40 81 40M193 54Q193 40 179 40M67 284Q67 298 81 298M193 284Q193 298 179 298' fill='none' stroke='url(#b)' stroke-width='3'/>"
    "<path d='M60 60l7-6M60 80l7-6M60 128l7-6M60 148l7-6M60 196l7-6M60 216l7-6M60 262l7-6M60 282l7-6"
    "M194 60l7-6M194 80l7-6M194 128l7-6M194 148l7-6M194 196l7-6M194 216l7-6M194 262l7-6M194 282l7-6' stroke='#3A2E17' stroke-width='1.4'/>"
    "<g fill='#2E2412'><circle cx='72' cy='29' r='1.8'/><circle cx='100' cy='29' r='1.8'/><circle cx='160' cy='29' r='1.8'/>"
    "<circle cx='188' cy='29' r='1.8'/><circle cx='72' cy='309' r='1.8'/><circle cx='100' cy='309' r='1.8'/>"
    "<circle cx='160' cy='309' r='1.8'/><circle cx='188' cy='309' r='1.8'/></g>"
    "<circle cx='130' cy='17' r='13' fill='#0E121C' stroke='url(#b)' stroke-width='2.5'/>"
    "</g>"
    # Vidrio: se dibuja sobre la arena.
    "<g id='v' stroke='#F3E6C8' stroke-opacity='.45' stroke-width='1.2'>"
    "<path d='M86 40H174V100Q174 132 136 146L133 160H127L124 146Q86 132 86 100Z' fill='#fff' fill-opacity='.025'/>"
    "<path d='M127 160H133L136 174Q174 188 174 206V298H86V206Q86 188 124 174Z' fill='#fff' fill-opacity='.025'/>"
    "<path d='M95 46V94M95 212V290' stroke='#fff' stroke-opacity='.22' stroke-width='3' stroke-linecap='round'/>"
    "</g>"
    "<path id='e' d='M0-6L1.4-1.4L6 0L1.4 1.4L0 6L-1.4 1.4L-6 0L-1.4-1.4Z' fill='#F3D79B'/>"
    "</defs>"
)


def miles(n: int) -> str:
    """FORMAT ( n, "#,0" ) con cultura es-ES; negativo con signo menos tipográfico."""
    s = f"{abs(n):,}".replace(",", ".")
    return ("−" if n < 0 else "") + s


def reloj(orden: int, clave: str, nombre: str, color: str, elemento: str, puntos: int | None, puesto: int, maximo: int,
          empatados_en_punta: int, atenuado: bool) -> str:
    escala = maximo if maximo > 0 else 1
    p = puntos or 0
    positivo = max(p, 0)
    alto = int(ALTO_INFERIOR * positivo / escala + 0.5)  # ROUND de DAX: mitad hacia arriba
    lider = maximo > 0 and p == maximo
    if puntos is None:
        detalle = "Sin anotaciones"
    elif p < 0:
        detalle = "Saldo negativo"
    elif lider:
        detalle = "Comparte la punta" if empatados_en_punta > 1 else "Lidera"
    elif maximo <= 0:
        detalle = "Sin puntos a favor"
    else:
        detalle = f"a {miles(maximo - p)} del líder"
    partes = [
        f"<g transform='translate({(orden - 1) * ANCHO_CELDA} 0)' opacity='{'.3' if atenuado else '1'}'"
        f" data-casa='{clave}' data-puntos='{p}' data-nivel='{alto}' data-puesto='{puesto}'>",
        ("<ellipse cx='130' cy='165' rx='122' ry='165' fill='url(#l)'/>"
         "<use href='#e' x='36' y='70' opacity='.8'/><use href='#e' x='226' y='130' opacity='.6'/>"
         "<use href='#e' x='222' y='46' opacity='.9'/>") if lider else "",
        f"<ellipse cx='130' cy='329' rx='84' ry='4' fill='{color}' fill-opacity='.35'/>",
        "<use href='#r'/>",
        f"<text x='130' y='22' text-anchor='middle' font-family='Georgia,serif' font-size='13' fill='#F3D79B'>{ROMANOS[puesto]}</text>",
    ]
    if alto > 0:
        y = BASE_INFERIOR - alto
        partes += [
            f"<path d='M130 150V{y}' stroke='{color}' stroke-width='2' stroke-dasharray='2 4'/>",
            f"<rect x='87' y='{y}' width='86' height='{alto}' fill='{color}'/>",
            f"<rect x='87' y='{y}' width='86' height='{alto}' fill='url(#g)'/>",
            f"<rect x='87' y='{y}' width='86' height='{alto}' fill='url(#s)'/>",
            f"<rect x='87' y='{y}' width='86' height='2' fill='#fff' fill-opacity='.5'/>",
        ]
    partes += [
        "<use href='#v'/>",
        f"<g transform='translate(122 336) scale(.67)'><path d='{GLIFOS[elemento]}' fill='none' stroke='{color}' stroke-width='2.6' stroke-linejoin='round'/></g>",
        f"<text x='130' y='371' text-anchor='middle' font-family='Georgia,serif' font-size='20' letter-spacing='3' fill='#EDE6D6'>{nombre.upper()}</text>",
        f"<text x='130' y='413' text-anchor='middle' font-family='Segoe UI Light,Segoe UI,sans-serif' font-size='38' fill='#F4EEDF'>{'—' if puntos is None else miles(p)}</text>",
        f"<text x='130' y='437' text-anchor='middle' font-family='Segoe UI,sans-serif' font-size='17' fill='#B9B1A0'>{detalle}</text>",
        "</g>",
    ]
    return "".join(partes)


def svg(casas: list[dict], seleccion: set[str] | None = None) -> str:
    """casas: [{orden, clave, nombre, color, puntos (int|None)}]. seleccion: casas filtradas (None = sin filtro)."""
    valores = [c["puntos"] or 0 for c in casas]
    maximo = max(max(valores), 0)
    cuerpo = []
    for c in sorted(casas, key=lambda c: c["orden"]):
        p = c["puntos"] or 0
        puesto = 1 + sum(1 for v in valores if v > p)
        empatados = sum(1 for v in valores if v == maximo)
        atenuado = seleccion is not None and c["clave"] not in seleccion
        cuerpo.append(reloj(c["orden"], c["clave"], c["nombre"], c["color"], c["elemento"], c["puntos"], puesto, maximo, empatados, atenuado))
    contenido = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1040 442'>" + DEFS + "".join(cuerpo) + "</svg>"
    return "data:image/svg+xml;utf8," + contenido.replace("#", "%23")


if __name__ == "__main__":
    import sys
    from pathlib import Path
    from urllib.parse import unquote

    ejemplo = [
        {"orden": 1, "clave": "gryffindor", "nombre": "Gryffindor", "color": "#C23634", "elemento": "Fuego", "puntos": 575},
        {"orden": 2, "clave": "slytherin", "nombre": "Slytherin", "color": "#33A47D", "elemento": "Agua", "puntos": 780},
        {"orden": 3, "clave": "ravenclaw", "nombre": "Ravenclaw", "color": "#6A8FE0", "elemento": "Aire", "puntos": 670},
        {"orden": 4, "clave": "hufflepuff", "nombre": "Hufflepuff", "color": "#BC8C2A", "elemento": "Tierra", "puntos": 710},
    ]
    uri = svg(ejemplo)
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("relojes.svg")
    destino.write_text(unquote(uri.split(",", 1)[1]), encoding="utf-8")
    print(f"{len(uri)} caracteres → {destino}")
