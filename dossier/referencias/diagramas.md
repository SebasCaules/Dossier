# Diagramas de relaciones

Un diagrama se gana el lugar cuando muestra una relación que el texto tendría que contar
en un párrafo: qué causa qué, qué va antes, qué pertenece a qué, qué no se mezcla con qué.
Si solo pone una lista dentro de cajas, es una tabla o una lista.

## Qué diagrama para qué relación

| La relación | El diagrama | Con |
|---|---|---|
| etapas en orden, sin ramas | proceso | `\proceso` |
| fechas y dónde estamos | línea de tiempo | `\hitos` |
| pasos con ramas (sí o no, qué pasa si falta algo) | árbol de decisión | `cajag` + `flecha`, sí y no como nodos aparte |
| pasos que vuelven atrás | flujo de cajas y flechas | `cajag` + `flecha` |
| dos mundos que no se mezclan (entrenamiento y test, cliente y banco, antes y después) | carriles | `\carril` + cajas blancas |
| el mismo flujo en varias corridas (el camino feliz y dos variantes) | carriles, uno por corrida, con los pasos como fichas o cajas según su estado | `\carril` + `\fichas` o cajas |
| la arquitectura de un sistema | carriles por zona (pública y privada, cliente y proveedor); cada flecha que cruza lleva lo que cruza, y el pie dice lo que no cruza | `\carril` + cajas blancas + `relacion` |
| un mecanismo en el tiempo (una tasa por tramos, una cola que crece) | esquema sin valores en los ejes, con alturas neutras y un pie que empieza con «Esquema»; si el texto dice que algo está acotado, se dibuja la cota | TikZ con rellenos y un trazo |
| qué pertenece a qué (variables en familias, leyes en grupos) | grupos con fichas | nodo `grupo` + `\grupo{…}` |
| muchos a uno (predictoras y objetivo, causas y efecto) | grupos o conceptos unidos por un bus | estilo `bus` |
| cómo se conectan ideas, con un verbo (causa, evita, requiere, es parte de) | mapa conceptual | `concepto`, `concepto central`, `rel` + `relacion` |
| dos dimensiones a la vez (costo y valor, sesgo y varianza) | matriz de 2 × 2 | cuatro `cajag` con rótulos `etiqueta`; la celda vacía, punteada |

El código de cada uno está en `componentes.md`: «Diagramas de relaciones» (grupos,
carriles, mapa conceptual, árbol de decisión, matriz) y «Dos columnas» (un esquema en el
tiempo).

## Reglas

1. **El diagrama dice el mensaje de la sección.** Antes de dibujar, escribir en una
   oración qué tiene que verse («solo `km_reales` se sabe después de entregar»). El
   diagrama lo pone en el espacio (una línea que separa, un carril, un borde), no solo en
   el texto de una caja.
2. **Cada relación tiene nombre.** En un mapa conceptual, cada flecha lleva un verbo:
   causa, evita, requiere, es parte de. Una flecha sin verbo dice que algo pasa, no qué.
   Y el verbo es algo que el texto dice: un mapa que afirma «decide igual que» sin que
   ninguna sección lo explique enseña una relación que el documento no sostiene.
3. **Pocas piezas.** Hasta 7 nodos, 9 como mucho. Con más, agrupar en fichas o partir en
   dos diagramas. La excepción es un mapa de familias con nodos de una o dos palabras
   (distribuciones, tipos de contrato): 10 a 12 nodos en una grilla, con una leyenda de
   tipos de flecha en el pie («llena: se obtiene de; punteada: la aproxima»). Partirlo
   cortaría el puente que el mapa tiene que mostrar.
4. **Una sola dirección, sin cruces.** De izquierda a derecha o de arriba abajo. Ninguna
   flecha cruza otra ni atraviesa un nodo; si pasa, cambiar el orden o pasar a capas
   (causas en una fila, prácticas en otra, el efecto abajo).
5. **Un solo destacado.** El acento marca lo único que el lector tiene que ver; el resto
   va en gris.
6. **El pie nombra los colores como se ven en el PDF final.** Con la paleta por defecto,
   `acento` es azul oscuro, `acento2` terracota, `suave` celeste, `suave2` rosa claro y
   `fondo` gris claro. Si el documento adopta los colores de un proyecto, mirar el valor
   que quedó (con una paleta propia, `acento` puede ser bordó y `acento2`, ocre). En los
   gráficos, `SERIES` es azul, naranja, verde, amarillo, rosa, verde oscuro, violeta y rojo. Un pie
   que dice «naranja» debajo de un terracota confunde.
7. **Texto corto en los nodos.** Unas 60 palabras por diagrama en total, contando los
   rótulos de flechas y carriles: con 7 nodos, unas 6 por nodo. Un nodo con más de 12 es
   texto en una caja; `medir.py` avisa por cada uno (salvo los grupos con fichas) y por
   cada diagrama que pasa de 60. El mapa del tema no entra en esa cuenta.
8. **Títulos alineados.** Cajas vecinas con el mismo alto (`\grupo[alto]` o `\arriba`;
   `minimum height` centra el contenido y no alinea los títulos). Si el contenido no entra
   en ese alto, la caja crece y `medir.py` lo marca.
9. **Muchos a uno, con bus.** En lugar de una flecha diagonal desde cada caja: una línea
   corta desde cada una, una horizontal que las junta y una sola flecha al destino.
10. **La condición va con la ficha.** Si acortar una ficha le quita la condición que la
    hace verdadera, la condición va en la ficha o la ficha va aparte con su rótulo. Si un
    grupo dice «todos responden por el total» y uno de ellos solo responde por una parte,
    la ficha afirma algo falso: ese va aparte, con su condición («proveedor: solo por su
    tramo»).
11. **En papel, una categoría no se marca solo con un relleno claro.** Con `impresion`,
    `fondo` y blanco casi no se distinguen (1,1:1): sumar un borde, un trazo punteado o
    el nombre del grupo, y decirlo en el pie.
12. **Una pieza no repite a otra.** Si un árbol resume dos tablas, va el árbol o van las
    tablas. Una elección repetida en dos tablas y en un árbol llegó a ocupar unos ¾ de
    página de un documento de cinco.

## Lo que no va como imagen

- **Una página de otro documento** (el enunciado, un apunte, un paper): es texto metido
  como foto, ilegible al tamaño de una figura. `medir.py` la marca como problema y no la
  cuenta como pieza visual. Si el documento necesita lo que dice esa página, se resume con
  palabras propias y la fuente al lado.
- **Una lista de ítems en cajas sin relación entre ellas**: va como tabla o como lista.
- **Un diagrama decorativo para llegar al mínimo de imágenes.** El mínimo del perfil se
  completa con material real o no se completa, y se dice en el reporte.

Una captura sí vale cuando muestra algo que el documento no puede redibujar: una
interfaz, un tablero, una figura original de la fuente.

## Un caso, antes y después

Un resumen de un proyecto de predicción tenía dos diagramas que eran listas en cajas:

- **Variables del dataset**: cuatro cajas con los nombres separados por comas y
  flechas diagonales a `y`. El mensaje («solo `km_reales` se sabe después de entregar»)
  estaba en una palabra en rojo y en un pie que decía «naranja». **Después**: cada
  familia es un grupo con fichas, `km_reales` va sola del otro lado de una línea
  «momento de predecir», y un bus junta todo en `y`.
- **Recorrido sin fuga**: una cadena de cajas con una línea punteada «test: no se toca»
  que bajaba y doblaba. **Después**: dos carriles, entrenamiento y test; el test entra
  apartado a la izquierda y solo toca la evaluación final. Que nada cruza de un carril al
  otro se ve sin leer.

Además, el documento pegaba la foto de la página 1 del enunciado. Ahora `medir.py` la
marca y la descuenta de las piezas visuales.
