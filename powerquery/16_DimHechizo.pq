// DimHechizo
// Catálogo de hechizos (nombres del universo, descripciones propias; dificultad y año son valores de demostración).

let
    Origen = fnLeerCsv("hechizos.csv"),
    Tipado = Table.TransformColumnTypes(
        Origen,
        {{"id", type text}, {"name", type text}, {"effect", type text}, {"category", type text}, {"difficulty", Int64.Type}, {"yearTaught", Int64.Type}},
        "en-US"
    ),
    Normalizado = Table.TransformColumns(Tipado, {{"id", Text.Lower, type text}, {"category", Text.Lower, type text}}),
    Ramas = #table(
        type table [category = text, Rama = text, RamaOrden = Int64.Type],
        {
            {"encantamiento", "Encantamientos", 1},
            {"transformacion", "Transformaciones", 2},
            {"defensa", "Defensa", 3},
            {"maleficio", "Maleficios", 4},
            {"curacion", "Curación", 5},
            {"contrahechizo", "Contrahechizos", 6}
        }
    ),
    ConRama = Table.ExpandTableColumn(
        Table.NestedJoin(Normalizado, {"category"}, Ramas, {"category"}, "R", JoinKind.LeftOuter),
        "R",
        {"Rama", "RamaOrden"}
    ),
    Validado =
        if List.Contains(ConRama[Rama], null)
        then error Error.Record("Rama desconocida", "hechizos.csv contiene una categoría sin rama definida.")
        else ConRama,
    // La dificultad debe estar entre 1 y 5; fuera de rango se informa en lugar de truncar.
    RangoOk =
        if List.MatchesAll(Validado[difficulty], each _ >= 1 and _ <= 5)
        then Validado
        else error Error.Record("Dificultad fuera de rango", "hechizos.csv tiene dificultades fuera de 1–5."),
    ConNivel = Table.AddColumn(RangoOk, "Nivel de Dificultad", each "Nivel " & Text.From([difficulty]), type text),
    Renombrado = Table.RenameColumns(
        ConNivel,
        {{"id", "HechizoKey"}, {"name", "Hechizo"}, {"effect", "Efecto"}, {"difficulty", "Dificultad"}, {"yearTaught", "Año de Enseñanza"}}
    ),
    SinDuplicados = Table.Distinct(Renombrado, {"HechizoKey"}),
    Resultado = Table.SelectColumns(
        SinDuplicados,
        {"HechizoKey", "Hechizo", "Efecto", "Rama", "RamaOrden", "Dificultad", "Nivel de Dificultad", "Año de Enseñanza"}
    )
in
    Resultado
