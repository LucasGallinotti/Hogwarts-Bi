"""
Genera los casos de validación del modelo: consultas DAX + resultados esperados.

    python powerbi/scripts/generar_casos_validacion.py

Los resultados esperados se calculan aquí, en Python puro, leyendo los CSV de
powerbi/data con reglas de negocio escritas de forma independiente del DAX.
Si una medida y este cálculo coinciden, hay dos implementaciones distintas que
llegan al mismo número.

Salida: powerbi/validacion/casos.json. La ejecución contra Power BI Desktop la
hace ejecutar_validacion.ps1 y la comparación, comparar_validacion.py.
"""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # consolas Windows en cp1252

RAIZ = Path(__file__).resolve().parents[1]
DATOS = RAIZ / "data"
SALIDA = RAIZ / "validacion" / "casos.json"

CASAS = ["gryffindor", "slytherin", "ravenclaw", "hufflepuff"]
NOMBRE_CASA = {"gryffindor": "Gryffindor", "slytherin": "Slytherin", "ravenclaw": "Ravenclaw", "hufflepuff": "Hufflepuff"}
TERMINOS = ["otono", "invierno", "primavera"]
ROMANOS = ["I", "II", "III", "IV", "V"]


def leer(nombre: str) -> list[dict]:
    with open(DATOS / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f))


eventos = leer("eventos_puntos.csv")
partidos = leer("partidos.csv")
goles = leer("goles.csv")
practicas = leer("practicas_hechizos.csv")
hechizos = {h["id"]: h for h in leer("hechizos.csv")}
estudiantes = {e["id"]: e for e in leer("estudiantes.csv")}
calendario = leer("calendario.csv")

for e in eventos:
    e["curso"], e["week"], e["points"] = int(e["curso"]), int(e["week"]), int(e["points"])
for m in partidos:
    for k in ("curso", "week", "homeScore", "awayScore"):
        m[k] = int(m[k])
for p in practicas:
    p["curso"], p["casts"], p["successes"] = int(p["curso"]), int(p["casts"]), int(p["successes"])

# Rangos de semanas por trimestre (de calendario.csv).
RANGO = {(int(c["curso"]), c["term"]): (int(c["firstWeek"]), int(c["lastWeek"])) for c in calendario}


def termino_de(semana: int) -> str:
    for t in TERMINOS:
        a, b = RANGO[(1, t)]
        if a <= semana <= b:
            return t
    raise ValueError(semana)


def indice_trimestre(curso: int, termino: str) -> int:
    return (curso - 1) * 3 + TERMINOS.index(termino) + 1


# ── Helpers de negocio ───────────────────────────────────────────────────────

def en_periodo(curso: int, semana: int, cursos=None, terminos=None) -> bool:
    return (cursos is None or curso in cursos) and (terminos is None or termino_de(semana) in terminos)


def puntos(cursos=None, terminos=None, casa=None, filtro=lambda e: True):
    """Suma de puntos; None si no hay filas (equivale a BLANK)."""
    filas = [e for e in eventos if en_periodo(e["curso"], e["week"], cursos, terminos) and (casa is None or e["houseId"] == casa) and filtro(e)]
    return sum(e["points"] for e in filas) if filas else None


def ranking(valores: dict) -> dict:
    """Ranking de competición (1, 2, 2, 4); vacío cuenta como 0, igual que RANKX."""
    v = {k: (x or 0) for k, x in valores.items()}
    return {k: 1 + sum(1 for o in v.values() if o > v[k]) for k in v}


casos: list[dict] = []


def caso(id_: str, descripcion: str, dax: str, claves: list[str], filas: list[dict], tolerancia: float = 0.0005):
    casos.append({"id": id_, "descripcion": descripcion, "dax": dax.strip(), "claves": claves, "esperado": filas, "tolerancia": tolerancia})


FILTRO_CURSO = "TREATAS ( {{ {c} }}, DimTrimestre[CursoNumero] )"


# 1. Conteos de filas por tabla (tipos y transformaciones cargaron todo).
conteos = {
    "DimTrimestre": len(calendario),
    "DimSemana": sum(int(c["lastWeek"]) - int(c["firstWeek"]) + 1 for c in calendario),
    "DimCasa": 4,
    "DimEstudiante": len(estudiantes) + 1,
    "DimCategoria": 5,
    "DimHechizo": len(hechizos),
    "DimPartido": len(partidos),
    "FactPuntos": len(eventos),
    "FactPartidoEquipo": len(partidos) * 2,
    "FactGoles": len(goles),
    "FactPracticas": len(practicas),
}
caso(
    "filas-por-tabla",
    "Cantidad de filas cargadas en cada tabla",
    "EVALUATE UNION ( " + ", ".join(f'ROW ( "Tabla", "{t}", "Filas", COUNTROWS ( {t} ) )' for t in conteos) + " )",
    ["Tabla"],
    [{"Tabla": t, "Filas": n} for t, n in conteos.items()],
)

# 2. Puntos netos, otorgados y descontados por casa y curso.
filas = []
for c in range(1, 6):
    for h in CASAS:
        filas.append({
            "CursoNumero": c, "CasaKey": h,
            "netos": puntos({c}, None, h),
            "otorgados": puntos({c}, None, h, lambda e: e["points"] > 0),
            "descontados": (lambda v: -v if v is not None else None)(puntos({c}, None, h, lambda e: e["points"] < 0)),
        })
caso(
    "puntos-casa-curso",
    "Puntos netos, otorgados y descontados por casa y curso",
    """EVALUATE SUMMARIZECOLUMNS ( DimTrimestre[CursoNumero], DimCasa[CasaKey],
        "netos", [Puntos Netos], "otorgados", [Puntos Otorgados], "descontados", [Puntos Descontados] )""",
    ["CursoNumero", "CasaKey"],
    filas,
)

# 3. Posición en la Copa y ventaja del líder por curso.
filas_pos, filas_lider = [], []
for c in range(1, 6):
    netos = {h: puntos({c}, None, h) for h in CASAS}
    rk = ranking(netos)
    filas_pos += [{"CursoNumero": c, "CasaKey": h, "pos": rk[h]} for h in CASAS]
    orden = sorted(netos.values(), reverse=True)
    lideres = [NOMBRE_CASA[h] for h in CASAS if netos[h] == orden[0]]
    filas_lider.append({
        "CursoNumero": c,
        "lider": " y ".join(sorted(lideres)),
        "ventaja": 0 if len(lideres) > 1 else orden[0] - orden[1],
        "maximo": orden[0],
    })
caso("posicion-curso", "Posición de cada casa en la Copa de cada curso (empates comparten puesto)",
     """EVALUATE SUMMARIZECOLUMNS ( DimTrimestre[CursoNumero], DimCasa[CasaKey], "pos", [Posición] )""",
     ["CursoNumero", "CasaKey"], filas_pos)
caso("lider-curso", "Casa líder, puntos del líder y ventaja sobre el segundo por curso",
     """EVALUATE SUMMARIZECOLUMNS ( DimTrimestre[CursoNumero], "lider", [Casa Líder], "ventaja", [Ventaja del Líder], "maximo", [Puntos del Líder] )""",
     ["CursoNumero"], filas_lider)

# 3b. Los visuales agrupan y filtran por el NOMBRE de la casa, no por la clave. Estos
#     casos reproducen esa forma de consulta (fue la que expuso un error real: un
#     RANKX sobre ALL ( DimCasa[CasaKey] ) dejaba vivo el filtro por nombre).
filas_nombre = []
for c in range(1, 6):
    netos = {h: puntos({c}, None, h) for h in CASAS}
    rk = ranking(netos)
    lider = max(netos.values())
    filas_nombre += [{"Curso": f"Curso {ROMANOS[c - 1]}", "Casa": NOMBRE_CASA[h], "pos": rk[h], "al_lider": lider - netos[h]} for h in CASAS]
caso("ranking-por-nombre-de-casa", "Matriz del informe: puesto y distancia al líder agrupando por DimCasa[Casa] y DimTrimestre[Curso]",
     """EVALUATE SUMMARIZECOLUMNS ( DimTrimestre[Curso], DimCasa[Casa], "pos", [Posición], "al_lider", [Distancia al Líder] )""",
     ["Curso", "Casa"], filas_nombre)

netos_v5 = {h: puntos({5}, None, h) for h in CASAS}
orden_v5 = sorted(netos_v5.values(), reverse=True)
caso("lider-con-filtro-de-casa", "Con el segmentador de casa en Gryffindor, el líder y la ventaja siguen comparando contra las cuatro casas",
     """EVALUATE CALCULATETABLE ( ROW ( "pos", [Posición], "maximo", [Puntos del Líder], "ventaja", [Ventaja del Líder], "lider", [Casa Líder] ),
        TREATAS ( { "Gryffindor" }, DimCasa[Casa] ), """ + FILTRO_CURSO.format(c=5) + """ )""",
     [], [{"pos": ranking(netos_v5)["gryffindor"], "maximo": orden_v5[0], "ventaja": orden_v5[0] - orden_v5[1],
           "lider": NOMBRE_CASA[max(netos_v5, key=netos_v5.get)]}])

# 4. Período anterior: trimestre a trimestre (cruzando cursos) y curso a curso.
filas = []
for c in range(1, 6):
    for t in TERMINOS:
        idx = indice_trimestre(c, t)
        for h in CASAS:
            if idx == 1:
                ant = None
            else:
                pc, pt = divmod(idx - 2, 3)
                ant = puntos({pc + 1}, {TERMINOS[pt]}, h) or 0
            act = puntos({c}, {t}, h)
            filas.append({
                "CursoNumero": c, "TrimestreOrden": TERMINOS.index(t) + 1, "CasaKey": h,
                "anterior": ant,
                "variacion": None if ant is None else (act or 0) - ant,
                "variacion_pct": None if ant is None or ant == 0 else ((act or 0) - ant) / abs(ant),
            })
caso("periodo-anterior-trimestre", "Puntos del trimestre anterior y variaciones (el Otoño compara con la Primavera del curso previo)",
     """EVALUATE SUMMARIZECOLUMNS ( DimTrimestre[CursoNumero], DimTrimestre[TrimestreOrden], DimCasa[CasaKey],
        "anterior", [Puntos Período Anterior], "variacion", [Variación vs Período Anterior], "variacion_pct", [Variación % vs Período Anterior] )""",
     ["CursoNumero", "TrimestreOrden", "CasaKey"], filas)

filas = []
for c in range(1, 6):
    actual = {h: puntos({c}, None, h) for h in CASAS}
    anterior = {h: (puntos({c - 1}, None, h) or 0) if c > 1 else None for h in CASAS}
    rk_act = ranking(actual)
    rk_ant = ranking(anterior) if c > 1 else None
    for h in CASAS:
        filas.append({
            "CursoNumero": c, "CasaKey": h,
            "anterior": anterior[h],
            "cambio": None if c == 1 else rk_ant[h] - rk_act[h],
        })
caso("periodo-anterior-curso", "Curso contra curso anterior: puntos y cambio de posición en el ranking",
     """EVALUATE SUMMARIZECOLUMNS ( DimTrimestre[CursoNumero], DimCasa[CasaKey], "anterior", [Puntos Período Anterior], "cambio", [Cambio de Posición] )""",
     ["CursoNumero", "CasaKey"], filas)

# Mismos trimestres del curso anterior cuando se eligen dos trimestres de un curso.
filas = [{"CasaKey": h, "anterior": puntos({4}, {"otono", "invierno"}, h) or 0} for h in CASAS]
caso("periodo-anterior-mismos-trimestres", "Curso V con Otoño + Invierno se compara con Otoño + Invierno del Curso IV",
     """EVALUATE SUMMARIZECOLUMNS ( DimCasa[CasaKey], TREATAS ( { 5 }, DimTrimestre[CursoNumero] ),
        TREATAS ( { 1, 2 }, DimTrimestre[TrimestreOrden] ), "anterior", [Puntos Período Anterior] )""",
     ["CasaKey"], filas)

# 5. Acumulados semana a semana, con eje en la clave y con eje en la fecha (trampa clásica de filtros).
semanal = defaultdict(int)
for e in eventos:
    semanal[(e["curso"], e["week"], e["houseId"])] += e["points"]
filas = []
for h in CASAS:
    acum = 0
    for w in range(1, 37):
        acum += semanal[(5, w, h)]
        filas.append({"SemanaCurso": w, "CasaKey": h, "acum": acum})
caso("acumulado-curso-v", "Puntos acumulados por semana en el Curso V (eje SemanaCurso)",
     """EVALUATE SUMMARIZECOLUMNS ( DimSemana[SemanaCurso], DimCasa[CasaKey], """ + FILTRO_CURSO.format(c=5) + """, "acum", [Puntos Acumulados] )""",
     ["SemanaCurso", "CasaKey"], filas)

orden_semanas = [(c, w) for c in range(1, 6) for w in range(1, 37)]
filas = []
for h in CASAS:
    acum = 0
    for i, (c, w) in enumerate(orden_semanas, start=1):
        acum += semanal[(c, w, h)]
        if w in (12, 24, 36):
            filas.append({"SemanaGlobal": i, "CasaKey": h, "acum": acum})
caso("acumulado-archivo-completo", "Acumulado a lo largo de los cinco cursos (cierres de trimestre)",
     """EVALUATE FILTER ( SUMMARIZECOLUMNS ( DimSemana[SemanaGlobal], DimCasa[CasaKey], "acum", [Puntos Acumulados] ),
        MOD ( DimSemana[SemanaGlobal] - 1, 36 ) + 1 IN { 12, 24, 36 } )""",
     ["SemanaGlobal", "CasaKey"], filas)

filas = [{"CasaKey": h, "acum": sum(semanal[(5, w, h)] for w in range(1, 37))} for h in CASAS]
caso("acumulado-eje-fecha", "El acumulado con eje en FechaInicioSemana llega al total del curso (no se queda en la última semana)",
     """EVALUATE TOPN ( 4, SUMMARIZECOLUMNS ( DimSemana[FechaInicioSemana], DimCasa[CasaKey], """ + FILTRO_CURSO.format(c=5) + """, "acum", [Puntos Acumulados] ),
        DimSemana[FechaInicioSemana], DESC )""",
     ["CasaKey"], filas)

# 6. Participación y composición.
total = puntos({5})
filas = [{"CasaKey": h, "part": puntos({5}, None, h) / total} for h in CASAS]
caso("participacion", "Participación de cada casa en los puntos netos del Curso V",
     """EVALUATE SUMMARIZECOLUMNS ( DimCasa[CasaKey], """ + FILTRO_CURSO.format(c=5) + """, "part", [% Participación] )""",
     ["CasaKey"], filas)

otorgados = sum(e["points"] for e in eventos if e["points"] > 0)
por_cat = defaultdict(int)
for e in eventos:
    if e["points"] > 0:
        por_cat[e["category"]] += e["points"]
filas = [{"CategoriaKey": k, "pct": v / otorgados} for k, v in por_cat.items()]
caso("composicion-categorias", "Peso de cada categoría en los puntos otorgados (todo el archivo)",
     """EVALUATE SUMMARIZECOLUMNS ( DimCategoria[CategoriaKey], "pct", [% de Puntos Otorgados] )""",
     ["CategoriaKey"], filas)

# 7. Estudiantes: ranking y contribución (Curso V).
netos_est = defaultdict(int)
for e in eventos:
    if e["curso"] == 5 and e["studentId"]:
        netos_est[e["studentId"]] += e["points"]
rk_est = ranking(netos_est)
netos_casa_v = {h: puntos({5}, None, h) for h in CASAS}
filas = [
    {"EstudianteKey": s, "pts": v, "pos": rk_est[s], "contrib": v / netos_casa_v[estudiantes[s]["houseId"]]}
    for s, v in netos_est.items()
]
caso("estudiantes-curso-v", "Puntos, puesto y contribución a su casa de cada estudiante en el Curso V (sin el miembro colectivo)",
     """EVALUATE FILTER ( SUMMARIZECOLUMNS ( DimEstudiante[EstudianteKey], """ + FILTRO_CURSO.format(c=5) + """,
        "pts", [Puntos Netos Estudiante], "pos", [Posición Estudiante], "contrib", [% Contribución a la Casa] ), NOT ISBLANK ( [pts] ) )""",
     ["EstudianteKey"], filas)

# 8. Quidditch por casa y curso.
def tabla_quidditch(ms):
    filas_ = {}
    for h in CASAS:
        jug = [m for m in ms if h in (m["homeId"], m["awayId"])]
        pf = sum(m["homeScore"] if m["homeId"] == h else m["awayScore"] for m in jug)
        pc = sum(m["awayScore"] if m["homeId"] == h else m["homeScore"] for m in jug)
        v = sum(1 for m in jug if (m["homeScore"] > m["awayScore"]) == (m["homeId"] == h))
        filas_[h] = {"jugados": len(jug) or None, "victorias": v if jug else None, "derrotas": len(jug) - v if jug else None,
                     "pct": v / len(jug) if jug else None, "pf": pf if jug else None, "pc": pc if jug else None,
                     "snitch": sum(1 for m in jug if m["snitchHouseId"] == h) if jug else None}
    clave = {h: (f["pf"] or 0) * 1000 + (f["victorias"] or 0) for h, f in filas_.items()}
    rk = ranking(clave)
    for h in CASAS:
        filas_[h]["copa"] = rk[h] if filas_[h]["jugados"] else None
    return filas_


filas = []
for c in range(1, 6):
    t = tabla_quidditch([m for m in partidos if m["curso"] == c])
    for h in CASAS:
        filas.append({"CursoNumero": c, "CasaKey": h, **t[h]})
caso("quidditch-casa-curso", "Tabla de Quidditch por casa y curso (jugados, victorias, derrotas, %, puntos, Snitch, puesto)",
     """EVALUATE SUMMARIZECOLUMNS ( DimTrimestre[CursoNumero], DimCasa[CasaKey],
        "jugados", [Partidos Jugados], "victorias", [Victorias], "derrotas", [Derrotas], "pct", [% Victorias],
        "pf", [Puntos a Favor], "pc", [Puntos en Contra], "snitch", [Snitches Atrapadas], "copa", [Posición Copa Quidditch] )""",
     ["CursoNumero", "CasaKey"], filas)


def snitch_decidio(m) -> bool:
    l = m["homeScore"] - (150 if m["snitchHouseId"] == m["homeId"] else 0)
    v = m["awayScore"] - (150 if m["snitchHouseId"] == m["awayId"] else 0)
    return l == v or (l > v) != (m["homeScore"] > m["awayScore"])


filas = []
for c in range(1, 6):
    t = tabla_quidditch([m for m in partidos if m["curso"] == c])
    filas += [{"Curso": f"Curso {ROMANOS[c - 1]}", "Casa": NOMBRE_CASA[h], "copa": t[h]["copa"]} for h in CASAS]
caso("copa-quidditch-por-nombre", "Puesto en la Copa de Quidditch agrupando por nombre de casa (forma de consulta de la tabla del informe)",
     """EVALUATE SUMMARIZECOLUMNS ( DimTrimestre[Curso], DimCasa[Casa], "copa", [Posición Copa Quidditch] )""",
     ["Curso", "Casa"], filas)

filas = []
for c in range(1, 6):
    ms = [m for m in partidos if m["curso"] == c]
    filas.append({"CursoNumero": c, "partidos": len(ms), "decididos": sum(snitch_decidio(m) for m in ms),
                  "promedio": sum(m["homeScore"] + m["awayScore"] for m in ms) / len(ms)})
caso("quidditch-curso", "Partidos, partidos decididos por la Snitch y puntos por partido en cada curso",
     """EVALUATE SUMMARIZECOLUMNS ( DimTrimestre[CursoNumero], "partidos", [Partidos], "decididos", [Partidos Decididos por la Snitch], "promedio", [Puntos por Partido] )""",
     ["CursoNumero"], filas)

# Con una casa filtrada, el promedio incluye al rival.
filas = []
for h in CASAS:
    ms = [m for m in partidos if m["curso"] == 5 and h in (m["homeId"], m["awayId"])]
    filas.append({"CasaKey": h, "promedio": sum(m["homeScore"] + m["awayScore"] for m in ms) / len(ms)})
caso("quidditch-promedio-por-casa", "Puntos por partido de los partidos de cada casa en el Curso V (ambos equipos)",
     """EVALUATE SUMMARIZECOLUMNS ( DimCasa[CasaKey], """ + FILTRO_CURSO.format(c=5) + """, "promedio", [Puntos por Partido] )""",
     ["CasaKey"], filas)

# Período sin partidos de una casa: las medidas quedan vacías (no 0 ni error).
otono_c1 = [m for m in partidos if m["curso"] == 1 and termino_de(m["week"]) == "otono"]
sin_partido = [h for h in CASAS if not any(h in (m["homeId"], m["awayId"]) for m in otono_c1)]
filas = [{"CasaKey": h, "jugados": None, "victorias": None, "pct": None} for h in sin_partido]
if filas:
    caso("quidditch-sin-registros", "Casa sin partidos en el Otoño del Curso I: medidas vacías, sin errores",
         """EVALUATE SUMMARIZECOLUMNS ( DimCasa[CasaKey], """ + FILTRO_CURSO.format(c=1) + """, TREATAS ( { 1 }, DimTrimestre[TrimestreOrden] ),
            TREATAS ( { """ + ", ".join(f'"{h}"' for h in sin_partido) + """ }, DimCasa[CasaKey] ),
            "jugados", [Partidos Jugados], "victorias", [Victorias], "pct", [% Victorias], "control", 1 )""",
         ["CasaKey"], filas)

goles_est = defaultdict(int)
for g in goles:
    goles_est[g["studentId"]] += int(g["goals"])
caso("goles-por-estudiante", "Goles por estudiante en todo el archivo",
     """EVALUATE SUMMARIZECOLUMNS ( DimEstudiante[EstudianteKey], "goles", [Goles] )""",
     ["EstudianteKey"], [{"EstudianteKey": k, "goles": v} for k, v in goles_est.items()])

# Consistencia entre el libro de puntos y los partidos, por casa y curso.
caso("control-quidditch", "Puntos de Quidditch en el libro = 50 × victorias, por casa y curso",
     """EVALUATE SUMMARIZECOLUMNS ( DimTrimestre[CursoNumero], DimCasa[CasaKey], "control", [Control Quidditch (debe ser 0)] )""",
     ["CursoNumero", "CasaKey"], [{"CursoNumero": c, "CasaKey": h, "control": 0} for c in range(1, 6) for h in CASAS])

# 9. Hechizos.
def tasas(filtro):
    acc = defaultdict(lambda: [0, 0])
    for p in practicas:
        k = filtro(p)
        if k is None:
            continue
        acc[k][0] += p["casts"]
        acc[k][1] += p["successes"]
    return acc


ramas = tasas(lambda p: hechizos[p["spellId"]]["category"])
caso("hechizos-por-rama", "Intentos, éxitos y tasa de éxito por rama (todo el archivo)",
     """EVALUATE SUMMARIZECOLUMNS ( DimHechizo[RamaOrden], "intentos", [Intentos], "exitos", [Éxitos], "tasa", [Tasa de Éxito] )""",
     ["RamaOrden"],
     [{"RamaOrden": ["encantamiento", "transformacion", "defensa", "maleficio", "curacion", "contrahechizo"].index(k) + 1,
       "intentos": v[0], "exitos": v[1], "tasa": v[1] / v[0]} for k, v in ramas.items()])

dif = tasas(lambda p: int(hechizos[p["spellId"]]["difficulty"]))
caso("hechizos-por-dificultad", "Tasa de éxito por nivel de dificultad",
     """EVALUATE SUMMARIZECOLUMNS ( DimHechizo[Dificultad], "tasa", [Tasa de Éxito] )""",
     ["Dificultad"], [{"Dificultad": k, "tasa": v[1] / v[0]} for k, v in dif.items()])

casa_rama = tasas(lambda p: (p["houseId"], hechizos[p["spellId"]]["category"]) if p["curso"] == 5 else None)
colegio_rama = tasas(lambda p: hechizos[p["spellId"]]["category"] if p["curso"] == 5 else None)
caso("hechizos-vs-colegio", "Diferencia en puntos porcentuales de cada casa contra el colegio, por rama, Curso V",
     """EVALUATE SUMMARIZECOLUMNS ( DimCasa[CasaKey], DimHechizo[RamaOrden], """ + FILTRO_CURSO.format(c=5) + """, "pp", [Diferencia vs Colegio (pp)] )""",
     ["CasaKey", "RamaOrden"],
     [{"CasaKey": h, "RamaOrden": ["encantamiento", "transformacion", "defensa", "maleficio", "curacion", "contrahechizo"].index(r) + 1,
       "pp": (v[1] / v[0] - colegio_rama[r][1] / colegio_rama[r][0]) * 100} for (h, r), v in casa_rama.items()],
     tolerancia=0.0005)


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    return cov / math.sqrt(vx * vy)


filas = []
for h in [None] + CASAS:
    por_hechizo = tasas(lambda p: p["spellId"] if h is None or p["houseId"] == h else None)
    ids = list(por_hechizo)
    r = pearson([int(hechizos[i]["difficulty"]) for i in ids], [por_hechizo[i][1] / por_hechizo[i][0] for i in ids])
    filas.append({"CasaKey": h or "(todas)", "r": r})
caso("correlacion-dificultad-exito", "Correlación de Pearson dificultad–tasa de éxito: colegio y por casa",
     """EVALUATE UNION (
        ROW ( "CasaKey", "(todas)", "r", [Correlación Dificultad–Éxito] ),
        SELECTCOLUMNS ( SUMMARIZECOLUMNS ( DimCasa[CasaKey], "r", [Correlación Dificultad–Éxito] ), "CasaKey", DimCasa[CasaKey], "r", [r] ) )""",
     ["CasaKey"], filas, tolerancia=0.000001)

v_curso5 = tasas(lambda p: p["spellId"] if p["curso"] == 5 else None)
top = sorted(v_curso5.items(), key=lambda kv: (-kv[1][0], hechizos[kv[0]]["name"]))[0][0]
caso("hechizo-mas-practicado", "Hechizo más practicado en el Curso V",
     """EVALUATE CALCULATETABLE ( ROW ( "top", [Hechizo Más Practicado], "practicados", [Hechizos Practicados] ), """ + FILTRO_CURSO.format(c=5) + """ )""",
     [], [{"top": hechizos[top]["name"], "practicados": len(v_curso5)}])

# 10. Calidad de datos y titulares.
caso("calidad-de-datos", "Todos los controles de calidad en 0",
     """EVALUATE ROW ( "problemas", [Controles con Problemas], "controles", COUNTROWS ( ControlCalidad ), "filas", SUM ( ControlCalidad[FilasConProblema] ) )""",
     [], [{"problemas": 0, "controles": 19, "filas": 0}])

def miles(n: int) -> str:
    """Formato es-ES de "#,0": punto como separador de miles."""
    return f"{n:,}".replace(",", ".")


netos_v = {h: puntos({5}, None, h) for h in CASAS}
orden_v = sorted(netos_v.items(), key=lambda kv: -kv[1])
caso("titular-curso-v", "Titular dinámico del Gran Comedor para el Curso V",
     """EVALUATE CALCULATETABLE ( ROW ( "titular", [Titular Gran Comedor] ), """ + FILTRO_CURSO.format(c=5) + """ )""",
     [], [{"titular": f"{NOMBRE_CASA[orden_v[0][0]]} lidera el Curso V: {miles(orden_v[0][1])} puntos "
                      f"(+{miles(orden_v[0][1] - orden_v[1][1])} sobre el segundo)"}])

# Texto de variación para la tarjeta: Curso V contra Curso IV, y sin período previo en el Curso I.
var_v = puntos({5}) - puntos({4})
caso("variacion-texto", "Texto de la tarjeta de variación: con período previo y sin él",
     """EVALUATE UNION (
        CALCULATETABLE ( ROW ( "Curso", 5, "texto", [Variación vs Período Anterior (texto)] ), """ + FILTRO_CURSO.format(c=5) + """ ),
        CALCULATETABLE ( ROW ( "Curso", 1, "texto", [Variación vs Período Anterior (texto)] ), """ + FILTRO_CURSO.format(c=1) + """ ) )""",
     ["Curso"], [{"Curso": 5, "texto": ("+" if var_v > 0 else "−" if var_v < 0 else "") .replace("−", "-") + miles(abs(var_v)) + " vs. Curso IV"},
                 {"Curso": 1, "texto": "Sin período previo"}])


# 11. Visuales SVG: la cadena DAX debe ser idéntica a la referencia de Python
#     (mismos niveles de arena, cifras, puestos y textos) en contextos de borde.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import svg_estandartes  # noqa: E402
import svg_relojes  # noqa: E402

COLOR = {"gryffindor": "#C23634", "slytherin": "#33A47D", "ravenclaw": "#6A8FE0", "hufflepuff": "#BC8C2A"}
casas_csv = {c["id"]: c for c in leer("casas.csv")}


def casas_contexto(cursos, terminos, filtro=lambda e: True):
    return [
        {"orden": i + 1, "clave": h, "nombre": NOMBRE_CASA[h], "color": COLOR[h],
         "elemento": casas_csv[h]["element"].capitalize(), "rasgos": casas_csv[h]["traits"].replace("|", " · "),
         "puntos": puntos(cursos, terminos, h, filtro)}
        for i, h in enumerate(CASAS)
    ]


def filtro_dax(cursos=None, terminos=None, casa=None, categoria=None):
    partes = []
    if cursos:
        partes.append("TREATAS ( { " + ", ".join(str(c) for c in sorted(cursos)) + " }, DimTrimestre[CursoNumero] )")
    if terminos:
        partes.append("TREATAS ( { " + ", ".join(str(TERMINOS.index(t) + 1) for t in terminos) + " }, DimTrimestre[TrimestreOrden] )")
    if casa:
        partes.append('TREATAS ( { "' + NOMBRE_CASA[casa] + '" }, DimCasa[Casa] )')
    if categoria:
        partes.append('TREATAS ( { "' + categoria + '" }, DimCategoria[CategoriaKey] )')
    return ", ".join(partes)


contextos_relojes = [
    ("curso-v", "Curso V", {5}, None, None, None),
    ("curso-i-invierno", "Curso I, Invierno", {1}, ["invierno"], None, None),
    ("archivo-completo", "los cinco cursos", None, None, None, None),
    ("filtro-slytherin", "Curso V con el segmentador de casa en Slytherin (las demás se atenúan)", {5}, None, "slytherin", None),
    ("sin-registros", "Otoño del Curso I, sólo premios de Quidditch (casas sin anotaciones)", {1}, ["otono"], None, "quidditch"),
    ("todo-negativo", "Curso V, sólo sanciones (sin máximo positivo: niveles en 0, sin división por cero)", {5}, None, None, "sancion"),
]
for clave, desc, cursos, terminos, casa, categoria in contextos_relojes:
    filtro = (lambda cat: (lambda e: e["category"] == cat))(categoria) if categoria else (lambda e: True)
    esperado = svg_relojes.svg(casas_contexto(cursos, terminos, filtro), {casa} if casa else None)
    dax = 'EVALUATE ROW ( "svg", [Relojes de Arena (SVG)] )'
    f = filtro_dax(cursos, terminos, casa, categoria)
    if f:
        dax = 'EVALUATE CALCULATETABLE ( ROW ( "svg", [Relojes de Arena (SVG)] ), ' + f + " )"
    caso(f"relojes-{clave}", f"Relojes de arena (SVG idéntico a la referencia): {desc}", dax, [], [{"svg": esperado}])


def periodo_label(curso, termino):
    nombres = {"otono": "Otoño", "invierno": "Invierno", "primavera": "Primavera"}
    return f"C.{ROMANOS[curso - 1]} · {nombres[termino]}"


contextos_estandartes = [
    ("curso-v", {5}, None, None),
    ("curso-v-slytherin", {5}, None, "slytherin"),
    ("curso-i", {1}, None, None),
    ("curso-ii-invierno", {2}, ["invierno"], None),
]
for clave, cursos, terminos, casa in contextos_estandartes:
    curso = next(iter(cursos))
    casas = casas_contexto(cursos, terminos)
    if terminos:
        idx = indice_trimestre(curso, terminos[0])
        pc, pt = divmod(idx - 2, 3)
        comparacion = "vs. " + periodo_label(pc + 1, TERMINOS[pt])
        anteriores = {h: puntos({pc + 1}, {TERMINOS[pt]}, h) or 0 for h in CASAS}
    elif curso > 1:
        comparacion = f"vs. Curso {ROMANOS[curso - 2]}"
        anteriores = {h: puntos({curso - 1}, None, h) or 0 for h in CASAS}
    else:
        comparacion = "Sin período anterior comparable"
        anteriores = None
    for c in casas:
        c["variacion"] = None if anteriores is None else (c["puntos"] or 0) - anteriores[c["clave"]]
    esperado = svg_estandartes.svg(casas, {casa} if casa else None, comparacion)
    dax = 'EVALUATE CALCULATETABLE ( ROW ( "svg", [Estandartes de las Casas (SVG)] ), ' + filtro_dax(cursos, terminos, casa) + " )"
    caso(f"estandartes-{clave}", f"Estandartes de las casas (SVG idéntico a la referencia): {clave}", dax, [], [{"svg": esperado}])


# Marcador de Quidditch: misma tabla de la Copa (tabla_quidditch) dibujada como SVG.
import svg_marcador  # noqa: E402


def marcador_contexto(cursos, terminos):
    ms = [m for m in partidos if (not cursos or m["curso"] in cursos) and (not terminos or termino_de(m["week"]) in terminos)]
    t = tabla_quidditch(ms)
    casas = [{"orden": i + 1, "clave": h, "nombre": NOMBRE_CASA[h], "color": COLOR[h],
              "elemento": casas_csv[h]["element"].capitalize(), "jugados": t[h]["jugados"], "victorias": t[h]["victorias"],
              "derrotas": t[h]["derrotas"], "favor": t[h]["pf"], "contra": t[h]["pc"], "snitches": t[h]["snitch"],
              "puesto": t[h]["copa"]} for i, h in enumerate(CASAS)]
    return ms, casas


def goleadores_contexto(ms, casa=None):
    """Goles por jugador en los partidos del contexto (con el segmentador de casa, sólo los de esa casa)."""
    por_partido = {m["id"]: m for m in ms}
    total = defaultdict(int)
    for g in goles:
        m = por_partido.get(g["matchId"])
        equipo = m and (m["homeId"] if g["side"] == "home" else m["awayId"])
        if m and (casa is None or equipo == casa):
            total[g["studentId"]] += int(g["goals"])
    return [{"nombre": estudiantes[k]["name"], "color": COLOR[estudiantes[k]["houseId"]], "goles": v} for k, v in total.items() if v > 0]


contextos_marcador = [
    ("curso-v", "Curso V", {5}, None, None),
    ("curso-i-otono", "Otoño del Curso I (una casa sin partidos: fila con «—» al final)", {1}, ["otono"], None),
    ("archivo-completo", "los cinco cursos", None, None, None),
    ("filtro-hufflepuff", "Curso V con el segmentador en Hufflepuff (resumen de sus partidos; las demás se atenúan)", {5}, None, "hufflepuff"),
    ("curso-i-invierno-ravenclaw", "Curso I, Invierno, segmentador en Ravenclaw: un solo partido (singular) y Hufflepuff sin partidos",
     {1}, ["invierno"], "ravenclaw"),
]
for clave, desc, cursos, terminos, casa in contextos_marcador:
    ms, casas = marcador_contexto(cursos, terminos)
    top = goleadores_contexto(ms, casa)
    if casa:  # [Partidos] y sus derivadas respetan el segmentador: sólo los partidos de esa casa
        ms = [m for m in ms if casa in (m["homeId"], m["awayId"])]
    promedio = sum(m["homeScore"] + m["awayScore"] for m in ms) / len(ms) if ms else None
    esperado = svg_marcador.svg(casas, {casa} if casa else None, len(ms), sum(snitch_decidio(m) for m in ms), promedio, top)
    f = filtro_dax(cursos, terminos, casa)
    dax = 'EVALUATE ROW ( "svg", [Marcador de Quidditch (SVG)] )'
    if f:
        dax = 'EVALUATE CALCULATETABLE ( ROW ( "svg", [Marcador de Quidditch (SVG)] ), ' + f + " )"
    caso(f"marcador-{clave}", f"Marcador de Quidditch (SVG idéntico a la referencia): {desc}", dax, [], [{"svg": esperado}])

# Sin partidos en absoluto (una semana sin Quidditch): aviso explícito y todas las filas con «—».
semana_sin = next(w for w in range(1, 53) if not any(m["curso"] == 5 and m["week"] == w for m in partidos)
                  and any(e["curso"] == 5 and e["week"] == w for e in eventos))
_, casas = marcador_contexto({5}, None)
for c in casas:
    for k in ("jugados", "victorias", "derrotas", "favor", "contra", "snitches", "puesto"):
        c[k] = None
caso("marcador-sin-partidos", f"Marcador sin partidos (Curso V, semana {semana_sin}): aviso y filas vacías, sin errores",
     'EVALUATE CALCULATETABLE ( ROW ( "svg", [Marcador de Quidditch (SVG)], "alt", [Marcador de Quidditch (descripción)] ), '
     + filtro_dax({5}) + f", TREATAS ( {{ {semana_sin} }}, DimSemana[SemanaCurso] ) )",
     [], [{"svg": svg_marcador.svg(casas, None, 0, 0, None, []), "alt": svg_marcador.descripcion(casas)}])

_, casas = marcador_contexto({1}, ["otono"])
caso("marcador-descripcion", "Texto alternativo del marcador (Otoño del Curso I)",
     'EVALUATE CALCULATETABLE ( ROW ( "alt", [Marcador de Quidditch (descripción)] ), ' + filtro_dax({1}, ["otono"]) + " )",
     [], [{"alt": svg_marcador.descripcion(casas)}])

SALIDA.parent.mkdir(parents=True, exist_ok=True)
SALIDA.write_text(json.dumps(casos, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(casos)} casos · {sum(len(c['esperado']) for c in casos)} valores esperados → {SALIDA.relative_to(RAIZ)}")
