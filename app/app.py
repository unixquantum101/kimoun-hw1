import os
import socket

import redis
from flask import Flask, Response

app = Flask(__name__)

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
PAGE_TITLE = os.environ.get("PAGE_TITLE", "Cloud Computing Homework - v2")
APP_VERSION = os.environ.get("APP_VERSION", "v1")

cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_connect_timeout=2)


def get_hit_count():
    """Increment and return the visit counter.

    Returns None if Redis is unreachable, so the page still renders
    (useful on EC2 when the app is run as a single container).
    """
    try:
        return cache.incr("hits")
    except redis.exceptions.RedisError:
        return None


@app.route("/")
def index():
    count = get_hit_count()
    container = socket.gethostname()

    if count is None:
        counter_line = "Redis is not reachable - counter unavailable."
    else:
        counter_line = f"This page has been visited {count} time(s)."

    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{PAGE_TITLE}</title>
    <style>
      body {{ font-family: system-ui, sans-serif; margin: 3rem auto; max-width: 34rem;
             line-height: 1.6; color: #14202b; }}
      .badge {{ display: inline-block; background: #0b7285; color: #fff;
                padding: .15rem .6rem; border-radius: 999px; font-size: .85rem; }}
      code {{ background: #eef2f5; padding: .1rem .35rem; border-radius: 4px; }}
    </style>
  </head>
  <body>
    <h1>{PAGE_TITLE}</h1>
    <p><span class="badge">{APP_VERSION}</span></p>
    <p>{counter_line}</p>
    <p>Served by container <code>{container}</code>.</p>
  </body>
</html>"""

    resp = Response(html, mimetype="text/html")
    resp.headers["X-App-Version"] = APP_VERSION
    return resp


@app.route("/health")
def health():
    return {"status": "ok", "version": APP_VERSION}


if __name__ == "__main__":
    # Development entrypoint only; the container runs gunicorn (see Dockerfile).
    app.run(host="0.0.0.0", port=5000)
