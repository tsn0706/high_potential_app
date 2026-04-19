import io
import pandas as pd
from docx import Document
import pdfplumber

def parse_uploaded_file(file):
    """
    接收 Flask 上傳檔案，回傳 list of dict，包含履歷文字。
    支援 pdf / docx / txt / csv / xlsx
    """
    filename = file.filename.lower()
    records = []

    # PDF
    if filename.endswith('.pdf'):
        with pdfplumber.open(file) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            records.append({'Resume_Text': text, 'Name': extract_name(text)})

    # DOCX
    elif filename.endswith('.docx'):
        doc = Document(file)
        text = "\n".join([p.text for p in doc.paragraphs])
        records.append({'Resume_Text': text, 'Name': extract_name(text)})

    # TXT
    elif filename.endswith('.txt'):
        text = file.read().decode('utf-8', errors='ignore')
        records.append({'Resume_Text': text, 'Name': extract_name(text)})

    # CSV/XLSX
    elif filename.endswith('.csv') or filename.endswith('.xlsx'):
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        for _, row in df.iterrows():
            text = str(row.get('Resume_Text', ''))
            records.append({'Resume_Text': text, 'Name': row.get('Name', extract_name(text))})

    else:
        raise ValueError("不支援的檔案格式")

    return records

def extract_name(text):
    """
    從文字中抓名字（簡單示範，實務可用 NLP）
    """
    lines = text.splitlines()
    for line in lines:
        if len(line.strip()) > 0:
            return line.strip().split()[0]  # 取第一個字串
    return "未知"