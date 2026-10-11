// DimCasa
// Las cuatro casas. Filtra todas las tablas de hechos.

let
    Origen = fnLeerCsv("casas.csv"),
    Tipado = Table.TransformColumnTypes(
        Origen,
        {{"id", type text}, {"name", type text}, {"element", type text}, {"founder", type text}, {"traits", type text}, {"motto", type text}},
        "en-US"
    ),
    ClaveNormalizada = Table.TransformColumns(Tipado, {{"id", Text.Lower, type text}}),
    // Identidad visual: presentación, no dato de negocio. Colores validados para daltonismo en la web.
    Identidad = #table(
        type table [id = text, Orden = Int64.Type, Sigla = text, ColorHex = text],
        {
            {"gryffindor", 1, "GRY", "#C23634"},
            {"slytherin", 2, "SLY", "#33A47D"},
            {"ravenclaw", 3, "RAV", "#6A8FE0"},
            {"hufflepuff", 4, "HUF", "#BC8C2A"}
        }
    ),
    Unido = Table.NestedJoin(ClaveNormalizada, {"id"}, Identidad, {"id"}, "Identidad", JoinKind.LeftOuter),
    Expandido = Table.ExpandTableColumn(Unido, "Identidad", {"Orden", "Sigla", "ColorHex"}),
    // Una casa sin identidad definida detiene la carga: evita colores o un orden por defecto engañosos.
    Validado =
        if List.Contains(Expandido[Orden], null)
        then error Error.Record("Casa sin identidad visual", "casas.csv contiene una casa que no figura en la tabla de identidad.")
        else Expandido,
    Formateado = Table.TransformColumns(
        Validado,
        {{"element", Text.Proper, type text}, {"traits", each Text.Replace(_, "|", " · "), type text}}
    ),
    Renombrado = Table.RenameColumns(
        Formateado,
        {{"id", "CasaKey"}, {"name", "Casa"}, {"element", "Elemento"}, {"founder", "Fundador"}, {"traits", "Rasgos"}, {"motto", "Lema"}}
    ),
    SinDuplicados = Table.Distinct(Renombrado, {"CasaKey"}),
    Resultado = Table.SelectColumns(SinDuplicados, {"CasaKey", "Casa", "Sigla", "Elemento", "Fundador", "Rasgos", "Lema", "Orden", "ColorHex"})
in
    Resultado
