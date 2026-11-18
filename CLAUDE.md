# Reglas generales
- Responde siempre en español, directo y breve. Sin relleno.
- Antes de actuar en algo irreversible o externo (subir vídeos, gastar créditos, publicar), pide confirmación.
- No inventes datos: si no tienes la cifra real, dilo y marca "estimado".
- Ahorra tokens: NUNCA mostrar vídeos/imágenes en el chat (ni leer fotogramas salvo para depurar un fallo); subirlos a `entregas/<ID>/` en git y avisar solo con la ruta. Respuestas cortas.
- Ahorra tokens (cont.): lee solo los archivos necesarios, no repitas contexto.

# Oficina del canal de YouTube
Proyecto en `canal-youtube/`. Equipo = subagentes en `.claude/agents/`.
Lee `canal-youtube/README.md` solo cuando trabajes en el canal.
Nicho: GTA VI en español (Shorts + TikTok). Comandos: `/short <tema>` y `/clip <ID> <fuente>`. Código: `clipfactory/` (`python3 -m clipfactory -h`, tests con `python3 -m pytest -q`). Fuentes ajenas solo con permiso: `canal-youtube/politica-fuentes.md`. Equipo de 13 agentes con función única (ver `canal-youtube/README.md`): tendencias, estratega, guionista, voz-audio (locución IA), sonido, director-arte, animacion, packaging, editor (clipper), documentalista, studio, retencion, comunidad. Un skill = un dueño; no duplicar roles. Voz del canal: `canal-youtube/voice.md`.
Config y umbrales: `canal-youtube/config.md`. Los agentes se comunican por archivos en `canal-youtube/data/`.
Producción: guion = `canal-youtube/guiones/<ID>.yaml` (ver PLANTILLA.yaml). Push → GitHub Actions `produccion` genera voz IA (el usuario NUNCA graba), vídeo, 3 portadas y publicacion.md en `entregas/<ID>/` (log en `entregas/_logs/`). Radar cada 30 min: `canal-youtube/data/radar/ultimo.md`. Recortes de personajes: workflow `recortes` → `media/recortes/`.
