"""Registro de fuentes y política de uso (ver canal-youtube/politica-fuentes.md).

Tipos permitidos:
  propia  - grabación propia (gameplay capturado por el canal). Sin límite de fragmento.
  oficial - material oficial del editor (tráilers). Fragmentos cortos + comentario obligatorio.
  permiso - clip de otro creador con permiso escrito/campaña de clipping. Requiere prueba y crédito.
  cc-by   - licencia Creative Commons con atribución. Requiere crédito.
Cualquier otro tipo (filtraciones, "sin permiso", resubidas) se rechaza.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

DEFAULT_REGISTRY = Path("canal-youtube/fuentes/fuentes.yaml")
ALLOWED_TYPES = {"propia", "oficial", "permiso", "cc-by"}
# Límites internos conservadores (no son ley; reducen riesgo de Content ID / contenido reutilizado).
MAX_FRAGMENT_S = {"propia": None, "oficial": 15.0, "permiso": 45.0, "cc-by": 30.0}
NEEDS_COMMENTARY = {"oficial", "permiso", "cc-by"}
MIN_COMMENTARY_RATIO = 0.5  # voz propia >= 50 % de la duración del clip si la fuente no es propia


class PolicyError(ValueError):
    pass


@dataclass
class Source:
    id: str
    tipo: str
    url: str = ""
    archivo: str = ""
    creador: str = ""
    credito: str = ""
    permiso: str = ""
    licencia: str = ""
    notas: str = ""
    max_fragmento_s: float | None = None
    extra: dict = field(default_factory=dict)

    @property
    def fragment_limit(self) -> float | None:
        if self.max_fragmento_s is not None:
            return float(self.max_fragmento_s)
        return MAX_FRAGMENT_S.get(self.tipo)

    @property
    def needs_commentary(self) -> bool:
        return self.tipo in NEEDS_COMMENTARY


def validate(src: Source) -> None:
    if src.tipo not in ALLOWED_TYPES:
        raise PolicyError(f"Fuente '{src.id}': tipo '{src.tipo}' no permitido. Tipos válidos: {sorted(ALLOWED_TYPES)}")
    if src.tipo == "permiso" and not src.permiso.strip():
        raise PolicyError(f"Fuente '{src.id}': tipo 'permiso' exige el campo 'permiso' (enlace o ruta a la prueba del permiso).")
    if src.tipo in {"permiso", "cc-by", "oficial"} and not src.credito.strip():
        raise PolicyError(f"Fuente '{src.id}': falta 'credito' (p. ej. 'Clip: @canal' o 'Tráiler oficial: Rockstar Games').")
    if src.tipo == "cc-by" and "cc" not in src.licencia.lower():
        raise PolicyError(f"Fuente '{src.id}': tipo 'cc-by' exige 'licencia' indicando la licencia Creative Commons.")
    if not (src.url or src.archivo):
        raise PolicyError(f"Fuente '{src.id}': indica 'url' o 'archivo'.")


def load_registry(path: str | Path = DEFAULT_REGISTRY) -> dict[str, Source]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"No existe el registro de fuentes: {p}")
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    out: dict[str, Source] = {}
    known = set(Source.__dataclass_fields__) - {"extra"}
    for raw in data.get("fuentes") or []:
        raw = dict(raw)
        extra = {k: raw.pop(k) for k in list(raw) if k not in known}
        src = Source(**{k: ("" if v is None and k not in {"max_fragmento_s"} else v) for k, v in raw.items()}, extra=extra)
        if src.id in out:
            raise PolicyError(f"Fuente duplicada: {src.id}")
        out[src.id] = src
    return out


def get_source(source_id: str, path: str | Path = DEFAULT_REGISTRY) -> Source:
    reg = load_registry(path)
    if source_id not in reg:
        raise PolicyError(f"La fuente '{source_id}' no está registrada en {path}. Regístrala antes de usarla.")
    src = reg[source_id]
    validate(src)
    return src


def check_segment(src: Source, start: float, end: float, commentary_s: float = 0.0) -> None:
    dur = end - start
    if dur <= 0:
        raise PolicyError("El segmento debe tener fin > inicio.")
    limit = src.fragment_limit
    if limit is not None and dur > limit + 1e-6:
        raise PolicyError(f"Fuente '{src.id}' ({src.tipo}): fragmento de {dur:.1f} s supera el máximo de {limit:.0f} s.")
    if src.needs_commentary and commentary_s < MIN_COMMENTARY_RATIO * dur:
        raise PolicyError(
            f"Fuente '{src.id}' ({src.tipo}) exige comentario propio >= {int(MIN_COMMENTARY_RATIO*100)} % del clip "
            f"({MIN_COMMENTARY_RATIO*dur:.1f} s); la voz dura {commentary_s:.1f} s."
        )
