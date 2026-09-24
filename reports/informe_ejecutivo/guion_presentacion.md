# Guion de defensa — Inteligencia de Catálogo (StreamView Analytics)

**Duración objetivo: ~10 minutos de exposición + 5 minutos de preguntas.**
Suma de los tiempos orientativos abajo: ≈9 min 50 s, dejando margen para transiciones y nervios.

> **Recuerda:** la defensa es individual aunque el trabajo sea grupal, y el docente puede hacer
> preguntas cruzadas — es decir, a cualquiera sobre cualquier parte, no solo sobre lo que presentó.
> Todos los integrantes deberían leer el guion completo al menos una vez, no solo su tramo.

## Cómo dividir las diapositivas si son varios en el equipo

| Si son... | División sugerida |
|---|---|
| 2 personas | Persona A: diapositivas 1–9 (encargo, método, contexto, hallazgo central) · Persona B: 10–18 (oportunidades, riesgo, herramienta, propuestas, cierre) |
| 3 personas | Persona A: 1–6 · Persona B: 7–13 · Persona C: 14–18 |
| 4 personas | Corta cada bloque de 3 personas por la mitad |

Ajusta los cortes para que cada quien hable un tiempo similar; no es necesario respetar los
cortes exactos de arriba.

---

## Diapositiva 1 — Portada (~20 s)

Buenos días/tardes. Somos el equipo consultor a cargo de Inteligencia de Catálogo para
StreamView Analytics, una plataforma de streaming que necesita entender su catálogo de 31.991
títulos, entre 2010 y 2025, para tomar mejores decisiones de contenido. Trabajamos bajo
metodología CRISP-DM y nuestro destinatario principal es la Dirección de Contenidos.

## Diapositiva 2 — El encargo (~40 s)

El problema que nos encargaron no es de falta de datos: es de falta de una lectura integrada.
Hoy StreamView no distingue entre el contenido que genera tráfico y el que genera satisfacción
real — y eso importa, porque el tráfico sostiene el consumo del mes, pero la satisfacción
sostiene la renovación de la suscripción. La pregunta que guía todo nuestro trabajo es: ¿qué
concentra la atención, qué concentra la valoración, y qué decisiones se desprenden de esa
diferencia? Diseñamos la solución para tres audiencias: la Dirección de Contenidos, que decide
qué adquirir y producir; el comité ejecutivo, que asigna presupuesto; y el equipo de producto,
que decide qué promover.

## Diapositiva 3 — Metodología (~30 s)

Trabajamos con CRISP-DM, las seis fases clásicas de minería de datos. Quiero destacar algo: el
método fue realmente iterativo. En la fase de análisis descubrimos que películas y series usaban
taxonomías de género distintas, y tuvimos que volver a la fase de preparación para armonizarlas
antes de seguir.

## Diapositiva 4 — Comprensión de los datos (~40 s)

Antes de sacar cualquier conclusión hicimos un diagnóstico riguroso de los datos, y encontramos
algo clave: ambas fuentes tienen exactamente 1.000 títulos por año, sin excepción. Eso no es el
catálogo real: es una muestra estratificada, así que nunca vamos a decir que el catálogo
"creció", porque el diseño del muestreo lo impide. También corregimos calificaciones en cero que
en realidad eran ausencia de votos, columnas redundantes, y armonizamos las taxonomías de género
entre ambos formatos.

## Diapositiva 5 — Contexto 1/2 (~25 s)

Partimos por entender la composición del catálogo. Drama y Comedia concentran la oferta, tanto
en películas como en series: es una apuesta bastante concentrada en géneros masivos.

## Diapositiva 6 — Contexto 2/2 (~25 s)

Y en cuanto a calidad, la noticia es buena: mejora sostenidamente año a año en ambos formatos.
No hay, a priori, un problema de calidad del contenido.

## Diapositiva 7 — Tensión (~35 s)

Pero aquí aparece la primera tensión del relato: la atención de la audiencia no se reparte
parejo, se concentra en muy pocos títulos. El título más popular supera 291 veces al título
mediano, y solo 320 títulos superan el percentil 99. La inmensa mayoría del catálogo vive con
una exposición marginal.

## Diapositiva 8 — El giro · Hallazgo central (~45 s)

Y acá viene el giro de toda nuestra narrativa: si la atención se concentra en pocos títulos, uno
esperaría que al menos esos títulos sean los mejor evaluados. No es así. Calculamos la
correlación entre popularidad y calificación por separado en cada formato, porque el índice de
popularidad no es comparable entre películas y series. El resultado: 0,09 en películas, 0,01 en
series. Prácticamente cero. Saber que un título es popular no nos dice nada sobre si es bueno.
Esto divide el catálogo en cuatro cuadrantes de decisión.

**Si preguntan por qué se calculó por separado:** porque la mediana de popularidad de las series
(47,6) cuadruplica la de las películas (11,4) — son escalas distintas y agregarlas produciría un
corte que separa formato, no visibilidad.

## Diapositiva 9 — Consecuencia operativa (~40 s)

Esos cuatro cuadrantes son accionables: los éxitos consolidados, 4.438 títulos, hay que
protegerlos. Los populares mal evaluados, 3.262 títulos, hay que vigilarlos porque generan
tráfico pero erosionan la percepción de calidad. Los de bajo rendimiento son candidatos a
depuración. Y el cuadrante que más nos importa: calidad sin visibilidad, 3.222 títulos. Es
contenido que la audiencia valora, pero que hoy no está encontrando. Ese va a ser el corazón de
nuestra propuesta comercial.

## Diapositiva 10 — Oportunidad de género (~30 s)

Si miramos por género, el patrón se repite: los géneros mejor evaluados —documental, infantil,
musical— son justamente los menos representados en el catálogo. En el extremo opuesto, terror y
suspenso concentran casi 6.000 títulos con las peores calificaciones.

## Diapositiva 11 — Oportunidad de mercado (~30 s)

Lo mismo pasa con los mercados de origen. El inglés concentra casi la mitad del catálogo
calificado, un 47%, pero ocupa el lugar 10 de 12 en calificación promedio. Hay mercados como el
japonés o el chino que rinden mejor y están subrepresentados.

## Diapositiva 12 — Riesgo comercial (~35 s)

En lo financiero encontramos algo contraintuitivo: la tasa de éxito comercial efectivamente
crece con la escala de inversión, pero el peor desempeño no está en las apuestas chicas, está en
el tramo medio de presupuesto: solo 56,2% de éxito, por debajo incluso del tramo bajo. Y es
justamente donde se concentra el mayor número de películas, 1.632.

## Diapositiva 13 — La herramienta (~35 s)

Todo este análisis lo hicimos explorable en un dashboard interactivo, construido en Python con
Plotly. Tiene KPIs que se recalculan en vivo, cinco filtros cruzados, cuatro pestañas de
navegación e interacción completa. Lo construimos en HTML autocontenido a propósito: para que
cualquier persona en la organización lo pueda abrir sin instalar nada.

## Diapositiva 14 — Evaluación crítica (~35 s)

Somos igual de rigurosos con nuestras propias limitaciones. La principal: no tenemos datos de
comportamiento real de usuarios, ni reproducciones, ni suscripciones, ni cancelaciones. Usamos
popularidad como aproximación de atención, pero no podemos medir retención real. Eso condiciona
cómo hay que leer nuestras recomendaciones.

## Diapositiva 15 — Tres palancas comerciales (~30 s)

A partir de estos hallazgos proponemos tres palancas comerciales concretas, ninguna basada en
variables financieras: Joyas Ocultas, Momentum por Género, y Series como Ancla de suscripción.
Cada una con su mecanismo de atracción, de retención, y su KPI.

## Diapositiva 16 — Programa Joyas Ocultas (~40 s)

Nos detenemos en la primera porque es la más importante: Programa Joyas Ocultas. Son 3.222
títulos que ya están en el catálogo, ya pagados, con calificaciones de 7,03 en películas y 7,99
en series, por encima del resto del catálogo. La propuesta es simple: exponerlos mejor en el
descubrimiento, con una fila editorial dedicada. El costo de adquisición de contenido es cero.
La palanca es exposición, no compra.

## Diapositiva 17 — Recomendaciones (~30 s)

Cerramos con cinco recomendaciones priorizadas por costo de implementación: desde activar la
calidad sin visibilidad —costo marginal cero— hasta incorporar datos de usuario a futuro, que es
la recomendación de mayor alcance pero también la de mayor inversión.

## Diapositiva 18 — Cierre (~25 s)

Y la conclusión que queremos dejarles es esta: StreamView Analytics no tiene un problema de
catálogo, tiene un problema de visibilidad. El contenido que su audiencia mejor valora ya está
comprado. Solo no se está mostrando. Muchas gracias, quedamos atentos a sus preguntas.

---

## Notas de producción

- Este mismo texto está cargado como **notas del orador** en `presentacion_ejecutiva.pptx`
  (Vista → Notas, o Vista de moderador al proyectar). Puedes practicar desde aquí o directamente
  desde PowerPoint.
- Los tiempos son orientativos: practica en voz alta con cronómetro al menos dos veces antes de
  la defensa, y ajusta el ritmo de las diapositivas 8, 9 y 16 (las más densas en contenido).
- Si el docente interrumpe con una pregunta a mitad de la exposición, no te desordenes: responde
  breve y retoma la frase siguiente del guion donde ibas.
