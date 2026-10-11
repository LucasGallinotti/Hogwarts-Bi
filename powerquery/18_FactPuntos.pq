// FactPuntos
// Libro contable de puntos de casa. Grano: una anotación (premio o sanción) por fila. Incluye los +50 por cada victoria de Quidditch.

let
    Origen = fnLeerCsv("eventos_puntos.csv"),
    Tipado = Table.TransformColumnTypes(
        Origen,
        {
            {"id", type text}, {"curso", Int64.Type}, {"week", Int64.Type}, {"houseId", type text}, {"studentId", type text},
            {"category", type text}, {"points", Int64.Type}, {"reason", type text}, {"matchId", type text}
        },
        "en-US"
    ),
    Normalizado = Table.TransformColumns(
        Tipado,
        {{"houseId", Text.Lower, type text}, {"studentId", each if _ = null then null else Text.Lower(_), type nullable text}, {"category", Text.Lower, type text}}
    ),
    // Valor faltante con significado: los premios colectivos no tienen estudiante y se asignan al miembro "(colectivo)".
    SinNulos = Table.ReplaceValue(Normalizado, null, "(colectivo)", Replacer.ReplaceValue, {"studentId"}),
    ConSemana = Table.AddColumn(SinNulos, "SemanaKey", each [curso] * 100 + [week], Int64.Type),
    Renombrado = Table.RenameColumns(
        ConSemana,
        {{"id", "EventoID"}, {"houseId", "CasaKey"}, {"studentId", "EstudianteKey"}, {"category", "CategoriaKey"}, {"points", "Puntos"}, {"reason", "Motivo"}, {"matchId", "PartidoID"}}
    ),
    SinDuplicados = Table.Distinct(Renombrado, {"EventoID"}),
    Resultado = Table.SelectColumns(SinDuplicados, {"EventoID", "SemanaKey", "CasaKey", "EstudianteKey", "CategoriaKey", "Puntos", "Motivo", "PartidoID"})
in
    Resultado
