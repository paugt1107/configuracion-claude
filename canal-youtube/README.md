# Oficina virtual — sistema de Shorts virales

Ciclo: `/short <tema>` (o `/short` solo) → tendencias → guionista → [aprobación] → voz-audio → animacion → miniaturas → studio → [aprobación] → subir.
72 h después: "usa el agente retencion sobre el Short X" → si hay fallo, reabre al guionista.

| Agente | Función | Skills que usa |
|---|---|---|
| tendencias | Nicho en auge, alarma 10x, ideas | viral-short-form-ideas |
| guionista | Guion + gancho en el fotograma 1, reescribe con feedback | viral-youtube-shorts, viral-hooks |
| voz-audio | Narración TTS, música libre, bucle | viral-youtube-shorts (monetización) |
| animacion | Escenas 9:16, sin repetir ninguna | registro escenas-usadas.json |
| miniaturas | Mejor fotograma 1 (Shorts) / 10 variantes (largos) | — |
| studio | Título, descripción, puente a vídeo largo, programación | shorts-to-longform-bridge |
| retencion | VVSA y curva; avisa al guionista | shorts-retention |

Archivos: `config.md` (umbrales), `data/shorts-log.md` (registro y aprendizaje), `data/alertas.md`, `data/retencion.md`.

## Necesita claves o tu aprobación
- YouTube Data/Analytics API (OAuth): subir y leer retención. Sin ella, `studio` y `retencion` trabajan con paquetes/CSV manuales.
- Voz (TTS) y generador de imagen/vídeo: servicios de pago con clave.
- Subidas siempre privadas/programadas hasta que apruebes. Nadie promete viralidad: se mide, se aprende y se repite lo que funciona.
