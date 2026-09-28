# Problemas conocidos

Cada uno ya costó tiempo en algún proyecto. Síntoma, causa y arreglo.

## Compilación

- **`dossier.sty` pide LuaLaTeX.** Con `pdflatex` o `xelatex` se detiene a propósito:
  usa `fontspec` y las fuentes del sistema. Compilar con `medir.py` o `latexmk -lualatex`.
- **Un carácter sale en blanco.** El log dice `Missing character: There is no → ...` y
  `medir.py` lo marca. Avenir Next (la letra en macOS) no tiene flechas (→ ↗ ↑):
  usar `$\rightarrow$`, `$\nearrow$`, o `{\ttfamily →}` (Menlo sí las tiene); en otros
  sistemas, mirar el log, porque depende de la letra que quedó.
- **El índice no aparece o da error.** `\indice` abre el archivo `.toc`; no combinarlo con
  `\tableofcontents` ni usarlo dos veces. Necesita dos pasadas (latexmk las hace solo).
- **Aviso de `caption` sobre `\setcaptiontype`.** Es un `\captionof` suelto. Usar
  `\figura`, `\captura` o el entorno `bloque`, que ponen la pieza y su pie en una caja.
- **Una celda de tabla empieza con una línea vacía.** Un `\color` al principio de una
  columna `p{}`; anteponer `\leavevmode` (`\fuente` ya lo hace).
- **Fuera de macOS no hay Avenir Next ni Menlo.** `dossier.sty` pasa a Helvetica Neue o
  TeX Gyre Heros y a Fira Mono (con negrita, que Latin Modern Mono no tiene), y
  `estilo_graficos.py` a DejaVu Sans. Sin Fira Math (viene con TeX Live
  completo), las fórmulas pasan a Latin Modern, con serifa. El documento compila igual;
  la letra cambia.
- **Desaparece un `~` o se corta el texto en un `%`.** En LaTeX, `~` es un espacio duro
  y `%` abre un comentario. Escribir `\textasciitilde`, `\%`, `\&`, `\#` y `\_`; para
  «aproximadamente», «unos». `medir.py` avisa un `~` antes de un número. Un `%` dentro de
  un pie o de otro argumento se come el resto y el log dice «File ended while scanning».
  El contexto de `\portada` sale en mayúsculas: no poner rutas ahí.
- **Dos porcentajes escritos distinto salen iguales.** babel en español pone un espacio
  fino antes de `\%` y absorbe el que se escriba antes. Para un `%` pegado a propósito
  (por ejemplo, para mostrar un formato inconsistente), `{\char37}`.
- **«Missing number» en un nodo TikZ.** `font=\scriptsize\hyphenpenalty=10000` sin llaves;
  va `font={...}`, o un estilo de `dossier.sty` (`caja`, `cajag`, `etiqueta`, `concepto`),
  que ya no parten palabras.
- **Un extracto de código renumerado desde 1, con caracteres de otras líneas.**
  `\lstinputlisting[linerange=…]` con LuaLaTeX pierde los números de línea reales y deja
  pasar caracteres de las líneas salteadas (por ejemplo, un «—» de un docstring y un
  `Missing character` por un emoji de una línea fuera del rango). Copiar los tramos en el
  `.tex`, cada uno en `\begin{codigo}[firstnumber=N]` (`componentes.md`, «Código»).

## Maquetación

- **Un marcador o un enlace lleva a la página anterior a su título.** Pasaba con las
  secciones y subsecciones que abren página: titlesec ponía el ancla antes del salto.
  `dossier.sty` pone `\phantomsection` en los dos títulos (en las subsecciones desde la
  0.2, en las secciones desde la 0.4); en un documento anterior, copiar el `dossier.sty`
  nuevo.
- **Un título solo al pie de la página.** Pasaba con `\anexo` seguido del glosario, que es
  un `multicols`; `\anexo` ya reserva lugar con `\needspace`. Para otro caso, anteponer
  `\needspace{8\baselineskip}` al título.
- **Un título se va a la página siguiente con el bloque que lo sigue.** Un título seguido
  de un `bloque`, una `\figura` o una tabla que no entra no se separa de ellos: se van
  juntos y queda el blanco. Con un párrafo corto en el medio, TeX a veces se lleva también
  el párrafo (el título de un anexo y su párrafo se fueron con un árbol y dejaron un
  25 % en blanco) y a veces deja el título y el párrafo solos al pie (para eso,
  `\needspace` antes del título: `componentes.md`, «Tablas»). Achicar la pieza los
  centímetros que faltan (la `Nota:` de `medir.py` dice cuántos quedan libres) o mover un
  párrafo antes.
- **`\needspace` antes de una caja la manda a la página siguiente aunque entre.** Delante
  de un `tcolorbox` (`repaso`, `cifras`) o después de un `\ojo` o un `\nota`, no es
  confiable: quedaban 194 pt, se pedían 104, y el repaso saltó y dejó un 27 %
  en blanco. Sirve antes de un título; para una caja, mover un párrafo o achicar la pieza.
- **Un hueco grande en el medio de la página.** Un `\vfill` que empuja una pieza al pie
  cuando el contenido de arriba no llena la página. `medir.py` avisa desde el 20 % (la
  zona de notas al pie, que con `impresion` lleva las direcciones de `\enlace`, no cuenta
  como hueco).

- **Una tabla cortada o empujada a la página siguiente.** `tabularx` no se parte entre
  páginas. Si pasa de media página, dividirla en dos tablas. Si la anuncia una oración
  («la tabla las define:»), la oración va como pie del `bloque` de la tabla: si no, queda
  sola al pie de la página anterior (`medir.py` avisa la página que termina en «:»).
- **Un bloque deja media página en blanco.** `\figura`, `\captura` y `bloque` no se
  parten: si no entran, saltan enteros. Achicar la pieza, mover un párrafo antes o
  aceptar el blanco si la página siguiente empieza sección.
- **Una fórmula alta toca la fila de arriba en una tabla.** `\dfrac` o `\dbinom` en una
  fila, y `\arraystretch` no alcanza. `\\[2pt]` no suma espacio si la fila tiene celdas
  `p{}` de varios renglones: poner `\addlinespace[2.5pt]` después de la fila.
- **Una fórmula se parte entre renglones en una celda.** Envolverla en `\mbox{$…$}` y
  ensanchar la columna hasta que `medir.py` no marque desborde. babel en español escribe
  «máx», «mín» y «lím», más anchos que en inglés: una columna que alcanzaba puede dejar
  de alcanzar.
- **Un identificador en `\texttt` se sale del margen.** La letra mono no se corta con
  guion: un nombre largo («PlanificadorPorPrioridades») se salió unos 30 pt. Usar
  `\cod{…}`, que se corta después de `_ . / -`; si el nombre no tiene ninguno de esos
  caracteres, reformular la oración.
- **Etiquetas que se pisan en un gráfico.** Pasa con valores cercanos (27,3 y 28,1) y con
  curvas que convergen. Usar barras desde cero con el valor al final (`barras_h`) o una
  leyenda.
- **Rótulos que se pisan en un gráfico de funciones.** Curvas que convergen en el centro
  dejan poco lugar, dos cortes cercanos (1,645 y 1,96) no admiten rótulos a los dos lados
  y las líneas guía cruzan otros rótulos. Las curvas se nombran en la leyenda, arriba a la
  izquierda (`densidad(..., rotulo=...)`); los rótulos de corte van del lado libre y
  escalonados (`corte(..., nivel=1)`); los de áreas, pegados al área y sin línea guía
  (`sombrear(..., rotulo=...)`).
- **Un diagrama más ancho que el texto.** `medir.py` lo marca como texto que se sale del
  margen, con las líneas donde termina el `bloque` o la figura (TeX no sabe decir qué nodo
  desborda). Hacer la cuenta: `n × (text width + 0,42 cm) + separaciones ≤ 17,4 cm` con
  `cajag`. Achicar los `text width` de las cajas o pasar a dos filas.
- **Un diagrama corrido unos milímetros del margen.** `bloque` centra el dibujo; si es
  apenas más angosto que el texto, se nota. Un trazo invisible `\path (0,0) (17.4,0);`
  lo lleva al ancho completo.
- **Rótulos de un diagrama cortados con guion** («determi-nado»). Pasa con `text width`
  y la división de palabras de TeX. Usar el estilo `etiqueta` o las cajas de
  `dossier.sty`. Hasta la 0.3, un `font=` propio sobre esas cajas volvía a partir
  palabras; desde la 0.4, no.
- **Títulos de cajas vecinas a distinta altura.** `minimum height` centra el contenido en
  vertical: la caja con un renglón menos deja su título más abajo. Usar
  `\arriba{alto}{ancho}{…}` con el mismo alto en todas (`componentes.md`, «Diagrama de
  cajas y flechas»).
- **El título de un `\grupo` se sale del margen.** No se parte en dos renglones: a
  `\footnotesize` en negrita entran unas 19 letras en 2,85 cm, y «Distribución y
  franquicia» (3,15 cm) se salió 8,7 pt. Acortarlo o ensanchar el grupo.
- **Los colores del gráfico no pasan el validador de dataviz.** Los de `dossier.sty` son
  para el documento. Para distinguir categorías, `SERIES` de `estilo_graficos.py`.
- **Todo el gráfico sale en negrita.** matplotlib lee solo la primera cara de
  `Avenir Next.ttc`, que es la Bold. `estilo_graficos.py` extrae la Regular, la Demi Bold
  y la Italic; no registrar el `.ttc` a mano.

- **La foto de una página de texto como figura.** Pasó en un resumen: la página 1 del
  enunciado, pegada para sumar imágenes. `medir.py` la marca (proporción de
  hoja y renglones) y la descuenta; se quita y lo que decía se resume con palabras propias.
- **Las fichas de un grupo se salen de la caja.** Con `\grupo[alto]` o `\arriba`, si el
  contenido no entra, la caja crece y el log avisa; `medir.py` lo muestra como problema.
  Subir el alto de toda la fila, para que los títulos sigan alineados.
- **«Missing \endcsname» o «No shape named» en un diagrama.** En `\foreach`, las
  opciones como `[count=\n]` van antes de `in`; las variables no pueden llamarse `\c`,
  `\i`, `\l`, `\o` ni `\p` (son comandos de LaTeX), y los nombres de nodo no llevan
  puntos (`p-5.4` se lee como el nodo `p-5` con el ancla `4`).

## Resuelto en la 0.4

Si un documento hecho con una versión anterior muestra alguno de estos síntomas, copiar
el `dossier.sty` nuevo a su carpeta y compilar de nuevo. Antes, quitar del preámbulo lo
que la 0.4 ya carga o define: `\usepackage{amsmath,amssymb}` (`amssymb` choca con
`unicode-math`: «\eth already defined»), `listings` e `icomma`, y las definiciones propias
de `codigo`, `\cod` o `\columna` (renombrarlas o pasar a los entornos de la 0.4). Si no,
el documento no compila («already defined»). Los síntomas:

- En `\indicelista`, el número de página pegado a un título que llena la línea
  («…es una aspiración3»).
- El título de `\portada` cortado con guion («demostra-ble») o fuera del margen.
- Un `repaso` partido entre dos páginas, con una sola pregunta al pie.
- Pies de una línea centrados y los de dos, a la izquierda.
- `\proceso` sin `[hoy]` con un centímetro en blanco abajo.

## Scripts

- **`SyntaxError` en un script de edición.** En Python, una cadena entre comillas
  simples o dobles (también `r"..."`) no puede ocupar varias líneas; hacen falta comillas
  triples. Escribir los scripts largos a un archivo, no dentro de un heredoc.
- **`UnicodeDecodeError` al leer la salida de LaTeX.** El log y la salida pueden venir
  en latin-1. Decodificar con `errors="replace"` (`medir.py` ya lo hace).
- **Unir PDFs con pypdf deja letras rotas.** Si las páginas comparten `/Resources`,
  `merge_page` renombra fuentes. Dar a cada página su propia copia de `/Resources` antes
  de unir.
- **zsh aborta un comando con `*.pdf` sin coincidencias.** Entrecomillar los globs o
  listar con Python. En macOS no existe `timeout`.

## Entrega

- **El PDF se entregó sin mirarlo y tenía cortes entre páginas.** Pasó en dos proyectos
  seguidos. `revisar.py` y leer cada página antes de entregar.
- **Una cifra no coincide con la fuente.** El crítico del paso 8 la encuentra si se le
  pasan las fuentes; sin fuentes no hay contra qué cotejar.
