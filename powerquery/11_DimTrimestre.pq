// DimTrimestre
// Calendario escolar a nivel trimestre (5 cursos × 3 trimestres). Es el nivel superior del tiempo: filtra DimSemana y, directamente, FactPracticas (cuyo grano es el trimestre).

let
    Origen = fnLeerCsv("calendario.csv"),
    Tipado = Table.TransformColumnTypes(
        Origen,
        {
            {"curso", Int64.Type}, {"cursoLabel", type text}, {"term", type text}, {"termName", type text},
            {"firstWeek", Int64.Type}, {"lastWeek", Int64.Type}, {"termStartDate", type date}, {"schoolYear", type text}
        },
        "en-US"
    ),
    CodigoNormalizado = Table.TransformColumns(Tipado, {{"term", Text.Lower, type text}}),
    ConOrden = Table.AddColumn(CodigoNormalizado, "TrimestreOrden", each List.PositionOf({"otono", "invierno", "primavera"}, [term]) + 1, Int64.Type),
    // Un código desconocido daría orden 0: se detiene la carga en lugar de clasificar mal los datos.
    Validado =
        if List.Contains(ConOrden[TrimestreOrden], 0)
        then error Error.Record("Trimestre desconocido", "calendario.csv tiene códigos de trimestre fuera de otono/invierno/primavera.")
        else ConOrden,
    ConClave = Table.AddColumn(Validado, "TrimestreKey", each [curso] * 10 + [TrimestreOrden], Int64.Type),
    Ordenado = Table.Sort(ConClave, {{"curso", Order.Ascending}, {"TrimestreOrden", Order.Ascending}}),
    ConIndice = Table.AddIndexColumn(Ordenado, "IndiceTrimestre", 1, 1, Int64.Type),
    ConEtiqueta = Table.AddColumn(ConIndice, "Periodo", each "C." & Text.AfterDelimiter([cursoLabel], " ") & " · " & [termName], type text),
    Renombrado = Table.RenameColumns(
        ConEtiqueta,
        {
            {"curso", "CursoNumero"}, {"cursoLabel", "Curso"}, {"termName", "Trimestre"}, {"schoolYear", "AnioEscolar"},
            {"termStartDate", "FechaInicio"}, {"firstWeek", "PrimeraSemana"}, {"lastWeek", "UltimaSemana"}
        }
    ),
    SinDuplicados = Table.Distinct(Renombrado, {"TrimestreKey"}),
    Resultado = Table.SelectColumns(
        SinDuplicados,
        {"TrimestreKey", "CursoNumero", "Curso", "AnioEscolar", "TrimestreOrden", "Trimestre", "IndiceTrimestre", "Periodo", "FechaInicio", "PrimeraSemana", "UltimaSemana"}
    )
in
    Resultado
