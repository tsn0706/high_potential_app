# utils/candidate_profile.py

import re
import os
from datetime import datetime
import pandas as pd
import nltk
from nltk import pos_tag, ne_chunk
from nltk.tree import Tree
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from .config_manager import load_config


def init_nltk():
    required_resources = [
        'punkt', 'punkt_tab', 'stopwords', 
        'averaged_perceptron_tagger', 'averaged_perceptron_tagger_eng',  # 新版英文標註器
        'maxent_ne_chunker', 'maxent_ne_chunker_tab',
        'words', 'wordnet'
    ]# 如果跳出需要nltk.download提示，請在此補上
    
    for res in required_resources:
        try:
            # 嘗試下載，如果已存在會自動跳過
            nltk.download(res, quiet=True)
        except Exception as e:
            print(f"下載 {res} 失敗: {e}")

init_nltk()

STOP_WORDS = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def extract_name_smart(raw_text, file_path=None):
    # NER與位置判斷抓取名字
    BLACK_LIST = {'name', 'resume', 'cv', 'curriculum', 'page', 'profile', 'contact', 'email', 'phone', 'software',
                  'engineer', 'manager', 'developer', 'html', 'css'}#過濾黑名單
    # raw_text為空，回傳檔名。檔名為空回傳Unknown
    if not raw_text or len(raw_text.strip()) == 0:
        return os.path.basename(file_path) if file_path else "Unknown"
    
    # NLTK NER
    target_text = raw_text[:150] # 在文件前150字中尋找名字(效益化)
    try:
        tokens = word_tokenize(target_text)
        tags = pos_tag(tokens)
        chunks = ne_chunk(tags)
        
        for chunk in chunks:
            if isinstance(chunk, Tree) and chunk.label() == 'PERSON':
                name = " ".join([leaf[0] for leaf in chunk.leaves()])
                # 過濾:名字只取1-2組單字組成
                cuts = name.split() #切片
                filter = [n for n in cuts if n.lower() not in BLACK_LIST and n.isalpha()] #過濾黑名單與非字母
                if 1 <= len(filter) < 3:
                    return " ".join(filter) #回傳過濾後的名字
    except Exception as e:
        print(f"NER Error: {e}")

    # 首行過濾，如果NER失敗，抓取前三行中第一條非空白、非標題的文字
    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
    for line in lines[:3]:
        # 如果這行字數適中，且不在黑名單中，猜測是名字
        if 1 <= len(line.split()) < 3 and not any(b in line.lower() for b in BLACK_LIST) and line.isalpha():
            return line

    return os.path.basename(file_path).split('.')[0] if file_path else "Unknown" #毫無結果，直接去除副檔名作名字

def extract_years_experience(text):
    """嘗試從文字抓工作年資，格式 X years"""
    matches = re.findall(r'(\d+)\s+(?:years|yrs)\s+(?:of\s+)?experience', text, flags=re.I)
    direct_years = int(matches[0]) if matches else 0

    '''格式 19/20xx-20xx/Present'''
    year_range = re.findall(r'(20\d{2}|19\d{2})\s*[-–]\s*(20\d{2}|Present|Current|Now)', text, flags=re.I)
    total_years = 0
    for start, end in year_range:
        start_year = int(start)
        end_year = datetime.now().year if any(x in end.lower() for x in ['present', 'current', 'now']) else int(end)
        diff = end_year - start_year
        if 0 <= diff < 55:
            total_years += diff

    return max(direct_years, total_years)

def extract_education_level(text):
    """從文字抓教育程度"""
    text_lower = text.lower()
    if re.search(r'\b(ph\.?d\.?|doctorate|doctor)\b', text_lower):
        return 'phd'# 多樣式的學位名稱判定
    
    if re.search(r'\b(master|masters|m\.?sc\.?|m\.?b\.?a\.?)\b', text_lower):
        return 'master'
    if re.search(r'\b(ms|ma|m\.s\.|m\.a\.)\b', text_lower):
        if re.search(r'\b(university|college|degree|graduated)\b', text_lower):
            return 'master'# 多層判定:確保已有學位才確認在攻讀master

    if re.search(r'\b(bachelor|bachelors|b\.?sc\.?|b\.?b\.?a\.?)\b', text_lower):
        return 'bachelor'
    if re.search(r'\b(bs|ba|b\.s\.|b\.a\.)\b', text_lower):
        if re.search(r'\b(university|college|degree|graduated)\b', text_lower):
            return 'bachelor'
            
    return 'bachelor'

def clean_text(text):
    """文字清理 + NLTK 處理"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^A-Za-z0-9\s]', '', text)
    tokens = word_tokenize(text.lower())
    cleaned = [lemmatizer.lemmatize(t) for t in tokens if t.isalpha() and t not in STOP_WORDS]
    return ' '.join(cleaned)

# 主要功能:建立候選人資料
def create_candidate_profile(row_data, is_csv=True):
    """
    將 CSV row 或單檔案字典轉為統一候選人資料 dict
    """
    raw_text = str(row_data.get('Resume_Text') or row_data.get('Resume') or "")
    config = load_config()
    #建立名字，優先取用csv欄位。否則智慧抓取
    base_name = row_data.get('Name') if is_csv else row_data.get('Name', 'Unknown')
    final_name = base_name if is_csv and base_name else extract_name_smart(raw_text, base_name)
    
    years = row_data.get('Years_Experience')
    if is_csv:
        if pd.isna(years) or years is None or str(years).strip() == '' or float(years) == 0:
            final_years = extract_years_experience(raw_text)
        else:
            final_years = int(float(years))
    else:
        final_years = extract_years_experience(raw_text)

    skills = config['sub_items']['Skills']
    
    profile = {
        'Name': final_name,
        'Resume_Text': clean_text(raw_text),
        'Raw_Text': raw_text,
        'Skills_List': [s for s in skills if s in raw_text.lower()],
        'Years_Experience': final_years,
        'Education_Level': row_data.get('Education_Level') if is_csv and pd.notna(row_data.get('Education_Level')) else extract_education_level(raw_text),
        'Job_Role': row_data.get('Job_Role', ''),
        'University': row_data.get('University', '')
    }
    return profile