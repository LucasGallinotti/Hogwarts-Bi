# Catálogo de medidas DAX

> Generado automáticamente desde el TMDL. El código completo está en [`dax/medidas.dax`](../dax/medidas.dax).

## 1. Puntos

| Medida | Formato | Qué calcula |
|---|---|---|
| Puntos Netos | `#,0;-#,0;0` | Suma neta de puntos de casa (premios menos sanciones) en el contexto de filtro. |
| Puntos Otorgados | `#,0` | Puntos ganados por premios (sólo anotaciones positivas). |
| Puntos Descontados | `#,0` | Puntos perdidos por sanciones, expresados en positivo. |
| Anotaciones | `#,0` | Cantidad de anotaciones (premios y sanciones). |
| Puntos Acumulados | `#,0;-#,0;0` | Puntos netos acumulados semana a semana dentro del período seleccionado. Quita los filtros del eje (ALLSELECTED) y suma todas las semanas hasta la actual. |
| % Participación | `0.0%;-0.0%;0.0%` | Participación de la casa en los puntos netos de las cuatro casas. |
| % de Puntos Otorgados | `0.0%;-0.0%;0.0%` | Peso de cada categoría dentro de los puntos otorgados (las sanciones no forman parte del denominador). |

## 2. Ranking

| Medida | Formato | Qué calcula |
|---|---|---|
| Posición | `0` | Puesto de la casa en la Copa del período (1 = líder). Los empates comparten puesto (1, 2, 2, 4). Itera ALL ( DimCasa ) —la tabla completa— para que ningún filtro sobre otra columna de la casa (nombre, sigla) sobreviva a la transición de contexto. |
| Puntos del Líder | `#,0;-#,0;0` | Mayor puntaje neto entre las cuatro casas en el período. |
| Casa Líder | `—` | Casa (o casas, si empatan) con más puntos netos en el período. |
| Ventaja del Líder | `#,0` | Diferencia entre el primer y el segundo puesto (0 si hay empate en la punta). |
| Distancia al Líder | `#,0` | Puntos que separan a la casa del líder (0 para el líder). |
| Posición Período Anterior | `0` | Puesto de la casa en el período anterior (ver [Puntos Período Anterior]). |
| Cambio de Posición | `▲0;▼0;=` | Puestos ganados (▲) o perdidos (▼) respecto del período anterior. |

## 3. Comparación temporal

| Medida | Formato | Qué calcula |
|---|---|---|
| Puntos Período Anterior | `#,0;-#,0;0` | Puntos netos del período anterior del mismo nivel: si el contexto es un único trimestre, el trimestre previo (cruzando de curso si hace falta); si es un curso, el curso previo con los mismos trimestres seleccionados. Devuelve 0 si el período anterior existe pero no tuvo anotaciones, y vacío si no hay período anterior. |
| Período de Comparación | `—` | Texto que indica contra qué período se compara (p. ej. "vs. C.V · Otoño" o "vs. Curso IV"). |
| Variación vs Período Anterior | `+#,0;-#,0;0` | Diferencia de puntos netos contra el período anterior. |
| Variación vs Período Anterior (texto) | `—` | Variación como texto para tarjetas: el número y contra qué período se compara (o por qué no hay comparación). |
| Variación % vs Período Anterior | `+0.0%;-0.0%;0.0%` | Variación relativa contra el período anterior (sobre el valor absoluto del período anterior). |

## 4. Estudiantes

| Medida | Formato | Qué calcula |
|---|---|---|
| Puntos Netos Estudiante | `#,0;-#,0;0` | Puntos netos de estudiantes reales (excluye los premios colectivos de la casa). |
| Posición Estudiante | `0` | Puesto del estudiante entre los estudiantes con anotaciones en la selección actual. |
| % Contribución a la Casa | `0.0%;-0.0%;0.0%` | Porcentaje de los puntos netos de su casa que aportó el estudiante en el período. Usa TREATAS porque la casa del estudiante es un atributo sin relación. |

## 5. Quidditch

| Medida | Formato | Qué calcula |
|---|---|---|
| Partidos | `#,0` | Partidos distintos en el contexto (cada partido tiene dos filas en FactPartidoEquipo). |
| Partidos Jugados | `#,0` | Partidos disputados por la casa (o participaciones, si no hay una casa en contexto). |
| Victorias | `#,0` | Partidos ganados. Muestra 0 (no vacío) si la casa jugó y no ganó. |
| Derrotas | `#,0` | Partidos perdidos. Muestra 0 (no vacío) si la casa jugó y no perdió. |
| % Victorias | `0%` | Victorias sobre partidos jugados. Sólo tiene sentido por casa: a nivel total sería siempre 50 %. |
| Puntos a Favor | `#,0` | Puntos de partido anotados (goles × 10 + Snitch). |
| Puntos en Contra | `#,0` |  |
| Diferencia de Puntos | `+#,0;-#,0;0` |  |
| Snitches Atrapadas | `#,0` | Snitches atrapadas. |
| Goles | `#,0` | Goles convertidos (10 puntos cada uno). |
| Partidos Decididos por la Snitch | `#,0` | Partidos cuyo resultado habría cambiado sin los 150 puntos de la Snitch. |
| % Decididos por la Snitch | `0%` |  |
| Puntos por Partido | `#,0.0` | Promedio de puntos por partido sumando ambos equipos. Con una casa filtrada, promedia sus partidos (contando también al rival). |
| Margen del Partido | `#,0` | Diferencia de puntos entre ganador y perdedor de un partido (para tablas por partido). |
| Posición Copa Quidditch | `0` | Puesto en la Copa de Quidditch: más puntos de partido a favor; desempatan las victorias. Compara siempre contra las cuatro casas. |

## 6. Hechizos

| Medida | Formato | Qué calcula |
|---|---|---|
| Intentos | `#,0` | Lanzamientos de hechizos registrados en prácticas. |
| Éxitos | `#,0` | Lanzamientos exitosos. |
| Tasa de Éxito | `0.0%` | Éxitos sobre intentos. |
| Tasa de Éxito del Colegio | `0.0%` | Tasa de éxito de las cuatro casas juntas, con los demás filtros del contexto. |
| Diferencia vs Colegio (pp) | `+0.0 pp;-0.0 pp;0.0 pp` | Diferencia en puntos porcentuales entre la tasa de éxito del contexto y la del colegio. |
| Hechizos Practicados | `#,0` | Hechizos distintos con al menos un intento. |
| Hechizo Más Practicado | `—` | Hechizo con más intentos en el contexto (desempata por nombre). |
| Correlación Dificultad–Éxito | `0.00;-0.00;0.00` | Correlación de Pearson entre dificultad y tasa de éxito, calculada sobre los hechizos del contexto (necesita al menos 3). |

## 7. Formato y textos

| Medida | Formato | Qué calcula |
|---|---|---|
| Color Casa | `—` | Color de identidad de la casa en contexto (dorado si no hay una sola casa). Para formato condicional. |
| Titular Gran Comedor | `—` | Titular dinámico del Gran Comedor: quién lidera, en qué período y por cuánto. |
| Titular Quidditch | `—` | Titular dinámico de Quidditch. |
| Titular Hechizos | `—` | Titular dinámico de Hechizos a partir de la correlación. |
| Color Fondo Puesto | `—` | Fondo de celda para destacar al campeón en la matriz de puestos (formato condicional). |

## 8. Visuales SVG

| Medida | Formato | Qué calcula |
|---|---|---|
| Relojes de Arena (SVG) | `—` | SVG dinámico de los cuatro relojes de arena (Gran Comedor). La arena de cada reloj es proporcional a los [Puntos Netos] de la casa en el contexto de filtro: 92 px × max(puntos, 0) / máximo positivo entre las casas (sin división por cero ni niveles negativos). Itera ALL ( DimCasa ) para que el segmentador de casa no oculte las demás: las no seleccionadas se atenúan. Bajo cada reloj, el sigilo del elemento de la casa. Implementación de referencia y pruebas: scripts/svg_relojes.py. |
| Relojes de Arena (descripción) | `—` | Texto alternativo de los relojes de arena (accesibilidad y tooltip): casa, puntos y puesto. |
| Estandartes de las Casas (SVG) | `—` | SVG dinámico de los estandartes de las casas (Rendimiento de las casas): puesto, puntos netos y variación contra el período anterior en el contexto de filtro, más la identidad fija de cada casa (color, sigilo de su elemento y rasgos). Referencia y pruebas: scripts/svg_estandartes.py. |
| Marcador de Quidditch (SVG) | `—` | SVG dinámico del marcador de la Copa de Quidditch (página Quidditch y Hechizos): una fila por casa, ordenada por [Posición Copa Quidditch], con partidos jugados, victorias, derrotas, puntos a favor y en contra, diferencia y Snitches; al pie, [Partidos], [Partidos Decididos por la Snitch] y [Puntos por Partido], más los tres máximos goleadores ([Goles] por estudiante). Sólo reutiliza medidas existentes. Una casa sin partidos en el contexto muestra "—" y va al final; con el segmentador de casa, las demás se atenúan. Referencia y pruebas: scripts/svg_marcador.py. |
| Marcador de Quidditch (descripción) | `—` | Texto alternativo del marcador de Quidditch (accesibilidad): puesto, victorias y puntos a favor de cada casa que jugó. |

## 9. Calidad de datos

| Medida | Formato | Qué calcula |
|---|---|---|
| Control Quidditch (debe ser 0) | `0` | Debe ser 0: puntos de casa por Quidditch menos 50 × victorias en el mismo contexto. Verifica la consistencia entre el libro de puntos y los partidos. |
| Controles con Problemas | `0` | Cantidad de controles de calidad en estado "Revisar". |
| Estado de Calidad | `—` | Resumen legible del estado de calidad de datos. |
