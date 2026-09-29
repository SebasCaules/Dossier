# /dossier

Una skill para [Claude Code](https://claude.com/claude-code) que arma PDFs de lectura:
resúmenes para estudiar, informes para entregar, documentos para un equipo o un cliente y
hojas de consulta. Los hace con LaTeX, con gráficos, diagramas y navegación cliqueable, del
largo y con la cantidad de texto e imágenes que se le pidan. Antes de entregar, mide cada
compilación y mira cada página.

Los PDFs de [`ejemplos/`](ejemplos/) están hechos con la skill.

## Instalar

Con [`npx skills`](https://github.com/vercel-labs/skills) (hace falta Node.js), desde la
carpeta del proyecto:

```bash
npx skills add SebasCaules/Dossier -a claude-code        # solo en este proyecto
npx skills add SebasCaules/Dossier -a claude-code -g     # en todos los proyectos
```

La primera deja la skill en `.claude/skills/dossier` del proyecto (se puede subir al repo
para que la tenga todo el equipo); la segunda, en `~/.claude/skills/dossier`. Para
actualizarla, `npx skills update dossier`; para quitarla, `npx skills remove dossier`
(con `-g` si es la global).

Sin Node, a mano:

```bash
git clone https://github.com/SebasCaules/Dossier.git
mkdir -p ~/.claude/skills && cp -R Dossier/dossier ~/.claude/skills/
```

Además hace falta:

| | macOS | Ubuntu / Debian |
|---|---|---|
| LaTeX (LuaLaTeX y latexmk) | `brew install --cask mactex-no-gui` | `sudo apt install texlive-full` |
| Poppler (`pdftoppm`, `pdftotext`) | `brew install poppler` | `sudo apt install poppler-utils` |
| Python 3 | `pip3 install matplotlib numpy pillow pypdf pdfplumber` | igual |

En macOS usa la letra Avenir Next; en otros sistemas cae sola a TeX Gyre Heros.

## Usar

En Claude Code, escribir `/dossier`, los parámetros y el pedido:

```
/dossier breve lector=estudio un resumen de la unidad 3 con los apuntes de esta carpeta
/dossier 1 hoja impresion lo esencial del informe.pdf para llevar a la reunión
/dossier medio +imagenes lector=cliente un informe de ventas.csv para el directorio
```

También se activa sola cuando se pide un PDF para leer o compartir («quiero un PDF con lo
que hicimos»). Todos los parámetros son opcionales:

| Parámetro | Valores | Por defecto |
|---|---|---|
| Largo | `1 hoja` · `breve` (2 a 6 páginas) · `medio` (7 a 12) · `largo` (13 a 24) | `breve` |
| Texto | `-texto` · `+texto` | normal |
| Imágenes | `-imagenes` · `+imagenes` | normal |
| Lector | `estudio` · `entrega` · `equipo` · `cliente` | según el pedido |
| Formato | `digital` · `impresion` | `digital` |
| Ajustes | `temas=N` · `items=N` · `paginas=N` | — |

No importan las mayúsculas ni los acentos, y un error de tipeo se corrige si hay un solo
parámetro parecido; si no, la skill pregunta.

## Ejemplos

Hechos con la skill, sobre temas y fuentes públicas. Cada imagen abre su PDF; cada carpeta trae el
`.tex`, el código de los gráficos y un README con el pedido y las fuentes.

### [Doce estructuras de datos en una hoja](ejemplos/hoja-estructuras-de-datos/hoja-estructuras-de-datos.pdf)

`/dossier 1 hoja impresion -texto items=12` · 1 página: una hoja de consulta para imprimir, con la tabla de costos, un mapa de cómo se relacionan las estructuras y un gráfico (a la derecha, un detalle ampliado).

[![Doce estructuras de datos en una hoja](ejemplos/capturas/hoja-estructuras-de-datos.png)](ejemplos/hoja-estructuras-de-datos/hoja-estructuras-de-datos.pdf)

### [Cómo funciona HTTPS: de la URL al candado](ejemplos/breve-https/breve-https.pdf)

`/dossier breve lector=estudio` · 4 páginas: guía de estudio con mapa del tema, definición, ejemplo y confusión típica por concepto, preguntas de repaso y diagramas de secuencia.

[![Cómo funciona HTTPS: de la URL al candado](ejemplos/capturas/breve-https.png)](ejemplos/breve-https/breve-https.pdf)

### [Cómo guarda Git la historia por dentro](ejemplos/breve-git-por-dentro/breve-git-por-dentro.pdf)

`/dossier breve lector=entrega impresion` · 5 páginas: informe para entregar, con portada formal, resumen ejecutivo, sesiones de terminal con su salida, diagramas y referencias.

[![Cómo guarda Git la historia por dentro](ejemplos/capturas/breve-git-por-dentro.png)](ejemplos/breve-git-por-dentro/breve-git-por-dentro.pdf)

### [A quién llamar, cuándo y cuántas veces](ejemplos/medio-campana-depositos/medio-campana-depositos.pdf)

`/dossier medio lector=cliente +imagenes` · 7 páginas: informe para el área comercial de un banco ficticio, con la recomendación primero y 14 gráficos hechos con el dataset público Bank Marketing de UCI.

[![A quién llamar, cuándo y cuántas veces](ejemplos/capturas/medio-campana-depositos.png)](ejemplos/medio-campana-depositos/medio-campana-depositos.pdf)

## Qué hay adentro

```
dossier/
├── SKILL.md       ← el procedimiento que sigue Claude
├── plantilla/     ← dossier.sty (estilo LaTeX), plantillas .tex y estilo de los gráficos
├── scripts/       ← perfil.py (parámetros → números), nuevo.py, medir.py, revisar.py
└── referencias/   ← componentes, diagramas, escritura y problemas conocidos
```

## Actualizar

Con `npx skills update dossier` (o, si se instaló a mano, `git pull` en el clon y volver a
copiar la carpeta `dossier/`).
