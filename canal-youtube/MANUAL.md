# Manual de operación (de la captura al Short publicado)
Todo se ejecuta desde la raíz del repositorio. Requisitos: Python 3.10+, ffmpeg. `pip install -r requirements.txt` y, según el paso, `pip install -r requirements-extra.txt`.

## 0. Una vez
1. Rellena/ajusta `canal-youtube/voice.md` (o pásale a Claude 3 vídeos tuyos).
2. (Opcional) Clave de la YouTube Data API v3 → secreto `YOUTUBE_API_KEY` en GitHub (Settings → Secrets → Actions) para el radar diario automático.
3. (Opcional, subida automática a YouTube) `client_secret.json` de Google Cloud → variable `YT_CLIENT_SECRET`.

## 1. Captura (tú)
PS5/Xbox → clip → `media/AAAA-MM-DD-tema.mp4`. Radio del coche apagada. Registra la fuente:
```yaml
# canal-youtube/fuentes/fuentes.yaml
  - id: 2026-11-19-primer-dia
    tipo: propia
    archivo: media/2026-11-19-primer-dia.mp4
    creador: "@tucanal"
```
`python3 -m clipfactory fuentes`  → todo debe salir OK.

## 2. Encontrar los momentos
```
python3 -m clipfactory transcribir media/2026-11-19-primer-dia.mp4 --salida canal-youtube/transcripciones/2026-11-19-primer-dia
python3 -m clipfactory candidatos canal-youtube/transcripciones/2026-11-19-primer-dia.words.json --salida canal-youtube/data/candidatos-S002.json
```
Si el clip no tiene voz (gameplay puro), elige el momento viéndolo: el agente `editor` te pide minuto y segundo.

## 3. Guion, gancho y voz
En Claude Code: `/clip S002 2026-11-19-primer-dia` (el flujo llama a editor → guionista → voz-audio → packaging → studio).
Voz gratis: `python3 -m clipfactory voz --archivo canal-youtube/audio/S002-narracion.txt --salida canal-youtube/audio/S002-voz.mp3`
(genera también `S002-voz.words.json` para subtítulos). Voces: es-ES-AlvaroNeural, es-ES-ElviraNeural, es-MX-JorgeNeural, es-MX-DaliaNeural.

## 4. Render
`canal-youtube/jobs/S002.yaml` (ver `jobs/ejemplo.yaml`) →
`python3 -m clipfactory render canal-youtube/jobs/S002.yaml` → `salida/S002.mp4` (1080x1920, 30 fps, -14 LUFS).
Si la fuente no es tuya y no hay voz suficiente o el tramo es largo, el render SE NIEGA (política).

## 5. Publicar
- YouTube (manual): Studio → Crear → Subir → privado → revisar → programar. Copia título/descripción de `data/publicacion-S002.md`.
- YouTube (automático, opcional): `python3 -m clipfactory subir salida/S002.mp4 --titulo "..." --descripcion canal-youtube/data/descripcion-S002.txt --programar 2026-11-20T19:00:00+01:00 --confirmo`
- TikTok: subir desde la app, portada = fotograma 1, texto y hashtags de `publicacion-S002.md`. Marcar contenido IA si la voz es sintética y la plataforma lo pide.

## 6. Aprender
A las 72 h: exporta la retención (Studio → vídeo → Analítica → Interacción → descargar) → `canal-youtube/data/retencion/S002.csv` → `retencion` usa `yt-retention/retention.py`. Lecciones → `data/aprendizajes.md`.

## Automático en GitHub
- `tests` en cada push (render real con vídeo sintético).
- `radar-tendencias` cada día a las 07:17 (si hay `YOUTUBE_API_KEY`): guarda `canal-youtube/data/trends/*.md` y añade alarmas ≥10x a `alertas.md`.

## Voz IA automática (no grabas nada)
1. El guion va en `canal-youtube/audio/<ID>-narracion.txt`, una frase por línea (= una escena).
2. Al hacer push, GitHub Actions (`produccion`) genera la voz IA frase a frase, efectos, música y el vídeo, y lo sube a `entregas/<ID>/<ID>-final-ia.mp4`.
3. Voz: gratis por defecto (es-ES-AlvaroNeural). Escúchalas en `entregas/voces/` y fija la tuya en GitHub → Settings → Secrets and variables → Actions → Variables → `TTS_VOICE`.
4. Más calidad (opcional): secreto `OPENAI_API_KEY` (≈1,5 céntimos/min, voz dirigible por instrucciones) o `ELEVENLABS_API_KEY` (+ variable `ELEVENLABS_VOICE_ID`). Se usa sola la mejor disponible.
5. Relanzar a mano: GitHub → Actions → produccion → Run workflow.
