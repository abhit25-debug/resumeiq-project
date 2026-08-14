import re


# =========================================================
# KNOWN SKILLS
# =========================================================

KNOWN_SKILLS = [
    # -----------------------------------------------------
    # Programming Languages
    # -----------------------------------------------------
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "c++",
    "c#",
    "go",
    "rust",
    "php",
    "kotlin",
    "swift",

    # -----------------------------------------------------
    # Web / Frontend
    # -----------------------------------------------------
    "html",
    "css",
    "react",
    "react.js",
    "angular",
    "vue",
    "node",
    "node.js",
    "express",
    "express.js",
    "frontend",
    "front-end",
    "backend",
    "back-end",
    "full stack",
    "full-stack",
    "fullstack",

    # -----------------------------------------------------
    # APIs
    # -----------------------------------------------------
    "api",
    "apis",
    "rest",
    "rest api",
    "rest apis",
    "graphql",

    # -----------------------------------------------------
    # Databases
    # -----------------------------------------------------
    "sql",
    "mysql",
    "postgresql",
    "postgres",
    "mongodb",
    "database",
    "databases",
    "sqlite",
    "redis",

    # -----------------------------------------------------
    # DevOps / Tools
    # -----------------------------------------------------
    "git",
    "github",
    "gitlab",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "linux",

    # -----------------------------------------------------
    # Computer Science
    # -----------------------------------------------------
    "data structures",
    "algorithms",
    "data structures and algorithms",
    "object oriented programming",
    "oop",
    "operating systems",
    "computer networks",
    "dbms",

    # -----------------------------------------------------
    # AI / ML
    # -----------------------------------------------------
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "ai",
    "nlp",
    "natural language processing",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "sklearn",
    "pandas",
    "numpy",

    # -----------------------------------------------------
    # Robotics / Embedded
    # -----------------------------------------------------
    "robotics",
    "arduino",
    "esp32",
    "raspberry pi",
    "embedded systems",
    "iot",

    # -----------------------------------------------------
    # Software Engineering
    # -----------------------------------------------------
    "software development",
    "software engineering",
    "agile",
    "scrum",
    "testing",
    "unit testing",
    "debugging",
    "problem solving",
    "problem-solving",
]


# =========================================================
# CANONICAL SKILL ALIASES
#
# Every variation is converted to ONE standard name.
# =========================================================

SKILL_CANONICAL = {

    # Web
    "react": "react",
    "react.js": "react",

    "node": "node",
    "node.js": "node",

    "express": "express",
    "express.js": "express",

    "frontend": "frontend",
    "front-end": "frontend",

    "backend": "backend",
    "back-end": "backend",

    "full stack": "full stack",
    "full-stack": "full stack",
    "fullstack": "full stack",

    # APIs
    "api": "rest api",
    "apis": "rest api",
    "rest": "rest api",
    "rest api": "rest api",
    "rest apis": "rest api",

    # Databases
    "database": "database",
    "databases": "database",

    # CS
    "data structures and algorithms": "data structures and algorithms",

    "data structures": "data structures",

    "algorithms": "algorithms",

    "object oriented programming": "object oriented programming",
    "oop": "object oriented programming",

    # AI
    "artificial intelligence": "artificial intelligence",
    "ai": "artificial intelligence",

    "natural language processing": "nlp",
    "nlp": "nlp",

    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",

    # Software Engineering
    "problem-solving": "problem solving",
    "problem solving": "problem solving",
}


# =========================================================
# STOP WORDS
# =========================================================

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "good",
    "have",
    "has",
    "in",
    "into",
    "is",
    "it",
    "job",
    "join",
    "looking",
    "of",
    "on",
    "or",
    "our",
    "role",
    "should",
    "strong",
    "team",
    "teams",
    "the",
    "their",
    "this",
    "to",
    "we",
    "with",
    "you",
    "your",
    "ability",
    "able",
    "knowledge",
    "experience",
    "experienced",
    "familiarity",
    "familiar",
    "understanding",
    "requirements",
    "requirement",
    "candidate",
    "candidates",
    "work",
    "working",
    "skills",
    "skill",
    "plus",
    "preferred",
    "required",
    "responsibilities",
    "responsibility",
    "development",
}


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(text):
    """
    Converts text to lowercase and normalizes common variations.
    """

    if not text:
        return ""

    text = str(text).lower()

    replacements = {
        "react.js": "react",
        "node.js": "node",
        "express.js": "express",

        "restful api": "rest api",
        "restful apis": "rest apis",

        "front-end": "frontend",
        "back-end": "backend",

        "full-stack": "full stack",
        "fullstack": "full stack",

        "machine-learning": "machine learning",
        "deep-learning": "deep learning",

        "data-structures": "data structures",

        "object-oriented programming":
            "object oriented programming",

        "problem-solving":
            "problem solving",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


# =========================================================
# CANONICALIZE SKILL
# =========================================================

def canonicalize_skill(skill):
    """
    Converts a skill or alias into one standard name.
    """

    skill = normalize_text(skill).strip()

    return SKILL_CANONICAL.get(skill, skill)


# =========================================================
# RESUME DICTIONARY -> SEARCHABLE TEXT
# =========================================================

def resume_to_text(resume):

    if resume is None:
        return ""

    if isinstance(resume, str):
        return resume

    if isinstance(resume, list):
        return " ".join(
            resume_to_text(item)
            for item in resume
        )

    if isinstance(resume, dict):

        parts = []

        for value in resume.values():
            parts.append(
                resume_to_text(value)
            )

        return " ".join(parts)

    return str(resume)


# =========================================================
# FIND KNOWN SKILLS
# =========================================================

def extract_known_skills(text):
    """
    Finds technical skills from text.

    Returns the original detected skill names.
    Canonicalization is done separately.
    """

    text = normalize_text(text)

    found = set()

    # Longest skills first.
    sorted_skills = sorted(
        KNOWN_SKILLS,
        key=len,
        reverse=True
    )

    for skill in sorted_skills:

        skill_normalized = normalize_text(skill)

        pattern = (
            r"(?<![a-z0-9+#])"
            + re.escape(skill_normalized)
            + r"(?![a-z0-9+#])"
        )

        if re.search(pattern, text):
            found.add(skill)

    return found


# =========================================================
# CANONICAL JD SKILLS
# =========================================================

def extract_canonical_skills(text):
    """
    Extracts JD skills and converts all aliases
    into canonical names.

    Example:

        api
        APIs
        REST
        REST API
        REST APIs

    become:

        rest api
    """

    detected_skills = extract_known_skills(text)

    canonical_skills = set()

    for skill in detected_skills:

        canonical_skill = canonicalize_skill(skill)

        canonical_skills.add(
            canonical_skill
        )

    return canonical_skills


# =========================================================
# EXTRACT MEANINGFUL WORDS
# =========================================================

def extract_meaningful_words(text):

    text = normalize_text(text)

    words = re.findall(
        r"[a-z][a-z0-9+#.-]*",
        text
    )

    meaningful = set()

    for word in words:

        word = word.strip(
            ".,:;!?()[]{}"
        )

        if not word:
            continue

        if word in STOP_WORDS:
            continue

        if len(word) < 3:
            continue

        meaningful.add(word)

    return meaningful


# =========================================================
# CHECK KEYWORD IN RESUME
# =========================================================

def keyword_in_resume(
    keyword,
    resume_text
):
    """
    Checks whether a canonical keyword exists
    in the resume.

    It also understands aliases.
    """

    resume_text = normalize_text(
        resume_text
    )

    keyword = canonicalize_skill(
        keyword
    )

    # -----------------------------------------------------
    # Build all possible aliases for this canonical skill
    # -----------------------------------------------------

    aliases_to_check = {
        keyword
    }

    for alias, canonical in SKILL_CANONICAL.items():

        if canonical == keyword:
            aliases_to_check.add(alias)

    # -----------------------------------------------------
    # Search every valid variation
    # -----------------------------------------------------

    for alias in aliases_to_check:

        alias = normalize_text(alias)

        pattern = (
            r"(?<![a-z0-9+#])"
            + re.escape(alias)
            + r"(?![a-z0-9+#])"
        )

        if re.search(
            pattern,
            resume_text
        ):
            return True

    # -----------------------------------------------------
    # Special case:
    #
    # "data structures and algorithms"
    #
    # can be represented in a resume as:
    #
    # "data structures"
    # AND
    # "algorithms"
    # -----------------------------------------------------

    if keyword == "data structures and algorithms":

        has_ds = re.search(
            r"(?<![a-z0-9])data structures(?![a-z0-9])",
            resume_text
        )

        has_algorithms = re.search(
            r"(?<![a-z0-9])algorithms(?![a-z0-9])",
            resume_text
        )

        if has_ds and has_algorithms:
            return True

    return False


# =========================================================
# MAIN JD MATCHING FUNCTION
# =========================================================

def match_resume_to_jd(
    resume,
    job_description
):

    # =====================================================
    # NO JOB DESCRIPTION
    # =====================================================

    if (
        not job_description
        or not job_description.strip()
    ):

        return {
            "jd_match_score": 0,
            "matched_keywords": [],
            "missing_keywords": [],
            "total_jd_keywords": 0,
            "recommendations": [
                "Add a job description to calculate JD compatibility."
            ],
        }


    # =====================================================
    # PREPARE TEXT
    # =====================================================

    resume_text = resume_to_text(
        resume
    )

    jd_text = normalize_text(
        job_description
    )


    # =====================================================
    # EXTRACT CANONICAL JD SKILLS
    # =====================================================

    jd_keywords = extract_canonical_skills(
        jd_text
    )


    # =====================================================
    # MATCH JD SKILLS AGAINST RESUME
    # =====================================================

    matched_keywords = []
    missing_keywords = []


    for keyword in sorted(jd_keywords):

        if keyword_in_resume(
            keyword,
            resume_text
        ):

            matched_keywords.append(
                keyword
            )

        else:

            missing_keywords.append(
                keyword
            )


    # =====================================================
    # TOTAL KEYWORDS
    # =====================================================

    total_keywords = len(
        jd_keywords
    )


    # =====================================================
    # CALCULATE MATCH SCORE
    # =====================================================

    if total_keywords == 0:

        match_score = 0

    else:

        match_score = round(
            (
                len(matched_keywords)
                / total_keywords
            )
            * 100
        )


    # =====================================================
    # RECOMMENDATIONS
    # =====================================================

    recommendations = []


    # -----------------------------------------------------
    # Missing skills recommendation
    # -----------------------------------------------------

    if missing_keywords:

        recommendations.append(
            "Consider adding relevant skills from the job "
            "description that you genuinely have experience "
            "with: "
            + ", ".join(
                missing_keywords[:8]
            )
            + "."
        )


    # -----------------------------------------------------
    # Score-based recommendation
    # -----------------------------------------------------

    if match_score < 40:

        recommendations.append(
            "Your resume has a low keyword match with this "
            "job description. Consider tailoring your skills "
            "and project descriptions to the target role."
        )

    elif match_score < 70:

        recommendations.append(
            "Your resume has a moderate match. Add relevant "
            "job-specific technologies and terminology "
            "where appropriate."
        )

    else:

        recommendations.append(
            "Your resume has strong keyword alignment "
            "with this job description."
        )


    # =====================================================
    # RETURN RESULT
    # =====================================================

    return {

        "jd_match_score": match_score,

        "matched_keywords":
            sorted(matched_keywords),

        "missing_keywords":
            sorted(missing_keywords),

        "total_jd_keywords":
            total_keywords,

        "recommendations":
            recommendations,
    }