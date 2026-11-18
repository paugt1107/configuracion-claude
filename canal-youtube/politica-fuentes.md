# Política de fuentes y derechos (OBLIGATORIA)
Por qué existe: en YouTube hay DOS sistemas independientes y los dos pueden hundir el canal.
1. **Contenido reutilizado** (monetización, se evalúa a nivel de CANAL): admite comentario, análisis y reacción con aportación propia; NO admite recopilaciones de clips con poca o ninguna narración. Aplica aunque tengas permiso del autor.
2. **Copyright / Content ID**: aunque el vídeo sea transformador, el titular puede reclamar ingresos, bloquear o dar un aviso (3 avisos = canal cerrado).
Además: la política pública de Rockstar sobre su material se refiere a uso ocasional y NO comercial por fans; Take-Two se reserva retirar contenido. Las radios del juego tienen música con licencia (reclamaciones de Content ID).
Fuentes: vidiq.com (reused content), air.io, theprint.in (declaración de YouTube 2026: el cambio "inauthentic" no apunta a reacciones/clips con aportación), support.rockstargames.com (resumen vía búsqueda), dexerto.com (reglas de violencia en gaming 2026). Verificar en los centros de ayuda oficiales antes de monetizar.

## Tipos de fuente (el código `clipfactory` lo hace cumplir)
| Tipo | Qué es | Límite por clip | Requisitos |
|---|---|---|---|
| `propia` | Tu captura de PS5/Xbox | sin límite | Radio del juego apagada o audio silenciado si suena música con licencia |
| `oficial` | Tráilers/material oficial de Rockstar | 15 s | Crédito visible + comentario propio ≥ 50 % del clip; sin spoilers filtrados |
| `permiso` | Clip de otro creador | 45 s (o lo que diga el permiso) | Prueba del permiso guardada (`permiso:`) + crédito "Clip: @canal" + comentario ≥ 50 % |
| `cc-by` | Licencia Creative Commons con atribución | 30 s | Licencia indicada + crédito |
| PROHIBIDO | Filtraciones (p. ej. la de 2022), resubidas sin permiso, material pirata, contenido de pago, clips de directos sin permiso | — | El código lo rechaza |

## Cómo conseguir clips de otros creadores legalmente
- **Campañas de clipping**: muchos creadores y marcas pagan a "clippers" por vistas (plataformas tipo Whop Clipping y similares; p. ej. pagos por cada 1.000 vistas). Ahí el permiso viene en las condiciones de la campaña: guarda captura o enlace en `canal-youtube/fuentes/permisos/`.
- **Permiso directo**: mensaje al creador con: qué vídeo, qué tramo, dónde se publica, cómo se acredita. Guarda la respuesta.
- **Sin respuesta = no se usa.** Sin excepciones.

## Reglas de transformación (lo que nos hace "originales")
1. Gancho propio en el fotograma 1 (no el del autor).
2. Voz/comentario propio ≥ 50 % del tiempo cuando la fuente no es tuya: explicar, contextualizar, comparar, corregir.
3. Edición propia: zoom, flechas, capturas de mapa, texto, montaje.
4. Crédito visible en pantalla + enlace en la descripción/comentario fijado.
5. Nada de "compilaciones" sin narración ni subir el mismo clip a varias cuentas.

## Spoilers
Las 2 primeras semanas tras el lanzamiento: nada de giros de historia en título, miniatura o primeros 3 s. Si hay spoiler, "SPOILER" visible al principio. Rockstar ha pedido históricamente no publicar spoilers.

## Anuncios (violencia en gaming)
Según informaciones de 2026 (Dexerto), YouTube permite anuncios con violencia gráfica de juego si no aparece en los primeros segundos (se citan 8-15 s) y no es una recopilación hecha para impactar. Regla interna: **los primeros 10 s sin violencia gráfica**; nada de "matanzas de NPC".

## Si llega una reclamación
1. No discutir en caliente. 2. Si es válida: retirar o recortar el tramo. 3. Anotar la lección en `data/aprendizajes.md`. 4. Disputar solo si la fuente es `propia` u `oficial` con comentario claro y la reclamación es errónea.
