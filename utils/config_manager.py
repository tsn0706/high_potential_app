import json
import os

# 設定檔儲存路徑
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'settings.json')

# 預設設定 (如果沒有記憶檔，就載入這個)
DEFAULT_CONFIG = {
    "main_weights": {
        "Skills": 2.0,
        "Experience": 1.5,
        "Education": 1.2,
        "JobRole": 2.0,
        "Resume": 1.0
    },#default權重，前端修改後回傳覆蓋
    "sub_items": {
        "Skills": {
            "python": 2,
            "machine learning": 2,
            "sql": 2,
            "tensorflow": 2,
            "java": 1,
            "numpy": 1,
            "scikit-learn": 1,
            "statistics": 1,
            "nlp": 1,
            "data visualization": 1,
            "pandas": 1,
            "pytorch": 2,
            "flask": 1,
            "html": 0.5,
            "css": 0.5,
        },
        "Education": {
            "phd": 3,
            "master": 2,
            "bachelor": 1
        },
        "JobRole": {
            "data scientist": 1,
            "ml engineer": 1,
            "ai researcher": 1
        },
        "Keywords": {
            "project": 1,
            "lead": 1,
            "research": 1,
            "deep learning": 1,
            "deployment": 1,
        }
    },#細項權重
    "threshold": 15
}

def load_config():
    # 讀取設定檔，如果不存在則建立預設值
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(new_config):
    # 儲存設定檔
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(new_config, f, indent=4, ensure_ascii=False)