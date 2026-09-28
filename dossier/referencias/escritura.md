# Escribir corto

Quien lee un dossier lo lee para entender algo o decidir algo. Cada oración tiene que
ganarse el lugar: si al sacarla el lector no pierde nada, sobra. Eso vale con cualquier
nivel de texto: `+texto` es más explicación, no más palabras.

## Estructura

- **Primero la respuesta.** Cada sección abre con lo que el título promete; las razones y
  el detalle van después. Si el lector deja de leer en la primera oración, igual se lleva
  lo principal.
- **Títulos que dicen el mensaje.** «Quitar duplicados mueve poco la cifra; la fecha
  la mueve mucho» dice más que «Resultados». También sirven las preguntas concretas: «Qué
  se entregó en el segundo avance», «El modelo: qué construir».
- **La página 1 cuenta todo.** Tres a cinco párrafos, cada uno con un rótulo en negrita y
  dos a cuatro oraciones: qué pasó, qué cambió, qué sigue. Quien solo lee la portada tiene
  que poder actuar. En una hoja, el resumen lleva tres párrafos; con `-texto`, tres
  viñetas.
- **Una página, un mensaje.** Si una sección necesita dos páginas, probablemente son dos
  mensajes.
- **Una pieza no repite a otra.** Si un árbol resume dos tablas, va el árbol o van las
  tablas; si el texto ya define un término con su fuente, el glosario no lo repite.

## Oraciones

- Hasta ~25 palabras, una idea, sujeto y verbo explícitos, voz activa.
- Cifras concretas con unidad y fuente: «sube de 27,3 % a 28,1 % \fuente{R14}», no
  «aumenta levemente».
- Redondear a lo que importa: 28,1 %, no 28,0871 %.
- Sin frases de relleno: «es importante destacar», «cabe mencionar», «en este documento
  se presenta», «a continuación», «como se puede observar», «en conclusión».
- Sin adjetivos que no informan («robusto», «integral», «clave», «significativo» sin cifra).
- Sin tríadas balanceadas ni paralelismos perfectos: suenan a relleno.
- El texto no repite lo que la figura ya muestra; dice qué significa.
- Registro neutro. Hay coloquialismos que pasan la guarda de voseo y siguen siendo
  coloquiales: «acá» → «aquí», «chequear» → «verificar», «se come 200 ms» → «consume
  200 ms», «pegarle a una API» → «llamar a una API».

**Antes:** «Es importante destacar que, como se puede observar en el gráfico, la tasa de
tickets atrasados presenta un aumento significativo luego de aplicar las decisiones de
calidad, lo cual resulta clave para el análisis.» (36 palabras)

**Después:** «Quitar duplicados sube el atraso de 27,3 % a 28,1 % \fuente{R14}. El cambio grande
viene de la fecha de medición.» (19 palabras, y dice más)

## Viñetas

- Rótulo en negrita más una oración: **Tickets duplicados.** 540 registros son 251
  pedidos.
- Tres a cinco por lista. Si todas tienen la misma forma (qué, cuánto, fuente), es una
  tabla.

## Pies de figura

Dicen primero qué se tiene que llevar el lector y después cómo leerlo, en una o dos
oraciones: «Quitar duplicados mueve poco la cifra; la fecha la mueve mucho. Rayado: medido
al 31/01/2026, antes del cambio de turnos». Nunca «Gráfico de barras de
la variable X».

Describir la disposición no alcanza. **Antes:** «Arriba, en milisegundos; abajo, el
control». **Después:** «El precio se calcula sin el nombre: la entrada segura lo cambia
por un seudónimo y el nombre real queda aparte». Cada destacado de la pieza (un color, un
borde, un rayado) se explica en el pie, y las cifras del pie son las de la figura.

## Cifras, definiciones y propuestas

- Cada cifra lleva `\fuente{...}` con su origen. Si no tiene origen, no va.
- Con archivos de nombre largo («prueba-de-hipotesis-para-la-proporcion»), `\fuente`
  lleva una sigla corta (`W-prop`, `G9·17`), y la equivalencia va en el README o en la
  lista de `referencias`. Un nombre largo ocupa medio renglón y, como `\fuente` no se
  corta en los guiones, puede salirse de una columna angosta.
- Las definiciones se copian del glosario, anexo o registro del proyecto.
- Lo que no está decidido se rotula como propuesta.
- **Fuentes que se contradicen.** Se sigue la más reciente o la que se declara corrección
  del material viejo, y el texto lo dice citando las dos: «15 días durante el período de
  prueba (hoy 6 meses; el material viejo dice 3)». Si el documento marca un valor como
  cambiado, se revisan las cifras que dependen de él: un plazo que pasa de 3 a 6 meses en
  el texto deja mal a la regla que dependía de él si esta sigue diciendo «con menos de 3
  meses».

## Según el parámetro texto

| | `-texto` | normal | `+texto` |
|---|---|---|---|
| Prosa, sobre el total de páginas | hasta 25 % | hasta 40 % | 40 a 60 % |
| Párrafo | hasta 2 oraciones | 2 a 4 | 3 a 6, con un porqué o un ejemplo |
| Página con una figura | 150 a 250 palabras | 250 a 450 | 400 a 600 |
| Qué carga el contenido | viñetas, pies, tablas y cifras | texto y piezas visuales a la par | el texto, con piezas visuales que lo ilustran |
| Portada | resumen en 3 viñetas | 3 a 5 párrafos con rótulo | 4 a 6 párrafos con rótulo |

- **`-texto`** no es telegráfico: cada viñeta sigue siendo una oración con sujeto y verbo.
  Lo que se va primero son las transiciones y los porqués obvios.
- **`+texto`** agrega lo que el lector necesita para entender sin la fuente al lado: el
  porqué de cada decisión, un ejemplo concreto, el error típico, la excepción. Si una
  oración nueva no cumple ninguna de esas funciones, es relleno.

## Con lector=estudio

- **La tríada, en los conceptos centrales.** Los 2 a 4 conceptos centrales de cada
  familia llevan la definición copiada de la fuente, un ejemplo y la confusión típica
  (patrón en `componentes.md`, «Conceptos centrales»); el resto va en una línea o en el
  glosario. No entra una tríada por concepto.
- **La confusión típica es un error que la fuente señala**: un ejercicio corregido, un
  «error común» del apunte, una trampa del parcial. No es «el error más común» ni «el que
  más se repite» si la fuente no lo cuenta: una fuente que dice «aquí hay un error común»
  no autoriza un superlativo.
- **Cada condición de uso lleva su umbral**, el que da la fuente: «$n$ grande» sin número
  no informa; «$n$ mayor que 200 \fuente{W-media}» sí.
- **Lo que la portada muestra, se responde.** Cada pregunta que la portada pone a la vista
  (un ranking de preguntas de examen, una caja del mapa del tema) se responde en el texto
  o en un repaso; si no entra, sale de la portada.
- **Repaso al cierre de cada sección**, con el entorno `repaso`: 3 a 5 preguntas cuya
  respuesta está en el texto. En una hoja, al final.

## Presupuesto de largo

Una página A4 llena de prosa (10 pt, márgenes de `dossier.sty`) lleva ~800 palabras; la
portada completa (cifras, resumen, aviso, índice), de 350 a 500. Los topes de cada perfil
salen de `perfil.py` y los controla `medir.py`, que cuenta como prosa también las tablas,
los pies, los avisos, el repaso, el glosario y las notas de `\cifra`, y da el desglose por
bloque en cada vuelta. En una hoja sin `items`, `perfil.py` da además un reparto
orientativo del tope (portada y resumen, tabla, avisos y pies).

Para recortar, en este orden: lo que repite a una figura, una pieza que repite a otra
(una tabla que ya resume un árbol, un glosario que repite definiciones del texto), los
calificativos, los párrafos que no cambian ninguna decisión.

## Correcciones

- **Precisar es cambiar palabras, no agregar párrafos.** La precisión entra en la frase
  que ya existe. Una observación que pedía precisar un párrafo terminó en cinco párrafos
  con tono de paper, y hubo que deshacerlo.
- **«Más corto» es menos texto**, no menos figuras.
