# -*- coding: utf-8 -*-
"""
Editor local de contenido de arqtwan.com.

Uso (desde la raiz del proyecto):
    python tools/editor.py

Abre el panel en http://127.0.0.1:8765/ y trabaja SOLO en tu equipo:
  * guarda data/content.js y las fotos en el proyecto (con copia de seguridad)
  * regenera los HTML con tools/build_pages.py
  * sirve la vista previa real en /preview/
  * prepara la carpeta _publicar/ con los archivos a subir a GitHub

No usa tokens, ni cuentas, ni conexion a GitHub. No publica nada.
"""

import base64
import json
import mimetypes
import re
import shutil
import subprocess
import sys
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "content.js"
ADMIN_DIR = ROOT / "admin"
PUBLIC_DIR = ROOT / "_publicar"
BACKUP_DIR = ROOT / "backup" / "content"
BUILD_SCRIPT = ROOT / "tools" / "build_pages.py"

HOST = "127.0.0.1"
PORT = 8765
MAX_IMAGE_BYTES = 12 * 1024 * 1024
MAX_VIDEO_BYTES = 15 * 1024 * 1024

MEDIA_RE = re.compile(r"^assets/(img|video)/[a-z0-9][a-z0-9._/-]*\.(jpg|jpeg|png|webp|svg|mp4)$")
BLOCKED_PARTS = {"data", "tools", "backup", "admin", "_publicar", "_site", ".git", ".github"}

sys.path.insert(0, str(ROOT / "tools"))
import build_pages as bp  # noqa: E402  (mismo generador que el sitio)


def read_data():
    raw = DATA_FILE.read_text(encoding="utf-8")
    match = re.search(r"window\.ARQTWAN\s*=\s*", raw)
    if not match:
        raise ValueError("data/content.js no contiene 'window.ARQTWAN ='")
    header = raw[: match.start()]
    body = re.sub(r";\s*$", "", raw[match.end():].strip())
    return header, json.loads(body), raw


def validate(data):
    if not isinstance(data, dict):
        raise ValueError("El contenido debe ser un objeto JSON.")
    for key in ("site", "services", "projects"):
        if key not in data:
            raise ValueError("Falta la clave obligatoria: {0}".format(key))
    if not isinstance(data["site"], dict):
        raise ValueError("site debe ser un objeto.")
    if not isinstance(data["services"], list) or not data["services"]:
        raise ValueError("services debe ser una lista con al menos un servicio.")
    if not isinstance(data["projects"], list):
        raise ValueError("projects debe ser una lista.")
    slugs = set()
    for service in data["services"]:
        if not isinstance(service, dict) or not service.get("slug") or not service.get("name"):
            raise ValueError("Cada servicio necesita 'slug' y 'name'.")
        if service["slug"] in slugs:
            raise ValueError("Slug de servicio repetido: {0}".format(service["slug"]))
        slugs.add(service["slug"])
    for project in data["projects"]:
        if not isinstance(project, dict) or not project.get("title"):
            raise ValueError("Cada proyecto necesita un titulo.")


def write_data(header, data):
    text = header + "window.ARQTWAN = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    DATA_FILE.write_text(text, encoding="utf-8", newline="\n")


def stamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def backup_file(path):
    if not path.exists():
        return None
    relative = path.relative_to(ROOT)
    target = BACKUP_DIR / stamp() / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    return target.relative_to(ROOT).as_posix()


def save_media(items):
    written = []
    for item in items or []:
        relative = str(item.get("path") or "").replace("\\", "/").strip("/")
        if not MEDIA_RE.match(relative):
            raise ValueError("Ruta de archivo no permitida: {0}".format(relative))
        data_url = str(item.get("dataUrl") or "")
        if "," not in data_url:
            raise ValueError("Archivo sin datos validos: {0}".format(relative))
        payload = base64.b64decode(data_url.split(",", 1)[1])
        is_video = relative.endswith(".mp4")
        limit = MAX_VIDEO_BYTES if is_video else MAX_IMAGE_BYTES
        if len(payload) > limit:
            raise ValueError(
                "{0} pesa {1} MB y el limite es {2} MB.".format(
                    relative, round(len(payload) / 1048576, 1), limit // 1048576
                )
            )
        target = (ROOT / relative).resolve()
        if ROOT not in target.parents:
            raise ValueError("Ruta fuera del proyecto: {0}".format(relative))
        backup_file(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        written.append({"path": relative, "bytes": len(payload)})
    return written


def build_site():
    result = subprocess.run(
        [sys.executable, str(BUILD_SCRIPT)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return {"ok": result.returncode == 0, "log": (result.stdout or "") + (result.stderr or "")}


def export_files(files):
    """Copia en _publicar/ los archivos indicados, conservando rutas."""
    if PUBLIC_DIR.exists():
        shutil.rmtree(PUBLIC_DIR)
    copied = []
    candidates = ["data/content.js"] + [str(f).replace("\\", "/").strip("/") for f in files or []]
    seen = set()
    for relative in candidates:
        if relative in seen:
            continue
        seen.add(relative)
        if relative != "data/content.js" and not MEDIA_RE.match(relative):
            raise ValueError("Archivo no permitido en la exportacion: {0}".format(relative))
        source = (ROOT / relative).resolve()
        if ROOT not in source.parents or not source.is_file():
            raise ValueError("No existe el archivo: {0}".format(relative))
        target = PUBLIC_DIR / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append(relative)

    leeme = (
        "ARCHIVOS PARA GITHUB - ARQTWAN\n"
        "=============================\n\n"
        "1. Abre la pagina de carga de tu repositorio en GitHub (/upload/main).\n"
        "2. Arrastra esta carpeta completa (_publicar) a la zona de carga.\n"
        "   GitHub conserva las rutas: data/content.js y assets/img/...\n"
        "3. Mensaje del commit: describe el cambio (ej. Nuevo proyecto Casa Patio).\n"
        "4. Pulsa 'Commit changes'. La GitHub Action reconstruye y publica el sitio.\n\n"
        "No subas nada mas: los HTML, sitemap.xml y robots.txt se generan solos.\n"
    )
    (PUBLIC_DIR / "LEEME.txt").write_text(leeme, encoding="utf-8", newline="\n")
    return {"folder": PUBLIC_DIR.relative_to(ROOT).as_posix(), "files": copied}



def seo_state(data):
    site = data["site"]
    base = (site.get("url") or "https://arqtwan.com").rstrip("/")
    pages_out = []

    def add(key, slug, label, path, title, description):
        custom_title, custom_description = bp.seo_override(data, key, slug)
        pages_out.append(
            {
                "key": key,
                "slug": slug,
                "label": label,
                "path": path,
                "url": base + "/" + path,
                "title": custom_title or title,
                "description": custom_description or description,
                "isCustom": bool(custom_title or custom_description),
            }
        )

    add(
        "home",
        None,
        "Inicio",
        "index.html",
        "Arqtwan | Licencias, arquitectura y construcción en Colombia",
        "Diseño arquitectónico, licencias de construcción, ingeniería y obra en Colombia. "
        "Un solo equipo para tramitar, diseñar y construir con criterio técnico.",
    )
    for service in data["services"]:
        default_description = bp.shorten(
            (service.get("short", "") + " " + service.get("summary", "")).strip()
            if service.get("short")
            else service.get("summary", ""),
            157,
        )
        add(
            "servicios",
            service["slug"],
            service["name"],
            "servicios/{0}.html".format(service["slug"]),
            "{0} en Colombia | Arqtwan".format(service["name"]),
            default_description,
        )
    add(
        "proyectos",
        None,
        "Proyectos",
        "proyectos.html",
        "Proyectos | Arqtwan arquitectura e ingeniería",
        "Portafolio de Arqtwan: proyectos de arquitectura, ingeniería y construcción "
        "documentados con datos verificables e imágenes propias.",
    )
    add(
        "contacto",
        None,
        "Contacto",
        "contacto.html",
        "Contacto y cotización | Arqtwan",
        "Escríbenos por WhatsApp o usa el formulario para cotizar tu proyecto de "
        "arquitectura, licencias, ingeniería o construcción en Colombia.",
    )
    add(
        "privacidad",
        None,
        "Privacidad",
        "privacidad.html",
        "Política de privacidad | Arqtwan",
        "Cómo trata Arqtwan los datos que recibe a través de este sitio: formulario de "
        "cotización, WhatsApp, alojamiento y derechos del titular.",
    )
    return pages_out


def state():
    _header, data, _raw = read_data()
    return {
        "ok": True,
        "content": data,
        "seo": seo_state(data),
        "meta": {
            "root": str(ROOT),
            "git": (ROOT / ".git").exists(),
            "repo": (data.get("site") or {}).get("repo", ""),
            "contentBytes": DATA_FILE.stat().st_size,
        },
    }


def safe_path(base, relative):
    target = (base / relative).resolve()
    if target != base.resolve() and base.resolve() not in target.parents:
        return None
    return target



class Handler(BaseHTTPRequestHandler):
    server_version = "ArqtwanEditor/1.0"

    def log_message(self, format, *args):
        return

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path):
        if path is None or not path.is_file():
            self.send_error(404, "No encontrado")
            return
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript", "application/json"):
            ctype += "; charset=utf-8"
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self):
        path = unquote(urlparse(self.path).path)

        if path in ("/", "/index.html"):
            self.send_file(ADMIN_DIR / "index.html")
            return
        if path == "/api/state":
            try:
                self.send_json(state())
            except Exception as exc:  # noqa: BLE001
                self.send_json({"ok": False, "error": str(exc)}, 500)
            return
        if path.startswith("/admin/"):
            self.send_file(safe_path(ADMIN_DIR, path[len("/admin/"):]))
            return
        if path.startswith("/preview/"):
            relative = path[len("/preview/"):]
            if any(part in BLOCKED_PARTS for part in Path(relative).parts):
                self.send_error(403, "Ruta reservada")
                return
            target = safe_path(ROOT, relative)
            if target is not None and target.is_dir():
                target = target / "index.html"
            self.send_file(target)
            return

        self.send_error(404, "No encontrado")

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            body = self.read_body()

            if path == "/api/save":
                header, _data, _raw = read_data()
                content = body.get("content")
                validate(content)
                backup_file(DATA_FILE)
                write_data(header, content)
                saved = save_media(body.get("images"))
                self.send_json(
                    {
                        "ok": True,
                        "files": ["data/content.js"] + [s["path"] for s in saved],
                        "media": saved,
                    }
                )
                return

            if path == "/api/build":
                self.send_json(build_site())
                return

            if path == "/api/export":
                result = export_files(body.get("files"))
                result["ok"] = True
                self.send_json(result)
                return

            if path == "/api/state":
                self.send_json(state())
                return

            self.send_json({"ok": False, "error": "Ruta desconocida"}, 404)
        except ValueError as exc:
            self.send_json({"ok": False, "error": str(exc)}, 400)
        except Exception as exc:  # noqa: BLE001
            self.send_json({"ok": False, "error": repr(exc)}, 500)


def main():
    port = PORT
    for _attempt in range(12):
        try:
            server = ThreadingHTTPServer((HOST, port), Handler)
            break
        except OSError:
            port += 1
    else:
        raise SystemExit("No hay puerto libre entre 8765 y 8776.")

    url = "http://{0}:{1}/".format(HOST, port)
    print("")
    print("  Editor ARQTWAN")
    print("  --------------")
    print("  Proyecto: {0}".format(ROOT))
    print("  Panel:    {0}".format(url))
    print("  Vista:    {0}preview/index.html".format(url))
    print("")
    print("  Ctrl+C para cerrar. No se publica nada automaticamente.")
    print("")
    if "--no-browser" not in sys.argv:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Editor cerrado.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

