$(document).ready(function () {
    // 1. 初始化 DataTable
    if (!$.fn.DataTable.isDataTable("#resultTable")) {
        $("#resultTable").DataTable({ 
            pageLength: 10, 
            lengthChange: false, 
            info: false 
        });
    }

    // 2. 詳情按鈕點擊事件
    $(document).off("click", ".detail-btn").on("click", ".detail-btn", function (e) {
        e.preventDefault();
        const name = $(this).attr("data-name");
        const modalElement = document.getElementById("detailModal");
        
        // 取得實例並顯示
        const detailModal = bootstrap.Modal.getOrCreateInstance(modalElement);
        $("#modal-text").text("載入中...");
        detailModal.show();

        fetch("/get_resume_detail", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: name })
        })
        .then(res => res.json())
        .then(data => {
            $("#modal-text").text(data.success ? data.text : "讀取失敗: " + data.text);
        })
        .catch(() => $("#modal-text").text("連線伺服器失敗"));
    });

    // 3. 【關鍵修正】當 Modal 隱藏時，強制清理所有遮罩與 Body 鎖定狀態
    $("#detailModal").on("hidden.bs.modal", function () {
        // 移除所有殘留的黑影遮罩
        $(".modal-backdrop").remove();
        // 恢復 Body 的滾動能力，防止頁面卡死無法移動
        $("body").removeClass("modal-open").css("overflow", "auto").css("padding-right", "0");
    });
});