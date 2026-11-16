from pathlib import Path


ROOT = Path(__file__).resolve().parent
FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "application/javascript; charset=utf-8"),
    "/config.js": ("config.js", "application/javascript; charset=utf-8"),
}


def handler(event, context):
    path = event.get("rawPath", "/")
    asset = FILES.get(path)
    if not asset:
        return {"statusCode": 404, "body": "Not found"}
    name, content_type = asset
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": content_type,
            "Cache-Control": "no-cache" if name in {"index.html", "config.js"} else "public, max-age=3600",
        },
        "body": (ROOT / name).read_text(encoding="utf-8"),
    }
