#!/usr/bin/env node
// Instala la skill /dossier para Claude Code y todo lo que necesita: LaTeX (TinyTeX, si no
// hay una distribución), un entorno de Python con sus paquetes y una hoja de prueba.
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const AYUDA = `Uso: npx github:SebasCaules/Dossier [opciones]

Sin opciones instala la skill en el proyecto de la carpeta actual (.claude/skills/dossier
en la raíz del repositorio git, o en esta carpeta si no hay repositorio) y después todo lo
que necesita: LaTeX (TinyTeX, si no hay), un entorno de Python con sus paquetes, y compila
una hoja de prueba. No pide permisos de administrador.

  -g, --global      para todos los proyectos (~/.claude/skills/dossier)
  --capturas        suma Playwright y Chromium, para las capturas de pantalla
  --solo-skill      copia la skill y no instala nada más
  --verificar       solo dice qué hay y qué falta
  --desinstalar     quita la skill (no toca LaTeX ni el entorno de Python)
  -h, --help        esta ayuda`;

const opciones = { global: false, capturas: false, soloSkill: false, verificar: false, desinstalar: false };
for (const arg of process.argv.slice(2)) {
  if (arg === '-g' || arg === '--global') opciones.global = true;
  else if (arg === '--capturas') opciones.capturas = true;
  else if (arg === '--solo-skill') opciones.soloSkill = true;
  else if (arg === '--verificar') opciones.verificar = true;
  else if (arg === '--desinstalar') opciones.desinstalar = true;
  else if (arg === '-h' || arg === '--help') { console.log(AYUDA); process.exit(0); }
  else { console.error(`Opción desconocida: ${arg}\n\n${AYUDA}`); process.exit(2); }
}

function raizDelProyecto() {
  const r = spawnSync('git', ['rev-parse', '--show-toplevel'], { encoding: 'utf8' });
  return r.status === 0 && r.stdout.trim() ? r.stdout.trim() : process.cwd();
}

function version(carpeta) {
  try {
    const m = fs.readFileSync(path.join(carpeta, 'SKILL.md'), 'utf8').match(/^version:\s*"?([^"\n]+)"?/m);
    return m ? m[1] : null;
  } catch { return null; }
}

function pythonDisponible() {
  for (const cmd of ['python3', 'python']) {
    const r = spawnSync(cmd, ['-c', 'import sys; print(sys.version_info >= (3, 9))'], { encoding: 'utf8' });
    if (r.status === 0 && r.stdout.trim() === 'True') return cmd;
  }
  return null;
}

const baseClaude = opciones.global
  ? (process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude'))
  : path.join(raizDelProyecto(), '.claude');
const destino = path.join(baseClaude, 'skills', 'dossier');
const origen = path.join(__dirname, '..', 'dossier');
const donde = opciones.global ? 'para todos los proyectos' : 'en este proyecto';

if (opciones.desinstalar) {
  if (fs.existsSync(destino)) {
    fs.rmSync(destino, { recursive: true, force: true });
    console.log(`Quité la skill de ${destino}.`);
  } else {
    console.log(`No hay skill en ${destino}.`);
  }
  process.exit(0);
}

if (!opciones.verificar) {
  const anterior = version(destino);
  fs.rmSync(destino, { recursive: true, force: true });
  fs.mkdirSync(path.dirname(destino), { recursive: true });
  fs.cpSync(origen, destino, { recursive: true, filter: (f) => !/(__pycache__|\.DS_Store|\.pyc)$/.test(f) });
  const nueva = version(destino);
  const cambio = anterior && anterior !== nueva ? ` (antes ${anterior})` : '';
  console.log(`Skill /dossier ${nueva}${cambio} instalada ${donde}: ${destino}`);
  if (opciones.soloSkill) {
    console.log('Para instalar lo que necesita: ' +
      `python3 "${path.join(destino, 'scripts', 'dependencias.py')}" instalar`);
    process.exit(0);
  }
}

if (process.platform === 'win32') {
  console.log('\nEn Windows las dependencias no se instalan solas: TeX Live (https://tug.org/texlive/) ' +
    'y, con pip, matplotlib numpy pillow pypdf pdfplumber pypdfium2. La skill funciona mejor dentro de WSL.');
  process.exit(opciones.verificar ? 1 : 0);
}

const python = pythonDisponible();
if (!python) {
  console.error('\nFalta Python 3.9 o más nuevo, que la skill usa para medir y dibujar.\n' +
    (process.platform === 'darwin'
      ? '  En macOS: xcode-select --install  (o https://www.python.org/downloads/)'
      : '  En Debian o Ubuntu: sudo apt install python3') +
    '\nDespués, volver a correr este comando.');
  process.exit(1);
}

const script = path.join(opciones.verificar && !fs.existsSync(destino) ? origen : destino, 'scripts', 'dependencias.py');
const args = [script, opciones.verificar ? 'verificar' : 'instalar'];
if (opciones.capturas && !opciones.verificar) args.push('--capturas');
console.log(opciones.verificar ? '' : '\nInstalando lo que necesita (la primera vez tarda unos minutos)…\n');
const r = spawnSync(python, ['-B', ...args], { stdio: 'inherit', env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' } });
if (r.status === 0 && !opciones.verificar) {
  console.log(`\nListo. En Claude Code, ${opciones.global ? 'en cualquier proyecto' : 'en ' + path.dirname(baseClaude)}, ` +
    'escribir /dossier y lo que se quiere, por ejemplo:\n  /dossier breve lector=estudio un resumen de los apuntes de esta carpeta');
}
process.exit(r.status === null ? 1 : r.status);
