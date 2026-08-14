import re
import spacy


nlp = spacy.load("en_core_web_sm")


SECTION_NAMES = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "objective",
        "career objective",
    ],
    "education": [
        "education",
        "academic background",
        "academic qualifications",
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "work history",
    ],
    "skills": [
        "skills",
        "technical skills",
        "core skills",
        "technologies",
        "technical expertise",
    ],
    "projects": [
        "projects",
        "academic projects",
        "personal projects",
        "key projects",
    ],
}


def normalize_text(text: str) -> str:
    """Clean extracted resume text."""

    text = text.replace("\r", "\n")

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def detect_section(line: str):
    """Identify whether a line is a known resume section heading."""

    cleaned = line.strip().lower()

    # Remove common punctuation around headings
    cleaned = re.sub(r"[:\-|]+$", "", cleaned).strip()

    for section, names in SECTION_NAMES.items():
        if cleaned in names:
            return section

    return None


def extract_sections(text: str) -> dict:
    """Split resume text into recognized sections."""

    text = normalize_text(text)

    lines = text.splitlines()

    sections = {
        "summary": [],
        "education": [],
        "experience": [],
        "skills": [],
        "projects": [],
    }

    current_section = None

    for line in lines:
        line = line.strip()

        if not line:
            continue

        detected = detect_section(line)

        if detected:
            current_section = detected
            continue

        if current_section:
            sections[current_section].append(line)

    return {
        section: "\n".join(content).strip()
        for section, content in sections.items()
    }


def extract_contact_info(text: str) -> dict:
    """Extract basic contact information."""

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    email_match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text,
    )

    phone_match = re.search(
        r"(?:\+91[\s-]?)?[6-9]\d{9}",
        text,
    )

    linkedin_match = re.search(
        r"(?:https?://)?(?:www\.)?linkedin\.com/[^\s|]+",
        text,
        re.IGNORECASE,
    )

    github_match = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/[^\s|]+",
        text,
        re.IGNORECASE,
    )

    # Most resumes put the person's name near the beginning.
    person_name = None

    if lines:
        first_line = lines[0]

        # Ignore obvious headings.
        ignored_names = {
            "resume",
            "curriculum vitae",
            "cv",
            "profile",
            "summary",
            "objective",
        }

        if (
            first_line.lower() not in ignored_names
            and len(first_line.split()) <= 5
            and not re.search(r"@|linkedin|github|http|www\.|\d{5,}", first_line, re.I)
        ):
            person_name = first_line

    return {
        "name": person_name,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "linkedin": linkedin_match.group(0) if linkedin_match else None,
        "github": github_match.group(0) if github_match else None,
    }

def extract_skills(text: str) -> list:
    """Extract technical skills using a controlled vocabulary."""

    skill_dictionary = [
        "Python",
        "Java",
        "C++",
        "C",
        "JavaScript",
        "TypeScript",
        "HTML",
        "CSS",
        "React",
        "Node.js",
        "Express",
        "FastAPI",
        "Flask",
        "Django",
        "SQL",
        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "Git",
        "GitHub",
        "Docker",
        "AWS",
        "Linux",
        "Machine Learning",
        "Deep Learning",
        "NLP",
        "Scikit-learn",
        "TensorFlow",
        "PyTorch",
        "OpenCV",
        "Computer Networks",
        "Data Structures",
        "Algorithms",
        "REST API",
        "Arduino",
        "ESP32",
        "Raspberry Pi",
    ]

    found_skills = []

    for skill in skill_dictionary:

        # Escape special characters such as + in C++
        escaped_skill = re.escape(skill)

        # Match complete words/phrases rather than substrings.
        pattern = rf"(?<![A-Za-z0-9]){escaped_skill}(?![A-Za-z0-9])"

        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    return sorted(set(found_skills))


def parse_resume(text: str) -> dict:
    """Run the complete ResumeIQ resume parsing pipeline."""

    cleaned_text = normalize_text(text)

    sections = extract_sections(cleaned_text)

    contact = extract_contact_info(cleaned_text)

    skills = extract_skills(cleaned_text)

    return {
        "contact": contact,
        "summary": sections["summary"],
        "education": sections["education"],
        "experience": sections["experience"],
        "skills": skills,
        "projects": sections["projects"],
    }