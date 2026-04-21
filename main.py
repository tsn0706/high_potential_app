import os
from flask import Flask, render_template, request, jsonify
from utils.parser import parse_uploaded_file
from utils.config_manager import load_config, save_config
from utils.storage import load_cached_results, save_cached_results, clear_cached_results
from utils.skill_analysis import analyze_candidate

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

LAST_RESULTS = load_cached_results()


def enrich_results(results):
    enriched = []
    for item in results:
        row = dict(item)
        row['Skill_Analysis'] = analyze_candidate(row)
        enriched.append(row)
    return enriched


@app.route("/", methods=["GET", "POST"])
def index():
    global LAST_RESULTS

    if request.method == "POST":
        files = request.files.getlist("file")
        all_results = []

        for file in files:
            if file and file.filename != "":
                path = os.path.join(UPLOAD_FOLDER, file.filename)
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
    app.run(debug=True, port=5050)
