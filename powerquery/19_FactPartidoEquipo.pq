// FactPartidoEquipo
// Rendimiento de cada equipo en cada partido. Grano: partido × casa (2 filas por partido: local y visitante). Permite medir victorias, derrotas y puntos por casa sin duplicar el conteo de partidos (que se cuenta con DISTINCTCOUNT).

let
    Partidos = Table.TransformColumnTypes(
        fnLeerCsv("partidos.csv"),
        {
            {"id", type text}, {"curso", Int64.Type}, {"week", Int64.Type}, {"homeId", type text}, {"awayId", type text},
            {"homeScore", Int64.Type}, {"awayScore", Int64.Type}, {"snitchHouseId", type text}
        },
        "en-US"
    ),
    Goles = Table.TransformColumnTypes(
        fnLeerCsv("goles.csv"),
        {{"matchId", type text}, {"side", type text}, {"studentId", type text}, {"goals", Int64.Type}},
        "en-US"
    ),
    GolesPorLado = Table.Group(Goles, {"matchId", "side"}, {{"Goles", each List.Sum([goals]), Int64.Type}}),
    // Un partido = dos filas (una por equipo): de formato ancho a largo.
    Lados = Table.AddColumn(
        Partidos,
        "Lado",
        each {
            [side = "home", Condicion = "Local", CasaKey = Text.Lower([homeId]), RivalCasaKey = Text.Lower([awayId]), PuntosAFavor = [homeScore], PuntosEnContra = [awayScore]],
            [side = "away", Condicion = "Visitante", CasaKey = Text.Lower([awayId]), RivalCasaKey = Text.Lower([homeId]), PuntosAFavor = [awayScore], PuntosEnContra = [homeScore]]
        }
    ),
    PorEquipo = Table.ExpandRecordColumn(
        Table.ExpandListColumn(Lados, "Lado"),
        "Lado",
        {"side", "Condicion", "CasaKey", "RivalCasaKey", "PuntosAFavor", "PuntosEnContra"}
    ),
    ConGoles = Table.ExpandTableColumn(
        Table.NestedJoin(PorEquipo, {"id", "side"}, GolesPorLado, {"matchId", "side"}, "G", JoinKind.LeftOuter),
        "G",
        {"Goles"}
    ),
    // Un equipo sin goles no aparece en goles.csv: ausencia de filas = 0 goles.
    GolesSinNulos = Table.ReplaceValue(ConGoles, null, 0, Replacer.ReplaceValue, {"Goles"}),
    ConSnitch = Table.AddColumn(GolesSinNulos, "AtrapoSnitch", each if Text.Lower([snitchHouseId]) = [CasaKey] then 1 else 0, Int64.Type),
    ConResultado = Table.AddColumn(ConSnitch, "Resultado", each if [PuntosAFavor] > [PuntosEnContra] then "Victoria" else "Derrota", type text),
    ConSemana = Table.AddColumn(ConResultado, "SemanaKey", each [curso] * 100 + [week], Int64.Type),
    Renombrado = Table.RenameColumns(ConSemana, {{"id", "PartidoKey"}}),
    Seleccion = Table.SelectColumns(
        Renombrado,
        {"PartidoKey", "SemanaKey", "CasaKey", "RivalCasaKey", "Condicion", "PuntosAFavor", "PuntosEnContra", "Goles", "AtrapoSnitch", "Resultado"}
    ),
    Resultado = Table.TransformColumnTypes(
        Seleccion,
        {
            {"CasaKey", type text}, {"RivalCasaKey", type text}, {"Condicion", type text},
            {"PuntosAFavor", Int64.Type}, {"PuntosEnContra", Int64.Type}, {"Goles", Int64.Type}
        }
    )
in
    Resultado
