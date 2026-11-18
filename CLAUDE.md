# Reglas (se cargan en cada mensaje: mantener corto)
- Español, directo y breve. Sin relleno. Confirmar antes de algo irreversible o externo (publicar, gastar créditos).
- No inventar datos: si no hay cifra real, decirlo y marcar "estimado".
- AHORRO DE TOKENS: no mostrar vídeos/imágenes (salvo depurar un fallo); leer solo lo necesario (head/grep, no archivos enteros);
  no vigilar procesos largos con bucles; respuestas cortas; trabajo pesado → GitHub Actions.
- Antes de commit: `ruff check clipfactory tests && python3 -m pytest -q`. Commits con push a main.

# Canal ¿Sabías que…? GTA 6
- Equipo (agentes en .claude/agents): VALENTÍN radar/datos · PEDRO guiones · FERNANDA producción · TOMMY imágenes (banco EN PAUSA) · IRENE calidad/publicación.
- Órdenes: `/canal N` (todo el ciclo) · `/guiones N` (solo guiones) · `/clip <ID> <fuente>`.
- Guion = `canal-youtube/guiones/SXXX.yaml` (PLANTILLA.yaml; ejemplo S006). Push → Actions produce en `entregas/SXXX/`.
- Juego: `canal-youtube/fuentes/juego.yaml` · Fases: `canal-youtube/docs/fases.md` · Pendientes del dueño: `canal-youtube/datos/pendientes.md` (recordar en 1 línea).
- Oficina: https://claude.ai/artifact/WpekPno864dqoiPW63BjzQ — actualizar al cerrar una tarea grande (`python3 -m clipfactory.oficina <json>` + ArtifactData set oficina/estado).
