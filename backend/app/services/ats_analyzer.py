import re


# Core resume sections expected by ResumeIQ
REQUIRED_SECTIONS = [
    "summary",
    "education",
    "experience",
    "skills",
    "projects",
]


def calculate_contact_score(contact: dict) -> int:
    """
    Score the completeness of contact information.
    Maximum: 15 points.
    """

    score = 0

    if contact.get("name"):
        score += 5

    if contact.get("email"):
        score += 4

    if contact.get("phone"):
        score += 3

    if contact.get("linkedin") or contact.get("github"):
        score += 3

    return score


def calculate_section_score(resume: dict) -> int:
    """
    Score the presence of important resume sections.
    Maximum: 25 points.
    """

    score = 0

    section_weights = {
        "summary": 5,
        "education": 5,
        "experience": 5,
        "skills": 5,
        "projects": 5,
    }

    for section, weight in section_weights.items():
        value = resume.get(section)

        if isinstance(value, list):
            if value:
                score += weight

        elif isinstance(value, str):
            if value.strip():
                score += weight

    return score


def calculate_skills_score(skills: list) -> int:
    """
    Score the number of detected technical skills.
    Maximum: 25 points.
    """

    skill_count = len(skills)

    if skill_count >= 15:
        return 25

    if skill_count >= 10:
        return 22

    if skill_count >= 7:
        return 18

    if skill_count >= 5:
        return 14

    if skill_count >= 3:
        return 10

    if skill_count >= 1:
        return 5

    return 0


def calculate_content_score(text: str) -> int:
    """
    Perform basic content-quality checks.
    Maximum: 20 points.
    """

    score = 0

    word_count = len(text.split())

    # Resume should contain enough content.
    if word_count >= 400:
        score += 7
    elif word_count >= 250:
        score += 5
    elif word_count >= 150:
        score += 3

    # Look for achievement/action-oriented language.
    action_words = [
        "developed",
        "implemented",
        "designed",
        "created",
        "built",
        "managed",
        "improved",
        "optimized",
        "analyzed",
        "engineered",
        "automated",
        "led",
        "achieved",
    ]

    action_count = sum(
        len(re.findall(rf"\b{re.escape(word)}\b", text, re.IGNORECASE))
        for word in action_words
    )

    if action_count >= 8:
        score += 7
    elif action_count >= 4:
        score += 5
    elif action_count >= 1:
        score += 3

    # Look for measurable results.
    metric_patterns = [
        r"\b\d+%",
        r"\b\d+\+",
        r"\b\d+\s*(users|projects|teams|requests|packets|records)",
        r"\b\d+\s*(seconds|ms|minutes|hours)",
    ]

    metric_count = sum(
        len(re.findall(pattern, text, re.IGNORECASE))
        for pattern in metric_patterns
    )

    if metric_count >= 4:
        score += 6
    elif metric_count >= 2:
        score += 4
    elif metric_count >= 1:
        score += 2

    return min(score, 20)


def generate_suggestions(
    resume: dict,
    text: str,
    score_breakdown: dict,
) -> list:
    """
    Generate actionable resume improvement suggestions.
    """

    suggestions = []

    contact = resume.get("contact", {})
    skills = resume.get("skills", [])

    if not contact.get("email"):
        suggestions.append(
            "Add a professional email address to your contact section."
        )

    if not contact.get("phone"):
        suggestions.append(
            "Consider adding a phone number to your contact information."
        )

    if not contact.get("linkedin"):
        suggestions.append(
            "Add a LinkedIn profile URL to strengthen your professional profile."
        )

    if not resume.get("summary", "").strip():
        suggestions.append(
            "Add a concise professional summary tailored to your target role."
        )

    if not resume.get("experience", "").strip():
        suggestions.append(
            "Add relevant work, internship, or practical experience."
        )

    if not resume.get("projects", "").strip():
        suggestions.append(
            "Add relevant projects and describe your technical contributions."
        )

    if len(skills) < 5:
        suggestions.append(
            "Add more relevant technical skills that match your target role."
        )

    if score_breakdown["content"] < 12:
        suggestions.append(
            "Use more action verbs and measurable achievements to demonstrate impact."
        )

    if len(text.split()) < 250:
        suggestions.append(
            "Add more relevant detail to your resume while keeping it concise."
        )

    return suggestions


def analyze_resume(resume: dict, text: str) -> dict:
    """
    Calculate the ResumeIQ ATS score.

    Total:
        Contact   = 15
        Sections  = 25
        Skills    = 25
        Content   = 20
        Base      = 85

    Remaining 15 points are reserved for job-description
    keyword matching, which will be added in the JD matching module.
    """

    contact_score = calculate_contact_score(
        resume.get("contact", {})
    )

    section_score = calculate_section_score(resume)

    skills_score = calculate_skills_score(
        resume.get("skills", [])
    )

    content_score = calculate_content_score(text)

    base_score = (
        contact_score
        + section_score
        + skills_score
        + content_score
    )

    # For resumes without a JD, normalize the available
    # 85-point evaluation to a 100-point ATS score.
    ats_score = round((base_score / 85) * 100)

    breakdown = {
        "contact": round((contact_score / 15) * 100),
        "sections": round((section_score / 25) * 100),
        "skills": round((skills_score / 25) * 100),
        "content": round((content_score / 20) * 100),
    }

    suggestions = generate_suggestions(
        resume,
        text,
        {
            "contact": contact_score,
            "sections": section_score,
            "skills": skills_score,
            "content": content_score,
        },
    )

    return {
        "ats_score": ats_score,
        "breakdown": breakdown,
        "suggestions": suggestions,
    }