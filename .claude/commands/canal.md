---
description: TODO el canal con una sola orden — qué busca la gente, N guiones sin repetir gancho, vídeos montados, títulos/portadas/descripción y calendario (uso: /canal [cuántos vídeos, por defecto 10])
---
Eres el DIRECTOR del canal. Una sola orden, todo el ciclo, para el juego de `canal-youtube/fuentes/juego.yaml` (si el dueño cambia el juego ahí, todo funciona igual). Argumentos: $ARGUMENTS (número de vídeos; por defecto 10).

1. `git pull --rebase origin main`. Lee: `canal-youtube/datos/pendientes.md` (recuerda en una línea lo que falte), `canal-youtube/docs/fases.md` (fase activa), `canal-youtube/datos/demanda.md` (QUÉ BUSCA la gente: autocompletado de Google y YouTube), `canal-youtube/datos/radar/ultimo.md` y `historia.md` (lo último, todos los idiomas), `canal-youtube/datos/registro-videos.md` (lo ya hecho) y las últimas 20 líneas de `aprendizajes.md`.
2. Si no existe una marca para el juego (entregas/marca/), créala: nombre del canal (juego.yaml → canal), `python3 -m clipfactory marca` (banner 2560x1440 y avatar) y `canal-youtube/docs/crear-canales.md`.
3. Elige N temas distintos cruzando demanda (lo que se busca) × radar (lo que acaba de pasar) × fase activa. Prioriza: frases 🆕 de demanda.md, guías de la fase 2, secretos verificados. Ningún tema repetido del registro.
4. Escribe los N guiones siguiendo `/guiones` al pie de la letra (verificar datos con el agente documentalista, gancho ≥ 55 y `calidad.gancho_repetido` = None también ENTRE los N nuevos, estilo diorama + 3D + banco de imágenes, sin spoilers hasta el 3-dic, fuentes con fecha). Registra cada uno en registro-videos.md (estado "guion").
5. Valida (`ruff check clipfactory tests && python3 -m pytest -q`), commit y push. FERNANDA monta cada vídeo en GitHub Actions (voz IA, música, efectos, pausas de misterio, subtítulos, imágenes de TOMMY), IRENE revisa (control-calidad.md) y el calendario reparte los APTO desde el próximo jueves (`canal-youtube/datos/calendario.md` + `.ics`).
6. Espera a que termine la producción (`gh run list -w produccion.yml`), revisa los control-calidad.md: si alguno sale ⚠️ REVISAR, arregla el guion y vuelve a subirlo (máx. 2 vueltas).
7. Actualiza la oficina (`python3 -m clipfactory.oficina` + ArtifactData set, ver CLAUDE.md).
8. Resume en pocas líneas: tabla ID · gancho · fecha de publicación, y lo que tiene que hacer el dueño (subir los vídeos a su hora; la subida automática necesita sus credenciales de YouTube/TikTok).
