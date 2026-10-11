// FactGoles
// Goles por jugador y partido. Grano: partido × estudiante (sólo cazadores/as que anotaron).

let
    Goles = Table.TransformColumnTypes(
        fnLeerCsv("goles.csv"),
        {{"matchId", type text}, {"side", type text}, {"studentId", type text}, {"goals", Int64.Type}},
        "en-US"
    ),
    Partidos = Table.TransformColumnTypes(
        Table.SelectColumns(fnLeerCsv("partidos.csv"), {"id", "curso", "week"}),
        {{"id", type text}, {"curso", Int64.Type}, {"week", Int64.Type}},
        "en-US"
    ),
    ConSemana = Table.ExpandTableColumn(
        Table.NestedJoin(Goles, {"matchId"}, Partidos, {"id"}, "P", JoinKind.LeftOuter),
        "P",
        {"curso", "week"}
    ),
    ConSemanaKey = Table.AddColumn(ConSemana, "SemanaKey", each [curso] * 100 + [week], Int64.Type),
    Estudiantes = Table.SelectColumns(DimEstudiante, {"EstudianteKey", "CasaKey"}),
    ConCasa = Table.ExpandTableColumn(
        Table.NestedJoin(
            Table.TransformColumns(ConSemanaKey, {{"studentId", Text.Lower, type text}}),
            {"studentId"}, Estudiantes, {"EstudianteKey"}, "E", JoinKind.LeftOuter
        ),
        "E",
        {"CasaKey"}
    ),
    Renombrado = Table.RenameColumns(ConCasa, {{"matchId", "PartidoKey"}, {"studentId", "EstudianteKey"}, {"goals", "Goles"}}),
    Resultado = Table.TransformColumnTypes(
        Table.SelectColumns(Renombrado, {"PartidoKey", "SemanaKey", "CasaKey", "EstudianteKey", "Goles"}),
        {{"CasaKey", type text}}
    )
in
    Resultado
