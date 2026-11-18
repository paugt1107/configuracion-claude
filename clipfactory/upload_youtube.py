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
