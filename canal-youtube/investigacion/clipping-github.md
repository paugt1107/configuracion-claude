# Clipping y fábricas de Shorts en GitHub — qué hacen y qué adoptamos (18-nov-2026)
Lectura de README (no del código completo). Estrellas = señal de interés, no de resultados. [A] adoptado, [N] no adoptado.

## Repos revisados
| Repo | Estrellas aprox. | Qué hace | Nota |
|---|---|---|---|
| mutonby/openshorts | ~9k | Vídeo largo → 3-15 momentos de 15-60 s con "virality score" (Gemini), 4 layouts (face-track, fondo desenfocado, split, screencast), subtítulos por palabra, gancho superpuesto, doblaje | MIT (parte cloud con licencia comercial). No publica el prompt de puntuación |
| fralapo/clippyme | ~70 | yt-dlp, faster-whisper, PySceneDetect, segmentación por temas (portada de ClipsAI), cortes en límites de frase y silencios, reencuadre por hablante, banner de atribución | MIT |
| Anil-matcha/AI-Youtube-Shorts-Generator | — | Alternativa a OpusClip: Whisper + LLM elige momentos + recorte vertical | — |
| ghost1412/shortsflow, artbyjazi/autoclip, supoclip, ai-video-clipper | — | Variantes locales (Whisper + Ollama/LLM), face tracking, subtítulos | — |
| harry0703/MoneyPrinterTurbo | ~50-100k (fuentes discrepan) | Tema → vídeo corto con stock + TTS + subtítulos | Generador "faceless", no clipping. MIT |
| RayVentura/ShortGPT | ~7-8k | Framework de automatización de vídeo | Para programadores |
| WyattBlue/auto-editor | — | Quita silencios por umbral de audio/movimiento, exporta a editores | Útil para tus grabaciones largas |
| tscupit/frameforge (fork de purffle-shorts) | 0 (fork) | Pipeline completo + subida programada (YouTube API, límite diario) | README promocional con incoherencias |
| jutsuhq/content-factory | ~6 | Fotograma 1 fija estilo y los demás lo editan; reparto fijo de personajes; -14 LUFS | Solo Mac; nunca publica por ti |
| opus-pro/reel-runbook | 1 | Gancho 0-3 s, re-gancho cada 5-8 s, bucle, revisión fotograma a fotograma | Calibración con 14 Shorts propios (débil) |

## Técnicas comunes (y dónde están en nuestro sistema)
1. [A] **Transcripción con marcas por palabra** (faster-whisper) → `python3 -m clipfactory transcribir`.
2. [A] **Cortes en límites de frase/pausa, 15-60 s, momento autónomo** → `candidatos` (heurística) + agente `editor` (criterio).
3. [A] **Puntuación de "viralidad" del momento** → nuestra versión es transparente: gancho en la 1.ª frase, pregunta, número, ritmo, final completo, penalización por empezar con conector. Los repos con LLM no publican su rúbrica; el agente `editor` revisa los 5 mejores.
4. [A] **Layouts**: fondo desenfocado (por defecto, sirve para gameplay 16:9) y recorte (`layout: crop`, `crop_x`). [N] face tracking: en gameplay no hay cara; se añadirá si grabas facecam.
5. [A] **Subtítulos palabra a palabra con palabra activa resaltada** en zona segura → `captions.py`.
6. [A] **Gancho superpuesto los primeros 2-3 s** → `gancho` en el job.
7. [A] **Banner de atribución** → crédito automático desde el registro de fuentes.
8. [A] **Voz en off + ducking del audio original + -14 LUFS** → `voz` (edge-tts gratis) + `render`.
9. [A] **Radar de outliers** (múltiplo sobre la mediana del canal) → `radar` + workflow diario.
10. [N] **Subida masiva/automática a TikTok/IG vía terceros** (Upload-Post, Zernio): de pago, no probados y riesgo de contenido masivo. YouTube: `subir` opcional, privado por defecto. TikTok: subida manual desde la app.
11. [N] **Descargar cualquier URL**: aquí solo se descargan fuentes registradas y autorizadas.

## Economía del clipping (contexto)
NPR (mayo 2026) y otros describen una "economía del clipping": creadores y marcas pagan por vistas a redes de clippers (ejemplos citados: 150 $ por 100.000 vistas; 3 $/1.000 vistas con tope por post). Es la vía legal para clipear a otros: entrar en campañas con permiso explícito. Riesgos citados: amplificar desinformación y penalizaciones por resubidas sin crédito.
