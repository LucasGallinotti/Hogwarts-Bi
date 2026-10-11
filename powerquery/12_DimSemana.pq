// DimSemana
// Calendario a nivel semana escolar (180 filas). Es el grano temporal de los eventos de puntos y de los partidos: los datos no tienen día, así que una tabla diaria sólo agregaría filas vacías.

let
    // Las semanas se derivan del calendario de trimestres: una sola definición del tiempo.
    Trimestres = Table.SelectColumns(DimTrimestre, {"TrimestreKey", "CursoNumero", "FechaInicio", "PrimeraSemana", "UltimaSemana"}),
    ConSemanas = Table.AddColumn(Trimestres, "SemanaCurso", each {[PrimeraSemana]..[UltimaSemana]}, type list),
    Expandido = Table.ExpandListColumn(ConSemanas, "SemanaCurso"),
    Tipado = Table.TransformColumnTypes(Expandido, {{"SemanaCurso", Int64.Type}}),
    ConClave = Table.AddColumn(Tipado, "SemanaKey", each [CursoNumero] * 100 + [SemanaCurso], Int64.Type),
    ConFecha = Table.AddColumn(ConClave, "FechaInicioSemana", each Date.AddDays([FechaInicio], 7 * ([SemanaCurso] - [PrimeraSemana])), type date),
    Ordenado = Table.Sort(ConFecha, {{"SemanaKey", Order.Ascending}}),
    ConIndice = Table.AddIndexColumn(Ordenado, "SemanaGlobal", 1, 1, Int64.Type),
    ConEtiqueta = Table.AddColumn(ConIndice, "Semana", each "S" & Text.PadStart(Text.From([SemanaCurso]), 2, "0"), type text),
    Resultado = Table.SelectColumns(ConEtiqueta, {"SemanaKey", "TrimestreKey", "SemanaCurso", "Semana", "SemanaGlobal", "FechaInicioSemana"})
in
    Resultado
