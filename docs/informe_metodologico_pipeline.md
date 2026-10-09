# Metodología del pipeline de evaluación de impacto de política pública

**De `main.py` a los resultados: diseño, supuestos y limitaciones**

---

## 1. Resumen

Este documento describe la metodología estadística implementada en el pipeline de evaluación de impacto (`main.py` y los módulos que orquesta), pensado como referencia para quien necesite evaluar, reproducir o extender el análisis. Cubre, en el orden en que el código las ejecuta: el linaje de los datos, la asignación a grupos, el muestreo, el remuestreo bootstrap, los chequeos de representatividad y balance, y los artefactos que el pipeline produce.

El pipeline evalúa el impacto de una política pública mediante un diseño cuasi-experimental de dos grupos (control/tratamiento), usando remuestreo bootstrap para caracterizar la variabilidad muestral y validar la representatividad y el balance de las muestras frente a la población de origen. No estima, en esta etapa, el efecto causal del tratamiento en sí — es un pipeline de preparación, muestreo y diagnóstico de calidad muestral; la estimación del efecto es un análisis posterior, separado.

---

## 2. Diseño del estudio

La asignación a grupos surge del estado administrativo de cada solicitud (`randomization.py`):

- **Tratamiento**: `state == "solicitud_adjudicada"` — la solicitud fue adjudicada.
- **Control**: cualquier otro estado que haya pasado el filtro de elegibilidad (en la práctica, `"solicitud_elegible_rechazadas_por_excedente"` — elegible pero rechazada por exceso de demanda sobre cupos disponibles).

**Lo que el código fija y lo que no.** El código define los grupos a partir de ese estado administrativo; no registra *cómo* se decidió qué solicitudes se adjudicaron. Ese mecanismo (por ejemplo, un sorteo entre solicitantes elegibles, u otra regla) es lo que determina el tipo de diseño y qué supuesto de identificación hay que defender, y debe documentarse por fuera del código. Si la adjudicación fue por sorteo entre elegibles, la asignación es aleatoria por diseño y el supuesto central es la integridad del sorteo; si siguió otra regla, el diseño es cuasi-experimental y la comparación depende de que "adjudicada" vs. "rechazada por excedente" no esté asociado a no-observables que afecten el resultado de interés. En ambos casos es un supuesto que este pipeline no testea (no es su función) y que cualquier lectura de sus resultados debe tener presente.

---

## 3. Fuentes de datos y linaje

Tres fuentes, unidas en `preprocessing.py` (`ProcessedDataframe.concatenate_df`):

| Fuente | Qué se sabe desde el código | Método de unión |
|---|---|---|
| `ficha_inscriptos.xlsx` | Una fila por inscripto; la fuente exacta de `etapa_inscripcion`, `state`, `fecha_de_nacimiento` y `fecha_carga` no está documentada en el código | — |
| `formularios_curso.xlsx` | Según `constants.py`, de acá salen las variables de análisis salvo `conurbano_interior` | Concatenación posicional (`axis=1`) con `ficha_inscriptos` |
| `base_municipios.xlsx` | Según `constants.py`, de acá sale `conurbano_interior` | `merge` por clave `municipio` |

**Dos supuestos de linaje, explícitos y con salvaguarda de código, no solo de intención:**

1. **`ficha_inscriptos` y `formularios_curso` no comparten una columna ID.** La unión es posicional: se asume que la fila *i* de un archivo corresponde a la misma persona que la fila *i* del otro. No hay forma de verificar esto desde el código — es un supuesto sobre cómo se generaron ambos archivos aguas arriba. La única salvaguarda posible en este punto es que ambos tengan la misma cantidad de filas (`len(df_2) == len(df_3)`, verificado antes del concat); si no coinciden, el pipeline se detiene en vez de producir un dataset desalineado en silencio.

2. **La unión con `base_municipios` depende de la calidad de la clave `municipio` como texto libre.** Antes de mergear, la clave se normaliza (recorte de espacios, minúsculas) en ambos lados, y se verifica que sea única en `base_municipios` — una clave duplicada ahí multiplicaría personas en el dataset final, y una clave no normalizada dejaría `conurbano_interior` en `NaN` para cualquier variación de escritura del nombre del municipio. Ambos chequeos fallan de forma explícita (`ValueError`) en vez de producir un dataset corrupto sin avisar.

---

## 4. Taxonomía de variables

`constants.py` clasifica cada variable en uno de tres tipos, con implicancias estadísticas distintas para cada uno (`bootstrap/models.py`, `column_registry.py`):

| Tipo | Variables | Estadístico | Validación |
|---|---|---|---|
| **Continua** | `ingreso_anual_hogar`, `edad`, `personas_por_ambiente` | media, desvío, varianza (ddof=1) | var ≈ std² (rtol 1e-5) |
| **Binaria** | `escenario_vulnerabilidad_social`, `paredes_ext_revocadas` | proporción *p* | var ≈ p(1-p) (consistencia Bernoulli, rtol 1e-5) |
| **Categórica** | `sexo_dni`, `relacion_de_parentezco_con_jefe_del_hogar`, `conurbano_interior` | proporciones por categoría + residual "otros" | Σ proporciones ≈ 1.0 (atol 1e-5) |

Tres observaciones metodológicas sobre esta clasificación, no bugs sino decisiones de diseño con costo estadístico a tener presente:

- **Dos de las tres variables categóricas son, en los hechos, binarias.** `relacion_de_parentezco_con_jefe_del_hogar` solo declara la categoría `"Soy jefa(e)"` (el resto cae en "otros"), y `conurbano_interior` solo declara `"Conurbano"` (el resto, presumiblemente "Interior", cae en "otros"). Tratarlas como categóricas en vez de binarias las excluye de la validación de consistencia Bernoulli que sí tienen `escenario_vulnerabilidad_social`/`paredes_ext_revocadas`, y las expone al mismo problema de estabilidad del punto siguiente sin esa red de seguridad adicional.

- **El coeficiente de representatividad (`1 - error_relativo`) es inestable cuando la media poblacional está cerca de 0.** Un error absoluto pequeño produce un error relativo grande cuando se lo divide por una media chica — un riesgo real para variables categóricas/binarias de baja prevalencia. El pipeline no filtra ni transforma para mitigar esto; lo hereda tal cual en cualquier variable de prevalencia baja.

- **`ingreso_anual_hogar` es, típicamente, una variable de cola pesada.** Resumirla con media/desvío estándar/CV crudos (como hace el pipeline, igual que con cualquier otra continua) es sensible a esa asimetría — una práctica común en la literatura de ingresos/hogares es trabajar en escala logarítmica, o reportar mediana/rango intercuartílico en paralelo. El pipeline no lo hace; queda como recomendación para quien interprete `ingreso_anual_hogar` específicamente.

---

## 5. Preprocesamiento

`ProcessedDataframe` (`preprocessing.py`), tres pasos encadenados manualmente (no automáticos en `__init__`):

1. **`concatenate_df()`** — linaje de datos, sección 3.
2. **`filter_df()`** — conserva solo `etapa_inscripcion == 1` y `state` en {`solicitud_adjudicada`, `solicitud_elegible_rechazadas_por_excedente`}. Es este filtro el que define la población de análisis (personas de la etapa de inscripción 1 con solicitud adjudicada o elegible rechazada por excedente) y, junto con `randomization.py`, la partición control/tratamiento.
3. **`calculate_age()`** — deriva `edad` a partir de `fecha_de_nacimiento` y `fecha_carga` (`dateutil.relativedelta`, en años completos). Fechas no parseables (`errors="coerce"`) devuelven `NA`.

---

## 6. Muestreo aleatorio simple (SRS) inicial

`randomization.py` extrae una muestra aleatoria simple de tamaño fijo (`SAMPLE_SIZE`, `constants.py`) de cada grupo, sin reemplazo, con semilla fija (`RANDOM_STATE`). Esta SRS (`srs_c`, `srs_t`) es la base sobre la que corre todo lo que sigue — bootstrap incluido. El bootstrap remuestrea *esta* muestra fija, no vuelve a tomar muestras de la población en cada réplica; es una fuente de varianza muestral **condicional a la SRS ya extraída**, no una re-estimación independiente del error de muestreo original de la SRS.

Sobre esta SRS, `SampleAnalysis`/`GroupSummary` calculan estadística descriptiva estándar (media/desvío, proporciones por condición), y `RepresentativenessCalculator` evalúa su representatividad frente a la población completa (sección 8).

---

## 7. Remuestreo bootstrap

`BootstrapExperiment.run_bootstrap()` (`bootstrap/bootstrapping_experiment.py`) genera `n_bootstrap` réplicas (default 10.000; el propio código advierte si se baja de 1.000) mediante remuestreo con reemplazo de `srs_c`/`srs_t`, cada una con su propia semilla derivada de `numpy.random.SeedSequence(RANDOM_STATE)` — lo que hace cada réplica reproducible individualmente sin tener que rehacer todo el proceso desde cero (ver sección 13).

Para cada réplica se calculan, por columna, las estadísticas correspondientes a su tipo (sección 4) y se acumulan en `BootstrapResults`, que al final resume la distribución completa (no solo un punto): percentiles e intervalo de confianza (95% por defecto) sobre las `n_bootstrap` réplicas, por media/desvío/varianza (continuas y binarias) o por proporción de cada categoría (categóricas).

---

## 8. Validación de representatividad

`RepresentativenessCalculator` compara la media (o proporción) de cada variable en una muestra contra la población completa:

```
error_relativo         = |media_muestra - media_población| / media_población
coef_representatividad = 1 - error_relativo
```

Un coeficiente cercano a 1 indica alta representatividad; puede ser negativo si el error relativo supera el 100% de la media de referencia (ver la advertencia de estabilidad en la sección 4). Se aplica en dos momentos:

- **Sobre la SRS** (una evaluación puntual, antes del bootstrap).
- **Sobre cada réplica bootstrap** (`evaluate_replica`), resumida después con el mismo esquema de percentiles/IC que el resto del pipeline (`summarize_bootstrap_replicas`).

En ambos casos el pipeline registra una advertencia si encuentra coeficientes negativos, pero no interrumpe la ejecución — es un diagnóstico, no un gate.

---

## 9. Diferencia de medias estandarizada (SMD)

Complementa la representatividad (muestra vs. población) con el **balance entre grupos** (control vs. tratamiento) — la pregunta relevante para cualquier comparación causal posterior: ¿tan parecidos son control y tratamiento entre sí en las variables de base?

```
SMD = (media_tratamiento - media_control) / desvío_pooled
```

con la fórmula exacta según el tipo de variable (`representativity/smd.py`, `SMDCalculator`):

- **Continua / binaria**: Cohen's *d* con desvío pooled, `sqrt((var₁ + var₂) / 2)`.
- **Categórica**: SMD por cada categoría vía codificación *dummy* (k-1 categorías, la última como referencia), resumido como el máximo `|SMD|` entre categorías — la convención estándar para reportar balance en variables nominales con más de dos niveles.

**Igual que el resto del pipeline, el SMD no es un número puntual de una sola muestra: se calcula por réplica bootstrap y se resume con percentiles/IC** (`replica_smd` + `summarize_bootstrap_replicas`, mismo patrón que la sección 8). La interpretación de balance sobre el SMD promedio usa umbrales empíricos de uso habitual en la literatura de balance de covariables (reglas prácticas, no un test estadístico):

| \|SMD promedio\| | Balance |
|---|---|
| < 0.10 | Excelente |
| 0.10 – 0.25 | Aceptable |
| > 0.25 | Desequilibrado |

El pipeline registra una advertencia (sin interrumpir la ejecución) si alguna variable queda "desequilibrado" en promedio.

---

## 10. Selección de "mejor réplica" para reporte descriptivo

De las `n_bootstrap` réplicas generadas, el pipeline identifica la réplica de control y la de tratamiento con **menor error de representatividad promedio frente a la población** (ranking por percentil promedio entre todas las variables, `_best_replica_index`) y las usa para los gráficos de distribución (sección 11) y como exportación de referencia (`best_control_sample.parquet` / `best_treatment_sample.parquet`).

**Esto requiere una advertencia explícita, central para cualquier lectura científica del pipeline**: por construcción, estas no son muestras típicas. Son, de entre miles de candidatas, la que más se parece a la población — elegida a propósito por ese criterio. Van a lucir sistemáticamente *más* representativas que cualquier muestra real, SRS incluida. Su uso previsto es exclusivamente descriptivo/ilustrativo. **No deben usarse como insumo de una estimación de efecto causal** — para eso corresponde la distribución bootstrap completa (sección 7) o la SRS original (sección 6), que no tienen este sesgo de selección. El pipeline deja esta advertencia tanto en el código (`run_bootstrap`) como en cada gráfico exportado (pie de página).

Adicionalmente, y solo a fines diagnósticos, el pipeline también identifica cuál habría sido la mejor réplica *por variable individual* (no la agregada) — útil para ver si el balance agregado está dominado por unas pocas variables, pero sin ningún efecto sobre qué muestra se grafica o exporta.

---

## 11. Trazabilidad y reproducibilidad

`BootstrapTraceability` (`bootstrap/traceability.py`) registra, por réplica: la semilla que la generó y sus estadísticos de representatividad (por variable y agregado). Esto permite dos cosas sin tener que guardar las `n_bootstrap` réplicas completas en memoria o disco:

- **Regenerar cualquier réplica puntual** a partir de su semilla (`regenerate_indexes`), incluida la ganadora, para auditoría posterior.
- **Reportar qué réplica ganó y por qué** (`to_summary_df`) — con dos métricas separadas y no intercambiables: el coeficiente de representatividad crudo (que es el criterio real solo en las filas por variable) y el score de selección basado en percentil (que es el criterio real solo en la fila agregada). No se promedian coeficientes de variables de distinto tipo/escala para el agregado — el mismo problema que motivó usar percentiles como criterio de selección en primer lugar.

Los artefactos de trazabilidad se guardan con timestamp de corrida (`run_id`) en un directorio que **no se limpia entre corridas** (a diferencia de las tablas de resultados), para que el historial de corridas se acumule en vez de perderse.

---

## 12. Visualizaciones

`GroupComparisonPlotter` (`visualizations/group_comparison.py`) genera, por variable: un KDE superpuesto (Población/Control/Tratamiento) para continuas, o un gráfico de barras de proporciones para binarias/categóricas. Cada gráfico incluye el pie de página de advertencia mencionado en la sección 10.

---

## 13. Artefactos exportados

Por corrida, en `data/final/`:

| Directorio | Contenido |
|---|---|
| `tables/` | Resúmenes bootstrap (control/tratamiento), representatividad (SRS y bootstrap), SMD, estadística descriptiva SRS, mejores muestras (`.parquet`) — se limpia antes de cada corrida |
| `distributions/` | Gráficos de distribución (`.png`) — se limpia antes de cada corrida |
| `traceability/` | JSON de trazabilidad + resumen de réplicas ganadoras, con `run_id` — **no** se limpia, conserva historial entre corridas |

---

## 14. Limitaciones metodológicas y consideraciones abiertas

Resumen consolidado de lo señalado en las secciones anteriores, para que quede en un solo lugar:

1. **Identificación causal no verificada.** El diseño control/tratamiento depende de que el estado de adjudicación no esté correlacionado con no-observables relevantes (sección 2) — supuesto, no testeado por este pipeline.
2. **Sesgo de selección en las muestras "mejores".** `best_control_sample`/`best_treatment_sample` están optimizadas por diseño para parecerse a la población; uso exclusivamente descriptivo (sección 10).
3. **Inestabilidad del coeficiente de representatividad cerca de media poblacional ≈ 0** — afecta más a variables categóricas/binarias de baja prevalencia (sección 4).
4. **Clasificación binaria-como-categórica** en dos de tres variables de `CAT_CONDITIONS`, sin la validación de consistencia Bernoulli que sí tienen las binarias explícitas (sección 4).
5. **Variables de cola pesada** (`ingreso_anual_hogar`) resumidas con estadísticos sensibles a la asimetría (sección 4).
6. **Dependencia de la calidad de `municipio` como clave de texto libre** — mitigada con normalización y chequeo de unicidad, pero la cobertura real de `base_municipios.xlsx` frente a los municipios presentes en los datos no está garantizada por el código (sección 3).
7. **El bootstrap es condicional a la SRS ya extraída** — no reestima el error de muestreo de la extracción original de la SRS (sección 6).

Ninguno de estos puntos es, individualmente, motivo para descartar el pipeline — son supuestos y decisiones de diseño que cualquier uso de sus resultados con fines de investigación o de política pública debería tener explícitos, no implícitos.

---

## 15. Apéndice: reproducibilidad

- **Semilla**: `RANDOM_STATE` (`constants.py`) fija la SRS inicial; `numpy.random.SeedSequence` deriva una semilla hija por réplica bootstrap, registrada individualmente en `traceability/`.
- **Estructura de paquetes**: `bootstrap/` (experimento, resultados, trazabilidad, registro de columnas, modelos Pydantic), `representativity/` (representatividad, SMD), `src/` (preprocesamiento, aleatorización, resumen por grupo, utilidades), `visualizations/` (gráficos).
- **Punto de entrada**: `main.py`, función `main()`, sin argumentos de línea de comandos — la configuración vive en `constants.py` (qué variables) y `config.py` (rutas de datos).
- **Dependencias**: pandas, numpy, pydantic, matplotlib, seaborn, openpyxl, pyarrow, python-dateutil.

Este informe fue validado ejecutando el pipeline real de punta a punta (`main()` completo, sin parches) contra datos sintéticos que preservan la estructura de columnas y el linaje de fuentes descrito en la sección 3, incluidos los casos límite de la unión con `base_municipios` (filas desalineadas, clave sin normalizar, clave duplicada) y los dos caminos de balance SMD (aceptable y desequilibrado).
