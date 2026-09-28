#!/bin/sh
# Repositorio de prueba del informe: arma un repositorio chico en una carpeta temporal y
# muestra cada comando con su salida, tal como aparecen en el PDF. Autor, fechas y
# contenido son fijos, así que los hashes salen iguales en cualquier máquina.
#   sh demo.sh
set -e
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME="Ana Ejemplo" GIT_AUTHOR_EMAIL="ana@example.com"
export GIT_COMMITTER_NAME="Ana Ejemplo" GIT_COMMITTER_EMAIL="ana@example.com"
export LC_ALL=C TZ=UTC

fecha() { export GIT_AUTHOR_DATE="$1 +0000" GIT_COMMITTER_DATE="$1 +0000"; }
cmd() { printf '$ %s\n' "$*"; sh -c "$*"; }
objetos() { find .git/objects -type f ! -path '*/info/*' ! -path '*/pack/*' | wc -l | tr -d ' '; }
titulo() { printf '\n## %s\n' "$1"; }

DIR=$(mktemp -d)
cd "$DIR"
git init -q -b main recetario
cd recetario
git config core.autocrlf false

titulo "1. Un blob: el contenido y su hash"
cmd "find .git/objects -type f"
cmd "echo 'harina, agua, sal' | git hash-object -w --stdin"
cmd "find .git/objects -type f"
cmd "git cat-file -t 23e2177"
cmd "git cat-file -s 23e2177"
# El mismo hash, calculado a mano: encabezado «blob <bytes>\0» + contenido, con SHA-1.
cmd "printf 'blob 18\\000harina, agua, sal\\n' | shasum -a 1"

titulo "2. Primer commit: tree y commit"
mkdir recetas
echo "Recetario de ejemplo" > README.md
echo "harina, agua, sal" > recetas/pan.txt
git add README.md recetas/pan.txt
fecha "2026-03-02T10:00:00"
git commit -q -m "Primera receta"
echo "objetos tras el commit 1: $(objetos)"
cmd "git cat-file -p HEAD"
cmd "git cat-file -p 'HEAD^{tree}'"
cmd "git cat-file -p 'HEAD^{tree}:recetas'"

titulo "3a. El segundo commit, a mano, en una copia del repositorio (anexo)"
cp -R ../recetario ../a-mano
cd ../a-mano
fecha "2026-03-03T10:00:00"
echo "harina, agua, sal, levadura" > recetas/pan.txt
cmd "git update-index recetas/pan.txt"
cmd "git write-tree"
cmd "echo 'Pan con levadura' | git commit-tree 44b097b -p HEAD"
cmd "git update-ref refs/heads/main e5086a9"
cmd "git log --oneline"
cd ../recetario

titulo "3. Segundo commit: solo se escribe lo que cambió"
antes=$(objetos)
echo "harina, agua, sal, levadura" > recetas/pan.txt
git add recetas/pan.txt
fecha "2026-03-03T10:00:00"
git commit -q -m "Pan con levadura"
echo "objetos nuevos en el commit 2: $(( $(objetos) - antes ))"
cmd "git cat-file -p 'HEAD^{tree}'"
cmd "git cat-file -p 'HEAD^{tree}:recetas'"
cmd "git cat-file -p HEAD | head -3"

titulo "4. Referencias y ramas"
cmd "cat .git/HEAD"
cmd "cat .git/refs/heads/main"
cmd "wc -c < .git/refs/heads/main"
cmd "git branch sopa"
cmd "cat .git/refs/heads/sopa"
cmd "git symbolic-ref HEAD"

titulo "5. Merge por avance rápido"
git switch -q -c postres
echo "azúcar, huevos, leche" > recetas/flan.txt
git add recetas/flan.txt
fecha "2026-03-04T10:00:00"
git commit -q -m "Flan"
git switch -q main
cmd "git merge postres"
cmd "git log --oneline --graph"

titulo "6. Merge de tres vías"
git switch -q sopa
echo "zapallo, cebolla, caldo" > recetas/sopa.txt
git add recetas/sopa.txt
fecha "2026-03-05T10:00:00"
git commit -q -m "Sopa"
git switch -q main
echo "Recetario de ejemplo: pan, flan y sopa" > README.md
git add README.md
fecha "2026-03-06T10:00:00"
git commit -q -m "README con las tres recetas"
cmd "git merge-base main sopa"
fecha "2026-03-07T10:00:00"
cmd "git merge --no-edit sopa"
cmd "git cat-file -p HEAD"
cmd "git log --oneline --graph"
cmd "git count-objects -v | head -2"

titulo "7. Conteo por commit (para el gráfico)"
# Por cada commit, cuántas entradas de sus trees (incluido el tree raíz) y cuántos
# objetos escribe por primera vez y cuántos reutiliza de commits anteriores.
vistos=$(mktemp)
for c in $(git rev-list --reverse --date-order HEAD); do
  nuevos=0; reus=0
  for o in $(git rev-parse "$c^{tree}") $(git ls-tree -r -t "$c" | awk '{print $3}'); do
    if grep -qx "$o" "$vistos"; then reus=$((reus + 1)); else nuevos=$((nuevos + 1)); echo "$o" >> "$vistos"; fi
  done
  echo "$(git log -1 --format=%s "$c")|$((nuevos + 1))|$reus"
done

rm -rf "$DIR"
