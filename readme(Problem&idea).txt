# 新增功能memo
# 1.添加排行榜，透明化評分標準。鎖定個人身分資料，讓使用者從排行中看到位置在何處。
# 2.資料庫功能，持久化存儲候選人資料。比對舊有資料，確認文檔真實性。
# 3.資料庫抓取網路上評分校際成績，分析學校背景對職涯的影響。

請建立requirements.txt方便函式庫下載&removeTracking .vevn

Bug&Update
1.修正PDF閱讀時人名附帶副檔名問題->可能出現機器學習問題人名前有Name:...
    ann white極度無法辨認，可用於測試。03/27大量混亂資料，自然語言無法處理。難以辨識
    新功能讀取時間長...
2.修正PDF閱讀年資問題，整合功能完成(parser.py & file_parser & candidate_profile)
    file_parser is Not working now.
    parser only doing extract file.
    candidate_profile is only making resume package.
3.新增分類功能，新分類可於main.js添加
    可自訂分類，並保留自定義分類?
4.新增自定義分數比重
    可由前端功能進行自定義權重類別、分數
    由settings.json讀取，設定在config_manager
5.修正職位閱讀問題
    建立動態職位相關性權重
    修正talent_vector職位閱讀，不僅以固定格式搜索，前500字判定
    q:大量文字的履歷該如何有效益的讀取?
    

incorrect startxref pointer(1)，PDF讀取錯誤。可嘗試新套件?