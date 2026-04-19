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


    const skillCanvasEl = document.getElementById("skillAnalysisPanel");
    const skillPanel = skillCanvasEl ? new bootstrap.Offcanvas(skillCanvasEl) : null;

    function renderChipList(containerId, items, emptyText = "無資料") {
        const container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = "";
        if (!items || items.length === 0) {
            container.innerHTML = `<span class="text-muted">${emptyText}</span>`;
            return;
        }
        items.forEach(item => {
            const chip = document.createElement("span");
            chip.className = "analysis-chip";
            chip.textContent = item;
            container.appendChild(chip);
        });
    }

    function renderSkillCategories(skillByCategory) {
        const container = document.getElementById("analysisSkillCategories");
        if (!container) return;
        container.innerHTML = "";
        const entries = Object.entries(skillByCategory || {});
        if (entries.length === 0) {
            container.innerHTML = '<span class="text-muted">尚未偵測到明確技能分類</span>';
            return;
        }
        entries.forEach(([category, skills]) => {
            const block = document.createElement("div");
            block.className = "category-block";
            block.innerHTML = `
                <div class="category-title">${category}</div>
                <div class="chip-container">${skills.map(skill => `<span class="analysis-chip">${skill}</span>`).join("")}</div>
            `;
            container.appendChild(block);
        });
    }

    function renderRoleScores(roleScores) {
        const container = document.getElementById("analysisRoleScores");
        if (!container) return;
        container.innerHTML = "";
        const entries = Object.entries(roleScores || {}).sort((a, b) => b[1] - a[1]);
        if (entries.length === 0) {
            container.innerHTML = '<span class="text-muted">目前沒有職位匹配資料</span>';
            return;
        }
        entries.forEach(([role, score]) => {
            const row = document.createElement("div");
            row.className = "role-score-row";
            row.innerHTML = `
                <span>${role}</span>
                <span class="fw-bold">${score}</span>
            `;
            container.appendChild(row);
        });
    }

    function renderSkillAnalysis(analysis) {
        document.getElementById("analysisCandidateName").textContent = analysis.name || "未知候選人";
        document.getElementById("analysisPredictedRole").textContent = analysis.predicted_role || "未判定";
        document.getElementById("analysisSkillCompleteness").textContent = `${Math.round((analysis.skill_completeness || 0) * 100)}%`;
        document.getElementById("analysisCategoryCoverage").textContent = analysis.category_coverage || 0;
        document.getElementById("analysisStrengthSummary").textContent = (analysis.strength_summary || []).join("、") || "尚未產生摘要";
        document.getElementById("analysisGapAnalysis").textContent = analysis.gap_analysis || "尚未產生缺口分析";

        const hpEl = document.getElementById("analysisHighPotential");
        hpEl.textContent = analysis.high_potential ? "高潛力" : "一般潛力";
        hpEl.className = analysis.high_potential ? "analysis-pill high" : "analysis-pill low";

        const levelItems = Object.entries(analysis.skill_levels || {}).map(([skill, level]) => `${skill}｜${level}`);
        renderSkillCategories(analysis.skill_by_category || {});
        renderChipList("analysisSkillLevels", levelItems, "尚未估計技能熟練度");
        renderChipList("analysisMissingSkills", analysis.missing_skills_recommendation || [], "目前沒有缺技能建議");
        renderRoleScores(analysis.role_scores || {});
    }

    function loadSkillAnalysis(name) {
        fetch("/get_skill_analysis", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name })
        })
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                alert(data.message || "技能分析讀取失敗");
                return;
            }
            renderSkillAnalysis(data.analysis);
        })
        .catch(err => {
            console.error("技能分析讀取失敗:", err);
            alert("技能分析讀取失敗");
        });
    }

    function openSkillPanel(defaultName = "") {
        fetch("/get_skill_candidates")
            .then(res => res.json())
            .then(data => {
                const emptyEl = document.getElementById("skillPanelEmpty");
                const contentEl = document.getElementById("skillPanelContent");
                const selectEl = document.getElementById("skillCandidateSelect");

                if (!data.success || !data.candidates || data.candidates.length === 0) {
                    emptyEl.style.display = "block";
                    contentEl.style.display = "none";
                    skillPanel && skillPanel.show();
                    return;
                }

                emptyEl.style.display = "none";
                contentEl.style.display = "block";
                selectEl.innerHTML = "";

                data.candidates.forEach(candidate => {
                    const option = document.createElement("option");
                    option.value = candidate.name;
                    option.textContent = `${candidate.name}｜${candidate.predicted_role}｜總分 ${candidate.total_score}`;
                    selectEl.appendChild(option);
                });

                const pickedName = defaultName || data.candidates[0].name;
                selectEl.value = pickedName;
                loadSkillAnalysis(pickedName);
                skillPanel && skillPanel.show();
            })
            .catch(err => {
                console.error("候選人清單讀取失敗:", err);
                alert("目前無法開啟技能分析側欄");
            });
    }

    $(document).on("click", "#openSkillPanel", function (e) {
        e.preventDefault();
        openSkillPanel();
    });

    $(document).on("change", "#skillCandidateSelect", function () {
        loadSkillAnalysis($(this).val());
    });

    $(document).on("click", ".detail-btn", function () {
        const name = $(this).attr("data-name");
        $(document).one("hidden.bs.modal", "#detailModal", function() {
            openSkillPanel(name);
        });
    });


});