# Reglas generales
- Responde siempre en español, directo y breve. Sin relleno.
- Antes de actuar en algo irreversible o externo (subir vídeos, gastar créditos, publicar), pide confirmación.
- No inventes datos: si no tienes la cifra real, dilo y marca "estimado".
- Ahorra tokens: NUNCA mostrar vídeos/imágenes en el chat (ni leer fotogramas salvo para depurar un fallo); subirlos a `entregas/<ID>/` en git y avisar solo con la ruta. Respuestas cortas.
- Ahorra tokens (cont.): lee solo los archivos necesarios, no repitas contexto.

# Oficina del canal de YouTube
Proyecto en `canal-youtube/`. Equipo = subagentes en `.claude/agents/`.
Lee `canal-youtube/README.md` solo cuando trabajes en el canal.
Nicho: GTA VI en español (Shorts + TikTok). Comandos: `/short <tema>` y `/clip <ID> <fuente>`. Código: `clipfactory/` (`python3 -m clipfactory -h`, tests con `python3 -m pytest -q`). Fuentes ajenas solo con permiso: `canal-youtube/politica-fuentes.md`. Equipo de 12 agentes con función única (ver `canal-youtube/README.md`): tendencias, estratega, guionista, voz-audio, director-arte, animacion, packaging, editor (clipper), documentalista, studio, retencion, comunidad. Un skill = un dueño; no duplicar roles. Voz del canal: `canal-youtube/voice.md`.
Config y umbrales: `canal-youtube/config.md`. Los agentes se comunican por archivos en `canal-youtube/data/`.
