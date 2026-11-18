# Aprendizajes del canal (memoria compartida del equipo)
Todos los agentes LEEN este archivo al empezar y AÑADEN al terminar 1-3 líneas con lo aprendido.
Formato: `- [AAAA-MM-DD] [agente] [S00X] Lección concreta → qué hacer distinto. (evidencia: dato o fuente)`
Reglas: solo lecciones con evidencia o error real; marca "hipótesis" lo no probado; si dos lecciones se contradicen, anótalo y resuélvelo con datos. Mantén el archivo corto: fusiona duplicados.

## Lecciones
- [2026-11-18] [tendencias] [S001] Sin acceso a la pestaña Shorts ni a vistas/medianas reales, el análisis de formatos es solo hipótesis → pedir al usuario 10-15 Shorts del tema con sus vistas, o conectar la API de YouTube. (evidencia: informe del agente)
- [2026-11-18] [tendencias] [S001] Los artículos de medios no se podían abrir; la hora de desbloqueo salió de resúmenes de búsqueda y las fuentes se contradicen → verificar siempre los datos clave antes del guion y redactar "según medios" si no hay fuente oficial. (evidencia: búsquedas del 18-nov)
- [2026-11-18] [miniaturas] [S001] El guion pone "logo de GTA VI" en el último plano (ficha, bucle) pero el fotograma 1 no lleva logo → no usar logo/arte de Rockstar en imagen; usar reloj 00:00 genérico en ambos para el bucle. (evidencia: guion vs. regla de derechos)
- [2026-11-18] [miniaturas] [S001] Puntuación 43/39/40 es predicción sin clics → medir retención 0-3 s y "viewed vs swiped away" a 72 h; "Probar y comparar" puede no estar disponible en Shorts (hipótesis). (evidencia: ninguna aún)
- [2026-11-18] [tecnico-audio] [S001] Narración de 143 palabras no cabe en 35 s a ritmo rápido (~3 palabras/s = ~45-48 s) → contar palabras y estimar duración antes de aprobar el guion; objetivo máx. ~100-110 palabras para 35 s. (evidencia: conteo wc sobre S001-narracion.txt)
- [2026-11-18] [tecnico-audio] [S001] Sin clave TTS en el entorno (ni ELEVENLABS ni OPENAI) → audio de voz pendiente; decidir proveedor antes de producir. Opciones baratas a valorar: Google Cloud TTS (capa gratuita mensual) y OpenAI TTS (coste por caracteres muy bajo para ~600 caracteres por Short). (evidencia: entorno sin claves)
- [2026-11-18] [guionista] [S001] El guion prometía "vídeo completo" que no existe → comprobar antes que exista el vídeo largo al que se enlaza, o no prometerlo. (evidencia: informe del guionista)
