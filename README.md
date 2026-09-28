# /dossier

Una skill para [Claude Code](https://claude.com/claude-code) que arma PDFs de lectura:
resúmenes para estudiar, informes para entregar, documentos para un equipo o un cliente y
hojas de consulta. Los hace con LaTeX, con gráficos, diagramas y navegación cliqueable, del
largo y con la cantidad de texto e imágenes que se le pidan. Antes de entregar, mide cada
compilación y mira cada página.

Los PDFs de [`ejemplos/`](ejemplos/) están hechos con la skill.

## Instalar

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

| Ejemplo | Pedido | Páginas |
|---|---|---|
| [Doce estructuras de datos](ejemplos/hoja-estructuras-de-datos/hoja-estructuras-de-datos.pdf) | `1 hoja impresion -texto items=12` | 1 |
| [Cómo funciona HTTPS](ejemplos/breve-https/breve-https.pdf) | `breve lector=estudio` | 4 |
| [Cómo guarda Git la historia](ejemplos/breve-git-por-dentro/breve-git-por-dentro.pdf) | `breve lector=entrega impresion` | 5 |
| [A quién llamar en una campaña](ejemplos/medio-campana-depositos/medio-campana-depositos.pdf) | `medio lector=cliente +imagenes` | 7 |

Cada carpeta trae el `.tex`, el código de sus gráficos y un README con el pedido y las
fuentes.

## Qué hay adentro

```
dossier/
├── SKILL.md       ← el procedimiento que sigue Claude
├── plantilla/     ← dossier.sty (estilo LaTeX), plantillas .tex y estilo de los gráficos
├── scripts/       ← perfil.py (parámetros → números), nuevo.py, medir.py, revisar.py
└── referencias/   ← componentes, diagramas, escritura y problemas conocidos
```

## Actualizar

```bash
cd Dossier && git pull && rm -rf ~/.claude/skills/dossier && cp -R dossier ~/.claude/skills/
```
