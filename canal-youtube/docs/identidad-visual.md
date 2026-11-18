# Personajes y estilo visual del canal (PROPUESTA v0, la define `director-arte`)
Estado: propuesta de Claude, pendiente de aprobación. No hay imágenes generadas: Claude no genera imágenes; las crea la herramienta que elijas con estos prompts y referencias.

## Reglas de consistencia (aplican a todos los agentes)
1. Un personaje = una ficha. Todas las generaciones incluyen la descripción exacta + imágenes de referencia aprobadas.
2. Primer fotograma fija el estilo; los siguientes EDITAN el anterior (cambia el estado del mundo, no la cámara ni el estilo).
3. Paleta fija: naranja neón #FF7A1A, cian #19D3FF, magenta #FF2E93 sobre azul marino #0B1630 y carbón #14161C.
4. Sin logos, personajes ni arte con derechos de terceros (juegos, marcas, consolas): solo elementos originales o genéricos.
5. Nunca cambiar rasgos definidos (silueta, color, accesorio) sin versionar la ficha.

## Personaje 1 — "Tic" (presentador mascota, propuesta)
- Concepto: pequeño reloj-robot retro de neón que "cuenta" noticias; encaja con el formato de cuenta atrás y horarios.
- Silueta: cuerpo cuadrado redondeado (relación 1:1,2), pantalla-cara circular, dos antenas cortas, brazos finos.
- Rasgos fijos: esfera de reloj en el pecho con aguja naranja; ojos = dos puntos cian; contorno magenta fino; sin boca (la voz se muestra con barra de ondas bajo la cara).
- Personalidad: curioso, escéptico, dice "ojo" cuando algo no está confirmado.
- 6 emociones: neutral, sorpresa (ojos grandes), duda (un ojo entornado), confirmado (aguja arriba + destello), rumor (pantalla con ruido), alerta (parpadeo magenta).
- Prompt base de ficha (para tu herramienta de imágenes): "character reference sheet, small retro neon robot clock mascot, rounded square body, circular screen face with two cyan dot eyes, no mouth, short antennae, thin magenta outline, clock dial on chest with orange hand, flat 2D vector style with soft glow, front/side/three-quarter views and 6 emotions, dark navy background #0B1630, no text, no logos, no existing franchise characters"
- Negativos: sin personajes de videojuegos existentes, sin logos, sin texto en la imagen, sin manos realistas.

## Cómo se produce (3 rutas, de menor a mayor coste)
A. Ilustración vectorial (SVG) hecha por Claude + movimiento en el editor: coste 0, coherencia total.
B. Imágenes con modelo + referencia (p. ej. FLUX Kontext/Nano Banana vía API o app): coste bajo, ficha como entrada.
C. Identidad entrenada (Higgsfield Soul ID u otra) + vídeo corto: coste mayor; probar con 1 personaje y comparar con B antes de contratar plan.

## Identidad visual del canal de clipping GTA (v1)
El protagonista visual es el juego (capturas propias). La marca del canal va en los elementos superpuestos:
- Subtítulos: blanco con contorno negro, palabra activa naranja #FF7A1A, Inter Bold, en el tercio central.
- Gancho: caja negra 60 % con texto blanco en mayúsculas, centrado, a la altura del 27 % de la pantalla, primeros 2-3 s.
- Crédito: texto pequeño en caja negra 45 % al 21 % de altura ("Clip: @canal" / "Tráiler oficial: Rockstar Games").
- Señalización: círculos y flechas en cian #19D3FF. Esquina opcional con "Tic" (mascota) si se aprueba.
- Personajes del juego (Lucia, Jason…): solo como aparecen en capturas propias o material oficial con crédito; sus datos los mantiene `documentalista`.

- Banderas: cuando un dato habla de un país, se muestra su bandera dibujada (`motion.flag('nz'|'es'|'mx'|'ar')`; simplificada, sin escudos). Para más países, añadir su función en `clipfactory/motion.py`.
