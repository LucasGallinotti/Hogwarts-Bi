// ControlCalidad
// Controles de calidad de datos que se recalculan en cada actualización: unicidad de claves en los archivos fuente, integridad referencial de los hechos y reglas de negocio. Un control con FilasConProblema > 0 queda en estado "Revisar".

let
    Duplicados = (tabla as table, columna as text) as number =>
        Table.RowCount(tabla) - List.Count(List.Distinct(Table.Column(tabla, columna))),
    Huerfanos = (hecho as table, columnaHecho as text, dimension as table, columnaDim as text) as number =>
        let
            Claves = List.Buffer(List.Distinct(Table.Column(dimension, columnaDim)))
        in
            Table.RowCount(Table.SelectRows(hecho, each not List.Contains(Claves, Record.Field(_, columnaHecho)))),
    SinPareja = (izquierda as table, clavesIzq as list, derecha as table, clavesDer as list) as number =>
        Table.RowCount(Table.NestedJoin(izquierda, clavesIzq, derecha, clavesDer, "x", JoinKind.LeftAnti)),
    Victorias = Table.SelectColumns(Table.SelectRows(FactPartidoEquipo, each [Resultado] = "Victoria"), {"PartidoKey", "CasaKey"}),
    PremiosQuidditch = Table.SelectColumns(
        Table.SelectRows(FactPuntos, each [CategoriaKey] = "quidditch" and [Puntos] = 50),
        {"PartidoID", "CasaKey"}
    ),
    VictoriasPorPartido = Table.Group(
        FactPartidoEquipo,
        {"PartidoKey"},
        {{"Victorias", each List.Count(List.Select([Resultado], each _ = "Victoria")), Int64.Type}}
    ),
    Controles = {
        {"Unicidad", "Casas: claves repetidas en casas.csv", Duplicados(fnLeerCsv("casas.csv"), "id")},
        {"Unicidad", "Estudiantes: claves repetidas en estudiantes.csv", Duplicados(fnLeerCsv("estudiantes.csv"), "id")},
        {"Unicidad", "Hechizos: claves repetidas en hechizos.csv", Duplicados(fnLeerCsv("hechizos.csv"), "id")},
        {"Unicidad", "Eventos: identificadores repetidos en eventos_puntos.csv", Duplicados(fnLeerCsv("eventos_puntos.csv"), "id")},
        {"Unicidad", "Partidos: identificadores repetidos en partidos.csv", Duplicados(fnLeerCsv("partidos.csv"), "id")},
        {"Integridad referencial", "Puntos sin casa válida", Huerfanos(FactPuntos, "CasaKey", DimCasa, "CasaKey")},
        {"Integridad referencial", "Puntos sin estudiante válido", Huerfanos(FactPuntos, "EstudianteKey", DimEstudiante, "EstudianteKey")},
        {"Integridad referencial", "Puntos sin semana válida", Huerfanos(FactPuntos, "SemanaKey", DimSemana, "SemanaKey")},
        {"Integridad referencial", "Puntos sin categoría válida", Huerfanos(FactPuntos, "CategoriaKey", DimCategoria, "CategoriaKey")},
        {"Integridad referencial", "Partidos por equipo sin partido válido", Huerfanos(FactPartidoEquipo, "PartidoKey", DimPartido, "PartidoKey")},
        {"Integridad referencial", "Partidos por equipo sin semana o casa válida",
            Huerfanos(FactPartidoEquipo, "SemanaKey", DimSemana, "SemanaKey") + Huerfanos(FactPartidoEquipo, "CasaKey", DimCasa, "CasaKey")},
        {"Integridad referencial", "Goles sin estudiante o partido válido",
            Huerfanos(FactGoles, "EstudianteKey", DimEstudiante, "EstudianteKey") + Huerfanos(FactGoles, "PartidoKey", DimPartido, "PartidoKey")},
        {"Integridad referencial", "Prácticas sin hechizo, casa o trimestre válido",
            Huerfanos(FactPracticas, "HechizoKey", DimHechizo, "HechizoKey")
                + Huerfanos(FactPracticas, "CasaKey", DimCasa, "CasaKey")
                + Huerfanos(FactPracticas, "TrimestreKey", DimTrimestre, "TrimestreKey")},
        {"Regla de negocio", "Premios positivos y sanciones negativas",
            Table.RowCount(Table.SelectRows(FactPuntos, each if [CategoriaKey] = "sancion" then [Puntos] >= 0 else [Puntos] <= 0))},
        {"Regla de negocio", "Marcador = 10 × goles + 150 por la Snitch",
            Table.RowCount(Table.SelectRows(FactPartidoEquipo, each [PuntosAFavor] <> 10 * [Goles] + 150 * [AtrapoSnitch]))},
        {"Regla de negocio", "Exactamente una victoria por partido", Table.RowCount(Table.SelectRows(VictoriasPorPartido, each [Victorias] <> 1))},
        {"Regla de negocio", "Cada victoria tiene su premio de +50 y viceversa",
            SinPareja(Victorias, {"PartidoKey", "CasaKey"}, PremiosQuidditch, {"PartidoID", "CasaKey"})
                + SinPareja(PremiosQuidditch, {"PartidoID", "CasaKey"}, Victorias, {"PartidoKey", "CasaKey"})},
        {"Regla de negocio", "Cada goleador jugó para su casa en ese partido",
            SinPareja(FactGoles, {"PartidoKey", "CasaKey"}, FactPartidoEquipo, {"PartidoKey", "CasaKey"})},
        {"Regla de negocio", "Éxitos entre 0 y la cantidad de intentos",
            Table.RowCount(Table.SelectRows(FactPracticas, each [Exitos] < 0 or [Exitos] > [Intentos]))}
    },
    Tabla = #table(type table [Tipo = text, Control = text, FilasConProblema = Int64.Type], Controles),
    ConEstado = Table.AddColumn(Tabla, "Estado", each if [FilasConProblema] = 0 then "OK" else "Revisar", type text),
    Resultado = Table.AddIndexColumn(ConEstado, "Orden", 1, 1, Int64.Type)
in
    Resultado
