# Reglas generales
- Responde siempre en español, directo y breve. Sin relleno.
- Antes de actuar en algo irreversible o externo (subir vídeos, gastar créditos, publicar), pide confirmación.
- No inventes datos: si no tienes la cifra real, dilo y marca "estimado".
- Ahorra tokens: lee solo los archivos necesarios, no repitas contexto.

# Oficina del canal de YouTube
Proyecto en `canal-youtube/`. Equipo = subagentes en `.claude/agents/`.
Lee `canal-youtube/README.md` solo cuando trabajes en el canal.
Formato: YouTube Shorts. Comando: `/short <tema>`. Equipo de 11 agentes con función única (ver `canal-youtube/README.md`): tendencias, estratega, guionista, voz-audio, director-arte, animacion, packaging, editor, studio, retencion, comunidad. Un skill = un dueño; no duplicar roles. Voz del canal: `canal-youtube/voice.md`.
Config y umbrales: `canal-youtube/config.md`. Los agentes se comunican por archivos en `canal-youtube/data/`.
