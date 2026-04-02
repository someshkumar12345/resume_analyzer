import re

# --- PRECISION SKILL MAP ---
SKILL_MAP = {
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "javascript": ["javascript", "js", "java script"],
    "nodejs": ["nodejs", "node js", "node.js"],
    "react": ["react", "reactjs", "react.js"],
    "python": ["python", "python3"],
    "java": ["java"],
    "sql": ["sql", "mysql", "postgresql"],
    "aws": ["aws", "amazon web services"],
    "docker": ["docker", "containerization"],
    "kubernetes": ["kubernetes", "k8s"],
    "c": ["c"],
    "cpp": ["c++", "cpp"],
    "csharp": ["c#", "csharp"],
    "git": ["git", "github", "bitbucket"],
    "agile": ["agile", "scrum", "kanban"]
}

def detect_experience_level(text):
    """Detects professional experience level based on keywords."""
    text = text.lower()
    if any(k in text for k in ["senior", "lead", "5 years", "10 years", "architect"]):
        return "Senior / Expert", 100
    if any(k in text for k in ["junior", "fresher", "intern", "trainee", "entry level"]):
        return "Fresher / Junior", 40
    return "Intermediate", 75

def detect_project_intensity(text):
    """Detects the relevance of projects mentioned in the resume."""
    text = text.lower()
    project_keywords = ["project", "developed", "built", "implemented", "launched", "repo"]
    count = sum(1 for k in project_keywords if k in text)
    score = min(count * 20, 100)
    return "High" if score >= 80 else "Moderate" if score >= 40 else "Minimal", score

def count_keyword_strength(text, matched_skills):
    """Counts how many times each skill appears for strength analysis."""
    text = text.lower()
    strength = {}
    for skill in matched_skills:
        count = len(re.findall(r'\b' + re.escape(skill.lower()) + r'\b', text))
        strength[skill] = max(count, 1)
    return strength

def generate_ai_summary(name, score, experience, match_count):
    """Generates a 2-3 line SaaS-style summary."""
    if score >= 80:
        return f"This candidate is a top-tier {experience} professional. With a high match percentage and strong skill alignment, they are the ideal recommendation for this role."
    if score >= 50:
        return f"This candidate shows strong potential as an {experience} professional. They possess {match_count} core skills and align well with the team's needs."
    return f"This candidate is an {experience} level developer. While they lack some core requirements, their foundational knowledge could be valuable for junior roles."

def calculate_advanced_metrics(resume_text, job_description):
    """
    Implements the Winning Scoring Formula:
    If matched_skills == 0:
        Score = Cap at 10%
    Else:
        Score = (Skill Match * 0.7) + (Projects * 0.2) + (Experience * 0.1)
    """
    # 1. Skill Match (Primary 70%)
    job_skills_raw = get_raw_skills(job_description)
    res_skills_raw = get_raw_skills(resume_text)
    
    if not job_skills_raw:
        return 0, [], [], "Unknown", 0, "Minimal", 0, {}

    matched_keys = job_skills_raw.intersection(res_skills_raw)
    missing_keys = job_skills_raw.difference(res_skills_raw)
    
    skill_match_score = (len(matched_keys) / len(job_skills_raw)) * 100
    
    # 2. Experience Level (10%)
    exp_label, exp_score = detect_experience_level(resume_text)
    
    # 3. Project Relevance (20%)
    proj_label, proj_score = detect_project_intensity(resume_text)
    
    # 4. Final Weighted Score (With Match Guard #1 Upgrade)
    if len(matched_keys) == 0:
        # Cap score at 10% if no core skills matched (prevent false positives)
        final_score = min((proj_score * 0.2) + (exp_score * 0.1), 10.0)
    else:
        # Standard weighted score
        final_score = (skill_match_score * 0.7) + (proj_score * 0.2) + (exp_score * 0.1)
    
    # Formatting For UI
    UI_MAP = {"html": "HTML", "css": "CSS", "javascript": "JavaScript", "nodejs": "Node.js", "react": "React", "sql": "SQL", "aws": "AWS", "docker": "Docker", "csharp": "C#", "cpp": "C++"}
    matched_ui = sorted([UI_MAP.get(k, k.title()) for k in matched_keys])
    missing_ui = sorted([UI_MAP.get(k, k.title()) for k in missing_keys])
    
    # Keyword Strength
    strength = count_keyword_strength(resume_text, matched_ui)
    
    return round(final_score, 2), matched_ui, missing_ui, exp_label, exp_score, proj_label, proj_score, strength

def get_raw_skills(text):
    """Helper to get set of canonical skill keys using Regex boundaries."""
    text = text.lower()
    found = set()
    for canonical, variations in SKILL_MAP.items():
        if any(re.search(r'\b' + re.escape(v) + r'\b', text) for v in variations):
            found.add(canonical)
    return found
