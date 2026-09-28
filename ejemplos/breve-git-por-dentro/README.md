# Ejemplo: informe breve para entregar

Un informe técnico de 5 páginas, listo para imprimir, sobre cómo guarda Git la historia
por dentro: objetos blob, tree y commit, referencias y ramas, y qué escribe un merge. Muestra
la portada formal con renglones para completar, el resumen ejecutivo, las sesiones de
terminal con su salida, cinco diagramas, un gráfico y las referencias citadas en cada párrafo.

Lo generó este pedido:

```
/dossier breve lector=entrega impresion
Un informe técnico para entregar: cómo guarda Git la historia por dentro (objetos blob,
tree y commit, referencias y ramas, qué hace un merge), con fragmentos de comandos y su salida.
```

## Fuentes

- Scott Chacon y Ben Straub, *Pro Git*, 2.ª edición, secciones 3.1, 10.2, 10.3 y 10.4
  (<https://git-scm.com/book/en/v2>, licencia CC BY-NC-SA 3.0). Se cita; no se copia.
- Documentación oficial de Git: `git-merge`, `git-merge-base` y `git-cat-file`
  (<https://git-scm.com/docs>).
- Las salidas de los comandos y las cifras del gráfico salen de `demo.sh`, que arma un
  repositorio de prueba con autor, fechas y contenido fijos. La autora «Ana Ejemplo» es
  ficticia.

## Regenerar

Desde esta carpeta, con la skill instalada:

```
sh demo.sh                       # imprime cada comando del informe con su salida
python3 graficos.py              # rehace fig/f1_escritos_reutilizados.pdf (corre demo.sh)
python3 ~/.claude/skills/dossier/scripts/medir.py breve-git-por-dentro.tex --paginas 5 --paginas-min 2 --paginas-texto 2.0 --parte-texto 0.4 --densa 550 --visuales-min 4 --lector entrega
```

`medir.py` compila (los auxiliares van a `_build/`) y controla el largo, el texto y las
piezas visuales del perfil. Sin la skill, alcanza con `latexmk -lualatex breve-git-por-dentro.tex`.
