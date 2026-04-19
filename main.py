import os
from flask import Flask, render_template, request, jsonify
from utils.parser import parse_uploaded_file
from utils.config_manager import load_config, save_config

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

LAST_RESULTS = []

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

        LAST_RESULTS = all_results
        return render_template("index.html", results=all_results)

    return render_template("index.html", results=None)

@app.route("/get_resume_detail", methods=["POST"])
def get_resume_detail():
    data = request.get_json()
    name = data.get("name")

    if not LAST_RESULTS or not name:
        return jsonify({"success": False, "text": "無暫存資料"})

    for r in LAST_RESULTS:
        # 關鍵：這裡必須回傳Raw_Text給前端顯示
        if r.get("Name") == name:
            return jsonify({"success": True, "text": r.get("Raw_Text", "無內容")})

    return jsonify({"success": False, "text": "查無此人"})


@app.route("/get_skill_analysis", methods=["POST"])
def get_skill_analysis():
    data = request.get_json() or {}
    name = data.get("name")

    if not LAST_RESULTS:
        return jsonify({"success": False, "message": "目前沒有分析資料"})

    target = None
    if name:
        for r in LAST_RESULTS:
            if r.get("Name") == name:
                target = r
                break
    else:
        target = LAST_RESULTS[0]

    if not target:
        return jsonify({"success": False, "message": "查無此候選人"})

    return jsonify({
        "success": True,
        "analysis": {
            "name": target.get("Name", "Unknown"),
            "total_score": target.get("Total_Score", 0),
            "high_potential": target.get("High_Potential", False),
            "predicted_role": target.get("Predicted_Role", "未判定"),
            "detected_skills": target.get("Detected_Skills", []),
            "skill_by_category": target.get("Skill_By_Category", {}),
            "skill_levels": target.get("Skill_Levels", {}),
            "missing_skills_recommendation": target.get("Missing_Skills_Recommendation", []),
            "gap_analysis": target.get("Gap_Analysis", ""),
            "skill_completeness": target.get("Skill_Completeness", 0),
            "category_coverage": target.get("Category_Coverage", 0),
            "strength_summary": target.get("Strength_Summary", []),
            "role_scores": target.get("Role_Scores", {}),
            "skill_summary_text": target.get("Skill_Summary_Text", ""),
            "experience_score": target.get("Experience_Score", 0),
            "education_score": target.get("Education_Score", 0),
            "skills_score": target.get("Skills_Score", 0),
        }
    })

@app.route("/get_skill_candidates", methods=["GET"])
def get_skill_candidates():
    candidates = [
        {
            "name": r.get("Name", "Unknown"),
            "predicted_role": r.get("Predicted_Role", "未判定"),
            "total_score": r.get("Total_Score", 0),
        }
        for r in LAST_RESULTS
    ]
    return jsonify({"success": True, "candidates": candidates})

@app.route("/settings", methods=["GET", "POST"])
def setting_page():
    current_config = load_config()
    return render_template("settings.html", config=current_config)

@app.route("/api/save_settings", methods=["POST"])
def save_setting():
    try:
        new_config = request.get_json()
        save_config(new_config)
        return jsonify({"success": True, "message": "儲存設定以生效，請重新上傳履歷!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"儲存失敗{str(e)}"})


if __name__ == "__main__":
    app.run(debug=True, port=5050)