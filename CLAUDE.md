# Reglas generales
- Responde siempre en español, directo y breve. Sin relleno.
- Antes de actuar en algo irreversible o externo (subir vídeos, gastar créditos, publicar), pide confirmación.
- No inventes datos: si no tienes la cifra real, dilo y marca "estimado".
- Ahorra tokens: NUNCA mostrar vídeos/imágenes en el chat (ni leer fotogramas salvo para depurar un fallo); subirlos a `entregas/<ID>/` en git y avisar solo con la ruta. Respuestas cortas.
- Ahorra tokens (cont.): lee solo los archivos necesarios, no repitas contexto.

# Oficina del canal de YouTube
Proyecto en `canal-youtube/`. Equipo = subagentes en `.claude/agents/`.
Índice: `canal-youtube/README.md` (léelo solo cuando trabajes en el canal). Docs en `canal-youtube/docs/`, datos en `canal-youtube/datos/`.
Nicho: GTA VI en español (Shorts + TikTok). Comandos: `/short <tema>` y `/clip <ID> <fuente>`. Código: `clipfactory/` (`python3 -m clipfactory -h`, tests con `python3 -m pytest -q`). Fuentes ajenas solo con permiso: `canal-youtube/docs/politica-fuentes.md`. Equipo de 13 agentes con función única (ver `canal-youtube/README.md`): tendencias, estratega, guionista, voz-audio (locución IA), sonido, director-arte, animacion, packaging, editor (clipper), documentalista, studio, retencion, comunidad. Un skill = un dueño; no duplicar roles. Voz del canal: `canal-youtube/docs/voz-del-canal.md`.
Config y umbrales: `canal-youtube/docs/configuracion.md`. Los agentes se comunican por archivos en `canal-youtube/datos/`.
Producción: guion = `canal-youtube/guiones/<ID>.yaml` (ver PLANTILLA.yaml). Push → GitHub Actions `produccion` genera voz IA (el usuario NUNCA graba), vídeo, 3 portadas y publicacion.md en `entregas/<ID>/` (log en `entregas/_logs/`). Radar cada 30 min: `canal-youtube/datos/radar/ultimo.md`. Recortes de personajes: workflow `recortes` → `media/recortes/`.
Código: rutas centralizadas en `clipfactory/rutas.py`; antes de commit `ruff check clipfactory tests && python -m pytest`.
Pendientes del usuario: `canal-youtube/datos/pendientes.md` (revísalo al empezar y recuérdale lo que falte, en una línea).
Trabajadores: VALENTÍN (radar, 15 min) · PEDRO (guiones, SOLO cuando el usuario lo pida: /guiones) · FERNANDA (producción) · TOMMY (imágenes sincronizadas y recortes) · IRENE (calidad). Ver README.md.
Oficina virtual: https://claude.ai/artifact/WpekPno864dqoiPW63BjzQ (canal-youtube/docs/oficina.html). Al acabar cada tarea, actualízala: `python3 -m clipfactory.oficina <json>` y súbelo con ArtifactData set (colección oficina, doc estado).
Fases del canal: `canal-youtube/docs/fases.md` (fase activa: 2 = guías desde el lanzamiento; 3 = mods y GTA Online).
