# Configuración del canal (editable)
- Formato principal: YouTube Shorts, vertical 9:16, 30-45 s (máx. 60 s salvo que la historia lo pida)
- Nicho FIJADO: GTA VI en español — cómo se hizo, misiones, curiosidades de personajes, detalles ocultos, vida real vs juego (ver estrategia.md). `tendencias` elige ángulo y formato, no el nicho
- Idioma del canal: español
- Cadencia: 1 Short al día (cambiar aquí). Calidad > cantidad; nada de contenido repetitivo en masa
- Alarma de viral: Short con >= 10x las vistas de la mediana de su nicho (últimos 30 Shorts comparables)
- Gancho: máx. 12 palabras, impacto visual + verbal en el fotograma 1; sin saludo, logo ni intro
- Retención: objetivo VVSA >= 70%; alerta si VVSA < 60% o si retención seg. 0-3 < 80%; revisar a las 72 h
- Bucle: el final debe encajar con el principio
- Embudo: todo Short con vídeo largo relacionado enlaza a él (llamada en vídeo + comentario fijado)
- Audio: original; evitar música con licencia
- Miniaturas: 3 variantes para Shorts, 10 para vídeos largos
- Privacidad de subida por defecto: private/programado hasta aprobación del usuario
- Zona horaria de publicación: Europe/Madrid
- Plataformas: YouTube Shorts + TikTok (mismo contenido base, texto y hashtags propios de cada una)
- Re-gancho cada 5-8 s; primer fotograma legible sin sonido; subtítulos palabra a palabra; música CC0 con ducking, -14 LUFS
- Anti contenido masivo: cada vídeo aporta algo propio verificable; ritmo sostenible; nunca clones del mismo formato en serie
- IA: marcar contenido sintético realista con la etiqueta de cada plataforma; verificar política oficial antes de monetizar
- Personajes y paleta: ver `docs/identidad-visual.md` (director-arte)
- Clipping: solo fuentes registradas y válidas (politica-fuentes.md); oficial ≤15 s, permiso ≤45 s; comentario propio ≥50 % si la fuente no es propia; crédito visible
- Primeros 10 s sin violencia gráfica (anuncios); sin spoilers de historia las 2 primeras semanas; radio del juego apagada al grabar
- Ganchos en español: `python3 -m clipfactory.hookscore_es` ≥55 para producir
- Herramientas: `python3 -m clipfactory -h` (render, voz, candidatos, radar, subir). Manual: docs/manual.md

## Subida programada a YouTube (workflow «Studio · Subir y programar en YouTube»)
Una sola vez (15 min), con la cuenta del CANAL:
1. https://console.cloud.google.com → crea un proyecto → «APIs y servicios» → habilita **YouTube Data API v3**.
2. «Pantalla de consentimiento OAuth» → Externa → modo **Prueba** → añade tu Gmail del canal como usuario de prueba.
3. «Credenciales» → Crear → **ID de cliente OAuth** → tipo «Aplicación web» → URI de redirección: `https://developers.google.com/oauthplayground`.
   Copia el **Client ID** y el **Client secret**.
4. https://developers.google.com/oauthplayground → engranaje → «Use your own OAuth credentials» → pega los dos.
   En el paso 1 escribe el alcance `https://www.googleapis.com/auth/youtube.upload` → Authorize (con la cuenta del canal)
   → «Exchange authorization code for tokens» → copia el **Refresh token**.
5. GitHub → Settings → Secrets and variables → Actions → New secret: `YT_CLIENT_ID`, `YT_CLIENT_SECRET_VALUE`, `YT_REFRESH_TOKEN`.
6. Actions → «Studio · Subir y programar en YouTube» → Run (primero con prueba = true; luego false).
Los vídeos suben PRIVADOS con fecha de publicación (se publican solos a su hora) y con la etiqueta de contenido sintético (IA).
