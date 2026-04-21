import re
from collections import defaultdict
from typing import Dict, List, Any

SKILL_TAXONOMY: Dict[str, Dict[str, List[str]]] = {
    "Programming": {
        "python": ["python", "py"],
        "java": ["java", "spring", "spring boot"],
        "javascript": ["javascript", "js", "node.js", "nodejs", "react", "angular"],
        "c++": ["c++", "cpp"],
        "html": ["html"],
        "css": ["css"],
        "flask": ["flask"],
    },
    "Data": {
        "sql": ["sql", "mysql", "postgresql", "oracle", "sqlite"],
        "numpy": ["numpy"],
        "pandas": ["pandas"],
        "statistics": ["statistics", "statistical"],
        "data visualization": ["data visualization", "visualization", "tableau", "power bi"],
        "excel": ["excel"],
    },
    "Machine Learning": {
        "machine learning": ["machine learning", "ml"],
        "deep learning": ["deep learning"],
        "tensorflow": ["tensorflow", "tf"],
        "pytorch": ["pytorch", "torch"],
        "scikit-learn": ["scikit-learn", "sklearn"],
        "nlp": ["nlp", "natural language processing"],
    },
    "Data Engineering": {
        "etl": ["etl", "data pipeline", "pipeline"],
        "spark": ["spark", "pyspark"],
        "hadoop": ["hadoop"],
    },
    "MLOps / Deployment": {
        "docker": ["docker"],
        "kubernetes": ["kubernetes", "k8s"],
        "aws": ["aws", "amazon web services"],
        "gcp": ["gcp", "google cloud"],
        "deployment": ["deployment", "deploy", "serving"],
    },
    "Business / PM": {
        "business analysis": ["business analyst", "business analysis", "bsa", "ba"],
        "project management": ["project manager", "project management", "pmp", "scrum master"],
        "agile": ["agile", "scrum", "kanban"],
    }
}

ROLE_TEMPLATES = {
    "Data Scientist": {
        "required": ["python", "sql", "machine learning"],
        "preferred": ["numpy", "pandas", "scikit-learn", "tensorflow", "statistics", "data visualization"],
    },
    "Machine Learning Engineer": {
        "required": ["python", "machine learning", "tensorflow"],
        "preferred": ["pytorch", "docker", "deployment", "aws", "gcp", "scikit-learn"],
    },
    "Software Engineer": {
        "required": ["java"],
        "preferred": ["javascript", "html", "css", "sql", "docker"],
    },
    "Data Analyst": {
        "required": ["sql"],
        "preferred": ["excel", "pandas", "data visualization", "statistics", "python"],
    },
    "Business Analyst": {
        "required": ["business analysis"],
        "preferred": ["sql", "excel", "agile", "project management"],
    },
    "Project Manager": {
        "required": ["project management"],
        "preferred": ["agile", "business analysis", "sql"],
    },
}


def _normalize_text(text: str) -> str:
    text = (text or "").lower().replace("\n", " ")
    text = re.sub(r"[^a-z0-9+#./ ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return f" {text} "


def _infer_role_from_text(text: str) -> str:
    raw = text.lower()
    hints = [
        ("Data Scientist", ["data scientist"]),
        ("Machine Learning Engineer", ["ml engineer", "machine learning engineer"]),
        ("Software Engineer", ["software engineer", "java developer", "full stack", "developer"]),
        ("Data Analyst", ["data analyst", "analyst"]),
        ("Business Analyst", ["business analyst", "bsa"]),
        ("Project Manager", ["project manager", "scrum master", "program manager", "pmp"]),
    ]
    for role, aliases in hints:
        if any(alias in raw for alias in aliases):
            return role
    return "未判定"


def _infer_experience_years(text: str, fallback: int = 0) -> int:
    patterns = [
        r"(\d+)\s*(?:\+)?\s*years?\s+(?:of\s+)?experience",
        r"experience\s+of\s+(\d+)\s+years?",
        r"(\d+)\s*yrs?",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            try:
                return int(match.group(1))
            except Exception:
                pass
    return int(fallback or 0)


def _extract_detected_skills(raw_text: str, skills_list: List[str] = None) -> Dict[str, List[str]]:
    text = _normalize_text(raw_text)
    found = defaultdict(list)
    input_skills = set((skills_list or []))

    for category, skill_map in SKILL_TAXONOMY.items():
        for canonical, aliases in skill_map.items():
            matched = canonical in input_skills
            if not matched:
                for alias in aliases:
                    alias_norm = _normalize_text(alias).strip()
                    if alias_norm and f" {alias_norm} " in text:
                        matched = True
                        break
            if matched:
                found[category].append(canonical)

    return {k: sorted(set(v)) for k, v in found.items()}


def _flatten(skill_map: Dict[str, List[str]]) -> List[str]:
    all_skills = []
    for skills in skill_map.values():
        all_skills.extend(skills)
    return sorted(set(all_skills))


def _estimate_level(skill: str, raw_text: str, years: int) -> str:
    text = raw_text.lower()
    score = 0
    if skill in text:
        score += 1
    if 'project' in text and skill in text:
        score += 1
    if years >= 7:
        score += 2
    elif years >= 3:
        score += 1
    if score >= 4:
        return '高'
    if score >= 2:
        return '中'
    return '低'


def _role_match(candidate_skills: List[str], role: str) -> Dict[str, Any]:
    template = ROLE_TEMPLATES[role]
    candidate_set = set(candidate_skills)
    required = template['required']
    preferred = template['preferred']
    score = 0.0
    missing_required = []
    missing_preferred = []

    for skill in required:
        if skill in candidate_set:
            score += 3.0
        else:
            missing_required.append(skill)
            score -= 1.5

    for skill in preferred:
        if skill in candidate_set:
            score += 1.0
        else:
            missing_preferred.append(skill)

    return {
        'score': round(score, 2),
        'missing_required': missing_required,
        'missing_preferred': missing_preferred,
    }


def analyze_candidate(result: Dict[str, Any]) -> Dict[str, Any]:
    raw_text = result.get('Raw_Text', '') or ''
    years = _infer_experience_years(raw_text, result.get('Experience_Score', 0))
    skill_by_category = _extract_detected_skills(raw_text, result.get('Skills_List', []))
    all_skills = _flatten(skill_by_category)

    role_scores = {role: _role_match(all_skills, role) for role in ROLE_TEMPLATES}
    predicted_role = max(role_scores, key=lambda role: role_scores[role]['score']) if role_scores else '未判定'

    if not all_skills:
        hinted_role = _infer_role_from_text(raw_text)
        if hinted_role != '未判定':
            predicted_role = hinted_role

    top_role_data = role_scores.get(predicted_role, {'score': 0.0, 'missing_required': [], 'missing_preferred': []})
    template = ROLE_TEMPLATES.get(predicted_role, {'required': [], 'preferred': []})
    template_total = len(template['required']) + len(template['preferred'])
    matched_count = sum(1 for s in template.get('required', []) + template.get('preferred', []) if s in set(all_skills))
    completeness = round((matched_count / template_total) * 100) if template_total else 0

    skill_levels = {skill: _estimate_level(skill, raw_text, years) for skill in all_skills}
    total_score = float(result.get('Total_Score', 0) or 0)
    potential_label = '高潛力' if result.get('High_Potential') else '一般潛力'

    summary_bits = []
    if all_skills:
        summary_bits.append(f"偵測到 {len(all_skills)} 項技能")
    if years:
        summary_bits.append(f"約 {years} 年相關經驗")
    if predicted_role != '未判定':
        summary_bits.append(f"較適合 {predicted_role}")
    summary = '、'.join(summary_bits) if summary_bits else '尚未從履歷辨識出足夠的技能資訊，建議補充更完整的技能、專案與職稱描述。'

    gap_items = top_role_data['missing_required'] + top_role_data['missing_preferred'][:5]
    gap_analysis = (
        f"目前較缺少 {', '.join(gap_items)} 等能力，可往 {predicted_role} 的完整職能補強。"
        if gap_items else
        '技能結構相對完整，與目前推測職位匹配度高。'
    )

    return {
        'candidate_name': result.get('Name', 'Unknown'),
        'total_score': total_score,
        'potential_label': potential_label,
        'predicted_role': predicted_role,
        'skill_completeness': completeness,
        'category_coverage': len(skill_by_category),
        'skill_by_category': skill_by_category,
        'skill_levels': skill_levels,
        'missing_skills_recommendation': gap_items,
        'role_scores': {role: info['score'] for role, info in role_scores.items()},
        'summary': summary,
        'gap_analysis': gap_analysis,
    }
