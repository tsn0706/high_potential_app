import json
import re
from collections import defaultdict
from typing import Any, Dict, List, Tuple

SKILL_TAXONOMY: Dict[str, Dict[str, List[str]]] = {
    "Programming": {
        "python": ["python", "py"],
        "java": ["java"],
        "javascript": ["javascript", "js", "node.js", "nodejs"],
        "c++": ["c++", "cpp"],
        "c#": ["c#", "csharp", ".net"],
        "html": ["html"],
        "css": ["css"],
        "react": ["react"],
        "flask": ["flask"],
        "fastapi": ["fastapi"],
    },
    "Data": {
        "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite", "mssql"],
        "numpy": ["numpy"],
        "pandas": ["pandas"],
        "excel": ["excel"],
        "power bi": ["power bi", "powerbi"],
        "tableau": ["tableau"],
        "statistics": ["statistics", "statistical", "statistical analysis"],
        "data visualization": ["data visualization", "visualization", "matplotlib", "seaborn"],
    },
    "Machine Learning": {
        "machine learning": ["machine learning", "ml"],
        "deep learning": ["deep learning", "dl"],
        "tensorflow": ["tensorflow", "tf"],
        "pytorch": ["pytorch", "torch"],
        "scikit-learn": ["scikit-learn", "sklearn"],
        "xgboost": ["xgboost"],
        "nlp": ["nlp", "natural language processing"],
        "computer vision": ["computer vision", "cv", "image processing"],
    },
    "Data Engineering": {
        "etl": ["etl", "data pipeline", "pipeline"],
        "spark": ["spark", "pyspark"],
        "hadoop": ["hadoop"],
        "airflow": ["airflow"],
        "data warehouse": ["data warehouse", "warehouse"],
    },
    "MLOps / Deployment": {
        "docker": ["docker"],
        "kubernetes": ["kubernetes", "k8s"],
        "aws": ["aws", "amazon web services"],
        "gcp": ["gcp", "google cloud", "google cloud platform"],
        "azure": ["azure"],
        "mlops": ["mlops", "model deployment", "model serving"],
    },
    "Business": {
        "project management": ["project management", "project manager", "pmp"],
        "agile": ["agile"],
        "scrum": ["scrum", "scrum master"],
        "business analysis": ["business analyst", "business analysis", "bsa", "ba "],
    },
}

ROLE_TEMPLATES: Dict[str, Dict[str, List[str]]] = {
    "Data Scientist": {
        "required": ["python", "sql", "machine learning"],
        "preferred": ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "tableau", "statistics"],
    },
    "Machine Learning Engineer": {
        "required": ["python", "machine learning", "tensorflow"],
        "preferred": ["pytorch", "docker", "kubernetes", "aws", "gcp", "mlops", "fastapi"],
    },
    "Data Analyst": {
        "required": ["sql", "excel"],
        "preferred": ["python", "pandas", "tableau", "power bi", "statistics", "data visualization"],
    },
    "Data Engineer": {
        "required": ["sql", "etl"],
        "preferred": ["python", "spark", "airflow", "data warehouse", "aws", "gcp"],
    },
    "AI Engineer": {
        "required": ["python", "machine learning", "deep learning"],
        "preferred": ["tensorflow", "pytorch", "docker", "aws", "gcp", "nlp", "computer vision"],
    },
    "Business Analyst": {
        "required": ["business analysis"],
        "preferred": ["sql", "excel", "project management", "agile", "scrum"],
    },
    "Project Manager": {
        "required": ["project management"],
        "preferred": ["agile", "scrum", "business analysis", "excel"],
    },
}


def normalize_text(text: Any) -> str:
    if text is None:
        return ""
    text = str(text).lower().replace("\n", " ")
    text = re.sub(r"[^a-z0-9+#./ ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return f" {text.strip()} "


def infer_experience_years(text: str, fallback: float = 0.0) -> float:
    patterns = [
        r"(\d+(?:\.\d+)?)\s+years? of experience",
        r"experience\s+of\s+(\d+(?:\.\d+)?)\s+years?",
        r"(\d+(?:\.\d+)?)\s+years? experience",
        r"(\d+(?:\.\d+)?)\+?\s+years?",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except Exception:
                pass
    try:
        return float(fallback or 0.0)
    except Exception:
        return 0.0


def detect_skills(text: str) -> Dict[str, List[str]]:
    found = defaultdict(list)
    for category, skills in SKILL_TAXONOMY.items():
        for canonical, aliases in skills.items():
            for alias in aliases:
                alias_norm = normalize_text(alias).strip()
                if alias_norm and f" {alias_norm} " in text:
                    found[category].append(canonical)
                    break
    return {k: sorted(set(v)) for k, v in found.items()}


def flatten_skills(skill_dict: Dict[str, List[str]]) -> List[str]:
    items: List[str] = []
    for values in skill_dict.values():
        items.extend(values)
    return sorted(set(items))


def estimate_skill_level(skill: str, text: str, experience_years: float) -> str:
    score = 0
    if f" {skill} " in text:
        score += 1
    if " project " in text and f" {skill} " in text:
        score += 1
    if experience_years >= 7:
        score += 2
    elif experience_years >= 3:
        score += 1

    if score >= 4:
        return "高"
    if score >= 2:
        return "中"
    return "低"


def role_match_score(candidate_skills: List[str], template: Dict[str, List[str]]) -> Tuple[float, List[str], List[str]]:
    candidate_set = set(candidate_skills)
    required = template.get("required", [])
    preferred = template.get("preferred", [])
    score = 0.0
    missing_required: List[str] = []
    missing_preferred: List[str] = []

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

    return score, missing_required, missing_preferred


def build_gap_analysis(predicted_role: str, missing_required: List[str], missing_preferred: List[str]) -> str:
    if not missing_required and not missing_preferred:
        return f"與 {predicted_role} 的技能結構高度匹配。"

    parts = []
    if missing_required:
        parts.append("缺少核心技能：" + "、".join(missing_required))
    if missing_preferred:
        parts.append("建議補強：" + "、".join(missing_preferred[:5]))
    return "；".join(parts)


def summarize_strengths(skill_by_category: Dict[str, List[str]], experience_years: float) -> List[str]:
    strengths: List[str] = []
    if skill_by_category.get("Machine Learning"):
        strengths.append("具備機器學習 / AI 相關能力")
    if skill_by_category.get("Programming"):
        strengths.append("具有程式開發基礎")
    if skill_by_category.get("Data"):
        strengths.append("可處理資料分析與資料庫相關工作")
    if experience_years >= 7:
        strengths.append("年資完整，偏中高階實務型人才")
    elif experience_years >= 3:
        strengths.append("已有一定實務經驗")
    return strengths[:4]


def analyze_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    raw_text = profile.get("Raw_Text") or profile.get("Resume_Text") or ""
    text = normalize_text(raw_text)
    experience_years = infer_experience_years(text, profile.get("Years_Experience", 0))
    skill_by_category = detect_skills(text)
    all_skills = flatten_skills(skill_by_category)
    skill_levels = {skill: estimate_skill_level(skill, text, experience_years) for skill in all_skills}

    role_scores: Dict[str, float] = {}
    role_missing: Dict[str, Dict[str, List[str]]] = {}
    for role_name, template in ROLE_TEMPLATES.items():
        score, missing_required, missing_preferred = role_match_score(all_skills, template)
        role_scores[role_name] = round(score, 2)
        role_missing[role_name] = {
            "required": missing_required,
            "preferred": missing_preferred,
        }

    predicted_role = max(role_scores, key=role_scores.get) if role_scores else "Unknown"
    missing_required = role_missing[predicted_role]["required"] if predicted_role in role_missing else []
    missing_preferred = role_missing[predicted_role]["preferred"] if predicted_role in role_missing else []
    recommended_missing = missing_required + missing_preferred[:5]

    target_all = ROLE_TEMPLATES.get(predicted_role, {}).get("required", []) + ROLE_TEMPLATES.get(predicted_role, {}).get("preferred", [])
    matched_count = sum(1 for s in target_all if s in set(all_skills))
    skill_completeness = round(matched_count / max(len(target_all), 1), 3)

    return {
        "Detected_Skills": all_skills,
        "Skill_By_Category": skill_by_category,
        "Skill_Levels": skill_levels,
        "Predicted_Role": predicted_role,
        "Role_Scores": role_scores,
        "Missing_Required": missing_required,
        "Missing_Preferred": missing_preferred,
        "Missing_Skills_Recommendation": recommended_missing,
        "Gap_Analysis": build_gap_analysis(predicted_role, missing_required, missing_preferred),
        "Skill_Completeness": skill_completeness,
        "Category_Coverage": len([1 for _, v in skill_by_category.items() if v]),
        "Strength_Summary": summarize_strengths(skill_by_category, experience_years),
        "Skill_Summary_Text": " | ".join([f"{k}: {', '.join(v)}" for k, v in skill_by_category.items() if v]),
        "Skill_Levels_JSON": json.dumps(skill_levels, ensure_ascii=False),
        "Role_Scores_JSON": json.dumps(role_scores, ensure_ascii=False),
    }
