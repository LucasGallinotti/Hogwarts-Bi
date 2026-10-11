// FactPracticas
// Prácticas de hechizos. Grano: curso × trimestre × casa × hechizo (lanzamientos y aciertos registrados). Se relaciona con el calendario a nivel trimestre porque la fuente no tiene semana.

let
    Origen = fnLeerCsv("practicas_hechizos.csv"),
    Tipado = Table.TransformColumnTypes(
        Origen,
        {{"curso", Int64.Type}, {"term", type text}, {"houseId", type text}, {"spellId", type text}, {"casts", Int64.Type}, {"successes", Int64.Type}},
        "en-US"
    ),
    Normalizado = Table.TransformColumns(Tipado, {{"term", Text.Lower, type text}, {"houseId", Text.Lower, type text}, {"spellId", Text.Lower, type text}}),
    ConTrimestre = Table.AddColumn(
        Normalizado,
        "TrimestreKey",
        each [curso] * 10 + List.PositionOf({"otono", "invierno", "primavera"}, [term]) + 1,
        Int64.Type
    ),
    Renombrado = Table.RenameColumns(ConTrimestre, {{"houseId", "CasaKey"}, {"spellId", "HechizoKey"}, {"casts", "Intentos"}, {"successes", "Exitos"}}),
    Resultado = Table.SelectColumns(Renombrado, {"TrimestreKey", "CasaKey", "HechizoKey", "Intentos", "Exitos"})
in
    Resultado
