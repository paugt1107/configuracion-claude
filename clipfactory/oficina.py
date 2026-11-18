"""OFICINA · foto del estado de la empresa para la oficina virtual (artifact "Oficina ¿Sabías que…? GTA 6").

Reúne, de los archivos del repo y de GitHub Actions (vía `gh`), qué está haciendo cada trabajador, su último resultado
y sus cifras. Escribe un JSON que Claude sube a la base de datos de la página (ArtifactData), así la oficina muestra
datos reales sin tener que estar encendida: se actualiza cada vez que Claude trabaja o cuando se lo pides.

Uso:  python3 -m clipfactory.oficina [salida.json]
"""

from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

from . import rutas

WORKFLOWS = {
    "valentin": "radar-web.yml",
    "fernanda": "produccion.yml",
    "tommy": "banco.yml",
    "tommy_recortes": "recortes.yml",
    "irene": "tests.yml",
}


def _gh_runs(wf: str, n: int = 5) -> list[dict]:
    try:
        out = subprocess.run(
            ["gh", "run", "list", "-w", wf, "-L", str(n), "--json", "status,conclusion,createdAt,updatedAt,displayTitle,databaseId"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return json.loads(out.stdout or "[]")
    except Exception:
        return []


def _estado(runs: list[dict]) -> tuple[str, str]:
    """(estado, cuándo): trabajando | ok | fallo | esperando."""
    if not runs:
        return "esperando", ""
    r = runs[0]
    if r["status"] in ("in_progress", "queued", "pending", "waiting"):
        return "trabajando", r["createdAt"]
    return ("ok" if r.get("conclusion") == "success" else "fallo" if r.get("conclusion") == "failure" else "esperando"), r["updatedAt"]


def _json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _radar() -> dict:
    ult = rutas.RADAR / "ultimo.md"
    txt = ult.read_text(encoding="utf-8") if ult.exists() else ""
    m = re.search(r"(\d+) novedades", txt)
    top = re.findall(r"\*\*([^*]+)\*\* · \[([^\]]+)\]", txt)[:3]
    hist = rutas.RADAR / "historia.md"
    n_hist = max(0, len(hist.read_text(encoding="utf-8").splitlines()) - 5) if hist.exists() else 0
    return {"novedades": int(m.group(1)) if m else 0, "top": [t for _, t in top], "historia": n_hist}


def _banco() -> dict:
    b = rutas.MEDIA / "banco"
    ind = {}
    for g in ("oficial", "trailers", "libres"):
        ind.update(_json(b / f"indice-{g}.json") or {})
    temas: dict[str, int] = {}
    for v in ind.values():
        t = v.get("tema") or v.get("categoria", "otros")
        temas[t] = temas.get(t, 0) + 1
    anim = len(list((b / "animadas").glob("*.mp4"))) if (b / "animadas").exists() else 0
    return {
        "imagenes": len(ind),
        "oficiales": sum(1 for v in ind.values() if v.get("fuente") == "oficial"),
        "libres": sum(1 for v in ind.values() if v.get("fuente") == "libre"),
        "animadas": anim,
        "temas": dict(sorted(temas.items(), key=lambda x: -x[1])[:12]),
    }


def _videos() -> list[dict]:
    out = []
    for d in sorted(rutas.ENTREGAS.glob("S[0-9]*")):
        qa = d / "control-calidad.md"
        estado = "sin control"
        if qa.exists():
            estado = "APTO" if "APTO" in qa.read_text(encoding="utf-8").splitlines()[0] else "REVISAR"
        g = rutas.GUIONES / f"{d.name}.yaml"
        titulo = ""
        if g.exists():
            titulo = ((yaml.safe_load(g.read_text(encoding="utf-8")) or {}).get("titulos") or [""])[0]
        out.append({"id": d.name, "titulo": titulo, "calidad": estado, "listo": (d / f"{d.name}-final.mp4").exists()})
    return out


def _pendientes() -> list[str]:
    p = rutas.DATOS / "pendientes.md"
    if not p.exists():
        return []
    return [re.sub(r"\*\*|`", "", m.group(1)).strip()[:90] for m in re.finditer(r"^- \[ \] (.+)$", p.read_text(encoding="utf-8"), re.M)]


def _skills() -> dict[str, list[str]]:
    """Skills instaladas (carpeta .claude/skills) y agentes (.claude/agents) con su descripción corta."""
    raiz = rutas.CANAL.parent / ".claude"
    out = {"skills": [], "agentes": {}}
    for d in sorted((raiz / "skills").glob("*/")):
        out["skills"].append(d.name)
    for a in sorted((raiz / "agents").glob("*.md")):
        txt = a.read_text(encoding="utf-8")
        m = re.search(r"^description:\s*(.+)$", txt, re.M)
        out["agentes"][a.stem] = (m.group(1).strip() if m else "")[:160]
    return out


def foto() -> dict:
    ahora = dt.datetime.now(dt.timezone.utc)
    runs = {k: _gh_runs(wf) for k, wf in WORKFLOWS.items()}
    est = {k: _estado(v) for k, v in runs.items()}
    radar, banco, videos = _radar(), _banco(), _videos()
    guiones = sorted(p.stem for p in rutas.GUIONES.glob("S[0-9]*.yaml"))
    hechos = {v["id"] for v in videos if v["listo"]}
    t = {
        "valentin": {
            "estado": est["valentin"][0],
            "desde": est["valentin"][1],
            "tarea": f"Radar en 14 idiomas: {radar['novedades']} novedades en la última pasada",
            "detalle": radar["top"],
            "cifras": {"novedades": radar["novedades"], "titulares de historia": radar["historia"]},
        },
        "pedro": {
            "estado": "esperando",
            "desde": "",
            "tarea": f"{len(guiones)} guiones escritos · espera tu /guiones",
            "detalle": guiones[-3:],
            "cifras": {"guiones": len(guiones)},
        },
        "fernanda": {
            "estado": est["fernanda"][0],
            "desde": est["fernanda"][1],
            "tarea": f"{len(hechos)} vídeos producidos" + (f" · en cola: {', '.join(sorted(set(guiones) - hechos))}" if set(guiones) - hechos else ""),
            "detalle": [f"{v['id']} · {v['titulo'][:60]}" for v in videos[-3:]],
            "cifras": {"vídeos": len(hechos)},
        },
        "tommy": {
            "estado": est["tommy"][0],
            "desde": est["tommy"][1],
            "tarea": f"Banco: {banco['imagenes']} imágenes · {banco['animadas']} animadas en 3D",
            "detalle": [f"{k}: {v}" for k, v in list(banco["temas"].items())[:4]],
            "cifras": {"imágenes": banco["imagenes"], "oficiales": banco["oficiales"], "libres": banco["libres"], "clips 3D": banco["animadas"]},
        },
        "irene": {
            "estado": est["irene"][0],
            "desde": est["irene"][1],
            "tarea": f"Control: {sum(1 for v in videos if v['calidad'] == 'APTO')}/{len(videos)} vídeos APTO · tests del código",
            "detalle": [f"{v['id']}: {v['calidad']}" for v in videos[-3:]],
            "cifras": {"aptos": sum(1 for v in videos if v["calidad"] == "APTO"), "a revisar": sum(1 for v in videos if v["calidad"] == "REVISAR")},
        },
    }
    feed = []
    for k, rs in runs.items():
        for r in rs[:3]:
            quien = k.split("_")[0]
            feed.append({"t": r["updatedAt"], "quien": quien, "texto": f"{r['displayTitle'][:80]} · {r.get('conclusion') or r['status']}"})
    feed.sort(key=lambda x: x["t"], reverse=True)
    return {
        "actualizado": ahora.isoformat(timespec="seconds"),
        "trabajadores": t,
        "videos": videos,
        "banco": banco,
        "pendientes": _pendientes(),
        "feed": feed[:14],
        "equipo": _skills(),
    }


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    out = Path(argv[0]) if argv else rutas.TRABAJO / "oficina.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(foto(), ensure_ascii=False, indent=1), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
