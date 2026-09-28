# Ejemplo: informe mediano para un cliente, con datos

Un informe de 7 páginas para el área comercial de un banco ficticio: a quién llamar en la
próxima campaña de depósitos a plazo, cuándo y cuántas veces. Muestra el perfil `medio`
con `lector=cliente` y `+imagenes`: la recomendación en la portada, una sección por
decisión, una tabla de qué gana y qué cuesta cada una, lo que se necesita del lado del
cliente, y 14 gráficos y 4 diagramas hechos con datos reales.

Lo generó este pedido:

```
/dossier medio lector=cliente +imagenes
Un informe para el área comercial de un banco (ficticio): a quién conviene llamar en la
próxima campaña de depósitos a plazo, cuándo y cuántas veces, con los datos de las
campañas anteriores.
```

## Fuentes

- **BM**: Moro, S., Rita, P. y Cortez, P. *Bank Marketing* [dataset]. UCI Machine Learning
  Repository, 2014. Licencia CC BY 4.0. <https://doi.org/10.24432/C5K306>. Se usa el
  archivo `bank-additional-full.csv` (41.188 clientes llamados por un banco portugués de
  mayo de 2008 a noviembre de 2010) y su descripción, `bank-additional-names.txt`.
- **MCR**: Moro, S., Cortez, P. y Rita, P. A Data-Driven Approach to Predict the Success
  of Bank Telemarketing. *Decision Support Systems*, 2014.
  <https://doi.org/10.1016/j.dss.2014.03.001>. Se cita como origen de los datos.
- Todas las cifras son cálculos propios con `graficos.py`. El banco, su área comercial y el
  «equipo de análisis de datos» que firma son ficticios. La columna `duration` (duración
  de la llamada) no se usa: se conoce después de llamar. Paleta: la de `dossier.sty`.

## Regenerar

Los datos no vienen con el ejemplo. Bajar el zip de
<https://archive.ics.uci.edu/dataset/222/bank+marketing>, descomprimir
`bank-additional.zip` que viene adentro y dejar `bank-additional-full.csv` en `datos/`.
Hace falta `pandas` y, para la curva del puntaje estadístico, `scikit-learn`. Desde esta
carpeta, con la skill instalada:

```
python3 graficos.py              # rehace los 14 gráficos de fig/
python3 graficos.py cifras       # imprime cada cifra que cita el texto
python3 ~/.claude/skills/dossier/scripts/medir.py medio-campana-depositos.tex --paginas 9 --paginas-min 7 --paginas-texto 2.7 --parte-texto 0.3 --densa 550 --visuales-min 14 --lector cliente
```

`medir.py` compila (los auxiliares van a `_build/`) y controla el largo, el texto y las
piezas visuales del perfil. Sin la skill, alcanza con
`latexmk -lualatex medio-campana-depositos.tex`.
