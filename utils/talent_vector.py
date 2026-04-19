from .config_manager import load_config

# # 定義技能清單與加權
# all_skills = ['python', 'sql', 'machine learning', 'tensorflow', 'numpy', 'scikit-learn', 'statistics', 'nlp', 'data visualization', 'pandas']
# important_skills = ['python', 'machine learning', 'sql', 'tensorflow']
# education_weights = {'Bachelor': 1, 'Master': 2, 'PhD': 3}
# high_potential_roles = ['data scientist', 'ml engineer', 'ai researcher']

def generate_talent_vector(profile: dict) -> dict:
    """
    將解析後的候選人資料轉換為評分向量，並計算總分。
    """
    vector = {}
    config = load_config() # 載入設定檔，取得權重
    main_weights = config['main_weights']
    sub_items = config['sub_items']
    
    # --- 1. 基礎資訊傳遞 (關鍵修正點) ---
    # 必須將 Raw_Text 放入回傳的字典中，API 才能讀取到原始內容
    vector['Name'] = profile.get('Name', 'Unknown')
    vector['Raw_Text'] = profile.get('Raw_Text', '')
    
    # --- 2. 技能評分 (Skills Score) ---
    skills_list = profile.get('Skills_List', [])
    skill_score = 0
    for skill in skills_list:
        if skill in sub_items['Skills']:
            # 根據自定義分數累加技能分
            skill_score += sub_items['Skills'][skill]
    vector['Skills_Score'] = int(skill_score)
    
    # --- 3. 經驗評分 (Experience Score) ---
    # 設定上限為 10 分，避免極端數值影響模型
    years = profile.get('Years_Experience', 0)
    vector['Experience_Score'] = min(int(years), 10)
    
    # --- 4. 教育評分 (Education Score) ---
    edu_level = profile.get('Education_Level', 'Bachelor').lower()
    vector['Education_Score'] = sub_items['Education'].get(edu_level, 1)
    
    # --- 5. 職位加分 (Job Role Score) ---
    job_role = profile.get('Job_Role', '').lower() # 固定格式職位名稱比對
    raw_text = profile.get('Raw_Text', '')[:500].lower() # 前500字關鍵比對
    job_score = 0
    for target_role, weight in sub_items['JobRole'].items():
        if target_role in job_role or target_role in raw_text:
            job_score += weight
    vector['JobRole_Score'] = job_score
    
    # --- 6. 履歷關鍵字加分 (Resume Score) ---
    # 針對 Resume_Text (已清理過的文字) 進行關鍵字掃描
    resume_text_clean = profile.get('Resume_Text', '').lower()
    vector['Resume_Score'] = sum([val for kw, val in sub_items['Keywords'].items() if kw in resume_text_clean])
    
    # --- 7. 總分計算 (Weighted Total Score) ---
    # 公式：技能(x2) + 經驗(x1.5) + 教育(x1.2) + 職位(x2) + 履歷關鍵字(x1) detail in config_manager.py
    total_score = (
        vector['Skills_Score'] * main_weights['Skills'] +
        vector['Experience_Score'] * main_weights['Experience'] +
        vector['Education_Score'] * main_weights['Education'] +
        vector['JobRole_Score'] * main_weights['JobRole'] +
        vector['Resume_Score'] * main_weights['Resume']
    )
    
    vector['Total_Score'] = round(total_score, 2)
    
    # --- 8. 高潛力判定 ---
    # 設定門檻，例如總分大於 15 分即為高潛力人才
    vector['High_Potential'] = total_score >= config['threshold']
    
    return vector