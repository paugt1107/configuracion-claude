"""Subida OPCIONAL a YouTube con la API oficial (OAuth del propio canal). Por defecto: privado.

Requiere: pip install google-api-python-client google-auth-oauthlib
Credenciales: client_secret.json de un proyecto de Google Cloud con YouTube Data API v3 activada
(ruta en YT_CLIENT_SECRET). El token se guarda en YT_TOKEN_FILE (por defecto .yt_token.json, ignorado por git).
No probado contra una cuenta real desde este repositorio: pruébalo primero con un vídeo privado.
"""

from __future__ import annotations

import os
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _service():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("Faltan dependencias: pip install google-api-python-client google-auth-oauthlib") from e
    # En GitHub Actions: secretos YT_CLIENT_ID, YT_CLIENT_SECRET_VALUE y YT_REFRESH_TOKEN (sin navegador)
    if os.environ.get("YT_REFRESH_TOKEN"):
        creds = Credentials(
            None, refresh_token=os.environ["YT_REFRESH_TOKEN"], token_uri="https://oauth2.googleapis.com/token",
            client_id=os.environ["YT_CLIENT_ID"], client_secret=os.environ["YT_CLIENT_SECRET_VALUE"], scopes=SCOPES,
        )  # fmt: skip
        creds.refresh(Request())
        return build("youtube", "v3", credentials=creds)
    token = Path(os.environ.get("YT_TOKEN_FILE", ".yt_token.json"))
    creds = Credentials.from_authorized_user_file(str(token), SCOPES) if token.exists() else None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            secret = os.environ.get("YT_CLIENT_SECRET", "client_secret.json")
            creds = InstalledAppFlow.from_client_secrets_file(secret, SCOPES).run_local_server(port=0)
        token.write_text(creds.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=creds)


def upload(
    video: str,
    title: str,
    description: str,
    tags: list[str] | None = None,
    privacy: str = "private",
    publish_at: str | None = None,
    made_for_kids: bool = False,
    synthetic: bool = False,
) -> str:
    from googleapiclient.http import MediaFileUpload  # type: ignore

    if privacy not in {"private", "unlisted", "public"}:
        raise ValueError("privacy debe ser private, unlisted o public")
    status = {
        "privacyStatus": "private" if publish_at else privacy,
        "selfDeclaredMadeForKids": made_for_kids,
        "containsSyntheticMedia": synthetic,
    }
    if publish_at:
        status["publishAt"] = publish_at  # RFC3339; requiere privacyStatus=private
    body = {"snippet": {"title": title[:100], "description": description, "tags": tags or [], "categoryId": "20"}, "status": status}
    req = _service().videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(video, chunksize=-1, resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    return resp["id"]


def programar_calendario(dry_run: bool = False) -> list[tuple[str, str]]:
    """Sube cada vídeo del calendario que aún no esté subido, PROGRAMADO (publishAt) para su hueco. Marca entregas/<ID>/subido.json.
    Título = el 1.º de publicacion.md; descripción = la de YouTube de publicacion.md; etiqueta de contenido sintético (IA) activada."""
    import datetime as dt
    import json
    import re

    from . import calendario, rutas

    hechos = []
    for t, v in calendario.planificar():
        marca = v["dir"] / "subido.json"
        if marca.exists():
            continue
        pub = (v["dir"] / "publicacion.md").read_text(encoding="utf-8") if (v["dir"] / "publicacion.md").exists() else ""
        m = re.search(r"## YouTube.*?\n(.*?)(?=\n## |\Z)", pub, re.S)
        desc = (m.group(1).strip() if m else v["titulo"])[:4900]
        cuando = t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if dry_run:
            hechos.append((v["id"], cuando))
            continue
        vid = upload(
            str(v["dir"] / f"{v['id']}-final.mp4"), v["titulo"], desc, tags=["GTA 6", "GTA VI", "Shorts"], publish_at=cuando, synthetic=True
        )
        marca.write_text(json.dumps({"youtube": vid, "publica": cuando}, ensure_ascii=False), encoding="utf-8")
        hechos.append((v["id"], cuando))
    (rutas.DATOS / "subidas.log").open("a", encoding="utf-8").write("".join(f"{i} → {c}\n" for i, c in hechos))
    return hechos
