$(document).ready(function () {

    // ✅ 初始化 DataTable(只初始化一次)
    let table;
    if (!$.fn.DataTable.isDataTable("#resultTable")) {
        table = $("#resultTable").DataTable({
            pageLength: 10,
            lengthChange: false,
            info: false
        });
    } else {
        table = $("#resultTable").DataTable();
    }
    $("#resultTable_filter").appendTo("#customSearchContainer");
    // 自定義大、小分類
    const categoryData = {
        "programming": ["Python", "SQL", "Machine Learning", "TensorFlow", "Java", "JavaScript", "C", "C#", "C++", "React",
            "Flask", "PyTorch", "Nodejs", "Html", "CSS"],
        "business": ["Project Management", "Agile", "Scrum", "Marketing", "Sales", "Strategy", "Excel"],
        "design": ["UI/UX", "Photoshop", "Illustrator", "Figma", "3D Modeling", "Animation"],
        "New": ["Testing",]
    };
    let selectedKeywords = new Set();

    // 實作大小分類
    $('#majorCategory').on('change', function() {
        const major = $(this).val();
        const container = $('#subCategoryContainer');
        
        // 清空小分類容器與已選關鍵字
        container.empty();
        selectedKeywords.clear(); 
        table.draw(); // 觸發表格重新渲染(取消過濾)

        if (major && categoryData[major]) {
            // 動態生成小方格
            categoryData[major].forEach(keyword => {
                const badge = $(`<div class="keyword-badge">${keyword}</div>`);
                
                // 監聽：點擊小方格時
                badge.on('click', function() {
                    $(this).toggleClass('active');
                    const lowerKeyword = keyword.toLowerCase();
                    
                    if ($(this).hasClass('active')) {
                        selectedKeywords.add(lowerKeyword);
                    } else {
                        selectedKeywords.delete(lowerKeyword);
                    }
                    
                    // 呼叫 DataTable 重新套用我們寫好的過濾條件
                    table.draw();
                });
                
                container.append(badge);
            });
        } else {
            container.append('<span class="text-muted mt-1" id="subCategoryHint">請先選擇左側大分類...</span>');
        }
    });
    $.fn.dataTable.ext.search.push(
        function(settings, data, dataIndex) {
            // 如果沒有選任何關鍵字，全部顯示
            if (selectedKeywords.size === 0) {
                return true; 
            }

            // 取得該行的「隱藏全文」 (位在索引 9，也就是第 10 欄)
            const resumeText = (data[9] || "").toLowerCase();

            // 採用 "AND" 邏輯：履歷必須包含「所有」選中的技能才會顯示
            // 如果你希望是 "OR" (包含任一項就顯示)，請把這裡改寫
            for (let keyword of selectedKeywords) {
                if (!resumeText.includes(keyword)) {
                    return false; // 只要有一個沒中，就不顯示這筆資料
                }
            }
            return true;
        }
    );

    // 點擊「詳情」按鈕
    $(document).on("click", ".detail-btn", function () {
        const name = $(this).attr("data-name"); // 從 data-name 取得姓名

        fetch("/get_resume_detail", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: name })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // 顯示在 Modal
                document.getElementById("modal-text").textContent = data.text;
                new bootstrap.Modal(document.getElementById("detailModal")).show();
            } else {
                alert("查無資料");
            }
        })
        .catch(err => {
            console.error("AJAX 發生錯誤:", err);
            alert("發生錯誤，請檢查後端 API");
        });
    });

});