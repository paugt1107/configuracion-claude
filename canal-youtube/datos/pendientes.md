# Pendientes del dueño del canal
Marca con [x] cuando lo hagas. Claude revisa esta lista al empezar cada sesión.

- [ ] **ElevenLabs (voz premium):** GitHub → Settings → Secrets and variables → Actions → *Secrets*: `ELEVENLABS_API_KEY` · *Variables*: `ELEVENLABS_VOICE_ID` (voz en español de la Voice Library). Luego Actions → Producción de vídeos → Run workflow.
- [ ] **Crear canal de YouTube aparte** (cuenta de marca) y subir `entregas/marca/banner-youtube-2560x1440.png` y `avatar-800x800.png`. Guía: `canal-youtube/docs/crear-canales.md`.
- [ ] **Crear TikTok e Instagram** con el mismo nombre y avatar.
- [ ] **FASE 2 · Capturas de tu partida** (desde el 19-nov 00:00) en `media/capturas/`: cuando encuentres un coche/arma/sitio secreto o pases una misión difícil, haz captura o clip corto del sitio exacto. Con gameplay propio las guías rinden muchísimo más.
- [ ] **Imágenes oficiales** en `media/oficial/` con estos nombres: `lucia-jason.jpg` (la foto de los dos en el coche que me enseñaste), `lucia.jpg`, `jason.jpg`, `rockstar-logo.png` (logo con fondo transparente). GitHub app → repo → media/oficial → Add file → Upload (fotos). Se usan solas en los vídeos.
- [ ] **Revisar y publicar S001** (`entregas/S001/`).
- [ ] (Opcional) `YOUTUBE_API_KEY` en Secrets para el radar de vídeos que superan 10x su canal.
- [ ] **Minutos de GitHub Actions:** el repo es privado (≈2.000 min/mes gratis). Valentín cada 15 min + producción puede pasarse. Elige: (a) Settings → Billing → poner método de pago y límite de gasto, o (b) hacer el repo público (minutos ilimitados; se vería tu estrategia). Si no, Valentín se parará a final de mes.
- [ ] (Opcional) **X/Twitter:** secreto `X_BEARER_TOKEN` (API de pago) para que Valentín lea X.
- [ ] (Recomendado) **Subida programada a YouTube:** 3 secretos (`YT_CLIENT_ID`, `YT_CLIENT_SECRET_VALUE`, `YT_REFRESH_TOKEN`). Pasos en `canal-youtube/docs/configuracion.md` → «Subida programada». Con eso el calendario sube y programa solo cuando lances el workflow.
