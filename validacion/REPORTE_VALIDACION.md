# Reporte de validación del modelo

Generado: 2026-10-11 17:30 · Casos: 47 · Valores comparados: 1043 · Diferencias: 0

Cada caso ejecuta una consulta DAX contra el modelo abierto en Power BI Desktop (tras una actualización completa) y la compara con un resultado calculado de forma independiente en Python a partir de los CSV (`scripts/generar_casos_validacion.py`).

| | Caso | Qué verifica | Filas esperadas |
|---|---|---|---|
| ✅ | `filas-por-tabla` | Cantidad de filas cargadas en cada tabla | 11 |
| ✅ | `puntos-casa-curso` | Puntos netos, otorgados y descontados por casa y curso | 20 |
| ✅ | `posicion-curso` | Posición de cada casa en la Copa de cada curso (empates comparten puesto) | 20 |
| ✅ | `lider-curso` | Casa líder, puntos del líder y ventaja sobre el segundo por curso | 5 |
| ✅ | `ranking-por-nombre-de-casa` | Matriz del informe: puesto y distancia al líder agrupando por DimCasa[Casa] y DimTrimestre[Curso] | 20 |
| ✅ | `lider-con-filtro-de-casa` | Con el segmentador de casa en Gryffindor, el líder y la ventaja siguen comparando contra las cuatro casas | 1 |
| ✅ | `periodo-anterior-trimestre` | Puntos del trimestre anterior y variaciones (el Otoño compara con la Primavera del curso previo) | 60 |
| ✅ | `periodo-anterior-curso` | Curso contra curso anterior: puntos y cambio de posición en el ranking | 20 |
| ✅ | `periodo-anterior-mismos-trimestres` | Curso V con Otoño + Invierno se compara con Otoño + Invierno del Curso IV | 4 |
| ✅ | `acumulado-curso-v` | Puntos acumulados por semana en el Curso V (eje SemanaCurso) | 144 |
| ✅ | `acumulado-archivo-completo` | Acumulado a lo largo de los cinco cursos (cierres de trimestre) | 60 |
| ✅ | `acumulado-eje-fecha` | El acumulado con eje en FechaInicioSemana llega al total del curso (no se queda en la última semana) | 4 |
| ✅ | `participacion` | Participación de cada casa en los puntos netos del Curso V | 4 |
| ✅ | `composicion-categorias` | Peso de cada categoría en los puntos otorgados (todo el archivo) | 4 |
| ✅ | `estudiantes-curso-v` | Puntos, puesto y contribución a su casa de cada estudiante en el Curso V (sin el miembro colectivo) | 47 |
| ✅ | `quidditch-casa-curso` | Tabla de Quidditch por casa y curso (jugados, victorias, derrotas, %, puntos, Snitch, puesto) | 20 |
| ✅ | `copa-quidditch-por-nombre` | Puesto en la Copa de Quidditch agrupando por nombre de casa (forma de consulta de la tabla del informe) | 20 |
| ✅ | `quidditch-curso` | Partidos, partidos decididos por la Snitch y puntos por partido en cada curso | 5 |
| ✅ | `quidditch-promedio-por-casa` | Puntos por partido de los partidos de cada casa en el Curso V (ambos equipos) | 4 |
| ✅ | `quidditch-sin-registros` | Casa sin partidos en el Otoño del Curso I: medidas vacías, sin errores | 1 |
| ✅ | `goles-por-estudiante` | Goles por estudiante en todo el archivo | 12 |
| ✅ | `control-quidditch` | Puntos de Quidditch en el libro = 50 × victorias, por casa y curso | 20 |
| ✅ | `hechizos-por-rama` | Intentos, éxitos y tasa de éxito por rama (todo el archivo) | 6 |
| ✅ | `hechizos-por-dificultad` | Tasa de éxito por nivel de dificultad | 5 |
| ✅ | `hechizos-vs-colegio` | Diferencia en puntos porcentuales de cada casa contra el colegio, por rama, Curso V | 24 |
| ✅ | `correlacion-dificultad-exito` | Correlación de Pearson dificultad–tasa de éxito: colegio y por casa | 5 |
| ✅ | `hechizo-mas-practicado` | Hechizo más practicado en el Curso V | 1 |
| ✅ | `calidad-de-datos` | Todos los controles de calidad en 0 | 1 |
| ✅ | `titular-curso-v` | Titular dinámico del Gran Comedor para el Curso V | 1 |
| ✅ | `variacion-texto` | Texto de la tarjeta de variación: con período previo y sin él | 2 |
| ✅ | `relojes-curso-v` | Relojes de arena (SVG idéntico a la referencia): Curso V | 1 |
| ✅ | `relojes-curso-i-invierno` | Relojes de arena (SVG idéntico a la referencia): Curso I, Invierno | 1 |
| ✅ | `relojes-archivo-completo` | Relojes de arena (SVG idéntico a la referencia): los cinco cursos | 1 |
| ✅ | `relojes-filtro-slytherin` | Relojes de arena (SVG idéntico a la referencia): Curso V con el segmentador de casa en Slytherin (las demás se atenúan) | 1 |
| ✅ | `relojes-sin-registros` | Relojes de arena (SVG idéntico a la referencia): Otoño del Curso I, sólo premios de Quidditch (casas sin anotaciones) | 1 |
| ✅ | `relojes-todo-negativo` | Relojes de arena (SVG idéntico a la referencia): Curso V, sólo sanciones (sin máximo positivo: niveles en 0, sin división por cero) | 1 |
| ✅ | `estandartes-curso-v` | Estandartes de las casas (SVG idéntico a la referencia): curso-v | 1 |
| ✅ | `estandartes-curso-v-slytherin` | Estandartes de las casas (SVG idéntico a la referencia): curso-v-slytherin | 1 |
| ✅ | `estandartes-curso-i` | Estandartes de las casas (SVG idéntico a la referencia): curso-i | 1 |
| ✅ | `estandartes-curso-ii-invierno` | Estandartes de las casas (SVG idéntico a la referencia): curso-ii-invierno | 1 |
| ✅ | `marcador-curso-v` | Marcador de Quidditch (SVG idéntico a la referencia): Curso V | 1 |
| ✅ | `marcador-curso-i-otono` | Marcador de Quidditch (SVG idéntico a la referencia): Otoño del Curso I (una casa sin partidos: fila con «—» al final) | 1 |
| ✅ | `marcador-archivo-completo` | Marcador de Quidditch (SVG idéntico a la referencia): los cinco cursos | 1 |
| ✅ | `marcador-filtro-hufflepuff` | Marcador de Quidditch (SVG idéntico a la referencia): Curso V con el segmentador en Hufflepuff (resumen de sus partidos; las demás se atenúan) | 1 |
| ✅ | `marcador-curso-i-invierno-ravenclaw` | Marcador de Quidditch (SVG idéntico a la referencia): Curso I, Invierno, segmentador en Ravenclaw: un solo partido (singular) y Hufflepuff sin partidos | 1 |
| ✅ | `marcador-sin-partidos` | Marcador sin partidos (Curso V, semana 1): aviso y filas vacías, sin errores | 1 |
| ✅ | `marcador-descripcion` | Texto alternativo del marcador (Otoño del Curso I) | 1 |
