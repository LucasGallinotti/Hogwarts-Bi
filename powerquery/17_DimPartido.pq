// DimPartido
// Un partido de Quidditch por fila (30). Atributos descriptivos del partido; las métricas por equipo viven en FactPartidoEquipo. No se relaciona con el calendario para no crear un segundo camino de filtro hacia los hechos.

let
    Origen = fnLeerCsv("partidos.csv"),
    Tipado = Table.TransformColumnTypes(
        Origen,
        {
            {"id", type text}, {"curso", Int64.Type}, {"week", Int64.Type}, {"homeId", type text}, {"awayId", type text},
            {"homeScore", Int64.Type}, {"awayScore", Int64.Type}, {"snitchHouseId", type text}, {"snitchStudentId", type text},
            {"durationMin", Int64.Type}
        },
        "en-US"
    ),
    Normalizado = Table.TransformColumns(Tipado, {{"homeId", Text.Lower, type text}, {"awayId", Text.Lower, type text}, {"snitchHouseId", Text.Lower, type text}}),
    Nombres = Record.FromList(DimCasa[Casa], DimCasa[CasaKey]),
    Siglas = Record.FromList(DimCasa[Sigla], DimCasa[CasaKey]),
    Romanos = {"I", "II", "III", "IV", "V", "VI", "VII"},
    ConNombres = Table.AddColumn(
        Normalizado,
        "Atributos",
        each
            let
                ganador = if [homeScore] > [awayScore] then [homeId] else [awayId],
                localSinSnitch = [homeScore] - (if [snitchHouseId] = [homeId] then 150 else 0),
                visitaSinSnitch = [awayScore] - (if [snitchHouseId] = [awayId] then 150 else 0)
            in
                [
                    Partido = "C." & Romanos{[curso] - 1} & " · S" & Text.PadStart(Text.From([week]), 2, "0") & " · "
                        & Record.Field(Siglas, [homeId]) & "–" & Record.Field(Siglas, [awayId]),
                    Local = Record.Field(Nombres, [homeId]),
                    Visitante = Record.Field(Nombres, [awayId]),
                    Marcador = Text.From([homeScore]) & "–" & Text.From([awayScore]),
                    Ganador = Record.Field(Nombres, ganador),
                    #"Casa de la Snitch" = Record.Field(Nombres, [snitchHouseId]),
                    // Misma regla que la web: si sin la Snitch empatan o gana el otro, la Snitch decidió.
                    SnitchDecisiva = localSinSnitch = visitaSinSnitch or (localSinSnitch > visitaSinSnitch) <> ([homeScore] > [awayScore]),
                    Orden = [curso] * 100 + [week]
                ]
    ),
    Expandido = Table.ExpandRecordColumn(
        ConNombres,
        "Atributos",
        {"Partido", "Local", "Visitante", "Marcador", "Ganador", "Casa de la Snitch", "SnitchDecisiva", "Orden"}
    ),
    ConTexto = Table.AddColumn(Expandido, "¿Decidió la Snitch?", each if [SnitchDecisiva] then "Sí" else "No", type text),
    Renombrado = Table.RenameColumns(ConTexto, {{"id", "PartidoKey"}, {"durationMin", "Duración (min)"}}),
    Seleccion = Table.SelectColumns(
        Renombrado,
        {"PartidoKey", "Partido", "Local", "Visitante", "Marcador", "Ganador", "Casa de la Snitch", "SnitchDecisiva", "¿Decidió la Snitch?", "Duración (min)", "Orden"}
    ),
    Tipos = Table.TransformColumnTypes(
        Seleccion,
        {
            {"Partido", type text}, {"Local", type text}, {"Visitante", type text}, {"Marcador", type text}, {"Ganador", type text},
            {"Casa de la Snitch", type text}, {"SnitchDecisiva", type logical}, {"Orden", Int64.Type}
        }
    ),
    Resultado = Table.Distinct(Tipos, {"PartidoKey"})
in
    Resultado
