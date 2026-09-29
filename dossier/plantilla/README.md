# NOMBRE

[`NOMBRE.pdf`](../pdfs/NOMBRE.pdf): <para quién es y qué responde, en una línea>. Creado el
FECHA con la skill `/dossier`, perfil PERFIL.

## Regenerar

Desde esta carpeta:

```
python3 graficos.py              # rehace los gráficos del documento en fig/ (si los tiene)
MEDIR
```

`medir.py` compila (los auxiliares van a `_build/`), deja el PDF en `../pdfs/`, junto a los
de los demás documentos, y controla el largo, el texto y las piezas visuales del perfil.
Sin la skill a mano basta con `latexmk`: lee `latexmkrc` y deja el PDF en el mismo lugar.

## Fuentes

- <archivo o registro del proyecto de donde salen las cifras, y cómo se citan en el texto>
- Paleta: <la de dossier.sty, o los tokens de dónde>
