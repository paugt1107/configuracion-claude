# Fábrica de Shorts · GTA VI en español

Canal **"¿Sabías que…?"** de GTA VI para **YouTube Shorts y TikTok**. Un equipo de 13 agentes de IA (Claude Code) investiga, escribe y produce vídeos verticales con **voz IA**, subtítulos animados, efectos y música, sin grabar nada. Tú revisas y publicas.

## El equipo automático
| Nombre | Qué hace | Cuándo | Dónde |
|---|---|---|---|
| **Valentín** · radar | Recoge lo que se dice de GTA VI en Google Noticias (14 idiomas/países), Bluesky, Mastodon, Reddit, YouTube y X (si hay API) → `canal-youtube/datos/radar/ultimo.md` | Cada 15 min | GitHub Actions |
| **Pedro** · guionista | Convierte lo de Valentín en guiones "¿Sabías que…?" con gancho, verificados → `canal-youtube/guiones/SXXX.yaml` | Cuando tú lo pidas: `/guiones` | Esta conversación |
| **Fernanda** · producción | Voz IA, escenas, efectos, música, subtítulos, portadas y textos → `entregas/SXXX/` | Al llegar un guion | GitHub Actions |
| **Tommy** · imágenes | Pone la imagen justo cuando la voz nombra algo (banderas, dinero, policía, coches, mapa, Lucía/Jason, fotos libres de lugares reales) y recorta personajes | En cada vídeo + al subir imágenes | GitHub Actions |
| **Irene** · calidad | Revisa cada vídeo (formato, duración, volumen, silencios, gancho, imágenes, fuentes) → `control-calidad.md` APTO/REVISAR; y el código en cada cambio | Siempre | GitHub Actions |
Detrás hay 13 agentes especialistas (`.claude/agents/`) que Pedro y Claude usan para cada tarea.

## Mapa de carpetas
| Carpeta | Qué hay | ¿Lo tocas tú? |
|---|---|---|
| `entregas/<ID>/` | **Lo terminado**: `<ID>-final.mp4`, `portada-1/2/3.png`, `publicacion.md` (títulos, descripción, TikTok) | Sí: descargar y publicar |
| `entregas/voces/` | Muestras de voces gratuitas para elegir | Escuchar |
| `canal-youtube/guiones/` | Guiones producibles (`S001.yaml`…) y `PLANTILLA.yaml` | Opcional |
| `canal-youtube/datos/` | Radar (`radar/ultimo.md`), registro de vídeos, aprendizajes, alertas | Leer |
| `canal-youtube/docs/` | Manual, estrategia, política de fuentes, ganchos, voz e identidad visual, organigrama | Leer |
| `canal-youtube/fuentes/` | Qué vigila el radar, fuentes autorizadas, imágenes oficiales | Editar si quieres |
| `canal-youtube/investigacion/` | Base de conocimiento de GTA VI y estudios | Leer |
| `canal-youtube/clips/` | Trabajos de recorte de clips de tus grabaciones | Rara vez |
| `media/` | `capturas/` (tus capturas), `oficial/` (imágenes oficiales), `recortes/` (personajes sin fondo) | Subir capturas |
| `clipfactory/` | El código (Python) | No |
| `.claude/agents/` | Los 13 agentes (uno por función) | No |
| `.claude/skills/` | Conocimiento especializado (guiones, ganchos, retención, SEO…) | No |
| `.github/workflows/` | Automatizaciones: producción, radar, recortes, tests | No |

## Voz IA
Automática por orden de calidad: **ElevenLabs** (si hay clave) → **OpenAI** → **voz gratuita** de Microsoft. Si una falla o se agota la cuota, se usa la siguiente sola.
Activar ElevenLabs: GitHub → *Settings → Secrets and variables → Actions*:
1. *Secrets* → **New repository secret** → nombre `ELEVENLABS_API_KEY`, valor tu clave (elevenlabs.io → Profile → API Keys).
2. *Variables* → **New repository variable** → `ELEVENLABS_VOICE_ID` = ID de la voz (Voice Library → filtra *Spanish* → copia el *Voice ID*). Opcional: `ELEVENLABS_MODEL` (por defecto `eleven_multilingual_v2`).
3. *Actions → Producción de vídeos → Run workflow* para regenerar.

## Para desarrolladores
```bash
pip install -e ".[dev,voz]"      # extras: voz, transcripcion, descargas, youtube, recortes, dev
ruff check clipfactory tests && python -m pytest
clipfactory -h                    # producir, portadas, recortar, narrar, voces, render, candidatos, radar, subir…
```

## Principios
1. Datos verificados (nada de rumores como hechos). 2. Material ajeno solo con permiso o fuente oficial con crédito (`canal-youtube/docs/politica-fuentes.md`). 3. Gancho en el primer segundo. 4. Nada se publica sin revisión humana. 5. Cada vídeo deja una lección en `canal-youtube/datos/aprendizajes.md`.
