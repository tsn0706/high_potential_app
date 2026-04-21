$(document).ready(function () {
    // 1.動態新增一列小項目
    $('.btn-add-sub').on('click', function() {
        const targetCat = $(this).attr('data-target');
        const container = $(`#${targetCat}-container`);
        
        const newRow = `
            <div class="sub-item-row">
                <input type="text" class="form-control modern-input item-key" placeholder="輸入名稱 (英文小寫)">
                <input type="number" step="1" class="form-control modern-input item-val" value="1" style="width: 100px;" placeholder="分數">
                <button class="btn btn-remove"><i class="fas fa-times"></i></button>
            </div>
        `;
        container.append(newRow);
    });

    // 2.刪除小項目
    $(document).on('click', '.btn-remove', function() {
        $(this).closest('.sub-item-row').remove();
    });

    // 3.打包資料並傳送給後端儲存
    $('#saveSettingsBtn').on('click', function() {
        // 改變按鈕狀態
        const btn = $(this);
        const originalText = btn.html();
        btn.html('<i class="fas fa-spinner fa-spin"></i> 儲存中...').prop('disabled', true);

        // 準備要送出的JSON資料結構
        let payload = {
            main_weights: {},
            sub_items: {
                Skills: {},
                Keywords: {},
                JobRole: {},
                // 暫時保留預設值，如果未來UI開放編輯可以再改成動態抓取
                Education: { "phd": 3, "master": 2, "bachelor": 1 }
            },
            threshold: parseFloat($('#thresholdInput').val()) || 15
        };

        // 收集大項權重
        $('.w-main-weight').each(function() {
            const key = $(this).attr('data-key');
            const val = parseFloat($(this).val()) || 1.0;
            payload.main_weights[key] = val;
        });

        // 收集細項分數(遍歷所有的容器)
        $('.sub-items-container').each(function() {
            const category = $(this).attr('data-category'); // e.g., 'Skills'
            
            $(this).find('.sub-item-row').each(function() {
                const itemKey = $(this).find('.item-key').val().trim().toLowerCase();
                const itemVal = parseFloat($(this).find('.item-val').val()) || 0;
                
                // 確保名稱不為空才存入
                if (itemKey) {
                    payload.sub_items[category][itemKey] = itemVal;
                }
            });
        });

        // 使用Fetch API送給Flask後端
        fetch("/api/save_settings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
            } else {
                alert("儲存失敗: " + data.message);
            }
        })
        .catch(err => {
            console.error(err);
            alert("網路錯誤，無法儲存設定！");
        })
        .finally(() => {
            // 恢復按鈕狀態
            btn.html(originalText).prop('disabled', false);
        });
    });
});