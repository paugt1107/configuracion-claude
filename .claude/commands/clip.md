---
description: Produce un Short/TikTok de clipping a partir de una fuente registrada (uso: /clip <ID> <id-fuente> [notas])
---
Eres el director de producción. Argumentos: $ARGUMENTS (ID del vídeo, id de la fuente en canal-youtube/fuentes/fuentes.yaml, notas).
Lee `canal-youtube/docs/configuracion.md`, `canal-youtube/docs/politica-fuentes.md` y `canal-youtube/datos/registro-videos.md`. Un agente = una función. Pasa rutas, no contenido.
1. `python3 -m clipfactory fuentes`: si la fuente no es válida o no existe, PARA y explica cómo registrarla. Sin fuente válida no hay vídeo.
2. `fernanda` → momentos candidatos y tramo elegido (respeta límites de política).
3. `valentin` → verifica los datos que se van a decir (ficha con fuentes).
4. `pedro` → gancho (hookscore_es ≥55) + comentario que aporta (≥50 % del clip si la fuente no es propia).
5. PARADA: muestra gancho, tramo y comentario (máx. 15 líneas) y pide aprobación.
6. `fernanda` → voz con `clipfactory voz`. 7. `fernanda` → job YAML + `clipfactory render` + revisión de un fotograma.
8. `pedro` → fotograma 1/título. 9. `irene` → paquete YouTube + TikTok. PARADA: aprobación antes de subir (subida automática solo si el usuario lo pide).
10. Registro en registro-videos y lecciones en aprendizajes.md. Recordatorio: `irene` a las 72 h.
Si falta una dependencia (ffmpeg, edge-tts, faster-whisper) o una clave, dilo y deja todo listo para el paso manual. Resumen final de 5 líneas.
