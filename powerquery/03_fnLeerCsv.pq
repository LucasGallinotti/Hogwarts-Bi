// fnLeerCsv (consulta compartida, no se carga al modelo)
// Lee un CSV de la carpeta fuente: UTF-8, separador coma, encabezados promovidos, espacios recortados y celdas vacías convertidas en null (valor faltante real, no texto vacío). Los tipos se asignan en cada consulta con cultura en-US para no depender de la configuración regional del equipo.

(archivo as text) as table =>
let
    Fila = Table.SelectRows(ArchivosFuente, each [Name] = archivo),
    Contenido =
        if Table.RowCount(Fila) = 1 then Fila{0}[Content]
        else error Error.Record("Archivo fuente faltante", "No se encontró " & archivo & " en la carpeta indicada por RutaDatos.", RutaDatos),
    Csv = Csv.Document(Contenido, [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    ConEncabezados = Table.PromoteHeaders(Csv, [PromoteAllScalars = true]),
    Limpio = Table.TransformColumns(
        ConEncabezados,
        {},
        each if _ is text then (if Text.Trim(_) = "" then null else Text.Trim(_)) else _
    )
in
    Limpio
