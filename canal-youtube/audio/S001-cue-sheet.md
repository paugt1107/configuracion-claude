# S001 - Cue sheet de audio (GTA VI, a qué hora se juega)

Estado: borrador de audio. Sin TTS configurado: el audio de voz aún no existe. Los tiempos son los del guion aprobado y deben re-medirse con la locución real.

## Voz del canal (una sola voz para todos los Shorts)
- Tipo: voz adulta, neutra, español neutro (sin acento regional marcado). Mujer o hombre, pero siempre la misma voz; elegirla una vez y fijarla aquí.
- Tono: informativo y cercano. Tranquilo, con ligera sorpresa en el gancho. Nunca gritar ni tono de anuncio.
- Velocidad: 1,15x sobre la velocidad normal del TTS (ritmo rápido, sin sonar atropellado). Pausas solo por puntuación.
- Energía: alta en 0-3 s (gancho); media en 3-26 s; baja y clara en 26-35 s (verificación, sin dramatismo).
- Pronunciación: "GTA seis" (no "VI"); "medianoche" (no "00:00"); horas en palabras; "hora universal" (no "UTC"); "PlayStation" y "Xbox" tal cual.
- Pausas: coma ~0,2 s, punto ~0,35 s, puntos suspensivos ~0,5 s. Ninguna pausa de voz supera 0,4 s.
- Nivel: voz a -14 LUFS integrado (normalización de YouTube), pico máximo -1 dBTP.

## Música (libre de derechos, sin licencia de terceros)
- Estilo: pad electrónico oscuro con pulso lento (~100 BPM), tensión suave que sube hasta 8 s y se abre en el giro. Sin letra, sin voces, sin melodía reconocible de videojuego.
- Fuentes permitidas (dominio público o CC0 / licencia libre de uso comercial): Pixabay Music, Free Music Archive (filtrar CC0/CC-BY), YouTube Audio Library (solo pistas marcadas sin atribución). Guardar nombre de pista, autor y licencia en un comentario del proyecto.
- Volumen: fondo a -26 LUFS; baja 8 dB durante la voz (ducking) y sube 3 dB en silencios de imagen. Nunca compite con la voz.
- Pistas: 1 sola. Sin música de tendencia ni de catálogo.

## Marcas de tiempo

| Tiempo | Bloque | Voz (resumen) | Música | Efectos | Notas |
|--------|--------|---------------|--------|---------|-------|
| 0,00-0,35 | Gancho impacto | (silencio de voz, impacto ya sonando) | Pad entra en 0,00 a -20 dB | **Impacto de graves** (boom + golpe seco) en 0,00 exacto, sincronizado con el reloj 00:00 del fotograma 1 | Efecto de impacto obligatorio en 0-1 s |
| 0,35-1,80 | Gancho | "GTA seis sale mañana, pero no a la misma hora." | Pad baja a -26 LUFS (ducking -8 dB) | Tic de reloj en 0,35 | Gancho <2 s; texto en pantalla ya visible |
| 1,80-3,00 | Gancho/promesa | "Según varios medios, se desbloquea a medianoche, hora local, en cada región." (inicio) | Pulso sigue | Whoosh suave en el corte a globo (2,0) | Corte de plano cada 2-3 s |
| 3,00-8,00 | Promesa + bucle | "...en cada región. Y hay un país que juega primero." | Riser sube de 3,0 a 8,0 | Riser ligero; tic de reloj cada segundo | Riser termina en el giro |
| 8,00-8,60 | Giro | "Nueva Zelanda, antes que nadie." | Corte de pad a 8,0 | **Impacto corto** en 8,0 | Revelación de país |
| 8,60-14,00 | Giro | "Ellos arrancan mientras tú todavía estás en el día dieciocho." | Pulso vuelve a -26 LUFS | Clic de pantalla en 11,0 (contador local) | Energía media |
| 14,00-20,00 | España | "En España, a medianoche... Eso son las once de la noche del día dieciocho, en hora universal." | Pulso | Campanilla de confirmación en 14,0 | Corte cada 2-3 s |
| 20,00-26,00 | México y Argentina | "México, centro: medianoche. Argentina: ..." | Pulso | Tres clics (uno por reloj) en 20,0 / 22,0 / 24,0 | Tres relojes encendiéndose |
| 26,00-30,00 | Precarga | "Y ojo: precargarlo desde el diez de noviembre no lo desbloquea antes." | Pad baja a -30 LUFS | **Stinger** de advertencia en 26,0 (tono bajo corto) | Cambio de energía: voz más baja |
| 30,00-35,00 | Verificación + CTA | "Rockstar no ha publicado una hora única... Enlace en el comentario fijado." | Pad sigue, sin pulso | Flecha/clic suave en 33,0 (CTA) | Voz clara y baja; sin dramatismo |
| 35,00-37,00 | Bucle | "Mañana, a medianoche... ¿pero a qué hora, exactamente?" | Pad se cierra en 35,8 con la misma nota del inicio | **Mismo impacto de graves** que en 0,00, en 36,0 | Ver sección Bucle |

## Silencios
- Ningún silencio mayor de 0,4 s en todo el Short (requisito de Shorts).
- Los "silencios" de imagen se cubren con pad o tic de reloj.
- Entre "Mañana" y el impacto final: la voz termina en 36,0; no dejar cola de silencio.

## Bucle (el final enlaza con el inicio)
- Último segundo (36,0-37,0): la pregunta "¿pero a qué hora, exactamente?" termina antes de 36,0 y deja el mismo impacto de graves que el segundo 0,00.
- Último fotograma: reloj 00:00 idéntico al fotograma 1.
- Pad: la última nota es la misma que la primera, con cola de 0,3 s que se solapa con el impacto del inicio al reproducir en bucle. Así el salto al inicio no tiene corte audible.
- Comprobación: reproducir el archivo en bucle dos veces; el impacto debe sonar una sola vez por vuelta y sin clic.

## Entregables de audio (cuando haya TTS)
- Voz: S001-voz.wav (o .mp3) a 48 kHz, normalizada a -14 LUFS.
- Música: S001-musica.wav con ducking aplicado; SFX en pista separada.
- Mezcla final: S001-mezcla.wav (la mezcla, no las pistas sueltas, se sube a Studio).
- Duración objetivo: 35-37 s. Si la locución supera 40 s, recortar antes que acelerar más la voz (ver nota).

## Nota de duración (aviso)
El texto de narración tiene 143 palabras. A ritmo rápido (1,15x) un TTS en español suele dar ~3 palabras/s, es decir, unos 45-48 s, por encima de los 35 s del guion. Opciones, a decidir por el usuario: (a) medir la locución real y aceptar hasta ~45 s (límite de la configuración del canal); (b) recortar 2 frases, p. ej. "Ellos arrancan mientras tú todavía estás en el día dieciocho." y "México, centro: medianoche.", con cambio de guion aprobado. No se cambia el texto sin confirmación.
