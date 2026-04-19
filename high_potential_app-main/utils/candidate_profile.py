def create_candidate_profile(record):
    """
    將解析出的履歷轉為統一 Candidate Profile
    """
    profile = {
        'Name': record.get('Name', '未知'),
        'Resume_Text': record.get('Resume_Text', ''),
        'Skills_Score': 0,
        'Experience_Score': 0,
        'Education_Score': 0,
        'JobRole_Score': 0,
        'Resume_Score': 0
    }
    return profile