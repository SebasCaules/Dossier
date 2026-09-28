# Componentes de `dossier.sty`

Todos compilan tal cual con `lualatex` y el `dossier.sty` de la 0.4. Los colores son los
nombres de la paleta: `tinta`, `rotulo`, `apagado`, `acento`, `acento2`, `suave`,
`suave2`, `fondo`, `linea`.

## Preámbulo

```latex
\documentclass[10pt,a4paper]{article}
\usepackage[spanish,es-noshorthands]{babel}
\usepackage{dossier}                     % para papel: \usepackage[impresion]{dossier}
\documento{Mesa de ayuda · Avance 2}{Avance 2 y lo que sigue}{Equipo de datos}
% Identidad del proyecto: redefinir la paleta después de \usepackage{dossier}.
\definecolor{acento}{HTML}{22456F}
\definecolor{acento2}{HTML}{B8433A}
```

`dossier.sty` ya carga `amsmath`, `unicode-math` con Fira Math (o `amssymb` si no está),
`icomma` y `listings`: el documento no los pide. No cargar `amssymb`: con Fira Math choca
con `unicode-math` («\eth already defined»). `estilo_graficos.py` lee estos mismos
`\definecolor`, así que los gráficos siguen la paleta sin tocarlos.

## Colores del proyecto

Si el proyecto tiene tokens (`estilos.css`, `DESIGN.md`, `tokens.md`), cada uno va al
nombre que cumple su rol:

| Nombre | Rol | Se usa como | Por defecto |
|---|---|---|---|
| `tinta` | texto principal | texto | `#16233A`, 15,7:1 |
| `rotulo`, `apagado` | texto secundario (rótulos, pies, fuentes) | texto chico | `#3D4D66`, 8,6:1; `#5F6779`, 5,7:1 |
| `acento` | color primario: títulos, enlaces, lo destacado | texto y relleno | `#22456F`, 9,8:1 |
| `acento2` | segundo color: números de sección, `\ojo`, «hoy» | texto chico | `#B8433A`, 5,4:1 |
| `suave`, `suave2` | versiones claras (en curso, avisos, fichas) | relleno | |
| `fondo` | superficie de cajas, cifras y paneles | relleno | |
| `linea` | bordes, filetes y lo pendiente | trazo | |

- Los que van como texto necesitan contraste de 4,5:1 o más sobre blanco (en la tabla,
  el de la paleta por defecto). Un acento de marca suele no llegar: un `--accent` de
  4,0:1 no sirve para texto; en `acento2` va su versión para texto, si el proyecto la
  tiene (un `--accent-ink` de 6,3:1).
- Si `fondo`, `suave` y `suave2` casi no se distinguen, las cajas `cajas` y `cajao` se ven
  iguales a `cajag`: el destacado va con borde (`draw=acento2,line width=0.8pt`). En la
  paleta por defecto se separan por 6 a 12 de ΔE; en una paleta crema (`#F3EFE5`,
  `#E9E3D5`, `#F1EADC`), por 3 a 5, y no se ven.
- Con `impresion`, buscar primero la convención de impresión del proyecto (un tema para
  papel, estilos `@media print`) y usar esos tokens.

Para medir el contraste de la paleta del documento, desde su carpeta:

```python
from estilo_graficos import P


def luz(color):
    c = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


for nombre in ("tinta", "rotulo", "apagado", "acento", "acento2"):
    print(nombre, P[nombre], round(1.05 / (luz(P[nombre]) + 0.05), 1))  # sobre blanco
```

## Portada y resumen (página 1)

```latex
\portada{Mesa de ayuda · equipo de datos · avance 2}        % contexto (sale en mayúsculas)
  {Avance 2 y lo que sigue}                                  % título
  {Qué se entregó, qué modelo construir y qué piden los avances 3 y 4}
  {Documento de lectura para el equipo, 12/05/2026. Cada cifra lleva en gris su fuente.}

\hitos[0.46]{0/inicio/02-03/hecho, 0.25/A1/06-04/hecho, 0.5/A2/18-05/pendiente,
             0.75/A3/15-06/pendiente, 1/A4 + final/13-07/pendiente}

\begin{cifras}[4]                       % columnas; 3 o 4
  \cifra{Fuentes perfiladas}{9}{5 dimensiones de calidad}
  \cifra{Decisiones de calidad}{12}{9 cerradas · 3 esperan respuesta}
  \cifra{Fuera de plazo}{28,1\,\%}{de 3.265 tickets \fuente{R14}}
  \cifra{Filas del registro}{21.748}{31 columnas \fuente{R02}}
\end{cifras}

\resumen                                 % «En una página»; \resumen[Otro título]
\textbf{Qué cierra el avance 2.} ...

\ojo[Antes del 18/05]{Lo único urgente.}
\indice                                  % índice corrido (hoja: ninguno; medio y largo: \indicelista)
```

Título y subtítulo van en bandera y sin guiones. La nota de cada `\cifra` (el tercer
argumento) cuenta como prosa. Cifras en la página 1 solo si 3 o 4 números responden la
pregunta del documento; la logística y la configuración no son cifras.

`\vfill` antes de una pieza la ancla al pie de la página; usarlo solo si el hueco que
deja es chico (`medir.py` avisa desde el 20 % de la altura).

`\indice` pone las secciones en una línea corrida; `\indicelista`, en una lista de dos
columnas con el número de página, que es lo que conviene desde siete páginas. Uno solo,
una sola vez. Los dos marcan el destino al que vuelve el título del encabezado. Con la
opción `impresion`, el índice corrido también muestra las páginas. Con `lector=estudio`
en `breve`, el mapa del tema reemplaza al `\indice`: sus cajas son los enlaces.

Una hoja (`largo=hoja`) usa la plantilla `hoja.tex`: `\portada`, cifras,
`\resumen[título que dice el mensaje de la hoja]` con tres párrafos (con `-texto`, tres
viñetas), una pieza visual, un aviso y un `\proceso` al pie, sin índice ni secciones. Con
`items=N`, `nuevo.py` copia `consulta.tex` en su lugar (ver «Hoja de consulta»).

`\hitos[hoy]{pos/nombre/fecha/estado, ...}`: `pos` va de 0 a 1 sobre el ancho; `estado`
es `hecho` (círculo lleno) o `pendiente`; `hoy` es la posición de la marca (se omite con
`\hitos{...}`). Sin espacios alrededor de las barras. Nombres de hasta ~12 caracteres.

## Referencias y datos de entrega (lector=entrega)

```latex
\portada{Sistemas Operativos · primer cuatrimestre de 2026}
  {Planificación de procesos: qué política conviene a cada carga}
  {Cómo elige el núcleo qué correr y qué cuesta cada política}
  {Informe del trabajo práctico. Las siglas en gris remiten a las referencias del final.}
\datosentrega{Sistemas Operativos}{Integrante Uno\\Integrante Dos}{}{Entrega: 10/06/2026}

El enunciado pide comparar tres políticas en un simulador propio \fuente{E, p. 3};
las definiciones siguen la documentación del núcleo Linux \fuente{W}.

\anexo{Referencias}
\begin{referencias}
\referencia{E}{Cátedra de Sistemas Operativos, enunciado del trabajo práctico, 2026.}
\referencia{W}{Documentación del planificador de Linux: \url{https://docs.kernel.org/scheduler/}.}
\end{referencias}
```

- `\datosentrega{materia}{integrantes}{docentes}{fecha}` va debajo de `\portada`. Varios
  nombres, separados por `\\`, con nombre completo. Un campo vacío deja renglones para
  completar a mano: 3 para integrantes, 2 para docentes, 1 para materia y fecha. Lo que
  las fuentes no traen se pregunta en la pregunta del plan; si no hay respuesta, quedan
  los renglones y el reporte lo dice.
- `\referencia{sigla}{texto}`: la etiqueta sale `[E]` y la columna toma el ancho de la
  más larga. En el texto, `\fuente{E, p. 3}` cita la referencia E. `medir.py` avisa cada
  sigla de la lista que ningún `\fuente` cita: se cita donde se usa o se quita.
- La lista es lo que la cátedra puede consultar. La trazabilidad a archivos internos,
  transcripciones y apuntes (diapositiva, línea) va al README.
- Dentro de `referencias`, las direcciones van con `\url{…}` y no con `\enlace` (con
  `impresion`, `\enlace` repetiría la dirección al pie). El cuerpo se lee como argumento:
  sin verbatim, y un `%` o un `#` de una dirección van escapados (`\%`, `\#`).

## Secciones

```latex
\newpage
\section{El modelo: qué construir}\label{sec:modelo}   % sale «05 El modelo: qué construir»
\subsection{Cómo se mide}                              % sin número; entra en los marcadores
\anexo{Glosario}                                       % sin número; entra en el índice
```

Referencia cliqueable con el título de la sección: `\ver{sec:modelo}` → «→ El modelo: qué
construir» (con `impresion`, «→ El modelo: qué construir, p. 6»). Con un título largo,
`\ver[el modelo]{sec:modelo}` → «→ el modelo».

En documentos largos, cada sección cierra con dos líneas que dicen lo esencial:
`\nota[En corto]{...}`. El detalle que no todos van a leer va en `\anexo{...}` al final.

## Texto

Porcentajes: escribir `28,1\%`. babel en español ya pone el espacio fino antes del signo
(y absorbe el que se escriba), así que `28,1\,\%` y `28,1~\%` salen iguales. Para
mostrar un `%` pegado, a propósito, `{\char37}`. Para «aproximadamente», «unos» o
`\textasciitilde`: `~` es un espacio duro y no se ve (`medir.py` avisa `~` antes de un
número).

```latex
\fuente{R14 · R01}                       % origen de una cifra, en gris
\chip{propuesta}                         % rótulo corto dentro del texto
\cod{simulador/planificador.py}          % identificador en letra mono; se corta después de _ . / -
\enlace{https://ejemplo.org/tablero/}{el tablero publicado}   % externo, con ↗ (en papel, la dirección al pie)
\ojo[Alarma]{Un AUC cercano a 1 casi siempre es una variable que mira el futuro.}
\nota[Cómo se midió]{Contexto que ayuda pero no urge.}
```

`\ojo` (filete terracota) es para lo que el lector tiene que hacer o no puede pasar por
alto; `\nota` (filete azul), para contexto. Como mucho uno de cada tipo por página: un
`\ojo[Confusión típica]` y un `\nota[En corto]` pueden compartir página, dos `\ojo` no.

## Figuras y capturas

```latex
\figura{fig/f2_cifras.pdf}{Pie que dice qué se ve y cómo leerlo.}        % tamaño natural
\figura[0.72]{fig/f8_v03.png}{Una imagen de mapa de bits, al 72\% del ancho.}
\captura[0.9]{capturas/03.png}{Pantalla 3: lo que hay que mirar en la captura.}  % con filete
```

No flotan: quedan donde se escriben y nunca se separan de su pie. Los gráficos de
`graficos.py` se dibujan al tamaño final y van sin ancho. Un `%` dentro de un pie abre un
comentario y se come el resto del argumento: `\%`.

Para un diagrama TikZ o una tabla con pie:

```latex
\begin{bloque}[Azul oscuro: hecho. Celeste: A3. Gris: A4 y lo que queda después.]
\proceso[2]{Relevamiento/A1/hecho, Datos y calidad/A2/hecho,
            Modelo/A3/actual, Plan y piloto/A4/futuro}
\end{bloque}

\begin{bloque}[Las cuatro fases del ATAM, en orden; el detalle de cada paso está en la tabla.]
\proceso{Formar el equipo/1/neutro, Pasos 1 a 6/2/neutro, Pasos 7 a 9/3/neutro, Reporte/4/neutro}
\end{bloque}
```

`\proceso[hoy]{texto/etiqueta/estado, ...}`: `estado` es `hecho`, `actual`, `futuro` o
`neutro`; `hoy` es cuántas etapas ya pasaron (2 = la marca entre la segunda y la
tercera). Los tres primeros dicen avance de un proyecto; `neutro` (relleno `fondo`, texto
en `tinta`) es para las etapas de un método, sin avance. Sin `[hoy]`, el dibujo no deja
lugar abajo para la marca. Textos de hasta tres palabras; el detalle va en el pie. Con
más de seis etapas, partir en dos filas o usar TikZ.

## Dos columnas

Una pieza junto a un aviso o una lista, alineadas por arriba, con `columna`:

```latex
\noindent\begin{columna}{0.52\linewidth}
\begin{bloque}[Esquema: cada cambio de tarifa abre un tramo con precio nuevo; al cierre, la factura suma los tramos \fuente{cl. 4}.]
\begin{tikzpicture}
  \fill[fondo] (0,0) rectangle (2.4,1.0);
  \fill[suave] (2.4,0) rectangle (5.0,1.25);
  \fill[fondo] (5.0,0) rectangle (7.4,1.1);
  \draw[tinta,line width=1pt] (0,1.0) -- (2.4,1.0) -- (2.4,1.25) -- (5.0,1.25) -- (5.0,1.1) -- (7.4,1.1);
  \draw[flecha] (0,0) -- (8.0,0);
  \node[etiqueta,anchor=north east] at (8.0,-0.05) {tiempo};
  \foreach \x in {2.4,5.0} \node[etiqueta,anchor=north] at (\x,-0.05) {cambio};
\end{tikzpicture}
\end{bloque}
\end{columna}\hfill
\begin{columna}{0.44\linewidth}
\ojo[De su lado]{\begin{itemize}
\item Enviar la lectura del medidor cada mes \fuente{cl. 5}.
\item Avisar antes de cambiar la potencia contratada \fuente{cl. 8}.
\end{itemize}}
\end{columna}
```

`columna{ancho}` es un `minipage` alineado por arriba, en bandera y con el espacio entre
párrafos del documento. Las dos suman menos que el ancho (0,52 + 0,44): el resto es el
hueco del `\hfill`. Adentro, `\linewidth` es el de la columna: la pieza se dibuja para
ese ancho (0,52 × 17,4 = 9 cm). Un gráfico chico junto a su explicación es el mismo
patrón, con texto en la segunda columna (`doc.tex` lo trae).

Para texto corrido en dos columnas, sin piezas:

```latex
\begin{multicols}{2}\raggedright
\textbf{Las 31 columnas.} ...
\columnbreak
\ojo[Tres cuidados]{...}
\end{multicols}
```

`multicols` reparte el texto como quiere: no sirve para decidir dónde cae una pieza.

## Diagrama de cajas y flechas

```latex
\begin{bloque}[Cómo se armó: de los archivos crudos a los tres productos.]
\begin{tikzpicture}[node distance=6mm and 6mm]
  \node[cajag] (a) {\arriba{1.05cm}{3.2cm}{\textbf{9 archivos CSV}\\tickets, clientes, agentes}};
  \node[cajag,right=of a] (b) {\arriba{1.05cm}{3.2cm}{\textbf{Perfilado}\\mapa 9 × 5}};
  \node[cajag,fill=acento,text=white,right=of b] (c)
    {\arriba{1.05cm}{3.2cm}{\textbf{12 decisiones}\\9 cerradas y 3 que esperan respuesta}};
  \node[cajag,fill=suave,text width=3.2cm,below=8mm of b] (d) {\textbf{Registro v0.1}\\21.748 × 31};
  \draw[flecha] (a) -- (b); \draw[flecha] (b) -- (c);
  \draw[flecha] (c.south) |- (d.east);
\end{tikzpicture}
\end{bloque}
```

Estilos: `caja` (letra chica), `cajag` (letra normal), `cajaa` (relleno de acento, texto
blanco), `cajas` (relleno suave), `cajao` (relleno de aviso), `flecha` y `etiqueta`
(rótulo suelto, sin caja). Ninguno parte palabras con guion, aunque el nodo lleve un
`font=` propio.

- **Ancho.** `cajag` suma 6 pt de cada lado al ancho del texto (0,42 cm en total); `caja`,
  5 pt (0,35 cm). Una fila entra si `n × (text width + 0,42 cm) + separaciones ≤ 17,4 cm`:
  cuatro cajas con 6 mm entre ellas llevan hasta 3,45 cm de texto; cinco, hasta 2,55 cm.
- **Títulos alineados.** Cajas vecinas con distinto número de renglones se centran en
  vertical, y los títulos quedan a distinta altura aunque todas tengan el mismo
  `minimum height`. `\arriba{alto}{ancho}{…}` (en lugar de `text width`) pone el título
  arriba y les da a todas el mismo alto: como en «12 decisiones», que tiene un renglón
  más. A `\footnotesize`, dos renglones piden un alto de 0,65 cm y tres, de 1,05 cm; si no
  alcanza, la caja crece y `medir.py` dice cuánto mide.
- **Una línea.** En una fila de nodos de un renglón, los que tienen letras que bajan
  (p, g) quedan más altos que los demás. El estilo `una linea` les da a todos la misma
  altura: `\node[caja,una linea] {generar\_reporte};`.

Rótulos sueltos: `\node[etiqueta,text width=3cm,align=left] at (0,0) {...};`. En un nodo
sin estilo de `dossier.sty`, la penalidad de guiones va entre llaves:
`font={\scriptsize\hyphenpenalty=10000}`; sin llaves no compila («Missing number»).

`bloque` centra el dibujo. Si un diagrama pensado para el ancho completo queda unos
milímetros más angosto, se ve corrido del margen; para alinearlo, agregar dentro del
`tikzpicture` un trazo invisible de 0 a 17,4 cm: `\path (0,0) (17.4,0);`.

## Diagramas de relaciones

Cuándo usar cada uno y las reglas: `diagramas.md`. Los tres primeros ejemplos son de un
modelo que predice si un envío llega tarde; el árbol y la matriz, de un resumen de derecho.

### Grupos con fichas, una línea que separa y un bus (muchos a uno)

```latex
\begin{bloque}[A la izquierda de la línea, lo que se sabe antes de despachar; \texttt{km\_reales} se sabe después.]
\begin{tikzpicture}
  \node[grupo] (a) at (0,0)     {\grupo[3.2cm]{3.1cm}{Pedido · 7}{monto, peso, bultos, rubro, pago, canal, cuotas}};
  \node[grupo] (c) at (3.65,0)  {\grupo[3.2cm]{2.6cm}{Cliente · 4}{zona, antigüedad, pedidos, reclamos}};
  \node[grupo] (d) at (6.8,0)   {\grupo[3.2cm]{3.2cm}{Clima y calendario · 5}{lluvia\_mm, temperatura, feriado, día\_semana, hora\_pico}};
  \node[grupo] (b) at (10.55,0) {\grupo[3.2cm]{2.75cm}{Depósito · 3}{depósito, turno, stock\_libre}};
  \node[grupo] (e) at (14.45,0) {\grupo[3.2cm]{2.3cm}{El viaje · 1}{!km\_reales}};
  \draw[acento2,dashed,line width=0.9pt] (14.1,0.3) -- (14.1,-3.85);
  \node[font=\scriptsize\bfseries,text=acento2,anchor=south east] at (14.0,0.02) {momento de predecir};
  \coordinate (bus) at (0,-3.95);
  \foreach \g in {a,c,d,b,e} \draw[bus] (\g.south) -- (\g.south |- bus);
  \draw[bus] (a.south |- bus) -- (e.south |- bus);
  \coordinate (medio) at ($(a.south |- bus)!0.5!(e.south |- bus)$);
  \node[concepto central,minimum width=5cm] (y) at ($(medio)+(0,-0.75)$) {$y$: ¿llega tarde?};
  \draw[rel] (medio) -- (y);
\end{tikzpicture}
\end{bloque}
```

- `\grupo[alto]{ancho}{título}{fichas}`: las fichas van separadas por comas; con `!`
  delante, destacada (`!km\_reales`). Con el mismo `alto`, los títulos quedan alineados; si
  un grupo no entra, crece y `medir.py` dice cuánto mide («mide 3.17cm»): subir el alto
  de toda la fila a ese valor. Sin `alto`, cada uno toma el suyo.
- El título no se parte: a `\footnotesize` en negrita, cada letra ocupa ~0,15 cm, así
  que en un grupo de 2,85 cm entran unas 19. «Distribución y franquicia» mide 3,15 cm y
  se sale del margen: acortarlo o ensanchar el grupo.
- Los anchos de los grupos más las separaciones suman el ancho del texto (17,4 cm).
- `\ficha{x}` y `\fichas{x, y}` también sirven sueltas dentro de un nodo o de un párrafo.

### Carriles (dos mundos que no se mezclan)

```latex
\begin{bloque}[El test se aparta primero y no vuelve a tocarse hasta el final.]
\begin{tikzpicture}[node distance=5mm]
  \carril{0}{1.9}{ENTRENAMIENTO}
  \carril{-1.75}{1.45}{TEST}
  \node[cajag,fill=white,text width=2.3cm] (csv) at (1.95,0.1) {\textbf{CSV}\\21.748 filas};
  \node[cajag,fill=white,text width=2.5cm,right=of csv,yshift=0.85cm] (kf) {\textbf{k-fold}\\pipeline ajustado en cada pliegue};
  \node[cajag,fill=white,text width=2.6cm,right=of kf] (cv) {\textbf{Curvas de validación}\\tres modelos};
  \node[cajag,fill=white,text width=2.6cm,right=of cv] (mf) {\textbf{Modelo final}\\con todo el train};
  \node[cajag,fill=white,text width=2.3cm] (te) at (6.0,-1.0) {\textbf{Test apartado}\\20\%, estratificado};
  \node[cajaa,text width=2.4cm] (ev) at (15.9,-1.0) {\textbf{Evaluar una vez}\\desempeño esperado};
  \draw[rel] (csv.east) -- ++(0.35,0) |- (kf.west);
  \draw[rel] (csv.east) -- ++(0.35,0) |- (te.west);
  \draw[rel] (kf) -- (cv); \draw[rel] (cv) -- (mf);
  \draw[rel] (mf.east) -| (ev.north);
  \draw[rel,dashed] (te.east) -- node[relacion,above] {no se usa para decidir nada} (ev.west);
\end{tikzpicture}
\end{bloque}
```

`\carril{y}{alto}{rótulo}` dibuja la franja a todo el ancho, con `y` y `alto` en cm. Las
cajas dentro de un carril van en blanco (`fill=white`) para que se lean sobre el gris.

### Mapa conceptual en capas

```latex
\begin{bloque}[Tres causas de fuga y la práctica que evita cada una. Con borde terracota, la que más pesa.]
\begin{tikzpicture}
  \foreach \x/\practica/\causa/\estilo [count=\n] in {
      -5.4/{Sacarla, o modelar\\con y sin ella}/{\texttt{km\_reales}\\en las variables}/concepto marcado,
      0/{Ajustar dentro de\\cada pliegue}/{Escalar o imputar\\fuera del pipeline}/concepto,
      5.4/{Pliegues por fecha,\\sin barajar}/{Barajar un archivo\\ordenado por fecha}/concepto}{
    \node[concepto,minimum width=3.6cm] (p\n) at (\x,2.6) {\practica};
    \node[\estilo,minimum width=3.6cm] (c\n) at (\x,0.9) {\causa};
    \draw[rel] (p\n) -- node[relacion,right] {evita} (c\n);
    \draw[rel] (c\n.south) -- node[relacion,pos=0.45] {causa} (0,-0.75);
  }
  \node[concepto central,minimum width=4cm] at (0,-1.05) {Fuga de información};
\end{tikzpicture}
\end{bloque}
```

Estilos: `concepto` (borde gris), `concepto central` (relleno de acento), `concepto
marcado` (borde terracota: el único destacado), `rel` (flecha) y `relacion` (el verbo
sobre la flecha, con fondo blanco para que no la tape la línea). En capas (prácticas
arriba, causas en el medio, efecto abajo) ninguna flecha cruza otra; en un mapa radial,
cuidar que ninguna flecha atraviese el concepto central.

En una fila horizontal, el hueco entre dos nodos tiene que ser más ancho que el verbo que
lleva la flecha. A `\scriptsize` en cursiva, «suma de $n$» mide 1,3 cm y «tiempo entre
eventos», 2,5 cm; partido en dos renglones (`align=center` y `\\`), 1,5 cm. Cinco nodos de
2 cm (`minimum width=2cm`) con 1,8 cm entre ellos llenan los 17,4 cm: ahí entra «suma de
$n$» en un renglón, y «tiempo entre eventos» solo en dos.

En `\foreach`, las opciones (`[count=\n]`) van antes de `in`, y las variables no se
llaman `\c`, `\i`, `\l`, `\o` ni `\p`: son comandos de LaTeX y rompen la compilación.
Tampoco van puntos en los nombres de nodo (`p-5.4` se lee como el nodo `p-5` y el ancla
`4`).

### Árbol de decisión (pasos con ramas)

```latex
\begin{bloque}[Qué pasa si falta la forma. En terracota, la trampa más tomada: la donación de un inmueble sin escritura es nula \fuente{arts. 969, 1015, 1018 y 1552 CCyC}.]
\begin{tikzpicture}
  \node[cajag,text width=2.9cm,anchor=west] (q1) at (0,0.35) {\textbf{¿La ley exige una forma?}};
  \node[cajag,text width=3.2cm,anchor=west] (q2) at (4.6,-0.7) {\textbf{¿La exige bajo pena de nulidad?}};
  \node[cajag,text width=5.8cm,anchor=west] (nf) at (9.4,1.4) {\textbf{No formal}\\vale; la forma solo sirve de prueba};
  \node[cajag,fill=suave2,draw=acento2,line width=0.8pt,text width=5.8cm,anchor=west] (ab) at (9.4,0)
    {\textbf{Solemne absoluta}\\nulidad plena: donación de un inmueble};
  \node[cajag,text width=5.8cm,anchor=west] (re) at (9.4,-1.4)
    {\textbf{Solemne relativa}\\obliga a otorgarla: boleto de compraventa};
  \draw[flecha] (q1.east) -- ++(0.5,0) |- (nf.west);
  \draw[flecha] (q1.east) -- ++(0.5,0) |- (q2.west);
  \draw[flecha] (q2.east) -- ++(0.5,0) |- (ab.west);
  \draw[flecha] (q2.east) -- ++(0.5,0) |- (re.west);
  % sí y no: un nodo aparte, sobre el tramo vertical
  \node[relacion] at ($(q1.east)+(0.5,0.55)$) {no};
  \node[relacion] at ($(q1.east)+(0.5,-0.55)$) {sí};
  \node[relacion] at ($(q2.east)+(0.5,0.35)$) {sí};
  \node[relacion] at ($(q2.east)+(0.5,-0.35)$) {no};
\end{tikzpicture}
\end{bloque}
```

- Las preguntas van en `cajag` con el título en negrita; las hojas, en una columna a la
  derecha, con la respuesta en negrita y un ejemplo en el segundo renglón.
- El «sí» y el «no» son nodos aparte, sobre el tramo vertical de la flecha. Puestos sobre
  la flecha con `pos=` en un camino `|-`, caen encima del texto de la caja de destino.
- Hojas de hasta dos renglones, a 1,4 cm entre centros: una caja de dos renglones mide
  1,06 cm de alto y deja 0,34 cm libres. Con tres renglones, 1,8 cm.
- La hoja destacada (la trampa, la respuesta que más se pregunta) va con borde, no solo
  con un relleno claro.

### Matriz de 2 × 2 (dos dimensiones a la vez)

```latex
\begin{bloque}[La celda vacía es la trampa: no existe una SRL de un solo socio. La SAS aparece dos veces porque admite uno o más \fuente{arts. 1 y 146 LGS · art. 40 Ley 27.349}.]
\begin{tikzpicture}
  \node[etiqueta,font=\footnotesize\bfseries,anchor=south] at (6.9,0.85) {Capital en cuotas};
  \node[etiqueta,font=\footnotesize\bfseries,anchor=south] at (13.95,0.85) {Capital en acciones};
  \node[etiqueta,font=\footnotesize\bfseries,text width=3cm,align=left,anchor=west] at (0,0) {Un solo socio};
  \node[etiqueta,font=\footnotesize\bfseries,text width=3cm,align=left,anchor=west] at (0,-1.75) {Dos o más socios};
  \node[draw=acento2,dashed,line width=0.8pt,rounded corners=2pt,minimum width=6.8cm,minimum height=1.5cm,
        align=center,font=\footnotesize,text=acento2] at (6.9,0) {\textbf{Ningún tipo}\\no hay SRL unipersonal};
  \node[cajag,minimum width=6.8cm,minimum height=1.5cm,align=center] at (13.95,0)
    {{\large\bfseries SAU · SAS}\\la SAU queda siempre bajo el art. 299};
  \node[cajag,minimum width=6.8cm,minimum height=1.5cm,align=center] at (6.9,-1.75)
    {{\large\bfseries SRL}\\de 2 a 50 socios};
  \node[cajag,minimum width=6.8cm,minimum height=1.5cm,align=center] at (13.95,-1.75)
    {{\large\bfseries SA · SAS}\\la SA de un solo socio es la SAU};
\end{tikzpicture}
\end{bloque}
```

Los rótulos de fila y de columna van como `etiqueta` en negrita; las cuatro celdas, con
el mismo `minimum width` y `minimum height` (en una matriz, el contenido centrado es lo
que se busca). La celda vacía no se quita: va punteada y dice por qué está vacía. Ancho:
3,5 cm de rótulos más dos celdas de 6,8 cm con 0,25 cm entre ellas.

## Mapa del tema (portada de lector=estudio)

```latex
\begin{bloque}[La base alimenta el método, y el método se juega en el parcial (agrupación propia). El título de cada caja lleva a su sección.]
\begin{tikzpicture}
  % una capa por columna: rótulo arriba, cajas de igual alto, un bus y una flecha con verbo
  \foreach \x/\capa in {0/BASE, 6.52/MÉTODO, 13.04/EL PARCIAL}
    \node[etiqueta,font=\scriptsize\ttfamily,text=rotulo,anchor=south west] at (\x,1.95) {\capa};
  \node[cajag,anchor=west] (m1) at (0,0.65)
    {\arriba{0.65cm}{3.9cm}{\hyperref[sec:fundamentos]{\textbf{01 Fundamentos}}\\lo caro de revertir}};
  \node[cajag,anchor=west] (m2) at (0,-0.65)
    {\arriba{0.65cm}{3.9cm}{\hyperref[sec:atributos]{\textbf{02 Atributos}}\\cada uno con su métrica}};
  \node[cajag,anchor=west] (m3) at (6.52,1.3)
    {\arriba{0.65cm}{3.9cm}{\hyperref[sec:add]{\textbf{03 ADD}}\\decidir por atributo}};
  \node[cajag,anchor=west] (m4) at (6.52,0)
    {\arriba{0.65cm}{3.9cm}{\hyperref[sec:estilos]{\textbf{04 Estilos}}\\según el atributo dominante}};
  \node[cajag,anchor=west] (m5) at (6.52,-1.3)
    {\arriba{0.65cm}{3.9cm}{\hyperref[sec:atam]{\textbf{05 ATAM}}\\evaluar con escenarios}};
  \node[cajag,anchor=west] (m6) at (13.04,0)
    {\arriba{0.65cm}{3.9cm}{\hyperref[sec:parcial]{\textbf{06 Cómo se aprueba}}\\estructura y errores}};
  \draw[bus] (m1.east) -- ++(0.25,0) |- (m2.east);
  \draw[bus] (m3.west) -- ++(-0.25,0) |- (m5.west);  \draw[bus] (m4.west) -- ++(-0.25,0);
  \draw[bus] (m3.east) -- ++(0.25,0) |- (m5.east);   \draw[bus] (m4.east) -- ++(0.25,0);
  \draw[rel] ($(m1.east)+(0.25,-0.65)$) -- node[relacion,above] {alimenta} ($(m4.west)+(-0.25,0)$);
  \draw[rel] ($(m4.east)+(0.25,0)$) -- node[relacion,above] {se juega en} (m6.west);
\end{tikzpicture}
\end{bloque}
```

- **En capas, con verbos.** Una capa por columna (la base, el método, lo que se evalúa),
  un bus que junta las cajas de cada capa y una flecha con verbo a la siguiente. Cuatro
  cajas sueltas en fila son una lista, no un mapa (`diagramas.md`). Si una flecha lleva
  verbo, el texto tiene que decirlo: el mapa no afirma relaciones que el documento no
  explica.
- **Títulos alineados.** Cada caja es `\arriba{alto}{ancho}{…}` con el mismo alto: el
  título queda arriba aunque una caja tenga un renglón menos. `minimum height` no sirve:
  centra en vertical.
- **Ancho.** Con `cajag`, `n × (ancho + 0,42 cm) + separaciones ≤ 17,4 cm`. Aquí, tres
  columnas de 3,9 cm y dos huecos de 2,2 cm: 3 × 4,32 + 2 × 2,2 = 17,36 cm. El hueco
  lleva el bus y un verbo de hasta ~1,4 cm («se juega en»).
- **De 8 a 12 secciones.** Cuatro capas de 2 a 4 cajas. Con 1,6 cm entre columnas (bus,
  flecha y un verbo de hasta ~1 cm, como «alimenta» o «elige»), cajas de 2,7 cm:
  4 × 3,12 + 3 × 1,6 = 17,28 cm. Títulos cortos («07 Persistencia») y un renglón de
  mensaje; con 1,3 cm entre centros, una columna de 4 cajas mide ~5 cm de alto. Con más
  de 12, agrupar.
- **Cuenta aparte.** Con 3 o más `\hyperref`, `medir.py` lo toma como mapa del tema: no
  suma piezas visuales ni entra en el aviso de 60 palabras («mapa del tema: 1»). En
  `breve` reemplaza al `\indice`; en `medio` y `largo` va junto a `\indicelista`.

## Conceptos centrales (lector=estudio)

```latex
\textbf{Definición.} El error tipo I es «rechazar $H_0$ siendo verdadera»; su probabilidad
máxima admisible es el nivel de significación $\alpha$ \fuente{W-errores}.

\textbf{Ejemplo.} En el ejercicio de la vida útil de lámparas ($\sigma = 40$, $n = 64$),
se rechaza que la media sea 1000 h si el promedio da menos de 990 h. Entonces
$\alpha = \Phi(-2) \approx 0,023$ \fuente{G9 ej. 2}.

\ojo[Confusión típica]{Fijar el valor crítico con $s$, el desvío de la muestra: la región
de rechazo se fija antes de muestrear y $s$ se conoce después. Con $\sigma$ desconocido
se usa el estadístico $T$ \fuente{parcial de práctica, ej. 2}.}
```

La tríada (definición copiada de la fuente, ejemplo, confusión típica) va en los 2 a 4
conceptos centrales de cada familia; el resto, en una línea o en el glosario. La confusión
típica es un error que la fuente señala (un ejercicio corregido, un «error común» del
apunte), no «el más común» si la fuente no lo cuenta. Un `\ojo[Confusión típica]` por
página, como cualquier `\ojo`.

## Para repasar (lector=estudio)

```latex
\begin{repaso}                          % \begin{repaso}[Autoevaluación] para otro rótulo
\item ¿Qué ley explica que una etiqueta equidistante de dos campos se lea mal?
\item ¿Cuándo conviene una barra de progreso en lugar de un spinner?
\end{repaso}
```

Al cierre de cada sección, de 3 a 5 preguntas (en una hoja, al final). Cada respuesta
tiene que estar en el texto del documento. Es una caja, no una sección: no repite «Para
repasar» en el índice ni en los marcadores, y no se parte entre páginas. Con
`--lector estudio`, `medir.py` avisa cada sección sin repaso.

## Tablas

```latex
\begin{bloque}[Qué se decidió sobre cada problema de calidad y dónde está el detalle.]
\begin{tabularx}{\linewidth}{@{}P{3cm}LP{2cm}@{}}
\toprule
\enc{Qué} & \enc{Detalle} & \enc{Fuente} \\
\midrule
\textbf{B1} tickets duplicados & unir por número de pedido & \fuente{R09} \\
\bottomrule
\end{tabularx}
\end{bloque}
```

`L` es una columna flexible alineada a la izquierda; `P{ancho}`, una de ancho fijo.
`tabularx` no se parte entre páginas: si la tabla pasa de media página, dividirla en dos.

La oración que presenta una tabla («la tabla las define:») va como pie de un `bloque` con
la tabla, no suelta antes: si la tabla no entra, salta sola y la oración queda al pie de
la página anterior (`medir.py` avisa la página que termina en «:»). Si la tabla abre una
sección después de una oración, `\needspace{N\baselineskip}` antes de `\section`, con N
el alto de título, oración y tabla en renglones (un renglón mide 4,6 mm: N ≈ 2,2 por
centímetro).

Próximos pasos: columnas `\enc{Qué}`, `\enc{Quién}`, `\enc{Para}` con `@{}LP{3.3cm}P{1.7cm}@{}`.
Cifras para tener a mano: `\enc{Qué}`, `\enc{Valor}`, `\enc{Fuente}`. Decisiones para un
cliente (una fila por decisión): `\enc{Decisión}`, `\enc{Qué gana}`, `\enc{Qué cuesta}`.

## Fórmulas

```latex
Con $\sigma = 40$ y $n = 64$, el error estándar es $\sigma/\sqrt{n} = 5$; con el corte
en 990, $\alpha = \Phi(-2) \approx 0,023$ \fuente{G9 ej. 2}. Con siete envases,
$t_{6;0,975} = 2,4469$ y el intervalo es $(496,30; 503,70)$ \fuente{G8 ej. 14}:
\[
  \bar x \pm t_{n-1;\,1-\alpha/2}\,\frac{s}{\sqrt{n}}
\]

{\footnotesize\renewcommand{\arraystretch}{1.3}%
\begin{tabularx}{\linewidth}{@{}P{2.7cm}P{3.1cm}P{2.6cm}P{1.8cm}L@{}}
\toprule
\enc{Distribución} & \enc{Soporte} & \enc{Masa} & \enc{Esperanza} & \enc{Cuándo se usa} \\
\midrule
\textbf{Binomial} $(n, p)$ & $\{0, \dots, n\}$ & $\dbinom{n}{k}p^k q^{\,n-k}$ & $np$ &
  Éxitos en $n$ ensayos independientes. \\ \addlinespace[2.5pt]
\textbf{Geométrica} $(p)$ & $\mathbb{N}_0$ & $q^{\,k}\,p$ & $\dfrac{q}{p}$ &
  Fracasos antes del primer éxito. \\ \addlinespace[2.5pt]
\textbf{Hipergeométrica} $(N, M, n)$ & \mbox{$\max\{0, n-(N-M)\}$,}\newline $\dots,\ \min\{n, M\}$ &
  $\dfrac{\binom{M}{k}\binom{N-M}{n-k}}{\binom{N}{n}}$ & $n\dfrac{M}{N}$ &
  Muestra sin reposición de una población de dos clases. \\
\bottomrule
\end{tabularx}}
```

- **Qué carga `dossier.sty`.** `amsmath`; con Fira Math instalada (viene con TeX Live),
  `unicode-math` con Fira Math, sin serifa como el texto; si no, `amssymb` y Latin Modern.
  `\mathbb{N}_0`, `\dfrac`, `\dbinom` y `\text{…}` funcionan en los dos casos.
- **Coma decimal.** `icomma`: `$0,039$` sale sin espacio y `$(a, b)$`, con espacio. Los
  pares y las listas se escriben con coma y espacio: sin espacio, `$(n,p)$` queda pegado.
- **Subíndices dobles** con `;`, como en muchos apuntes: `$t_{6;0,975}$`.
- **Palabras.** babel escribe `\max`, `\min` y `\lim` como «máx», «mín» y «lím»; ocupan
  más que en inglés. Otras palabras dentro de una fórmula, con `\text{…}`.
- **En tablas.** `\dfrac` en las celdas (`\tfrac` solo dentro de otra fórmula). Después
  de una fila con fórmulas altas, `\addlinespace[2.5pt]`: `\\[2pt]` no suma espacio si
  la fila tiene celdas de varios renglones. Lo que no se tiene que partir entre renglones
  va en `\mbox{$…$}`, y la columna se ensancha hasta que `medir.py` no marque desborde.
- **Destacada o en línea.** En línea, lo que se lee como parte de la oración (un valor,
  un estadístico, una condición). Destacada (`\[ … \]`), una fórmula con fracciones
  apiladas o que ocupa más de medio renglón: en línea se achica y separa los renglones.
  Cada fórmula en línea cuenta como una palabra de prosa; la destacada y la que está en la
  celda de una tabla no cuentan.

## Hoja de consulta

`consulta.tex` es la plantilla de un formulario, una chuleta o una tabla para un examen:
`nuevo.py` la copia con `hoja` e `items=N`. Lleva `\portada*`, un `\ojo` con las
convenciones, una tabla con una fila por ítem, una pieza que relaciona los ítems y
`cifras` solo si son valores que se consultan. Sin `\resumen` ni `\proceso`.

```latex
% \grupofila{título}{nota}: fila de grupo; consulta.tex la define en el preámbulo (6 columnas)
\providecommand{\grupofila}[2]{\multicolumn{6}{@{}l@{}}{\rule{0pt}{11pt}{\scriptsize\ttfamily\bfseries
  \color{acento}\MakeUppercase{#1}}\enspace{\scriptsize\color{apagado}#2}}\\}

\portada*{Estadística · para el parcial}
  {Doce distribuciones en una hoja}
  {Soporte, masa o densidad, esperanza, varianza y cuándo se usa cada una}

\ojo[Convenciones]{La geométrica cuenta \textbf{fracasos} (soporte $\mathbb{N}_0$); la
normal va con el \textbf{desvío}, $N(\mu, \sigma)$; la exponencial, con la \textbf{tasa} $\lambda$.}

{\footnotesize\setlength{\tabcolsep}{3.5pt}\renewcommand{\arraystretch}{1.3}%
\begin{tabularx}{\linewidth}{@{}P{2.4cm}P{2.45cm}P{2.6cm}P{1.8cm}P{2.1cm}L@{}}
\toprule
\enc{Distribución} & \enc{Soporte} & \enc{Masa o densidad} & \enc{Esperanza} & \enc{Varianza} & \enc{Cuándo se usa} \\
\midrule
\grupofila{Discretas}{$q=1-p$}
\textbf{Geométrica}\newline{\color{rotulo}$(p)$} & $\mathbb{N}_0$ & $q^{\,k}\,p$ & $\dfrac{q}{p}$ & $\dfrac{q}{p^2}$ &
  Fracasos antes del primer éxito. Única discreta sin memoria. \\
\textbf{Poisson}\newline{\color{rotulo}$(\lambda)$} & $\mathbb{N}_0$ & $\dfrac{\lambda^{k}}{k!}\,e^{-\lambda}$ & $\lambda$ & $\lambda$ &
  Eventos raros por intervalo, con tasa media $\lambda$. \\
\grupofila{Continuas}{fuera del soporte, $f_X=0$}
\textbf{Exponencial}\newline{\color{rotulo}$(\lambda)$} & $x>0$ & $\lambda e^{-\lambda x}$ & $\dfrac{1}{\lambda}$ & $\dfrac{1}{\lambda^2}$ &
  Tiempo hasta una falla o entre llegadas. Sin memoria. \\
\bottomrule
\end{tabularx}}
```

- `\portada*{contexto}{título}{subtítulo}`: título a 17 pt y sin la línea de «para quién
  y cómo leer»; deja el alto para la tabla.
- Una fila por ítem, con el nombre y los parámetros en la primera columna. `perfil.py`
  dice cuántas palabras tiene cada ítem (con 12 ítems y `-texto`, unas 20), y las celdas
  cuentan.
- La pieza que relaciona los ítems es un mapa de familias: nodos de una o dos palabras,
  flechas llenas y punteadas con una leyenda en el pie (`diagramas.md`, regla 3).
- Si la fuente trae más unidades que `items`, se eligen con un criterio, sin gastar dos
  ítems en la misma familia; lo que quedó afuera se dice en la hoja si hay lugar, y
  siempre en el README y el reporte.

## Código

```latex
El planificador está en \cod{simulador/planificador.py}: la función \cod{elegir_proceso}
recibe la cola que arma \cod{leer_llegadas}.

\begin{bloque}[Extracto de \cod{planificador.py}, con los números de línea del archivo: la política se elige por nombre y el quantum es fijo (48 a 53), y el bucle principal avanza de a un quantum (112 a 117) \fuente{S}.]
\begin{codigo}[language=Python,firstnumber=48]
POLITICAS = {
    "fcfs": primero_en_llegar,
    "sjf": trabajo_mas_corto,
    "rr": round_robin,  # turno rotativo: cada proceso corre a lo sumo un quantum
}
QUANTUM_MS = 20  # el del enunciado; se cambia con --quantum al correr la simulación
\end{codigo}
\vspace{3pt}
\begin{codigo}[language=Python,firstnumber=112]
    while cola or llegadas:
        cola.extend(leer_llegadas(reloj, llegadas))
        proceso = elegir_proceso(cola, politica)
        reloj += ejecutar(proceso, QUANTUM_MS)
        if proceso.restante > 0:
            cola.append(proceso)
\end{codigo}
\end{bloque}
```

- Se copian los tramos que el texto comenta, cada uno con su primera línea real
  (`firstnumber=N`) y la sangría del archivo, dentro de un `bloque` cuyo pie dice qué
  muestra cada tramo. El `bloque` no se parte: un tramo largo va en dos bloques.
- No `\lstinputlisting[linerange=…]`: con LuaLaTeX renumera desde 1 y deja pasar
  caracteres de las líneas salteadas.
- Tildes y eñes salen bien en código, comentarios y cadenas. Las líneas largas se parten
  y siguen con ↪.
- `\cod{…}` es para un identificador dentro de la prosa, un pie, una celda o un título
  (función, archivo, ruta): se corta solo después de `_ . / -` y acepta `_` sin barra.
  `\texttt` no se corta y se sale del margen.
- El código no cuenta como prosa; cada `\cod{…}`, como una palabra.

## Glosario

```latex
\anexo{Glosario}
\begin{glosario}
\termino{Tiempo de resolución}{Horas entre la apertura de un ticket y su cierre, sin contar las esperas al cliente.}
\end{glosario}
```

Solo los términos que el texto usa sin definir; si no hay, no va.

## Gráficos (`graficos.py`)

```python
from estilo_graficos import P, SERIES, figura, guardar, barras_h, rotular, num, pct

def cifras():
    # Fuente: registro de cifras, filas R14 y R01
    fig, ax = figura(alto_mm=34, ancho=0.62)          # ancho: fracción del texto
    barras_h(ax, ["Al 31/03/2026", "Sin duplicados", "Al 31/01/2026"],
             [27.3, 28.1, 19.6], destacar="Sin duplicados", fmt=pct)
    ax.set_title("Tickets fuera de plazo")               # en el color del texto
    guardar(fig, "f2_cifras.pdf")

def por_anio():
    fig, ax = figura(alto_mm=40, ancho=0.5)
    barras = ax.bar(["2023", "2024", "2025"], [310, 420, 380], color=SERIES[0], width=0.6)
    rotular(ax, barras)                                  # el valor sobre cada columna
    ax.set_yticks([]); ax.spines["left"].set_visible(False)
    guardar(fig, "f3_por_anio.pdf")
```

- **Destacar una serie contra el resto:** `barras_h(..., destacar=...)`, en el acento del
  documento sobre gris. Es el caso más común y no necesita paleta categórica. Los empates
  quedan en el orden en que se pasan.
- **Distinguir categorías o series:** `SERIES`, la paleta de referencia de la skill
  dataviz, validada sobre blanco en ese orden. Los colores del documento (`P`) no sirven
  para esto: el acento es demasiado oscuro y apagado y no pasa el validador. Con puntos o
  mapas, solo los tres primeros. Si el proyecto trae paleta categórica propia, validarla
  con la skill dataviz antes de usarla.
- **Títulos y rótulos** en el color del texto, nunca en el de una serie.
- `P` tiene la paleta del documento (`P["tinta"]`, `P["linea"]`...); `num(21748)` da
  `21.748` y `pct(28.1)` da `28,1 %`.

### Gráficos de funciones y tramos

```python
import numpy as np
from estilo_graficos import SERIES, figura, guardar, densidad, sombrear, corte, escalones

def una_cola():
    # Fuente: tabla de la normal estándar, fractiles de uso frecuente (z_0,95 y z_0,975)
    x = np.linspace(-4, 4, 400)
    y = np.exp(-x ** 2 / 2) / np.sqrt(2 * np.pi)
    fig, ax = figura(alto_mm=48, ancho=0.62)
    densidad(ax, x, y, rotulo="$N(0, 1)$")
    sombrear(ax, x, y, 1.645, 4, rotulo="$\\alpha = 0,05$")
    corte(ax, 1.645, "$z_{0,95} = 1,645$")
    corte(ax, 1.96, "$z_{0,975} = 1,96$", nivel=1)
    guardar(fig, "f4_una_cola.pdf")

def dos_hipotesis():
    # Fuente: ejercicio resuelto de errores de tipo I y II (G9 ej. 2): sigma = 40, n = 64,
    # error estándar 5; se rechaza H0 si el promedio es menor que 990.
    ee = 5
    x = np.linspace(970, 1016, 400)
    h0 = np.exp(-((x - 1000) / ee) ** 2 / 2) / (ee * np.sqrt(2 * np.pi))
    h1 = np.exp(-((x - 988) / ee) ** 2 / 2) / (ee * np.sqrt(2 * np.pi))
    fig, ax = figura(alto_mm=48, ancho=0.62)
    densidad(ax, x, h0, rotulo="si $H_0$: $\\mu = 1000$")
    densidad(ax, x, h1, color=SERIES[1], rotulo="real: $\\mu = 988$")
    sombrear(ax, x, h0, 970, 990, rotulo="$\\alpha$")        # los valores, en el pie
    sombrear(ax, x, h1, 990, 1016, color=SERIES[1], rotulo="$\\beta$")
    corte(ax, 990, "rechazar si $\\bar{x} < 990$")        # tocaba la leyenda: va a la derecha
    guardar(fig, "f6_dos_hipotesis.pdf")

def vacaciones():
    # Fuente: art. 150 LCT: días de vacaciones según la antigüedad. El último tramo (más
    # de 20 años) no tiene fin: se dibuja hasta 25 y el pie lo dice.
    fig, ax = figura(alto_mm=36, ancho=0.55)
    escalones(ax, [(0, 5, 14, "14 días"), (5, 10, 21, "21 días"),
                   (10, 20, 28, "28 días"), (20, 25, 35, "35 días")])
    ax.set_xlabel("antigüedad (años)")
    guardar(fig, "f5_vacaciones.pdf")
```

- Las fórmulas de los rótulos salen en Avenir, como el texto. La excepción es `\alpha`, que
  sale de DejaVu Sans oblicua: en Avenir itálica la α es igual a la «a».
- `densidad(ax, x, y, color=None, rotulo=None)`: una curva sobre un eje x limpio y sin
  eje y (la altura de una densidad no se lee). Con `rotulo`, la curva entra en la
  leyenda, arriba a la izquierda.
- `sombrear(ax, x, y, desde, hasta, color=None, fuerte=False, rotulo=None)`: el área bajo
  la curva. `fuerte` la oscurece (una parte dentro de otra: el valor p dentro de α). El
  rótulo queda pegado al área, sin línea guía: adentro si el área es alta; si es una
  cola, encima y hacia afuera.
- `corte(ax, x, rotulo, nivel=0, lado=None)`: una línea punteada con el rótulo arriba,
  del lado opuesto al pico (con dos curvas, al promedio de los picos); `lado="izq"` o
  `"der"` lo fija. Con dos cortes cercanos, `nivel=1` baja el segundo rótulo y no se
  pisan. Si el rótulo toca la leyenda, pasa al otro lado o, si ahí no entra (o `lado` lo
  fijó), baja un renglón y puede quedar sobre una curva: mirar el PNG.
- `escalones(ax, tramos, color=None)`, con `tramos = [(desde, hasta, valor, rótulo)]`:
  una escala por tramos (días según la antigüedad, una alícuota según el monto); sin
  rótulo, escribe el valor.
- Los parámetros salen de un ejemplo de la fuente (el ejercicio, el artículo), con la
  fuente en el comentario; nunca inventados para ilustrar. Las fórmulas de los rótulos
  (`$\\alpha = 0,05$`) salen en la letra del documento, con la coma decimal pegada.
