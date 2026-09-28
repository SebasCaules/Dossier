# Hoja de consulta: doce estructuras de datos

Una hoja A4 para imprimir con el costo de buscar, insertar, borrar y recorrer en orden en
doce estructuras de datos (promedio, peor caso y amortizado), cuándo conviene cada una, un
mapa de cómo se relacionan y un gráfico de alturas con un millón de claves.

Se generó con:

```
/dossier 1 hoja impresion -texto items=12
Una hoja de consulta para imprimir: el costo de las operaciones (buscar, insertar, borrar,
recorrer en orden) en doce estructuras de datos, con cuándo conviene cada una.
```

## Regenerar

Desde esta carpeta:

```
python3 graficos.py              # rehace fig/f1_alturas.pdf e imprime los valores
python3 ~/.claude/skills/dossier/scripts/medir.py hoja-estructuras-de-datos.tex --paginas 1 --paginas-texto 0.3 --parte-texto 0.3 --densa 400 --visuales-min 1
```

`medir.py` compila (los auxiliares van a `_build/`) y controla el largo, el texto y las
piezas visuales del perfil. Sin la skill instalada basta con
`latexmk -lualatex hoja-estructuras-de-datos.tex`.

## Fuentes

- **CLRS**: Cormen, Leiserson, Rivest y Stein, *Introduction to Algorithms*, 4.ª ed., MIT
  Press, 2022. En la hoja, el número es el capítulo (6 montículos, 10 listas, 11 hash,
  12 ABB, 13 rojo-negro, 16 análisis amortizado, 18 árboles B).
- **SW**: Sedgewick y Wayne, *Algorithms*, 4.ª ed., Addison-Wesley, 2011, y su sitio
  (algs4.cs.princeton.edu). El número es la sección (3.1 búsqueda binaria, 3.2 ABB,
  3.4 hash).
- **W**: Wikipedia en inglés, artículos *Dynamic array*, *AVL tree*, *Splay tree*,
  *Skip list*, *Binary heap* y *Red–black tree*, consultados el 28/09/2026.
- El gráfico es un cálculo propio en `graficos.py` con las cotas de CLRS 12, 13 y 18 y la
  recurrencia del AVL de Wikipedia.
- Las fuentes no coinciden en un punto: para borrar en un ABB, CLRS y Wikipedia dan
  O(log n) en promedio; la tabla resumen de SW da O(√n) tras muchas altas y bajas al azar.
  La hoja sigue a CLRS y lo anota con †.
- Quedaron afuera, por el tope de doce: trie, montículo de Fibonacci, árbol 2-3 y cola
  doble. Paleta: la de `dossier.sty`.
