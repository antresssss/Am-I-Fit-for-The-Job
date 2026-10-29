import re
from pathlib import Path

from pypdf import PdfReader

# Add or remove skills to suit the roles you are targeting.
SKILL_KEYWORDS = [
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "sql", "kotlin", "swift", "bash",
    # Web / mobile
    "react", "react native", "node.js", "express", "django", "flask", "fastapi",
    "html", "css", "tailwind", "next.js", "angular", "vue",
    # Data
    "pandas", "numpy", "spark", "pyspark", "kafka", "airflow", "etl",
    "data engineering", "data modeling", "power bi", "tableau", "excel",
    "mysql", "postgresql", "mongodb", "redis", "snowflake", "bigquery",
    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "github",
    "ci/cd", "linux", "terraform", "jenkins",
    # AI / ML
    "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
    "scikit-learn", "llm", "langchain", "google adk",
    # Embedded / networking
    "embedded", "c programming", "rtos", "wireless", "networking", "tcp/ip",
    # General
    "rest api", "graphql", "microservices", "agile", "scrum", "oop",
    "data structures", "algorithms", "unit testing",
]


def read_file(path: str) -> dict:
    """Reads a resume or job description from a .txt or .pdf file.

    Args:
        path: Path to the file, for example "samples/sample_resume.txt".

    Returns:
        A dict with status and either the file text or an error message.
    """
    file_path = Path(path).expanduser()
    if not file_path.exists():
        return {"status": "error", "error_message": f"File not found: {path}"}

    try:
        if file_path.suffix.lower() == ".pdf":
            reader = PdfReader(str(file_path))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        else:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:  # keep the agent alive if a file is unreadable
        return {"status": "error", "error_message": f"Could not read file: {e}"}

    if not text.strip():
        return {"status": "error", "error_message": "The file contains no readable text."}
    return {"status": "success", "text": text}


def extract_skills(text: str) -> dict:
    """Finds known technical skills mentioned in a block of text.

    Args:
        text: The full text of a resume or a job description.

    Returns:
        A dict with status and the sorted list of skills found.
    """
    lowered = text.lower()
    found = []
    for skill in SKILL_KEYWORDS:
        # Match the skill only when it is not part of a longer word.
        pattern = r"(?<![a-z0-9+#])" + re.escape(skill) + r"(?![a-z0-9+#])"
        if re.search(pattern, lowered):
            found.append(skill)
    return {"status": "success", "skills": sorted(found)}


def compare_skills(resume_skills: list[str], jd_skills: list[str]) -> dict:
    """Compares skills found in a resume against skills required by a job description.

    Args:
        resume_skills: Skills extracted from the resume.
        jd_skills: Skills extracted from the job description.

    Returns:
        A dict with matched skills, missing skills, and a match percentage.
    """
    resume_set = {s.lower() for s in resume_skills}
    jd_set = {s.lower() for s in jd_skills}

    matched = sorted(resume_set & jd_set)
    missing = sorted(jd_set - resume_set)
    score = round(100 * len(matched) / len(jd_set), 1) if jd_set else 0.0

    return {
        "status": "success",
        "matched": matched,
        "missing": missing,
        "match_percentage": score,
    }