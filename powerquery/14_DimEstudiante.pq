// DimEstudiante
// Estudiantes (nombres originales, ficticios) más un miembro "(colectivo)" para las anotaciones sin estudiante, como los premios por victorias de Quidditch. No se relaciona con DimCasa: la casa del estudiante es un atributo descriptivo y el filtro por casa llega a los hechos directamente, sin caminos ambiguos.

let
    Origen = fnLeerCsv("estudiantes.csv"),
    Tipado = Table.TransformColumnTypes(
        Origen,
        {{"id", type text}, {"name", type text}, {"houseId", type text}, {"quidditchRole", type text}},
        "en-US"
    ),
    ClavesNormalizadas = Table.TransformColumns(Tipado, {{"id", Text.Lower, type text}, {"houseId", Text.Lower, type text}}),
    Casas = Table.SelectColumns(DimCasa, {"CasaKey", "Casa"}),
    ConCasa = Table.ExpandTableColumn(
        Table.NestedJoin(ClavesNormalizadas, {"houseId"}, Casas, {"CasaKey"}, "C", JoinKind.LeftOuter),
        "C",
        {"Casa"},
        {"Casa del Estudiante"}
    ),
    // Normalización de puestos: el código de la fuente pasa a una etiqueta legible; vacío = sin puesto.
    Puestos = [cazador = "Cazador/a", golpeador = "Golpeador/a", guardian = "Guardián/a", buscador = "Buscador/a"],
    ConRol = Table.AddColumn(
        ConCasa,
        "Rol Quidditch",
        each if [quidditchRole] = null then "Sin puesto" else Record.FieldOrDefault(Puestos, Text.Lower([quidditchRole]), "Otro"),
        type text
    ),
    Marcado = Table.AddColumn(ConRol, "EsEstudiante", each true, type logical),
    Renombrado = Table.RenameColumns(Marcado, {{"id", "EstudianteKey"}, {"name", "Estudiante"}, {"houseId", "CasaKey"}}),
    Estudiantes = Table.SelectColumns(Renombrado, {"EstudianteKey", "Estudiante", "CasaKey", "Casa del Estudiante", "Rol Quidditch", "EsEstudiante"}),
    // Miembro explícito para valores faltantes: los hechos nunca quedan con clave vacía.
    Colectivo = #table(
        type table [EstudianteKey = text, Estudiante = text, CasaKey = nullable text, Casa del Estudiante = nullable text, Rol Quidditch = text, EsEstudiante = logical],
        {{"(colectivo)", "Premio colectivo de la casa", null, null, "Sin puesto", false}}
    ),
    Combinado = Table.Combine({Estudiantes, Colectivo}),
    Resultado = Table.Distinct(Combinado, {"EstudianteKey"})
in
    Resultado
