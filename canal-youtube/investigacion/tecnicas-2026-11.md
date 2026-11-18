# Investigación: qué hacen los proyectos públicos de GitHub (18-nov-2026)
Método: búsqueda web + lectura de los README de 5 repositorios. Etiquetas: [ALTA] coincide en varias fuentes; [MEDIA] una fuente concreta; [HIPÓTESIS] afirmación del autor sin datos independientes.

## Hallazgo honesto
- Ningún repositorio de los encontrados demuestra viralidad con datos independientes. Son jóvenes (0-59 estrellas), con métricas propias y mucho texto promocional. Lo valioso es lo que se REPITE entre ellos, no sus promesas.
- Pipeline común en generadores "faceless" (frameforge/purffle-shorts, ai-shorts-generator, content-factory): tema → guion con LLM → "Script Doctor" (puntuar y reescribir) → voz TTS con marcas de tiempo por palabra → imágenes o stock por escena → subtítulos palabra a palabra → render (ffmpeg/Remotion) → revisión humana → subida.
- Los que suben solos usan la API oficial de YouTube con OAuth y límite diario; TikTok/Instagram vía servicios de pago (Upload-Post) y su propio README dice que no los probó en cuentas reales [MEDIA].

## Técnicas con consenso [ALTA]
1. Gancho en 0-3 s; el primer fotograma ES un segundo gancho (debe leerse sin sonido y con la UI de la app encima).
2. Re-ganchos cada 5-8 s: cerrar una pregunta y abrir la siguiente justo donde el espectador podría irse (reel-runbook).
3. Final en bucle: acabar en el pago y que enlace con la primera frase (reel-runbook, viral-youtube-shorts).
4. Subtítulos palabra a palabra con la palabra activa resaltada, en zona segura (iart, frameforge, content-factory).
5. Audio: música libre/CC0 con ducking bajo la voz, normalizada a -14 LUFS (content-factory).
6. Señales de ranking que repiten todas las guías: tiempo de visionado, % completado, compartidos, repeticiones, guardados [ALTA en dirección; los umbrales numéricos son HIPÓTESIS: ninguna plataforma los publica].
7. Un "Script Doctor": puntuar el borrador y reescribir antes de producir (frameforge). Aquí lo hace `guionista` con hookscore.py.
8. Test del primer segundo: recorta el primer segundo; si el gancho sigue funcionando, ese segundo era relleno (reel-runbook).

## Personajes y consistencia visual [MEDIA]
- Content-factory: el primer fotograma fija el estilo; los siguientes se generan EDITANDO el anterior (solo cambia el estado del mundo) para que la cámara y el estilo no cambien; un reparto fijo de personajes con descripción + imágenes de referencia en cada generación.
- Higgsfield "Soul ID": entrena una identidad con 5+ fotos y la reutiliza en varios modelos de vídeo. Las comparativas encontradas son del propio proveedor [HIPÓTESIS]. Probar con 1 personaje antes de pagar plan anual.
- Alternativa gratis/barata: ilustración vectorial dibujada por el propio Claude (SVG) animada con movimiento de cámara; menos "wow", coherencia total y coste cero.

## Riesgo de política (el más importante para escalar) [MEDIA, verificar en fuente oficial]
- YouTube evalúa la SALIDA, no la herramienta: contenido masivo, genérico o de plantilla puede quedar excluido de monetización a nivel de canal; los Shorts son zona vigilada. Contenido sintético realista requiere etiqueta de IA. No pude abrir la página oficial (dominio bloqueado en esta sesión): verificar en el Centro de Ayuda de YouTube antes de monetizar.
- Consecuencia para el sistema: calidad y variedad por encima de cantidad; cada vídeo con aportación propia (verificación de datos, enfoque, voz propia); no 20 clones al día.

## Qué NO copiamos
Subidas masivas automáticas, scraping de Reddit sin permiso del autor, marcas de agua ajenas, claims de "vídeo viral garantizado".

## Fuentes
github.com/iart-ai/tiktok-video-skills · github.com/opus-pro/reel-runbook · github.com/jutsuhq/content-factory · github.com/tscupit/frameforge (fork de purffle-shorts) · github.com/vyralcontent/content-skills · higgsfield.ai/blog (comparativas del proveedor) · eclincher/hootsuite/darkroomagency (algoritmo TikTok) · air.io, vidiq.com, techrepublic.com (política YouTube 2026)
