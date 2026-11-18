# configuracion-claude — fábrica de Shorts/TikToks de GTA VI en español

Sistema para producir vídeos cortos virales **sin poner en riesgo el canal**: 12 agentes de Claude Code con una función cada uno, skills de contenido revisados, y `clipfactory`, el código que corta, subtitula, pone voz y renderiza en 1080x1920.

## Qué hay aquí
| Carpeta | Qué es |
|---|---|
| `CLAUDE.md` | Reglas generales que Claude Code carga en cada sesión |
| `.claude/agents/` | 12 agentes: tendencias, estratega, documentalista, guionista, voz-audio, director-arte, animacion, packaging, editor (clipper), studio, retencion, comunidad |
| `.claude/skills/` | Skills revisados (sin publicidad): yt-* (11), viral-youtube-shorts, viral-tiktok-content, viral-short-form-ideas, prompt-master |
| `.claude/commands/` | `/short <tema>` (Short original) y `/clip <ID> <fuente>` (clipping) |
| `clipfactory/` | Código Python: render vertical, subtítulos palabra a palabra, voz gratis, candidatos de clip, ganchos en español, radar de tendencias, subida opcional |
| `canal-youtube/` | Estrategia, política de fuentes, base de conocimiento GTA VI, banco de ganchos, manual, datos y aprendizajes |
| `.github/workflows/` | Tests en cada push y radar de tendencias diario |

## Empezar
```bash
pip install -r requirements.txt            # núcleo
pip install -r requirements-extra.txt      # voz, transcripción, descargas, subida (opcional)
python3 -m pytest -q                       # 20 tests, incluido un render real
python3 -m clipfactory -h
```
Guía paso a paso: [`canal-youtube/MANUAL.md`](canal-youtube/MANUAL.md). Estrategia: [`canal-youtube/estrategia-gta.md`](canal-youtube/estrategia-gta.md).

## Comandos de `clipfactory`
| Comando | Hace |
|---|---|
| `fuentes` | Valida el registro de fuentes (nada se usa si no está aquí y es válido) |
| `descargar <id>` | Descarga SOLO una fuente registrada (yt-dlp) |
| `transcribir <video> --salida base` | Palabras con tiempos + SRT (faster-whisper) |
| `candidatos <words.json>` | Propone los 5 mejores momentos de 20-55 s, con motivos |
| `voz "texto" --salida x.mp3` | Voz neuronal gratis (edge-tts) + palabras con tiempos |
| `render job.yaml` | 1080x1920: fondo desenfocado o recorte, gancho, crédito, subtítulos, ducking, -14 LUFS |
| `radar "GTA 6"` | Shorts que superan 10x la mediana de su canal (YouTube API) |
| `subir video --titulo ... --confirmo` | Subida a YouTube por OAuth, privada/programada por defecto |
| `python3 -m clipfactory.hookscore_es "gancho"` | Puntúa ganchos en español |

## Principios
1. **Fuentes ajenas solo con permiso** (campañas de clipping o permiso escrito) o material oficial en fragmentos cortos con comentario. Lo impone el código. Ver [`politica-fuentes.md`](canal-youtube/politica-fuentes.md).
2. **Siempre aportación propia**: gancho, voz, contexto, edición y crédito.
3. **Datos verificados**: nada de filtraciones ni rumores presentados como hechos.
4. **Nada se publica sin tu aprobación.** TikTok se sube a mano.
5. **Aprender de los datos**: retención a las 72 h → `canal-youtube/data/aprendizajes.md`.
