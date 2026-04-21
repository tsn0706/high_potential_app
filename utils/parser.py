import os
import pandas as pd
import docx
from PyPDF2 import PdfReader
from .candidate_profile import create_candidate_profile
from .talent_vector import generate_talent_vector

# 提取文件內容(除excel)
def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    if ext == '.docx':
        doc = docx.Document(file_path)
        text = '\n'.join([p.text for p in doc.paragraphs])
    elif ext == '.pdf':
        reader = PdfReader(file_path)
        text = '\n'.join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif ext == '.txt':
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    return text

#解析上傳文件，主要功能函式
def parse_uploaded_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    results = []

    if ext == '.csv':
        df = pd.read_csv(file_path, on_bad_lines='skip', encoding='utf-8-sig')
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            profile = create_candidate_profile(row_dict, is_csv=True)
            results.append(generate_talent_vector(profile))
    else:
        raw_text = extract_text_from_file(file_path)
        base_name = os.path.basename(file_path).split('.')[0]

        mock_row = {
            'Name': base_name,
            'Resume_Text': raw_text
        }
        profile = create_candidate_profile(mock_row, is_csv=False)
        results.append(generate_talent_vector(profile))
        
    return results