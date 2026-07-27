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
    <title>Terry Afram-Kumi | GRC & Security Assurance</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500;600;700&display=swap');
        .font-serif-custom {
            font-family: 'Instrument Serif', Georgia, serif;
        }
        body {
            font-family: 'Inter', sans-serif;
        }
    </style>
</head>
<body class="bg-black text-slate-200 min-h-screen flex flex-col antialiased">

    <!-- HEADER / NAVIGATION -->
    <header class="border-b border-zinc-800/80 bg-black/90 backdrop-blur sticky top-0 z-50">
        <div class="max-w-4xl mx-auto px-6 py-5 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-9 h-9 bg-amber-500 rounded-lg flex items-center justify-center font-bold text-black text-xs tracking-tighter">
                    GRC
                </div>
                <span class="font-bold text-white tracking-wider text-sm uppercase">TERRY AFRAM-KUMI</span>
            </div>
            <nav class="flex items-center space-x-6 text-sm font-medium text-zinc-400">
                <a href="#home" class="text-white underline underline-offset-8 decoration-2 decoration-zinc-500">Home</a>
                <a href="/projects.html" class="hover:text-white transition">GRC Lab</a>
                <a href="mailto:aframterry@gmail.com" class="hover:text-amber-400 transition flex items-center space-x-1">
                    <i class="fa-regular fa-envelope"></i>
                    <span>aframterry@gmail.com</span>
                </a>
            </nav>
        </div>
    </header>

    <!-- MAIN CONTENT CONTAINER -->
    <main class="max-w-2xl mx-auto px-6 py-12 flex-1 space-y-10">

        <!-- HERO HEADLINE & SUMMARY -->
        <section class="space-y-6">
            <h1 class="text-4xl sm:text-5xl font-serif-custom leading-tight text-zinc-100 tracking-wide">
                Governance works best when it's practical. <br>
                <span class="italic text-zinc-400">Not just on paper.</span>
            </h1>

            <p class="text-zinc-400 text-base leading-relaxed font-light">
                Cybersecurity, Risk Governance & Audit Assurance professional (M.Sc., CISA, PMP). Building automated, evidence-driven security programs focused on cloud compliance, policy-as-code, and AI risk management.
            </p>
        </section>

        <!-- OPEN TO ROLES CARD -->
        <section class="bg-zinc-900/60 border border-zinc-800 rounded-xl p-6 space-y-4">
            <span class="text-[11px] font-bold uppercase tracking-widest text-zinc-500 block">OPEN TO ROLES</span>
            <div class="flex flex-wrap gap-2.5">
                <span class="px-3 py-1.5 bg-zinc-900 border border-zinc-800 text-xs font-medium text-zinc-200 rounded-md">IT Audit Manager</span>
                <span class="px-3 py-1.5 bg-zinc-900 border border-zinc-800 text-xs font-medium text-zinc-200 rounded-md">Senior IT Auditor</span>
                <span class="px-3 py-1.5 bg-zinc-900 border border-zinc-800 text-xs font-medium text-zinc-200 rounded-md">Risk & Compliance Specialist</span>
                <span class="px-3 py-1.5 bg-zinc-900 border border-zinc-800 text-xs font-medium text-zinc-200 rounded-md">AI Governance Lead</span>
            </div>
        </section>

        <!-- CERTIFICATIONS & CREDENTIALS BADGES -->
        <section class="space-y-3">
            <div class="flex flex-wrap gap-2.5">
                <span class="px-3.5 py-2 bg-zinc-900/80 border border-zinc-800 text-xs text-zinc-300 rounded-lg">CISA — Certified Information Systems Auditor</span>
                <span class="px-3.5 py-2 bg-zinc-900/80 border border-zinc-800 text-xs text-zinc-300 rounded-lg">PMP — Project Management Professional</span>
                <span class="px-3.5 py-2 bg-zinc-900/80 border border-zinc-800 text-xs text-zinc-300 rounded-lg">ISO/IEC 27001 Annex A Alignment</span>
                <span class="px-3.5 py-2 bg-zinc-900/80 border border-zinc-800 text-xs text-zinc-300 rounded-lg">NIST SP 800-53 Rev 5 & CSF</span>
                <span class="px-3.5 py-2 bg-zinc-900/80 border border-zinc-800 text-xs text-zinc-300 rounded-lg">SOC 2 Trust Services Criteria</span>
                <span class="px-3.5 py-2 bg-zinc-900/80 border border-zinc-800 text-xs text-zinc-300 rounded-lg">NIST AI Risk Management Framework</span>
            </div>
        </section>

        <!-- ACTION BUTTONS -->
        <section class="space-y-3 pt-2">
            <a href="/projects.html" class="block w-full py-3.5 text-center bg-zinc-100 hover:bg-white text-zinc-900 font-semibold text-sm rounded-lg transition shadow-sm">
                Explore My GRC Lab
            </a>
            <a href="mailto:aframterry@gmail.com" class="block w-full py-3.5 text-center bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-200 font-medium text-sm rounded-lg transition flex items-center justify-center space-x-2">
                <i class="fa-regular fa-envelope"></i>
                <span>Get in Touch (aframterry@gmail.com)</span>
            </a>
        </section>

        <!-- PROFILE PHOTO SECTION -->
        <section class="pt-6">
            <div class="relative overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900 shadow-2xl">
                <img src="/api/profile.jpg" onerror="this.onerror=null; this.src='/static/terry.jpeg';" alt="Terry Afram-Kumi" class="w-full h-96 object-cover object-top grayscale hover:grayscale-0 transition duration-500">
                <div class="absolute bottom-4 left-0 right-0 flex justify-center">
                    <span class="px-4 py-1.5 bg-black/75 backdrop-blur-md border border-zinc-700/60 rounded-full text-xs font-mono text-zinc-300 shadow-lg flex items-center space-x-2">
                        <i class="fa-solid fa-envelope text-amber-400"></i>
                        <span>aframterry@gmail.com</span>
                    </span>
                </div>
            </div>
        </section>

    </main>

    <!-- FOOTER -->
    <footer class="border-t border-zinc-900 py-6 text-center text-xs text-zinc-600">
        &copy; 2026 Terry Afram-Kumi. All rights reserved.
    </footer>

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
                    "name": "corporate-audit-logs",
                    "type": "aws_s3_bucket",
                    "values": {
                        "acl": "public-read",
                        "encrypted": False
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
    msg = "ISO 27001 / NIST-ID.AM-01 Violation: S3 bucket is publicly accessible"
}

deny[msg] {
    r := input.resources[_]
    r.type == "aws_s3_bucket"
    r.values.encrypted == false
    msg = "ISO 27001 / NIST-ID.AM-02 Violation: S3 bucket lacks server-side encryption"
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
    base = request.host_url.rstrip('/')
    return jsonify({'url': f"{base}/api/profile.jpg"}), 201


@app.get('/api/profile.jpg')
def serve_profile():
    save_dir = os.path.join(os.getcwd(), 'static')
    file_path = os.path.join(save_dir, 'profile.jpg')
    if not os.path.exists(file_path):
        return jsonify({'error': 'Profile image not found'}), 404
    return send_from_directory(save_dir, 'profile.jpg')


@app.get('/projects.html')
def serve_projects_page():
    root = os.getcwd()
    projects_path = os.path.join(root, 'projects.html')
    if not os.path.exists(projects_path):
        abort(404)
    return send_from_directory(root, 'projects.html')


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
        output_html = '<div class="p-4 bg-emerald-950/50 border border-emerald-800 text-emerald-300 rounded-lg"><strong class="flex items-center space-x-2"><i class="fa-solid fa-circle-check"></i><span>Passed! No violations found.</span></strong><pre class="mt-2 text-xs font-mono bg-slate-900 p-3 rounded text-slate-300 overflow-x-auto">%s</pre></div>' % output
    else:
        output_html = '<div class="p-4 bg-rose-950/50 border border-rose-800 text-rose-300 rounded-lg"><strong class="flex items-center space-x-2"><i class="fa-solid fa-triangle-exclamation"></i><span>Failed! Violations detected:</span></strong><pre class="mt-2 text-xs font-mono bg-slate-900 p-3 rounded text-slate-300 overflow-x-auto">%s</pre></div>' % output

    return render_template_string(
        HTML_PAGE,
        json_data=json_content,
        rego_data=rego_content,
        output_html=output_html,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=get_runtime_port(), debug=False)
