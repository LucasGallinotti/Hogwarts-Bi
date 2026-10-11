// DimCategoria
// Origen de los puntos de casa. Catálogo controlado: si los eventos traen una categoría que no figura aquí, la carga se detiene.

let
    Catalogo = #table(
        type table [CategoriaKey = text, Categoria = text, Tipo = text, Orden = Int64.Type],
        {
            {"academico", "Académico", "Premio", 1},
            {"valor", "Valor", "Premio", 2},
            {"conducta", "Servicio", "Premio", 3},
            {"quidditch", "Quidditch", "Premio", 4},
            {"sancion", "Sanciones", "Sanción", 5}
        }
    ),
    EnEventos = List.Distinct(List.Transform(fnLeerCsv("eventos_puntos.csv")[category], Text.Lower)),
    Desconocidas = List.Difference(EnEventos, Catalogo[CategoriaKey]),
    Resultado =
        if List.IsEmpty(Desconocidas)
        then Catalogo
        else error Error.Record("Categoría desconocida", "eventos_puntos.csv contiene categorías sin catálogo: " & Text.Combine(Desconocidas, ", "))
in
    Resultado
