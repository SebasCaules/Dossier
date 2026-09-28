---
name: dossier
version: "0.4.0"
description: "Parámetros → Largo: 1 hoja, breve (default), medio o largo — Texto: +texto o -texto — Imágenes: +imagenes o -imagenes — Lector: equipo, estudio, entrega o cliente — Formato: impresion | digital — Ajustes: temas=N, items=N, paginas=N. \u2028Arma PDFs de lectura (resúmenes, informes, documentos para un equipo o un cliente, guías de estudio) con gráficos, diagramas, capturas y navegación cliqueable, a la medida de esos parámetros, y los verifica midiendo el largo y mirando cada página. Usar siempre que el usuario pida un PDF para leer o compartir que resuma o explique algo («un PDF con lo que hicimos», «un resumen en PDF del parcial», «un documento mediano con más gráficos», «una hoja con lo esencial»), aunque no nombre la skill, y para acortar, alargar o rehacer un PDF así. No usar para manipular PDFs existentes (unir, dividir, extraer texto, formularios: skill pdf) ni para diapositivas."
argument-hint: "Parámetros → Largo: 1 hoja, breve (default), medio o largo — Texto: +texto o -texto — Imágenes: +imagenes o -imagenes — Lector: equipo, estudio, entrega o cliente — Formato: impresion | digital — Ajustes: temas=N, items=N, paginas=N."
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Agent, Skill, AskUserQuestion
---

# /dossier — PDFs de lectura a medida

El resultado es un PDF A4 con portada que cuenta todo, cifras con su fuente, piezas
visuales hechas para el documento y navegación con clics. Cuánto mide, cuánto texto lleva
y cuántas imágenes tiene lo fijan los parámetros; por defecto sale **breve**. El modelo
es un resumen de 10 páginas que el usuario elogió.

Tres cosas hacen que salga bien a la primera, con cualquier perfil:

1. **El largo es un número**: lo fija el perfil antes de escribir y `medir.py` lo
   controla en cada compilación. Calibrar el largo a ojo costó regeneraciones enteras.
2. **Se mira cada página renderizada**, no el `.tex`. Los cortes entre páginas, las
   etiquetas pisadas y los diagramas que desbordan solo existen en el PDF.
3. **Las cifras y definiciones salen de la fuente del proyecto**, nunca de memoria.

## Parámetros

Van después de `/dossier`, en cualquier orden y mezclados con el tema. También valen
dichos en palabras («un dossier mediano con más imágenes» es `medio +imagenes`). El
lector y el formato van sueltos (`estudio`, `impresion`) o con clave (`lector=estudio`,
`formato=impresion`). Mayúsculas y acentos no importan (`IMPRESION`, `Imágenes`).

| Parámetro | Valores | Por defecto | Qué cambia |
|---|---|---|---|
| largo | `hoja` (1 hoja) · `breve` · `medio` · `largo` | `breve` | 1 página · 2 a 6 · 7 a 12 · 13 a 24; el índice y la estructura |
| texto | `-texto` · normal · `+texto` | normal | prosa hasta el 25 %, 40 % o 60 % de las páginas (en una hoja, 30 %, 45 % o 60 %; ±10 puntos según las imágenes); qué tan desarrollado va cada párrafo |
| imágenes | `-imagenes` · normal · `+imagenes` | normal | ~1 pieza visual cada 2 páginas, ~1 por página o ~1,5 por página |
| lector | `equipo` · `estudio` · `entrega` · `cliente` | según el pedido | las secciones que no pueden faltar (próximos pasos, repaso, portada formal, resumen ejecutivo) |
| formato | `digital` · `impresion` | `digital` | enlaces visibles y panel de marcadores, o enlaces del color del texto, direcciones al pie y páginas en las referencias |
| ajuste | `temas=N` · `items=N` · `paginas=N` | — | calcula las páginas según las secciones (temas) o las unidades a cubrir una por una (items: 19 leyes, 30 conceptos), o las fija; en una hoja, `items=N` pide la hoja de consulta |

Ejemplos: `/dossier sobre el informe de avance` · `/dossier hoja lo esencial del parcial` ·
`/dossier medio +imagenes -texto equipo sobre el tablero` ·
`/dossier largo +texto estudio impresion las 19 leyes de UX`.
Sinónimos aceptados: `short`/`medium`/`long`, `more-images`, `less-text`, `print`.

## Antes de empezar

`SKILL_DIR` es la carpeta de este archivo (el harness la informa al cargar la skill).
Requisitos: `lualatex` y `latexmk` (TeX Live), `pdfinfo`, `pdftoppm` y `pdftotext`
(poppler) y `python3` con matplotlib, Pillow (blancos de cada página) y pdfplumber
(palabras por página en la letra del cuerpo; sin él, `medir.py` cuenta todo el PDF y lo
dice en una `Nota`). Playwright solo hace falta para capturas.

## 1. Fijar el perfil y el encargo

Leer las fuentes lo necesario para contar los temas (y los ítems, si hay que cubrir
unidades una por una), y traducir los parámetros a números:

```bash
python3 "SKILL_DIR/scripts/perfil.py" <parámetros del pedido> temas=N items=N
```

Pasarle solo los parámetros, no el tema: una palabra del tema como «equipo» o «estudio»
se leería como lector. Van sueltos o entre comillas (`-imagenes` y `-texto` se aceptan
sin comillas).

`perfil.py` corrige los errores de tipeo cuando hay un solo parámetro parecido
(«imprecion» → `impresion`, «+imagnes» → `+imagenes`) y los informa como «Interpreté»:
mencionarlos en el plan. Si informa una **DUDA** (la palabra se parece a más de un
parámetro, o no lo bastante), preguntarle al usuario en una línea qué quiso decir, con las
opciones que da el script, antes de crear la carpeta; `nuevo.py` no crea nada mientras
haya dudas.

Imprime los números del perfil («Páginas: hasta 24 (largo: 13 a 24; menos de 13 es un
aviso)», tope de texto, piezas visuales; en una hoja, cómo repartir el tope), la
estructura del lector y la línea exacta de `medir.py`. Con eso, dejar en la respuesta un
plan de tres a seis líneas: el perfil, el mapa de páginas (una línea por página o
sección), las fuentes y la identidad visual (los tokens del proyecto si existen:
`estilos.css`, `DESIGN.md`, `tokens.md`).

- Si el pedido da un **tiempo de lectura**, contar ~200 palabras de texto por minuto
  (diez minutos: ~2.000 palabras) y elegir el largo que las contiene.
- Con **muchos ítems** (19 leyes, 30 conceptos), agrupar en familias de 4 a 6; cada
  familia es un tema, y `items=N` da el lugar que necesitan. Si la fuente no trae la
  agrupación, el documento dice que es propia.
- Si **`items=N` es menor que las unidades de la fuente**, elegir con un criterio, sin
  gastar dos ítems en la misma familia, y decir qué quedó afuera: en el documento si hay
  lugar, y siempre en el README y el reporte.
- `perfil.py` avisa las combinaciones exigentes (`hoja +texto +imagenes`), un `paginas=N`
  que no corresponde al largo pedido, los temas o ítems que no entran («AVISO: 10 temas ×
  2,5 + portada = 26 páginas: no entran en largo (máx. 24); agrupar temas.») y, en una
  hoja con ítems, las palabras que tiene cada uno.

Seguir sin esperar respuesta, salvo que el pedido admita lecturas que cambian el
documento entero (para quién es, qué cubre). En ese caso, una sola pregunta. Con
`lector=entrega`, si las fuentes no nombran a los integrantes o a los docentes,
preguntarlo en la única pregunta del plan; sin respuesta, `\datosentrega` deja renglones
para completar y el reporte lo dice.

## 2. Crear la carpeta del documento

```bash
python3 "SKILL_DIR/scripts/nuevo.py" "<proyecto>/<ruta>/<nombre>" --perfil "<parámetros> temas=N items=N" --titulo "<título>"
```

Va dentro del proyecto, junto al material del que habla; si no hay un lugar obvio,
`<proyecto>/pdf/<nombre>/`. Elige la plantilla (`doc.tex` para varias páginas, `hoja.tex`
para una hoja y `consulta.tex` para una hoja con `items=N`), el índice y la opción de
impresión. En la cabecera del `.tex` y en el `README.md` deja el perfil con sus ajustes,
el pedido tal como llegó (`% Pedido: «…»`) y la línea de `medir.py`, que se puede correr
tal cual. Copia `dossier.sty`, `estilo_graficos.py` y `graficos.py` (sin gráficos
activos), así el PDF se puede regenerar aunque la skill cambie.

El contenido de la plantilla es de ejemplo: se reemplaza entero. Las figuras de ejemplo
quedan en `fig/` (`nuevo.py` las dibuja una vez; `graficos.py` no las llama) y se
reemplazan con las del documento: las que no se usen, se borran. Si el documento no lleva
gráficos de datos, `graficos.py` queda sin funciones.

## 3. Juntar el contenido

- **Inventariar los títulos de las fuentes** y marcar cuáles entran. Si el PDF queda por
  debajo del perfil, el reporte nombra lo que quedó afuera y por qué.
- Anotar cada cifra con su origen (archivo, fila del registro, página). En el texto, cada
  cifra lleva `\fuente{...}`.
- Copiar las definiciones del glosario, anexo o registro del proyecto. Una definición
  escrita de memoria ya salió mal: el lift se definió contra el azar cuando el proyecto lo
  medía contra una regla.
- **Fuentes que se contradicen**: seguir la más reciente o la que se declara corrección, y
  decirlo en el texto citando las dos (`referencias/escritura.md`).
- Lo que no está decidido se rotula: `\chip{propuesta}` o «propuesta» en el pie.
- Si falta un dato para un gráfico, el gráfico no va. No se inventan valores.
- **El material real depende de la materia.** En una de fórmulas, una curva dibujada con
  los parámetros de un ejemplo de la fuente (nunca inventados); en una normativa, la
  frecuencia de preguntas del material de examen y los plazos y escalas de la norma.
- **Nunca se pega la foto de una página de texto** de otro documento (el enunciado, un
  apunte, un paper): es ilegible al tamaño de una figura y no cuenta como pieza visual
  (`medir.py` la marca como problema). Lo que dice esa página se resume con palabras
  propias y la fuente al lado.

## 4. Armar las páginas

**Según el largo:**

- **hoja**: todo en una página, sin índice ni secciones. `\portada`, `\begin{cifras}`,
  `\resumen[título que dice el mensaje]` con tres párrafos (con `-texto`, tres viñetas),
  una pieza visual, un `\ojo`, una tabla chica y, si queda lugar, un `\proceso` o diagrama
  al pie (`hoja.tex` trae todo, con una segunda pieza junto al `\ojo`). La **hoja de
  consulta** (formulario, chuleta, tabla para un examen; `consulta.tex`) lleva `\portada*`,
  un `\ojo` con las convenciones, una fila de tabla por ítem y una pieza que los relaciona,
  sin `\resumen` ni `\proceso` (`referencias/componentes.md`, «Hoja de consulta»).
- **breve**: la página 1 es el documento entero (`\portada`, `\hitos` si importan las
  fechas, cifras, `\resumen`, un `\ojo`, `\indice`). Después, una sección por mensaje.
  Las cifras van solo si 3 o 4 números responden la pregunta del documento (no logística
  ni configuración); con `lector=estudio`, el mapa del tema reemplaza al `\indice`.
- **medio**: la misma portada con `\indicelista` (lista con páginas). Secciones de una o
  dos páginas que abren con una o dos oraciones que dicen su conclusión.
- **largo**: como medio, más subsecciones con título que dice su mensaje, un
  `\nota[En corto]{...}` de dos líneas al cierre de cada sección y `\anexo{...}` para el
  detalle que no todos van a leer.

**Según el texto** (reglas completas en `referencias/escritura.md`): con `-texto`,
viñetas, pies y tablas cargan el contenido y los párrafos tienen hasta dos oraciones; con
`+texto`, cada idea lleva su porqué y un ejemplo. Más texto nunca es relleno.

**Según las imágenes**: con `-imagenes`, una pieza visual solo donde reemplaza un párrafo;
con `+imagenes`, cada sección se abre con una pieza visual grande y los procesos, las
comparaciones y las pantallas se muestran en lugar de describirse (con `lector=estudio`,
la sección abre con la oración y la definición, y la pieza grande viene después). Dos
piezas lado a lado (entorno `columna`) cuentan como dos. El mínimo del perfil es una
meta, no una cuota: se completa con material real (gráficos de los datos, diagramas que
muestran una relación, capturas de una interfaz) o no se completa, y se dice en el
reporte.

**Según el lector**, la estructura que `perfil.py` imprime:

- **estudio**: portada con el mapa del tema, que en breve reemplaza al índice (sus cajas
  son los enlaces); por familia de conceptos, la tríada (definición copiada de la fuente,
  ejemplo, confusión típica: un error que la fuente señala) en los 2 a 4 conceptos
  centrales, el resto en una línea o en el glosario; si la evaluación es por casos o
  ejercicios y la fuente trae uno resuelto, una sección que lo resuelve de punta a punta;
  cada condición de uso con el umbral que da la fuente; repaso de 3 a 5 preguntas al
  cierre de cada sección (en hoja, al final); glosario solo con los términos que el texto
  usa sin definir (si no hay, no va).
- **entrega**: portada formal con `\datosentrega` (materia, integrantes y docentes con
  nombre completo, fecha); lo que las fuentes no traen se pregunta en la pregunta del plan
  o queda en renglones y se avisa; resumen ejecutivo y un `\ojo` con la tesis; secciones
  numeradas; una cita por párrafo, no por oración; referencias que la cátedra puede
  consultar (la trazabilidad a archivos internos, transcripciones y apuntes va al README);
  sin notas de trabajo, rótulos internos ni «hoy».
- **cliente**: portada con quién propone, a quién y la fecha; la recomendación primero;
  cifras de negocio y, si la fuente no las tiene, metas del servicio rotuladas como
  propuesta (nunca estimaciones propias); una sección por decisión (en hoja, una fila por
  decisión en una tabla: qué gana y qué cuesta); qué se necesita de su lado, siempre;
  próximos pasos con fecha solo si la fuente los trae; sin jerga ni rótulos internos: cada
  término se entiende sin la fuente.
- **equipo**: portada con cifras, resumen y lo urgente; una sección por tema; próximos
  pasos: qué, quién y para cuándo; cifras para tener a mano; glosario si hay términos
  propios.

En `referencias/componentes.md`: el entorno `repaso` («Para repasar»), el «Mapa del
tema» (un diagrama en capas cuyas cajas enlazan a cada sección) y «Referencias y datos de
entrega».

**En todos**: cada sección tiene un mensaje, que dice su título. No quedan medias
páginas vacías: si una sección no llena su página, la siguiente sigue en la misma (sin
`\newpage`); solo la última puede quedar a medias, y usa al menos el 35 % de su alto. Si la
portada no se llena, que la primera sección empiece en ella o sumar una pieza de ancho
completo (un `\proceso`). `\vfill` antes de esa pieza la ancla al pie, pero solo sirve si
el hueco que deja es chico: `medir.py` avisa desde el 20 % de la página.

| Para mostrar | Usar |
|---|---|
| 3 o 4 números que responden la pregunta | `\begin{cifras}` + `\cifra` |
| fechas, hitos, dónde estamos | `\hitos` |
| etapas en orden (las de un método, sin avance: estado `neutro`) | `\proceso` |
| cómo se conectan las partes | TikZ con los estilos `caja`, `flecha` y `etiqueta` |
| qué pertenece a qué, dos mundos que no se mezclan, qué causa qué | grupos con fichas, carriles o mapa conceptual: `referencias/diagramas.md` |
| pasos con ramas | árbol de decisión (`referencias/componentes.md`) |
| cantidades que se comparan | gráfico con `graficos.py` |
| una función o un área de probabilidad | `densidad` + `sombrear` (y `corte`), con los parámetros de un ejemplo de la fuente: «Gráficos de funciones» |
| tramos (plazos, escalas, tarifas) | `escalones` |
| una fórmula o una tabla de fórmulas | `referencias/componentes.md`, «Fórmulas» |
| código fuente | `codigo` en tramos copiados con `firstnumber`, dentro de un `bloque` con pie; `\cod` para un identificador en el texto |
| varias cosas en varios atributos | tabla `tabularx` con `\enc` |
| una pieza junto a un aviso o una lista | dos entornos `columna` («Dos columnas») |
| una pantalla, un tablero, una web | `scripts/capturar.py` + `\captura` |

Cada componente tiene su ejemplo en `referencias/componentes.md`. Leerlo antes de armar
la primera página, y `referencias/diagramas.md` antes del primer diagrama de relaciones:
un diagrama tiene que mostrar la relación que afirma el texto, no una lista en cajas.

**Gráficos.** Si la skill `dataviz` está instalada, cargarla antes del primero: de ella
aplican la forma, el color por función, las marcas, la leyenda y mirar el resultado; el
hover y el modo oscuro no (es un PDF). Sin ella, alcanzan las reglas de abajo. Cada
gráfico va en `graficos.py`, dibujado con `figura(alto_mm, ancho)` de
`estilo_graficos.py` (la letra, el tamaño y la paleta del PDF, al tamaño final) e
incluido con `\figura{fig/x.pdf}{pie}` sin ancho.

- Para destacar una serie contra el resto, el acento sobre gris (`barras_h(...,
  destacar=...)`). Para distinguir categorías, `SERIES`, la paleta validada (la de
  referencia de dataviz).
- Valores cercanos o curvas que convergen: barras desde cero con el valor al final
  (`barras_h`, `rotular`) o una leyenda. Rótulos dentro de barras con `texto_sobre`.
- Títulos y rótulos en el color del texto, nunca en el de una serie.

**Navegación.** Sale sola: índice cliqueable, encabezado que vuelve al índice, panel de
marcadores, `\ver{sec:x}` a una sección (`\ver[texto]{sec:x}` con un texto propio) y
`\enlace{url}{texto}` a la web. Con `impresion`, los enlaces toman el color del texto,
`\ver` agrega la página y `\enlace` lleva la dirección al pie. Formularios, JavaScript y
video quedan fuera: la mayoría de los lectores no los ejecutan.

## 5. Escribir

Las reglas, por nivel de texto, están en `referencias/escritura.md`. En todos los
niveles: primero la respuesta; el título dice el mensaje; el texto dice qué significa la
figura, no la repite; corregir es acortar; idioma y registro del proyecto, y si no hay
regla, español neutro.

## 6. Compilar y medir, en cada vuelta

La línea exacta quedó en la cabecera del `.tex`:

```bash
python3 "SKILL_DIR/scripts/medir.py" <doc>.tex --paginas N --paginas-min m --paginas-texto M --parte-texto F --densa D --visuales-min V [...] [--lector L]
```

Compila con `latexmk -lualatex` (auxiliares en `_build/`, PDF junto al `.tex`), sigue
los `\input` y tiene que salir con 0. La prosa incluye repaso, glosario y notas de
`\cifra`; el código, la matemática destacada y el texto de los dibujos no cuentan, y
cada fórmula en línea o `\cod`, una palabra (en una celda de tabla, ninguna). Siempre
imprime el desglose:

```
Prosa: 2.385 = texto 1.010 · tablas 293 · pies 489 · repaso 265 · glosario 127 · avisos 144 · portada 57
```

Si no sale con 0:

- **Páginas o texto fuera de límite:** el script dice cuántas palabras sobran y dónde
  mirar: «Creció desde la medición anterior: pies +7.» o, la primera vez, «Además del
  texto, los bloques más grandes: tablas 54, cifras 35.». Recortar texto, no piezas
  visuales; el repaso y el glosario se ahorran con la estructura del lector.
- **Piezas visuales por encima del máximo** (con `-imagenes`): quitar las que repiten lo
  que dice el texto. Las tablas, las filas de cifras y el mapa del tema (un dibujo con 3
  o más `\hyperref`, que sale aparte: «mapa del tema: 1») no cuentan.
- **Imagen de texto:** una página de otro documento pegada como figura. Quitarla.
- **Texto que se sale del margen, carácter que la fuente no tiene, referencia rota:** ver
  `referencias/problemas.md`.

Los `AVISO` no cambian la salida, pero cada uno dice qué hacer y se resuelve; un aviso de
página densa (contada en la letra del cuerpo, sin código, fórmulas ni rótulos chicos) se
resuelve, no se descarta. Con `--parte-texto`, avisa si la prosa ocupa en las páginas
reales más de lo que pide el perfil («la prosa ocupa el 49,7 % de las 17 páginas; el
perfil pide 40 %»): el documento quedó más corto con el mismo texto. Los demás cubren
texto por debajo del piso de `+texto` (explicar más, no rellenar), blancos (una hoja por
debajo del 85 %, una última página por debajo del 35 %, más del 40 % al pie, huecos de
más del 20 %), páginas que terminan en «:», diagramas (no el mapa del tema) con más de
~60 palabras o un nodo con más de 12, «~» antes de un número, referencias que ningún
`\fuente` cita y, con `--lector estudio`, secciones sin `repaso` (una subsección «Para
repasar» también vale). Solo dos pueden quedar, dichos en el reporte: piezas visuales por
debajo del mínimo y menos páginas que el mínimo del largo, cuando las fuentes no traen
más material real.

Las `Nota` informan: un blanco de 15 a 40 % al pie («Nota: blanco al pie de 15 a 40 % en
la página 5 (4,2 cm libres).») se acepta, o se cierra moviendo un párrafo o achicando
una pieza.

## 7. Mirar cada página

```bash
python3 "SKILL_DIR/scripts/revisar.py" "<doc>.pdf" [--lector L]
```

Leer `hoja.png` (todas juntas: ritmo, blancos, paredes de texto) y después cada
`pagina-NN.png`; para lo fino, `--dpi 200 --paginas N`. El script imprime qué buscar, y
con `--lector cliente` o `estudio`, también lo de ese lector. En cada figura, mirar que
cada destacado esté explicado en el pie y que las cifras del pie coincidan con la
figura. Corregir y volver al paso 6. No se entrega un PDF sin haber mirado todas sus
páginas después de la última compilación.

## 8. Cotejar el contenido

Lanzar siempre **un** agente crítico de solo lectura, salvo en una hoja con menos de ~10
afirmaciones, que se cotejan a mano:

> Coteja contra `<fuentes>` cada cifra, fecha, definición, fórmula y regla (quién puede
> qué, hasta cuándo, con qué efecto) de `<doc>.tex`, incluidas la primera oración de cada
> sección y el texto de diagramas y fichas. Busca también las contradicciones internas y
> entre fuentes, y lo que la fuente le pide al lector y el documento omite. Si el
> documento describe código, cotéjalo contra el código, no contra su README; una tabla de
> fórmulas, celda por celda. Devuelve solo los desacuerdos, cada uno con la línea del
> .tex, lo que dice la fuente (ruta y línea) y la corrección. No edites nada.

Revisar la evidencia de cada hallazgo antes de aplicarlo. No hay segunda ronda: después
de corregir, pasos 6 y 7.

## 9. Entregar

- Completar el `README.md` de la carpeta: para quién es, de dónde salen las cifras y qué
  quedó afuera de las fuentes.
- Mostrar el PDF (con `SendUserFile` si está disponible; si no, la ruta).
- Reportar en no más de cinco líneas: ruta, perfil, páginas, texto y piezas visuales
  contra sus límites, qué es propuesta, qué quedó afuera y por qué, y qué dudas quedan
  (por ejemplo, los datos de entrega que faltan). Sin resumir el contenido.
- En un repositorio, sugerir agregar `_build/` al `.gitignore` (sin hacerlo).

## Pedidos de cambio

- **Cambiar el perfil** de un documento hecho («ahora mediano», «con más imágenes»):
  correr `perfil.py` con los parámetros nuevos, actualizar la cabecera del `.tex`
  (`% Perfil`, `% Pedido`, `% Medir`) y el `README.md`, y cambiar `\indice` o
  `\indicelista` si cambió el largo. No hace falta crear otra carpeta.
- **«Más corto»:** bajar un largo o pasar a `-texto`; recortar texto antes que piezas
  visuales. Si el pedido cambia de dirección («más corto» y después «más largo»), no es
  el largo global: preguntar qué sección quedó corta.
- **Queja visual ambigua** («tamaño», «largo»): preguntar cuál de las dos cosas o
  corregir ambas en la misma vuelta.

## Problemas conocidos

`referencias/problemas.md` junta los errores que ya costaron tiempo: fuentes sin
flechas, el `%` de babel, cadenas de Python de varias líneas, tablas que no se parten,
diagramas corridos del margen y más. Leerlo ante el primer error que no se entienda.
