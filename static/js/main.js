$(document).ready(function () {
    const rawResults = document.getElementById('results-data')?.textContent || '[]';
    let cachedResults = [];
    try {
        cachedResults = JSON.parse(rawResults);
    } catch (e) {
        cachedResults = [];
    }

    const skillCanvasEl = document.getElementById('skillAnalysisCanvas');
    const skillCanvas = skillCanvasEl ? new bootstrap.Offcanvas(skillCanvasEl) : null;
    const skillSelect = document.getElementById('skillCandidateSelect');
    const skillContent = document.getElementById('skillAnalysisContent');

    const table = $('#resultTable').length ? $('#resultTable').DataTable({
        language: {
            search: '搜尋：',
            lengthMenu: '顯示 _MENU_ 筆',
            info: '顯示第 _START_ 到 _END_ 筆，共 _TOTAL_ 筆',
            paginate: { previous: '上一頁', next: '下一頁' },
            emptyTable: '目前沒有資料'
        },
        order: [[6, 'desc']]
    }) : null;

    const categoryData = {
        programming: ["Python", "Java", "JavaScript", "HTML", "CSS", "SQL"],
        business: ["Project Manager", "Business Analyst", "Agile", "Scrum", "PMP"],
        design: ["Photoshop", "Illustrator", "Figma", "3D Modeling", "Animation"],
        New: ["Testing"]
    };
    let selectedKeywords = new Set();

    $('#majorCategory').on('change', function () {
        const major = $(this).val();
        const container = $('#subCategoryContainer');
        container.empty();
        selectedKeywords.clear();
        if (table) table.draw();

        if (major && categoryData[major]) {
            categoryData[major].forEach(keyword => {
                const badge = $(`<div class="keyword-badge">${keyword}</div>`);
                badge.on('click', function () {
                    $(this).toggleClass('active');
                    const lowerKeyword = keyword.toLowerCase();
                    if ($(this).hasClass('active')) selectedKeywords.add(lowerKeyword);
                    else selectedKeywords.delete(lowerKeyword);
                    if (table) table.draw();
                });
                container.append(badge);
            });
        } else {
            container.append('<span class="text-muted mt-1" id="subCategoryHint">請先選擇左側大分類...</span>');
        }
    });

    $.fn.dataTable.ext.search.push(function (settings, data) {
        if (selectedKeywords.size === 0) return true;
        const resumeText = (data[9] || '').toLowerCase();
        for (let keyword of selectedKeywords) {
            if (!resumeText.includes(keyword)) return false;
        }
        return true;
    });

    function escapeHtml(str) {
        return String(str || '').replace(/[&<>"]/g, function (tag) {
            const charsToReplace = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' };
            return charsToReplace[tag] || tag;
        });
    }

    function renderAnalysis(analysis) {
        if (!analysis) {
            skillContent.innerHTML = '<div class="analysis-placeholder">查無技能分析資料</div>';
            return;
        }

        const categoryHtml = Object.entries(analysis.skill_by_category || {}).length
            ? Object.entries(analysis.skill_by_category).map(([category, skills]) => `
                <div class="analysis-group">
                    <div class="analysis-group-title">${escapeHtml(category)}</div>
                    <div class="chip-wrap">${skills.map(skill => `<span class="skill-chip">${escapeHtml(skill)}</span>`).join('')}</div>
                </div>`).join('')
            : '<div class="muted-line">尚未偵測到明確技能分類</div>';

        const skillLevelHtml = Object.entries(analysis.skill_levels || {}).length
            ? Object.entries(analysis.skill_levels).map(([skill, level]) => `<div class="row-line"><span>${escapeHtml(skill)}</span><strong>${escapeHtml(level)}</strong></div>`).join('')
            : '<div class="muted-line">尚未估計技能熟練度</div>';

        const recommendHtml = (analysis.missing_skills_recommendation || []).length
            ? `<div class="chip-wrap">${analysis.missing_skills_recommendation.map(skill => `<span class="recommend-chip">${escapeHtml(skill)}</span>`).join('')}</div>`
            : '<div class="muted-line">目前沒有缺技能建議</div>';

        const roleScoreHtml = Object.keys(analysis.role_scores || {}).length
            ? Object.entries(analysis.role_scores).sort((a, b) => b[1] - a[1]).map(([role, score]) => `<div class="row-line"><span>${escapeHtml(role)}</span><strong>${escapeHtml(score)}</strong></div>`).join('')
            : '<div class="muted-line">目前沒有職位匹配資料</div>';

        skillContent.innerHTML = `
            <div class="candidate-head glass-panel mb-3">
                <div>
                    <div class="candidate-name">${escapeHtml(analysis.candidate_name)}</div>
                    <div class="candidate-sub">${escapeHtml(analysis.predicted_role)} ｜ 總分 ${escapeHtml(analysis.total_score)}</div>
                </div>
                <span class="potential-pill">${escapeHtml(analysis.potential_label)}</span>
            </div>

            <div class="stats-grid mb-3">
                <div class="stat-card glass-panel"><div class="stat-label">推薦職位</div><div class="stat-value">${escapeHtml(analysis.predicted_role)}</div></div>
                <div class="stat-card glass-panel"><div class="stat-label">技能完整度</div><div class="stat-value">${escapeHtml(analysis.skill_completeness)}%</div></div>
                <div class="stat-card glass-panel"><div class="stat-label">技能類別覆蓋</div><div class="stat-value">${escapeHtml(analysis.category_coverage)}</div></div>
            </div>

            <div class="glass-panel panel-block">
                <div class="panel-title">綜合摘要</div>
                <div class="summary-name">${escapeHtml(analysis.candidate_name)}</div>
                <div class="panel-text">${escapeHtml(analysis.summary)}</div>
                <div class="panel-text mt-2">${escapeHtml(analysis.gap_analysis)}</div>
            </div>

            <div class="glass-panel panel-block">
                <div class="panel-title">技能分類</div>
                ${categoryHtml}
            </div>

            <div class="glass-panel panel-block">
                <div class="panel-title">技能熟練度</div>
                ${skillLevelHtml}
            </div>

            <div class="glass-panel panel-block">
                <div class="panel-title">建議補強技能</div>
                ${recommendHtml}
            </div>

            <div class="glass-panel panel-block">
                <div class="panel-title">職位匹配分數</div>
                ${roleScoreHtml}
            </div>
        `;
    }

    function getLocalAnalysis(name) {
        const row = cachedResults.find(item => item.Name === name);
        return row ? row.Skill_Analysis : null;
    }

    function loadSkillAnalysis(name) {
        if (!name) {
            renderAnalysis(null);
            return;
        }

        const local = getLocalAnalysis(name);
        if (local) {
            renderAnalysis(local);
            if (skillSelect) skillSelect.value = name;
            return;
        }

        fetch('/api/skill_analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                renderAnalysis(data.analysis);
                if (skillSelect) skillSelect.value = name;
            } else {
                skillContent.innerHTML = `<div class="analysis-placeholder">${escapeHtml(data.message || '查無技能分析資料')}</div>`;
            }
        })
        .catch(() => {
            skillContent.innerHTML = '<div class="analysis-placeholder">技能分析載入失敗</div>';
        });
    }

    $('#openSkillPanel').on('click', function (e) {
        e.preventDefault();
        if (skillCanvas) skillCanvas.show();
        const defaultName = skillSelect?.value || cachedResults[0]?.Name;
        if (defaultName) loadSkillAnalysis(defaultName);
    });

    if (skillSelect) {
        skillSelect.addEventListener('change', function () {
            loadSkillAnalysis(this.value);
        });
    }

    $(document).on('click', '.skill-btn', function (e) {
        e.stopPropagation();
        const name = $(this).data('name');
        if (skillCanvas) skillCanvas.show();
        loadSkillAnalysis(name);
    });

    $(document).on('click', '.candidate-row', function (e) {
        if ($(e.target).closest('button').length) return;
        const name = $(this).data('name');
        if (skillCanvas) skillCanvas.show();
        loadSkillAnalysis(name);
    });

    $(document).on('click', '.detail-btn', function () {
        const name = $(this).attr('data-name');
        fetch('/get_resume_detail', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                document.getElementById('modal-text').textContent = data.text;
                new bootstrap.Modal(document.getElementById('detailModal')).show();
            } else {
                alert('查無資料');
            }
        })
        .catch(err => {
            console.error('AJAX 發生錯誤:', err);
            alert('發生錯誤，請檢查後端 API');
        });
    });

    $('#clearSavedResults').on('click', function () {
        if (!confirm('要清除目前保存的分析結果嗎？')) return;
        fetch('/api/clear_results', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                alert(data.message || '已清除');
                window.location.href = '/';
            })
            .catch(() => alert('清除失敗'));
    });

    if (cachedResults.length && skillSelect && !skillSelect.value) {
        skillSelect.value = cachedResults[0].Name;
    }
    const params = new URLSearchParams(window.location.search);
    if (params.get('open_skill') === '1') {
        if (skillCanvas) skillCanvas.show();
        const defaultName = skillSelect?.value || cachedResults[0]?.Name;
        if (defaultName) loadSkillAnalysis(defaultName);
    }
});
