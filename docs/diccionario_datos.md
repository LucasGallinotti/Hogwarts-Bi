# Diccionario de datos

> Generado automáticamente desde el TMDL (el script generador no se incluye en este repositorio). Datos ficticios de demostración.

## DimTrimestre

Calendario escolar a nivel trimestre (5 cursos × 3 trimestres). Es el nivel superior del tiempo: filtra DimSemana y, directamente, FactPracticas (cuyo grano es el trimestre).

| Columna | Tipo | Visible | Descripción |
|---|---|---|---|
| TrimestreKey | Entero | no | Clave del trimestre: CursoNumero × 10 + TrimestreOrden (p. ej. 52 = Invierno del Curso V). |
| CursoNumero | Entero | no | Número de curso (1–5). Columna de orden de Curso. |
| Curso | Texto | sí | Curso escolar: "Curso I" a "Curso V". Se ordena por `CursoNumero`. |
| Año Escolar | Texto | sí | Año escolar asignado al curso (supuesto de la capa BI: el Curso I es 2021-22). |
| TrimestreOrden | Entero | no | Orden del trimestre dentro del curso (1 Otoño, 2 Invierno, 3 Primavera). |
| Trimestre | Texto | sí | Trimestre: Otoño, Invierno o Primavera. Se ordena por `TrimestreOrden`. |
| IndiceTrimestre | Entero | no | Posición cronológica del trimestre en todo el archivo (1–15). Base de las comparaciones con el período anterior. |
| Período | Texto | sí | Etiqueta corta curso + trimestre (p. ej. "C.V · Invierno"), ordenada cronológicamente. Se ordena por `IndiceTrimestre`. |
| FechaInicio | Fecha | sí | Lunes de inicio del trimestre (calendario sintético documentado). |
| PrimeraSemana | Entero | no |  |
| UltimaSemana | Entero | no |  |

## DimSemana

Calendario a nivel semana escolar (180 filas). Es el grano temporal de los eventos de puntos y de los partidos: los datos no tienen día, así que una tabla diaria sólo agregaría filas vacías.

| Columna | Tipo | Visible | Descripción |
|---|---|---|---|
| SemanaKey | Entero | no | Clave de la semana: CursoNumero × 100 + SemanaCurso (p. ej. 507 = semana 7 del Curso V). |
| TrimestreKey | Entero | no |  |
| SemanaCurso | Entero | sí | Número de semana dentro del curso (1–36). |
| Semana | Texto | sí | Etiqueta de la semana dentro del curso: S01 a S36. Se ordena por `SemanaCurso`. |
| SemanaGlobal | Entero | no | Posición cronológica de la semana en todo el archivo (1–180). Base de los acumulados. |
| FechaInicioSemana | Fecha | sí | Lunes de inicio de la semana. Eje temporal de los gráficos de evolución (los recesos entre trimestres quedan visibles como saltos). |

## DimCasa

Las cuatro casas. Filtra todas las tablas de hechos.

| Columna | Tipo | Visible | Descripción |
|---|---|---|---|
| CasaKey | Texto | no | Clave natural de la casa (código estable de la fuente: gryffindor, slytherin, ravenclaw, hufflepuff). |
| Casa | Texto | sí | Nombre de la casa. Se ordena por `Orden`. |
| Sigla | Texto | sí | Sigla de tres letras para ejes compactos (GRY, SLY, RAV, HUF). Se ordena por `Orden`. |
| Elemento | Texto | sí | Elemento asociado a la casa. |
| Fundador | Texto | sí |  |
| Rasgos | Texto | sí | Rasgos de la casa separados por " · ". |
| Lema | Texto | sí |  |
| Orden | Entero | no | Orden de presentación fijo (no depende de los puntos). |
| ColorHex | Texto | no | Color de identidad (hex), el mismo de la web. Se usa en formato condicional mediante la medida [Color Casa]. |

## DimEstudiante

Estudiantes (nombres originales, ficticios) más un miembro "(colectivo)" para las anotaciones sin estudiante, como los premios por victorias de Quidditch. No se relaciona con DimCasa: la casa del estudiante es un atributo descriptivo y el filtro por casa llega a los hechos directamente, sin caminos ambiguos.

| Columna | Tipo | Visible | Descripción |
|---|---|---|---|
| EstudianteKey | Texto | no | Clave natural del estudiante; "(colectivo)" para premios de la casa sin estudiante. |
| Estudiante | Texto | sí |  |
| CasaKey | Texto | no | Clave de la casa del estudiante (atributo, sin relación). La usa [% Contribución a la Casa] con TREATAS. |
| Casa del Estudiante | Texto | sí | Casa del estudiante (atributo descriptivo). |
| Rol Quidditch | Texto | sí | Puesto en el equipo de Quidditch o "Sin puesto". |
| EsEstudiante | Lógico | no | Falso sólo para el miembro "(colectivo)". Permite excluirlo de los rankings de estudiantes. |

## DimCategoria

Origen de los puntos de casa. Catálogo controlado: si los eventos traen una categoría que no figura aquí, la carga se detiene.

| Columna | Tipo | Visible | Descripción |
|---|---|---|---|
| CategoriaKey | Texto | no |  |
| Categoría | Texto | sí | Nombre de la categoría: Académico, Valor, Servicio, Quidditch o Sanciones. Se ordena por `Orden`. |
| Tipo | Texto | sí | Premio (suma puntos) o Sanción (resta puntos). |
| Orden | Entero | no |  |

## DimHechizo

Catálogo de hechizos (nombres del universo, descripciones propias; dificultad y año son valores de demostración).

| Columna | Tipo | Visible | Descripción |
|---|---|---|---|
| HechizoKey | Texto | no |  |
| Hechizo | Texto | sí |  |
| Efecto | Texto | sí | Descripción breve del efecto. |
| Rama | Texto | sí | Rama de la magia: Encantamientos, Transformaciones, Defensa, Maleficios, Curación o Contrahechizos. Se ordena por `RamaOrden`. |
| RamaOrden | Entero | no |  |
| Dificultad | Entero | sí | Dificultad de 1 (elemental) a 5 (avanzada). Atributo, no se suma. |
| Nivel de Dificultad | Texto | sí | Etiqueta de dificultad para ejes: "Nivel 1" a "Nivel 5". Se ordena por `Dificultad`. |
| Año de Enseñanza | Entero | sí | Año de Hogwarts en el que suele enseñarse. |

## DimPartido

Un partido de Quidditch por fila (30). Atributos descriptivos del partido; las métricas por equipo viven en FactPartidoEquipo. No se relaciona con el calendario para no crear un segundo camino de filtro hacia los hechos.

| Columna | Tipo | Visible | Descripción |
|---|---|---|---|
| PartidoKey | Texto | no |  |
| Partido | Texto | sí | Etiqueta del partido: curso, semana y siglas (p. ej. "C.V · S07 · SLY–RAV"). Se ordena por `Orden`. |
| Local | Texto | sí |  |
| Visitante | Texto | sí |  |
| Marcador | Texto | sí | Marcador local–visitante. |
| Ganador | Texto | sí |  |
| Casa de la Snitch | Texto | sí | Casa que atrapó la Snitch (+150). |
| Snitch Decisiva | Lógico | no | Verdadero si, sin los 150 puntos de la Snitch, el resultado se habría invertido o empatado. Lógica (filtros DAX); oculta. |
| ¿Decidió la Snitch? | Texto | sí | "Sí" / "No": versión para mostrar de Snitch Decisiva. |
| Duración (min) | Entero | sí |  |
| Orden | Entero | no |  |

## FactPuntos

Libro contable de puntos de casa. Grano: una anotación (premio o sanción) por fila. Incluye los +50 por cada victoria de Quidditch.

| Columna | Tipo | Visible | Descripción |
|---|---|---|---|
| EventoID | Texto | no | Identificador del evento en la fuente. |
| SemanaKey | Entero | no |  |
| CasaKey | Texto | no |  |
| EstudianteKey | Texto | no | Estudiante que generó la anotación; "(colectivo)" si fue un premio de la casa. |
| CategoriaKey | Texto | no |  |
| Puntos | Entero | no | Puntos de la anotación: positivos para premios, negativos para sanciones. Se consumen mediante medidas. |
| Motivo | Texto | sí | Motivo registrado de la anotación. |
| PartidoID | Texto | no | Partido que originó el premio (sólo categoría Quidditch). Trazabilidad; sin relación. |

## FactPartidoEquipo

Rendimiento de cada equipo en cada partido. Grano: partido × casa (2 filas por partido: local y visitante). Permite medir victorias, derrotas y puntos por casa sin duplicar el conteo de partidos (que se cuenta con DISTINCTCOUNT).

| Columna | Tipo | Visible | Descripción |
|---|---|---|---|
| PartidoKey | Texto | no |  |
| SemanaKey | Entero | no |  |
| CasaKey | Texto | no | Casa del equipo de esta fila. |
| RivalCasaKey | Texto | no | Casa rival (atributo; sin relación para evitar ambigüedad con CasaKey). |
| Condicion | Texto | sí | Local o Visitante. |
| PuntosAFavor | Entero | no |  |
| PuntosEnContra | Entero | no |  |
| Goles | Entero | no | Goles del equipo (10 puntos cada uno). |
| AtrapoSnitch | Entero | no | 1 si el equipo atrapó la Snitch (+150), 0 si no. |
| Resultado | Texto | sí | Victoria o Derrota (no existen empates). |

## FactGoles

Goles por jugador y partido. Grano: partido × estudiante (sólo cazadores/as que anotaron).

| Columna | Tipo | Visible | Descripción |
|---|---|---|---|
| PartidoKey | Texto | no |  |
| SemanaKey | Entero | no |  |
| CasaKey | Texto | no | Casa del goleador, tomada del maestro de estudiantes. |
| EstudianteKey | Texto | no |  |
| Goles | Entero | no |  |

## FactPracticas

Prácticas de hechizos. Grano: curso × trimestre × casa × hechizo (lanzamientos y aciertos registrados). Se relaciona con el calendario a nivel trimestre porque la fuente no tiene semana.

| Columna | Tipo | Visible | Descripción |
|---|---|---|---|
| TrimestreKey | Entero | no |  |
| CasaKey | Texto | no |  |
| HechizoKey | Texto | no |  |
| Intentos | Entero | no | Lanzamientos registrados. |
| Exitos | Entero | no | Lanzamientos exitosos. |

## ControlCalidad

Controles de calidad de datos que se recalculan en cada actualización: unicidad de claves en los archivos fuente, integridad referencial de los hechos y reglas de negocio. Un control con FilasConProblema > 0 queda en estado "Revisar".

| Columna | Tipo | Visible | Descripción |
|---|---|---|---|
| Orden | Entero | no |  |
| Tipo | Texto | sí | Unicidad, Integridad referencial o Regla de negocio. |
| Control | Texto | sí |  Se ordena por `Orden`. |
| FilasConProblema | Entero | sí | Cantidad de filas que no cumplen el control (0 = correcto). |
| Estado | Texto | sí | OK o Revisar. |
