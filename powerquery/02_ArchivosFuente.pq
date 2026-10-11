// ArchivosFuente (consulta compartida, no se carga al modelo)
// Única conexión a datos del modelo: la carpeta de CSV. Todas las consultas leen sus archivos desde aquí, así Power Query ve un solo origen (sin conflictos de niveles de privacidad al combinar archivos).

let
    Ruta = if Text.EndsWith(RutaDatos, "\") then RutaDatos else RutaDatos & "\",
    Archivos = Folder.Files(Ruta),
    SoloCsv = Table.SelectRows(Archivos, each Text.Lower([Extension]) = ".csv" and [Folder Path] = Ruta),
    Columnas = Table.SelectColumns(SoloCsv, {"Name", "Content"})
in
    Columnas
