# breve-https

Guía de estudio de 4 páginas sobre cómo funciona HTTPS, de la URL al candado: DNS, TCP, el
handshake de TLS 1.3, certificados y cadena de confianza, y qué protege y qué no. Muestra el
perfil `breve` con `lector=estudio`: mapa del tema cliqueable en la portada, tríada
(definición, ejemplo, confusión típica), repaso al cierre de cada sección, un gráfico y cinco
diagramas.

Generado con:

```
/dossier breve lector=estudio Un resumen para estudiar cómo funciona HTTPS: de la URL al candado (DNS, TCP, el handshake de TLS 1.3, certificados y cadena de confianza, qué protege y qué no).
```

## Fuentes

Todas públicas; en el PDF se citan por sigla con la sección (`RFC 8446, §2.3`):

- RFC 8446 (TLS 1.3), RFC 5246 (TLS 1.2), RFC 9110 (semántica de HTTP), RFC 9293 (TCP),
  RFC 1035 (DNS), RFC 8484 (DNS sobre HTTPS) y RFC 5280 (certificados X.509), en
  <https://www.rfc-editor.org/>.
- MDN Web Docs, *Transport Layer Security (TLS)*.
- Let's Encrypt, *Chains of Trust* (actualizada el 8 de julio de 2026) y *How It Works*.

Los viajes de ida y vuelta (RTT) del gráfico son una cuenta propia sobre los diagramas de
mensajes de las RFC; `graficos.py` los tiene comentados con la figura de origen. Quedaron
afuera HTTP/3 y QUIC, la revocación en línea (OCSP) y Certificate Transparency.

## Regenerar

Desde esta carpeta, con la skill instalada:

```
python3 graficos.py
python3 ~/.claude/skills/dossier/scripts/medir.py breve-https.tex --paginas 5 --paginas-min 2 --paginas-texto 2.0 --parte-texto 0.4 --densa 550 --visuales-min 4 --lector estudio
```

`medir.py` compila (los auxiliares van a `_build/`) y controla el largo, el texto y las
piezas visuales del perfil. Sin la skill alcanza con `latexmk -lualatex breve-https.tex`.
