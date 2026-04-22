import os
import time
from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
from utils.parser import parse_uploaded_file
from utils.config_manager import load_config, save_config
from utils.storage import load_cached_results, save_cached_results, clear_cached_results
from utils.skill_analysis import analyze_candidate
from pyngrok import ngrok

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per hour"]  # 全站基本限制
)

app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8MB
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

LAST_RESULTS = load_cached_results()
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "csv"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def enrich_results(results):
    enriched = []
    for item in results:
        row = dict(item)
        row['Skill_Analysis'] = analyze_candidate(row)
        enriched.append(row)
    return enriched

@app.errorhandler(413)
def too_large(e):
    return "檔案過大", 413

@app.route("/", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def index():
    global LAST_RESULTS

    if request.method == "POST":
        files = request.files.getlist("file")

        # 上傳數量限制
        if len(files) > 200:
            return "超出單次檔案數量", 400

        all_results = []

        for file in files:
            if not file or file.filename == "":
                continue

            if not allowed_file(file.filename):
                return "不支援該檔案", 400

            # 防檔名路徑攻擊
            safe_name = secure_filename(file.filename)

            if not safe_name:
                return "檔名不合法", 400
            
            unique_name = f"{int(time.time())}_{safe_name}"
            path = os.path.join(UPLOAD_FOLDER, unique_name)

            file.save(path)

            try:
                data_list = parse_uploaded_file(path)
                all_results.extend(data_list)
            except Exception as e:
                print(f"Error processing {file.filename}: {e}")

        LAST_RESULTS = enrich_results(all_results)
        save_cached_results(LAST_RESULTS)
        return render_template("index.html", results=LAST_RESULTS)

    if LAST_RESULTS:
        return render_template("index.html", results=LAST_RESULTS)

    return render_template("index.html", results=None)



@app.route("/get_resume_detail", methods=["POST"])
@limiter.limit("30 per minute")
def get_resume_detail():
    data = request.get_json() or {}
    name = data.get("name")

    if not LAST_RESULTS or not name:
        return jsonify({"success": False, "text": "無暫存資料"})

    for r in LAST_RESULTS:
        if r.get("Name") == name:
            return jsonify({"success": True, "text": r.get("Raw_Text", "無內容")})

    return jsonify({"success": False, "text": "查無此人"})


@app.route("/api/results", methods=["GET"])
def get_results_api():
    return jsonify({"success": True, "results": LAST_RESULTS})


@app.route("/api/skill_analysis", methods=["POST"])
@limiter.limit("10 per minute")
def get_skill_analysis_api():
    data = request.get_json() or {}
    name = data.get("name")

    if not LAST_RESULTS:
        return jsonify({"success": False, "message": "目前沒有已保存的分析資料"})

    for r in LAST_RESULTS:
        if r.get("Name") == name:
            return jsonify({"success": True, "analysis": r.get("Skill_Analysis", analyze_candidate(r))})

    return jsonify({"success": False, "message": "查無此候選人資料"})


@app.route("/api/clear_results", methods=["POST"])
@limiter.limit("3 per minute")
def clear_results_api():
    global LAST_RESULTS
    LAST_RESULTS = []
    clear_cached_results()
    return jsonify({"success": True, "message": "已清除暫存結果"})


@app.route("/settings", methods=["GET", "POST"])
def setting_page():
    current_config = load_config()
    return render_template("settings.html", config=current_config)


@app.route("/api/save_settings", methods=["POST"])
def save_setting():
    try:
        new_config = request.get_json()
        save_config(new_config)
        return jsonify({"success": True, "message": "儲存設定已生效，重新整理後仍會保留分析結果。"})
    except Exception as e:
        return jsonify({"success": False, "message": f"儲存失敗：{str(e)}"})


if __name__ == "__main__":
    public_url = ngrok.connect(5000)
    print("公開網址：", public_url)
    app.run(host="0.0.0.0", port=5000, debug=False)
