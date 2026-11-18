---
name: canal-videojuego
description: Monta y lleva un canal automatizado de Shorts/TikTok/Reels sobre UN videojuego (ahora GTA 6). Úsala cuando el dueño pida vídeos, guiones, ideas, qué busca la gente, calendario o "todo el canal"; también para cambiar a otro juego (editar canal-youtube/fuentes/juego.yaml).
---
# Canal automatizado de un videojuego

Todo vive en este repo y no se borra. Para otro juego: cambia `canal-youtube/fuentes/juego.yaml` (nombre, corto, dicho, variantes,
lanzamiento, canal, hashtags, semillas) y `canal-youtube/fuentes/radar.yaml` (búsquedas), y sigue igual.

| Qué | Quién | Dónde |
|---|---|---|
| Qué publica el mundo (14 idiomas, cada 15 min) | VALENTÍN | `canal-youtube/datos/radar/ultimo.md`, `historia.md` |
| Qué BUSCA la gente (Google + YouTube autocompletado, cada hora) | VALENTÍN | `canal-youtube/datos/demanda.md` (`clipfactory/demanda.py`) |
| Nombre, logo y banner | DIRECTOR | `python3 -m clipfactory marca` → `entregas/marca/` |
| Guiones sin repetir gancho | PEDRO | `/guiones` o `/canal N`; `calidad.gancho_repetido` |
| Imágenes, dibujos y clips 3D | TOMMY | banco `media/banco/` (GALERIA.md), buscador `python3 -m clipfactory.buscador <palabra>` |
| Voz IA, música, efectos, misterio, montaje | FERNANDA | Actions `produccion.yml` (push de `canal-youtube/guiones/SXXX.yaml`) |
| Control de calidad | IRENE | `entregas/SXXX/control-calidad.md` |
| Título, portadas, descripción, calendario | STUDIO | `entregas/SXXX/publicacion.md`, `canal-youtube/datos/calendario.md/.ics` |
| Estado de todos | OFICINA | https://claude.ai/artifact/WpekPno864dqoiPW63BjzQ |

Orden única: `/canal 10`. Reglas: CLAUDE.md, `canal-youtube/docs/fases.md`, `canal-youtube/docs/politica-fuentes.md`.
