# utils/file_parser.py
import pandas as pd

def parse_uploaded_file(uploaded_file):
    """
    接收 Flask 的 uploaded_file，解析成 list of dict
    目前假設 CSV 檔案格式，並且有 'Resume_Text' 欄位
    """
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        # 如果是 Excel，也可以試：
        try:
            df = pd.read_excel(uploaded_file)
        except Exception as e2:
            raise ValueError("檔案格式不支援或讀取失敗") from e2

    # 將資料轉成字典列表
    records = df.to_dict(orient='records')
    return records