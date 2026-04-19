# utils/file_parser.py

import pandas as pd
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from .candidate_profile import create_candidate_profile
from .talent_vector import all_skills

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    """
    文字清理 + NLTK 處理
    """
    # 移除多餘空白和特殊字元
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^A-Za-z0-9\s]', '', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # 小寫化 & 去停用詞 & 詞形還原
    tokens = [lemmatizer.lemmatize(t.lower()) for t in tokens if t.lower() not in stop_words]
    
    # 回傳乾淨文字
    return ' '.join(tokens)

def extract_skills(text):
    """
    從文字中比對 all_skills，返回技能列表
    """
    text_lower = text.lower()
    skills_found = [s for s in all_skills if s in text_lower]
    return skills_found

def parse_uploaded_file(file):
    """
    將上傳檔案解析成候選人資料列表
    """
    filename = file.filename.lower()
    ext = filename.split('.')[-1]
    
    # CSV 檔案
    if ext == 'csv':
        df = pd.read_csv(file, on_bad_lines='skip', encoding='utf-8-sig')
        profiles = df.apply(create_candidate_profile, axis=1).tolist()
        for p in profiles:
            if not p.get('Skills_List'):
                p['Skills_List'] = extract_skills(p.get('Resume_Text', ''))
            # 清理 Resume_Text
            p['Resume_Text'] = clean_text(p.get('Resume_Text', ''))
        return profiles
    
    # 單一文件
    text = ''
    if ext == 'txt':
        text = file.read().decode('utf-8')
    elif ext == 'docx':
        from docx import Document
        doc = Document(file)
        text = '\n'.join([p.text for p in doc.paragraphs])
    elif ext == 'pdf':
        from PyPDF2 import PdfReader
        reader = PdfReader(file)
        text = '\n'.join([p.extract_text() for p in reader.pages if p.extract_text()])
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    # 模擬 CSV Row 結構
    mock_row = {
        'Name': '',
        'Resume_Text': text,
        'University': '',
        'Skills': '',
        'Years_Experience': 0,
        'Education_Level': 'Bachelor',
        'Job_Role': ''
    }
    
    profile = create_candidate_profile(mock_row)
    
    # 強化技能抓取
    profile['Skills_List'] = extract_skills(text)
    
    # 清理 Resume_Text
    profile['Resume_Text'] = clean_text(text)
    
    return [profile]