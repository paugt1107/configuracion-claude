# Oficina virtual del canal — 12 agentes, 1 función cada uno, 0 solapes

Regla anti-solape: cada skill tiene UN dueño y cada tarea UN agente. Si dos hacen lo mismo, se elimina uno.
Comandos: `/short <tema>` (Short original) y `/clip <ID> <fuente>` (clipping con política de fuentes). Código: `clipfactory/` (ver MANUAL.md). Memoria compartida: `data/aprendizajes.md`. Voz del canal: `voice.md` (rellenar primero).

| Agente | Modelo | Única función | Skills (dueño exclusivo) | Entrega |
|---|---|---|---|---|
| tendencias | sonnet | Elegir nicho, alarma 10x, ideas | yt-viral, viral-short-form-ideas | data/tendencias.md, alertas.md |
| estratega | sonnet | Plan semanal y auditoría (1 arreglo) | yt-plan, yt-audit | data/plan-semanal.md |
| guionista | opus | Gancho + guion (y reescritura) | yt-script (hookscore), viral-youtube-shorts, viral-tiktok-content | guiones/ |
| voz-audio | haiku | Narración TTS + música/efectos | — | audio/ |
| director-arte | sonnet | Personajes, paleta y fichas (identidad visual) | — (personajes.md) | personajes.md |
| animacion | sonnet | Escenas 9:16 sin repetir | — | guiones/*-escenas.md |
| packaging | sonnet | Título + miniatura/fotograma 1 | yt-package (title.py) | miniaturas/ |
| editor | haiku | Clipping: momentos de fuentes autorizadas, job y render 9:16 | yt-edit, yt-chapters, yt-shorts + clipfactory | jobs/*.yaml, salida/*.mp4 |
| documentalista | sonnet | Datos verificados de GTA VI (misiones, personajes, lugares) | — (base de conocimiento) | investigacion/gta-vi-base.md, investigacion/gta/ |
| studio | haiku | Descripción, etiquetas, comentario fijado, hora | yt-seo | data/publicacion-*.md |
| retencion | sonnet | Datos de retención/VVSA → aviso | yt-retention | data/retencion.md |
| comunidad | sonnet | Comentarios y comentario fijado | yt-comment | respuestas listas |

Skills de apoyo sin dueño-agente: `prompt-master` (optimiza prompts para Runway/Kling/Midjourney/ElevenLabs cuando se pida). Eliminado por solapar con yt-script: `viral-hooks`.
Ciclo Short: tendencias → guionista → [aprobación] → voz-audio → animacion → packaging → studio → [aprobación] → (72 h) retencion → (reabre guionista). Largos: + editor.

## Quién usa qué dato (flujo)
tendencias→ideas | guionista→guion | voz-audio/animacion/packaging←guion | studio←título(packaging)+capítulos(editor) | retencion→aviso→guionista/packaging | comunidad→ideas→tendencias.

## Base de conocimiento
`investigacion/tecnicas-2026-11.md` (qué hacen los repos públicos, con nivel de evidencia), `personajes.md`, `voice.md` (borrador v0).

## Límites honestos
- Nadie sube a YouTube: tú subes. Las claves API (voz, vídeo) solo si decides usarlas; sin ellas todo queda listo para hacer a mano.
- hookscore.py es una heurística, no un predictor; la puntuación de miniaturas es predicción hasta tener CTR real.
- Todo se aprende de los datos reales: `retencion` y `aprendizajes.md` cierran el ciclo.
