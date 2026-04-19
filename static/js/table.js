$(document).ready(function () {
    // 初始化 DataTable
    const table = $('#resultTable').DataTable({
        "order": [[4, "desc"]],
        "language": { "search": "搜尋姓名：", "paginate": { "next": "後一頁", "previous": "前一頁" } }
    });

    // 事件委託：處理點擊詳情
    $(document).on('click', '.detail-btn', function () {
        const id = $(this).attr('data-id');
        // 從對應的隱藏 div 抓取內容
        const text = $('#raw-text-' + id).text();
        
        console.log("正在顯示 ID:", id, "內容長度:", text.length);

        // 填入 Modal 並顯示
        $('#modal-content-area').text(text || "（此候選人無詳細履歷內容）");
        
        const myModal = new bootstrap.Modal(document.getElementById('detailModal'));
        myModal.show();
    });
});