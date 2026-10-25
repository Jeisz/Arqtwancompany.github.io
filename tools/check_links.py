"""Revisa enlaces internos, assets e ids duplicados en el sitio generado.

Uso:  python tools/check_links.py [--root CARPETA]
"""

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".github", "tools", "data", "node_modules", "admin", "backup", ".tmp_frames", ".tmp_review"}

ATTR = re.compile(r'(?:href|src|poster)="([^"]+)"')
ID = re.compile(r'\bid="([^"]+)"')
CANON = re.compile(r'<link rel="canonical" href="([^"]+)">')


def pages():
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        yield path


def resolve(page, ref):
    ref = ref.split("#")[0].split("?")[0]
    if not ref or ref.startswith(("http://", "https://", "mailto:", "tel:", "data:", "javascript:")):
        return None
    return (page.parent / unquote(ref)).resolve()


def main():
    global ROOT
    parser = argparse.ArgumentParser(description="Verifica el sitio generado.")
    parser.add_argument(
        "--root",
        metavar="CARPETA",
        help="Carpeta a revisar (por defecto, la raiz del proyecto).",
    )
    args = parser.parse_args()
    if args.root:
        ROOT = Path(args.root).resolve()
        if not ROOT.is_dir():
            raise SystemExit("No existe la carpeta: {0}".format(ROOT))

    errors = 0
    targets = list(pages())
    ids = {}

    for page in targets:
        rel = page.relative_to(ROOT).as_posix()
        text = page.read_text(encoding="utf-8")

        for ref in ATTR.findall(text):
            target = resolve(page, ref)
            if target is None:
                continue
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                print("ROTO  {0}  ->  {1}".format(rel, ref))
                errors += 1

        canon = CANON.findall(text)
        if len(canon) != 1:
            print("CANONICAL x{0} en {1}".format(len(canon), rel))
            errors += 1

        if "{{" in text or "}}" in text:
            print("PLACEHOLDER sin resolver en {0}".format(rel))
            errors += 1

        for block in re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', text, re.S
        ):
            try:
                json.loads(block)
            except Exception as exc:  # noqa: BLE001
                print("JSON-LD invalido en {0}: {1}".format(rel, exc))
                errors += 1

        ids[rel] = Counter(ID.findall(text))

    for rel, counter in ids.items():
        dupes = [i for i, n in counter.items() if n > 1]
        if dupes:
            print("ID DUPLICADO en {0}: {1}".format(rel, ", ".join(sorted(dupes))))
            errors += 1

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for loc in re.findall(r"<loc>([^<]+)</loc>", sitemap):
        path = urlparse(loc).path.lstrip("/") or "index.html"
        if not (ROOT / path).exists():
            print("SITEMAP apunta a archivo inexistente: {0}".format(loc))
            errors += 1

    print("\n{0} paginas revisadas · {1} problema(s)".format(len(targets), errors))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()

