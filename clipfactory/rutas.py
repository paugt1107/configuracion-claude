"""Rutas del proyecto en un solo sitio (cambiar aquí si se reorganizan carpetas)."""

from pathlib import Path

CANAL = Path("canal-youtube")
DOCS = CANAL / "docs"
DATOS = CANAL / "datos"
FUENTES = CANAL / "fuentes"
GUIONES = CANAL / "guiones"
CLIPS = CANAL / "clips"
RADAR = DATOS / "radar"
TENDENCIAS_YT = DATOS / "tendencias-youtube"
ALERTAS = DATOS / "alertas.md"
REGISTRO_FUENTES = FUENTES / "fuentes.yaml"
CONFIG_RADAR = FUENTES / "radar.yaml"
CONFIG_IMAGENES = FUENTES / "imagenes.yaml"
ENTREGAS = Path("entregas")
MEDIA = Path("media")
OFICIAL = MEDIA / "oficial"
RECORTES = MEDIA / "recortes"
TRABAJO = Path("salida")  # temporal, ignorado por git
