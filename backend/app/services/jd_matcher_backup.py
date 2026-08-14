import re


STOP_WORDS = {
    "the",
    "and",
    "or",
    "for",
    "with",
    "from",
    "this",
    "that",
    "are",
    "you",
    "your",
    "our",
    "will",
    "have",
    "has",
    "into",
    "about",
    "using",
    "their",
    "they",
    "them",
    "job",
    "role",
    "work",
    "working",
    "years",
    "year",
    "experience",
    "candidate",
    "required",
    "preferred",
    "responsibilities",
    "skills",
}


TECHNICAL_KEYWORDS = {
    "python",
    "java",
    "c",
    "c++",
    "javascript",
    "typescript",
    "react",
    "node.js",
    "express",
    "fastapi",
    "flask",
    "django",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "git",
    "github",
    "docker",
    "aws",
    "azure",
    "gcp",
    "linux",
    "machine learning",
    "deep learning",
    "nlp",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "opencv",
    "computer vision",
    "data structures",
    "algorithms",
    "rest api",
    "api",
    "arduino",
    "esp32",
    "kubernetes",
    "ci/cd",
    "agile",
    "microservices",
}


def normalize_text(text: str) -> str:
    """Normalize text for keyword matching."""

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9+#./-]+",
        " ",
        text,
    )

    return re.sub(r"\s+", " ", text).strip()


def extract_keywords(text: str) -> list:
    """Extract relevant technical keywords from a job description."""

    normalized = normalize_text(text)

    found_keywords = []

    for keyword in TECHNICAL_KEYWORDS:
        keyword_normalized = normalize_text(keyword)

        if keyword_normalized in normalized:
            found_keywords.append(keyword)

    # Also collect important non-technical words.
    words = normalized.split()

    for word in words:
        if (
            len(word) >= 4
            and word not in STOP_WORDS
            and word not in found_keywords
            and word.isalpha()
        ):
            found_keywords.append(word)

    return sorted(set(found_keywords))


def get_resume_keywords(resume: dict) -> set:
    """Create a keyword set from parsed resume information."""

    keywords = set()

    skills = resume.get("skills", [])

    for skill in skills:
        keywords.add(normalize_text(skill))

    for section in [
        "summary",
        "education",
        "experience",
        "projects",
    ]:
        content = resume.get(section, "")

        if content:
            words = normalize_text(content).split()

            for word in words:
                if (
                    len(word) >= 4
                    and word not in STOP_WORDS
                ):
                    keywords.add(word)

    return keywords


def match_resume_to_jd(
    resume: dict,
    job_description: str,
) -> dict:
    """Compare resume content against a job description."""

    if not job_description.strip():
        return {
            "jd_match_score": 0,
            "matched_keywords": [],
            "missing_keywords": [],
            "total_jd_keywords": 0,
            "recommendations": [
                "Provide a job description to calculate the JD match score."
            ],
        }

    jd_keywords = set(
        extract_keywords(job_description)
    )

    resume_keywords = get_resume_keywords(resume)

    matched_keywords = sorted(
        keyword
        for keyword in jd_keywords
        if keyword in resume_keywords
    )

    missing_keywords = sorted(
        keyword
        for keyword in jd_keywords
        if keyword not in resume_keywords
    )

    total_keywords = len(jd_keywords)

    if total_keywords:
        match_score = round(
            len(matched_keywords)
            / total_keywords
            * 100
        )
    else:
        match_score = 0

    recommendations = []

    if missing_keywords:
        important_missing = missing_keywords[:8]

        recommendations.append(
            "Consider adding these relevant keywords "
            "where they genuinely match your experience: "
            + ", ".join(important_missing)
            + "."
        )

    if match_score < 50:
        recommendations.append(
            "Your resume has a relatively low keyword match "
            "with this job description. Tailor your projects "
            "and experience toward the role."
        )
    elif match_score < 75:
        recommendations.append(
            "Your resume has a moderate match. Add relevant "
            "job-specific terminology where appropriate."
        )
    else:
        recommendations.append(
            "Your resume has strong keyword alignment with "
            "this job description."
        )

    return {
        "jd_match_score": match_score,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "total_jd_keywords": total_keywords,
        "recommendations": recommendations,
    }