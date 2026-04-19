def generate_talent_vector(profile):
    """
    計算分數並判斷高潛力（示範隨機或簡單規則）
    """
    # 這裡示範用文字長度計分
    text_len = len(profile['Resume_Text'])
    profile['Skills_Score'] = min(10, text_len // 50)
    profile['Experience_Score'] = min(10, text_len // 100)
    profile['Education_Score'] = 8  # 固定分數
    profile['JobRole_Score'] = 7
    profile['Resume_Score'] = min(10, text_len // 80)
    total = profile['Skills_Score'] + profile['Experience_Score'] + profile['Education_Score'] + profile['JobRole_Score'] + profile['Resume_Score']
    profile['Total_Score'] = total
    profile['High_Potential'] = total >= 30
    return profile