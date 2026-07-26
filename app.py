import http.server
import json
import os
import socket
import subprocess
import urllib.parse


def get_available_port(start_port: int) -> int:
    for port in range(start_port, start_port + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue
    raise OSError(f"Unable to find an available port from {start_port}")


PORT = get_available_port(int(os.environ.get("PORT", "8080")))

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>GRC Policy-as-Code Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f7f6; color: #222; }
        .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); max-width: 900px; }
        pre { background: #272822; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; }
        textarea { width: 100%; font-family: monospace; box-sizing: border-box; padding: 10px; border: 1px solid #ccc; border-radius: 4px; }
        .success { color: green; }
        .error { color: red; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🛡️ GRC Policy-as-Code Dashboard</h2>
        <form method="POST">
            <p><strong>Configuration JSON:</strong><br>
            <textarea name="json_data" rows="8">{DEFAULT_JSON}</textarea></p>
            <p><strong>Rego Policy:</strong><br>
            <textarea name="rego_data" rows="8">{DEFAULT_REGO}</textarea></p>
            <button type="submit">Run Evaluation</button>
        </form>
        {OUTPUT}
    </div>
</body>
</html>
"""

class DEFAULT_JSON:
    """Default JSON configuration provider."""

    @staticmethod
    def get():
        config = {
            "resources": [
                {
                    "type": "aws_s3_bucket",
                    "values": {
                        "acl": "public-read"
                    },
                }
            ]
        }
        return json.dumps(config, indent=2)

DEFAULT_REGO = """package main

deny[msg] {
    r := input.resources[_]
    r.type == "aws_s3_bucket"
    r.values.acl == "public-read"
    msg = "S3 bucket is publicly accessible"
}"""


class GRCRequestHandler(http.server.BaseHTTPRequestHandler):

  def do_GET(self):
    self.send_response(200)
    self.send_header("Content-type", "text/html; charset=utf-8")
    self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
    self.send_header("Pragma", "no-cache")
    self.send_header("Expires", "0")
    self.end_headers()
    default_json = DEFAULT_JSON.get()
    html: str = (
        HTML_PAGE.replace("{DEFAULT_JSON}", default_json)
        .replace("{DEFAULT_REGO}", DEFAULT_REGO)
        .replace("{OUTPUT}", "")
    )
    self.wfile.write(html.encode("utf-8"))

  def do_POST(self):
    content_length = int(self.headers.get("Content-Length", 0))
    post_data = self.rfile.read(content_length).decode("utf-8")
    params = urllib.parse.parse_qs(post_data)

    default_json = DEFAULT_JSON.get()
    json_content = params.get("json_data", [default_json])[0]
    rego_content = params.get("rego_data", [DEFAULT_REGO])[0]

    with open("temp_input.json", "w") as f:
      f.write(json_content)

    with open("temp_policy.rego", "w") as f:
      f.write(rego_content)

    cmd = ["conftest", "test", "temp_input.json", "-p", "temp_policy.rego"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout or result.stderr

    if result.returncode == 0:
      out_html = '<div class="success"><strong>✅ Passed! No violations found.</strong><pre>%s</pre></div>' % output
    else:
      out_html = (
          '<div class="error"><strong>❌ Failed! Violations detected:</strong><pre>%s</pre></div>'
          % output
      )

    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    html = HTML_PAGE.replace("{DEFAULT_JSON}", json_content).replace("{DEFAULT_REGO}", rego_content).replace("{OUTPUT}", out_html)
    self.wfile.write(html.encode("utf-8"))


if __name__ == "__main__":
  server = http.server.HTTPServer(("0.0.0.0", PORT), GRCRequestHandler)
  print(f"Server started on port {PORT}...")
  server.serve_forever() 


