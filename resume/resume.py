#!/usr/bin/env python3

import argparse
from jinja2 import Environment, FileSystemLoader, select_autoescape
import yaml
import os
import html
import http.server
import socketserver
from http import HTTPStatus
import traceback
from datetime import datetime

PORT = 8000
TEMPLATE_DIR = os.path.join(os.getcwd(), "templates")
STATIC_DIR = os.path.join(os.getcwd(), "assets")

def format_date(value, format="%b %Y"):
    date = datetime.strptime(value, "%Y-%m-%d")
    return datetime.strftime(date, format)

def scramble(value, chunk_size=2):
    chunks = [value[i:i+chunk_size] for i in range(0, len(value), chunk_size)]
    return "<span style=\"display:none\">1337</span>".join(chunks)

env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["html"])
)
env.filters['formatDate'] = format_date
env.filters['scramble'] = scramble


def render_resume(assets_prefix=""):
    with open("resume.json") as f:
        resume = yaml.safe_load(f)
    template = env.get_template("resume.j2")
    return template.render(resume=resume, assets_prefix=assets_prefix)

def render_cover_letter(assets_prefix=""):
    if not os.path.exists("cover-letter.yaml"):
        return None

    with open("resume.json") as f:
        resume = yaml.safe_load(f)
    with open("cover-letter.yaml") as f:
        cover_letter = yaml.safe_load(f)

    template = env.get_template("cover-letter.j2")
    today = datetime.strftime(datetime.now(), "%Y-%m-%d")
    return template.render(letter=cover_letter, today=today, resume=resume, assets_prefix=assets_prefix)

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        # Serve the resume when the root is accessed, otherwise fallback on the default behaviour
        if self.path == "/":
            self._serve_resume()
        elif self.path == "/cover-letter":
            self._serve_cover_letter()
        else:
            super().do_GET()

    def _serve_resume(self):
        self._serve_content(render_resume)

    def _serve_cover_letter(self):
        self._serve_content(render_cover_letter)

    def _serve_content(self, render):
        try:
            content = render()
            self.send_response(HTTPStatus.OK)
        except Exception:
            error = traceback.format_exc()
            content = f"<html><body><pre>{html.escape(error, quote=False)}</pre></body></html>"
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)

        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", len(content))
        self.end_headers()
        self.wfile.write(content.encode("UTF-8", "replace"))



parser = argparse.ArgumentParser()
parser.add_argument("--generate", action="store_true")

args = parser.parse_args()
if args.generate:
    print("Generating Resume")
    resume = render_resume("assets/")
    with open("index.html", "w") as f:
        f.write(resume)

    letter = render_cover_letter("assets/")
    if letter:
        with open("cover-letter.html", "w") as f:
            f.write(letter)

else:
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()
