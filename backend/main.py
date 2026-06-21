import json
import subprocess
from fastapi import FastAPI, Form, Query, HTTPException, status
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from auth import authenticate_user, create_access_token, SECRET_KEY, ALGORITHM, USERS

app = FastAPI(title="Baixe Link API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
        )
    token = create_access_token(data={"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}


def verify_token(token: str | None):
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or username not in USERS:
            return None
        return username
    except JWTError:
        return None


ERROR_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>Erro - Baixe Link</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#121212;color:#e0e0e0;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:2rem;text-align:center}
  .card{background:#1e1e1e;border-radius:12px;padding:2rem;max-width:480px;box-shadow:0 4px 24px rgba(0,0,0,0.4)}
  h1{font-size:1.5rem;margin-bottom:1rem}
  p{color:#aaa;margin-bottom:1.5rem;line-height:1.6;word-break:break-word}
  .error{color:#cf6679}
  a{display:inline-block;padding:0.7rem 1.5rem;border-radius:8px;background:#1a73e8;color:#fff;text-decoration:none;font-weight:600;transition:background 0.2s}
  a:hover{background:#1557b0}
</style>
</head>
<body>
<div class="card">
  <h1 class="error">&#x26A0; Erro</h1>
  <p>{mensagem}</p>
  <a href="/">&#x2190; Voltar ao app</a>
</div>
</body>
</html>"""


def validate_url(url: str, tipo: str) -> str | None:
    fmt = "mp4" if tipo == "mp4" else "mp3/best"
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-warnings",
        "-f", fmt,
        url,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            stderr = result.stderr.strip()
            if not stderr:
                return "Falha ao acessar o link. Verifique se a URL é válida."
            return stderr.split("\n")[-1]
        return None
    except subprocess.TimeoutExpired:
        return "Tempo limite excedido ao acessar o link."
    except Exception:
        return "Erro inesperado ao validar o link."


@app.get("/check")
def check_url(
    url: str = Query(...),
    tipo: str = Query(...),
    token: str = Query(None),
):
    user = verify_token(token)
    if not user:
        return {"ok": False, "error": "Token inválido ou expirado. Faça login novamente."}
    if tipo not in ("mp4", "mp3"):
        return {"ok": False, "error": "Tipo deve ser mp4 ou mp3."}
    err = validate_url(url, tipo)
    if err:
        return {"ok": False, "error": err}
    return {"ok": True}


@app.get("/dl")
def direct_download(
    url: str = Query(...),
    tipo: str = Query(...),
    token: str = Query(None),
):
    user = verify_token(token)
    if not user:
        return HTMLResponse(
            ERROR_HTML.replace("{mensagem}", "Token ausente, inválido ou expirado. Faça login novamente."),
            status_code=401,
        )

    if tipo not in ("mp4", "mp3"):
        return HTMLResponse(
            ERROR_HTML.replace("{mensagem}", "Tipo deve ser mp4 ou mp3."),
            status_code=400,
        )

    err = validate_url(url, tipo)
    if err:
        return HTMLResponse(
            ERROR_HTML.replace("{mensagem}", err),
            status_code=400,
        )

    if tipo == "mp4":
        filename = "video.mp4"
        content_type = "video/mp4"
        cmd = [
            "yt-dlp",
            "-f", "best[ext=mp4]/best",
            "--no-part",
            "--no-mtime",
            "-o", "-",
            url,
        ]
    else:
        filename = "audio.mp3"
        content_type = "audio/mpeg"
        cmd = [
            "yt-dlp",
            "-f", "bestaudio/best",
            "--no-part",
            "--no-mtime",
            "-o", "-",
            "-x", "--audio-format", "mp3",
            "--audio-quality", "0",
            url,
        ]

    def stream():
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        try:
            for chunk in iter(lambda: proc.stdout.read(65536), b""):
                yield chunk
        finally:
            proc.stdout.close()
            proc.wait()

    return StreamingResponse(
        stream(),
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
