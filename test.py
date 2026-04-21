from utils.file_parser import parse_docx

# 指定正確檔案路徑
file_path = "/home/user/high_potential_app_V2/data/docx/Aaron_Rodriguez.docx"

# 解析 docx
result = parse_docx(file_path)

# 印出結果
print("原文:", result['raw'])
print("斷詞:", result['tokens'])
print("去停用詞:", result['clean'])
print("詞形還原:", result['lemmatized'])