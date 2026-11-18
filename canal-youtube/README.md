# Oficina virtual del canal de YouTube

| # | Agente | Qué hace | Entrada → Salida |
|---|--------|----------|------------------|
| 1 | tendencias | Elige el nicho con más tendencia; alarma si un vídeo hace 10x la mediana | web → data/tendencias.md, alertas.md |
| 2 | guionista | Guion con gancho en el 1er segundo; reescribe con feedback | tendencias + retención → guiones/ |
| 3 | voz-audio | Narración lista para TTS + música/efectos | guion → audio/ |
| 4 | animacion | Escenas visuales, ninguna repetida | guion → escenas + registro |
| 5 | miniaturas | 10 versiones, puntúa y elige | guion → miniaturas/ |
| 6 | studio | Título, descripción y subida a la hora pico | todo → publicación |
| 7 | retencion | Detecta abandono (seg. 3) y avisa al guionista | analytics → retencion.md |

## Cómo se usa
Dile a Claude: "Ejecuta un ciclo del canal" o llama a un agente: "usa el agente tendencias".
Ciclo: 1→2→3→4→5→6, y 7 después de publicar; 7 reabre el 2.

## Qué necesita tu aprobación o claves (nada se hace solo)
- **YouTube Data/Analytics API** (OAuth del canal): para subir y leer retención.
- **TTS** (voz) y **generador de imagen/vídeo**: servicios de pago con clave API.
- Sin esas claves, cada agente entrega el material listo para hacerlo a mano. Las claves se piden de forma segura, nunca por chat.
- Las subidas son siempre privadas/programadas hasta que tú lo apruebes.
