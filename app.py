import json
import os
import subprocess
import urllib.request

from flask import Flask, jsonify, render_template_string, request, send_from_directory, abort


def get_runtime_port() -> int:
    return int(os.environ.get("PORT", "8080"))


app = Flask(__name__)

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
            <textarea name="json_data" rows="8">{{ json_data }}</textarea></p>
            <p><strong>Rego Policy:</strong><br>
            <textarea name="rego_data" rows="8">{{ rego_data }}</textarea></p>
            <button type="submit">Run Evaluation</button>
        </form>
        {{ output_html | safe }}
    </div>
</body>
</html>
"""


class DEFAULT_JSON:
    """Default JSON configuration provider."""

    @staticmethod
    def get() -> str:
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


@app.get("/")
def index():
    return render_template_string(
        HTML_PAGE,
        json_data=DEFAULT_JSON.get(),
        rego_data=DEFAULT_REGO,
        output_html="",
    )


@app.get("/health")
def health():
    return "ok", 200


@app.get("/api/health")
def api_health():
    return jsonify({"status": "ok", "message": "API is online"}), 200


@app.after_request
def add_cors_headers(response):
    if request.path.startswith("/api/"):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


@app.route("/api/<path:unused>", methods=["OPTIONS"])
def api_options(unused):
    response = jsonify({})
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


@app.post("/api/evaluate")
def api_evaluate():
    data = request.get_json(silent=True) or {}
    json_content = data.get("json_data", DEFAULT_JSON.get())
    rego_content = data.get("rego_data", DEFAULT_REGO)

    with open("temp_input.json", "w", encoding="utf-8") as f:
        f.write(json_content)

    with open("temp_policy.rego", "w", encoding="utf-8") as f:
        f.write(rego_content)

    cmd = ["conftest", "test", "temp_input.json", "-p", "temp_policy.rego"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout or result.stderr
    except FileNotFoundError:
        output = "Conftest CLI is not available in this environment."
        result = subprocess.CompletedProcess(cmd, 1, output, "")

    success = result.returncode == 0
    status_code = 200 if success else 400
    return jsonify({
        "success": success,
        "output": output,
        "json_data": json_content,
        "rego_data": rego_content,
    }), status_code


@app.post('/api/upload-profile')
def upload_profile():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    save_dir = os.path.join(os.getcwd(), 'static')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, 'profile.jpg')
    f.save(save_path)
    # Return a URL that the front-end can use to GET the image via this service
    base = request.host_url.rstrip('/')
    return jsonify({'url': f"{base}/api/profile.jpg"}), 201


@app.get('/api/profile.jpg')
def serve_profile():
    save_dir = os.path.join(os.getcwd(), 'static')
    file_path = os.path.join(save_dir, 'profile.jpg')
    if not os.path.exists(file_path):
        return jsonify({'error': 'Profile image not found'}), 404
    return send_from_directory(save_dir, 'profile.jpg')


@app.get('/api/github-portfolio')
def github_portfolio():
    # Fetch basic repo info from GitHub API for the portfolio repository
    repo_api = 'https://api.github.com/repos/TerryAfram/GRC-portfolio'
    try:
        with urllib.request.urlopen(repo_api, timeout=10) as resp:
            body = resp.read().decode('utf-8')
            data = json.loads(body)
            summary = {
                'name': data.get('name'),
                'description': data.get('description'),
                'stars': data.get('stargazers_count'),
                'forks': data.get('forks_count'),
                'url': data.get('html_url')
            }
            return jsonify(summary)
    except Exception as e:
        return jsonify({'error': 'could not fetch portfolio', 'detail': str(e)}), 502


@app.post('/api/fetch-portfolio-photo')
def fetch_portfolio_photo():
    """Search the GitHub repo for a likely profile image, download it, and save locally.

    Returns JSON with the served URL on success.
    """
    base_api = 'https://api.github.com/repos/TerryAfram/GRC-portfolio/contents'
    try:
        with urllib.request.urlopen(base_api, timeout=10) as resp:
            root = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return jsonify({'error': 'failed to list repo contents', 'detail': str(e)}), 502

    # helper to search a list of items for image files
    def find_image(items):
        for it in items:
            if it.get('type') == 'file' and it.get('name', '').lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                return it.get('path')
        return None

    image_path = find_image(root)
    # if not at root, try common folders
    if not image_path:
        # look for 'images', 'assets', or 'docs' dirs
        for dname in ('images', 'assets', 'docs'):
            try:
                with urllib.request.urlopen(base_api + '/' + dname, timeout=8) as resp:
                    items = json.loads(resp.read().decode('utf-8'))
                    image_path = find_image(items)
                    if image_path:
                        break
            except Exception:
                continue

    if not image_path:
        return jsonify({'error': 'no image file found in repository root or common folders'}), 404

    raw_url = f'https://raw.githubusercontent.com/TerryAfram/GRC-portfolio/main/{image_path}'
    try:
        with urllib.request.urlopen(raw_url, timeout=15) as resp:
            data = resp.read()
    except Exception as e:
        return jsonify({'error': 'failed to download image', 'detail': str(e)}), 502

    save_dir = os.path.join(os.getcwd(), 'static')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, 'profile.jpg')
    try:
        with open(save_path, 'wb') as f:
            f.write(data)
    except Exception as e:
        return jsonify({'error': 'failed to save image', 'detail': str(e)}), 500

    base = request.host_url.rstrip('/')
    return jsonify({'url': f"{base}/api/profile.jpg", 'source': raw_url}), 201


@app.post("/")
def evaluate():
    json_content = request.form.get("json_data", DEFAULT_JSON.get())
    rego_content = request.form.get("rego_data", DEFAULT_REGO)

    with open("temp_input.json", "w", encoding="utf-8") as f:
        f.write(json_content)

    with open("temp_policy.rego", "w", encoding="utf-8") as f:
        f.write(rego_content)

    cmd = ["conftest", "test", "temp_input.json", "-p", "temp_policy.rego"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout or result.stderr
    except FileNotFoundError:
        output = "Conftest CLI is not available in this environment."
        result = subprocess.CompletedProcess(cmd, 1, output, "")

    if result.returncode == 0:
        output_html = '<div class="success"><strong>✅ Passed! No violations found.</strong><pre>%s</pre></div>' % output
    else:
        output_html = '<div class="error"><strong>❌ Failed! Violations detected:</strong><pre>%s</pre></div>' % output

    return render_template_string(
        HTML_PAGE,
        json_data=json_content,
        rego_data=rego_content,
        output_html=output_html,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=get_runtime_port(), debug=False)


