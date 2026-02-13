"""Local dev server with clean URL support (mirrors .htaccess rewrite rules)."""
import http.server
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

class CleanURLHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        path = self.path.split("?")[0]

        # Serve / as index.html
        if path == "/":
            self.path = "/index.html"
            return super().do_GET()

        # If file exists as-is, serve it
        full = os.path.join(ROOT, path.lstrip("/"))
        if os.path.isfile(full):
            return super().do_GET()

        # Try appending .html
        if os.path.isfile(full + ".html"):
            self.path = path + ".html"
            return super().do_GET()

        # 404
        self.path = "/404.html"
        self.send_response(404)
        self.end_headers()
        with open(os.path.join(ROOT, "404.html"), "rb") as f:
            self.wfile.write(f.read())

if __name__ == "__main__":
    server = http.server.HTTPServer(("", 8080), CleanURLHandler)
    print("Serving at http://localhost:8080")
    server.serve_forever()
