import os
import subprocess
import threading
import traceback
from flask import Flask, render_template, request, jsonify, send_from_directory
from utils_yt import get_video_info, download_audio, DOWNLOAD_DIR

from jinja2 import ChoiceLoader, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(BASE_DIR, "templates")
static_dir = os.path.join(BASE_DIR, "static")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Garantir busca resiliente de templates no Linux/Railway (templates/, Templates/, raiz)
app.jinja_loader = ChoiceLoader([
    FileSystemLoader(template_dir),
    FileSystemLoader(BASE_DIR),
    FileSystemLoader(os.path.join(BASE_DIR, "Templates")),
    FileSystemLoader(os.path.join(BASE_DIR, "template")),
])

@app.errorhandler(500)
def server_error(e):
    err_msg = traceback.format_exc()
    print(f"[ERRO 500]: {err_msg}")
    return f"<h2>Erro Interno no Servidor (500)</h2><pre>{err_msg}</pre>", 500

# Garantir que a pasta de downloads exista
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Dicionário em memória para rastrear progresso de downloads ativos
download_status = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/info", methods=["POST"])
def video_info():
    data = request.json or {}
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"success": False, "error": "Por favor, insira um link do YouTube válido."}), 400

    try:
        info = get_video_info(url)
        return jsonify({"success": True, "data": info})
    except Exception as e:
        return jsonify({"success": False, "error": f"Erro ao obter informações do vídeo: {str(e)}"}), 500

@app.route("/api/download", methods=["POST"])
def download():
    data = request.json or {}
    url = data.get("url", "").strip()
    quality = data.get("quality", "320")

    if not url:
        return jsonify({"success": False, "error": "URL não fornecida."}), 400

    task_id = request.remote_addr + "_" + str(hash(url))
    download_status[task_id] = {"status": "iniciando", "percent": 0, "message": "Iniciando download..."}

    def hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percent = round(downloaded / total * 100, 1)
                download_status[task_id] = {
                    "status": "downloading",
                    "percent": percent,
                    "message": f"Baixando fluxo de áudio ({percent}%)"
                }
            else:
                download_status[task_id] = {
                    "status": "downloading",
                    "percent": 50,
                    "message": "Baixando dados do vídeo..."
                }
        elif d['status'] == 'finished':
            download_status[task_id] = {
                "status": "converting",
                "percent": 90,
                "message": "Convertendo áudio para MP3 alta definição..."
            }

    try:
        result = download_audio(url, quality=quality, progress_hook=hook)
        download_status[task_id] = {
            "status": "completed",
            "percent": 100,
            "message": "Conversão concluída!"
        }
        return jsonify({
            "success": True,
            "data": {
                "title": result["title"],
                "uploader": result["uploader"],
                "duration": result["duration"],
                "filename": result["filename"],
                "download_url": f"/api/file/{result['filename']}",
                "play_url": f"/api/play/{result['filename']}"
            }
        })
    except Exception as e:
        download_status[task_id] = {"status": "error", "percent": 0, "message": str(e)}
        return jsonify({"success": False, "error": f"Falha na conversão: {str(e)}"}), 500

@app.route("/api/file/<path:filename>")
def download_file(filename):
    from urllib.parse import quote, unquote
    import re
    
    filename = unquote(filename)
    safe_name = filename if filename.lower().endswith('.mp3') else f"{filename}.mp3"
    
    ascii_clean = re.sub(r'[^a-zA-Z0-9_.-]', '_', safe_name)
    encoded_utf8 = quote(safe_name)
    
    response = send_from_directory(
        DOWNLOAD_DIR, 
        filename, 
        as_attachment=True, 
        mimetype="audio/mpeg"
    )
    response.headers["Content-Type"] = "audio/mpeg"
    response.headers["Content-Disposition"] = f"attachment; filename=\"{ascii_clean}\"; filename*=UTF-8''{encoded_utf8}"
    return response

@app.route("/api/play/<path:filename>")
def play_file(filename):
    from urllib.parse import unquote
    filename = unquote(filename)
    response = send_from_directory(
        DOWNLOAD_DIR, 
        filename, 
        as_attachment=False, 
        mimetype="audio/mpeg"
    )
    response.headers["Content-Type"] = "audio/mpeg"
    return response

@app.route("/api/list", methods=["GET"])
def list_files():
    try:
        files = []
        if os.path.exists(DOWNLOAD_DIR):
            for f in os.listdir(DOWNLOAD_DIR):
                if f.lower().endswith(('.mp3', '.m4a', '.wav')):
                    fp = os.path.join(DOWNLOAD_DIR, f)
                    size_mb = round(os.path.getsize(fp) / (1024 * 1024), 2)
                    files.append({
                        "filename": f,
                        "size_mb": size_mb,
                        "mtime": os.path.getmtime(fp),
                        "download_url": f"/api/file/{f}",
                        "play_url": f"/api/play/{f}"
                    })
            files.sort(key=lambda x: x["mtime"], reverse=True)
        return jsonify({"success": True, "files": files})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/delete/<filename>", methods=["DELETE"])
def delete_file(filename):
    try:
        fp = os.path.join(DOWNLOAD_DIR, filename)
        if os.path.exists(fp):
            os.remove(fp)
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Arquivo não encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/open_folder", methods=["POST"])
def open_folder():
    try:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        if os.name == 'nt':
            os.startfile(DOWNLOAD_DIR)
        else:
            subprocess.Popen(['xdg-open', DOWNLOAD_DIR])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    port = int(os.environ.get("PORT", 5000))
    print(f"[SERVER] Servidor do Conversor de YouTube para MP3 iniciado na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
