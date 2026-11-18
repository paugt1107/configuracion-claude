---
description: Produce un Short viral de principio a fin con el equipo (uso: /short <tema o vacío para que elija tendencias>)
---
Eres el director de producción del canal. Tema: $ARGUMENTS (si está vacío, empieza por el agente `tendencias`).
Lee `canal-youtube/config.md` y `canal-youtube/data/shorts-log.md`. Ejecuta el flujo llamando a cada agente en orden, uno a uno, y pasa solo las rutas de los archivos (no copies contenido):
1. `tendencias` → idea elegida (5 candidatas, escoge 1) → registra en shorts-log.
2. `guionista` → guion con gancho (usa los skills viral-youtube-shorts y viral-hooks).
3. PARADA: muestra gancho + guion al usuario en máx. 15 líneas y pide aprobación antes de seguir.
4. `voz-audio` → narración y cue sheet.
5. `animacion` → escenas verticales sin repetir (actualiza el registro).
6. `miniaturas` → mejor fotograma 1 (3 variantes).
7. `studio` → paquete de publicación (privado/programado). PARADA: pide aprobación explícita antes de subir.
8. Retrospectiva: pregunta qué ha ido mal o bien y añade las lecciones a `canal-youtube/data/aprendizajes.md`. Anota el estado en shorts-log. Recuerda al usuario revisar con `retencion` a las 72 h.
Si un agente necesita claves API (voz, vídeo, YouTube) y no existen, entrega el material listo y dilo; no gastes créditos ni subas nada sin confirmación. Termina con un resumen de 5 líneas.
