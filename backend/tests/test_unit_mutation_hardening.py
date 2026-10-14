"""Extra unit tests added after the first mutation-testing run.

Each test targets a surviving mutant (exact messages, every dictionary
entry, every alias, every metric pattern) so that silent changes to those
values are detected.
"""
import pytest

from app.services import jd_matcher
from app.services.ats_analyzer import (
    analyze_resume, calculate_content_score, generate_suggestions)
from app.services.resume_parser import extract_skills, extract_sections

pytestmark = pytest.mark.unit

PARSER_SKILLS = [
    "Python", "Java", "C++", "C", "JavaScript", "TypeScript", "HTML", "CSS",
    "React", "Node.js", "Express", "FastAPI", "Flask", "Django", "SQL",
    "MySQL", "PostgreSQL", "MongoDB", "Git", "GitHub", "Docker", "AWS",
    "Linux", "Machine Learning", "Deep Learning", "NLP", "Scikit-learn",
    "TensorFlow", "PyTorch", "OpenCV", "Computer Networks",
    "Data Structures", "Algorithms", "REST API", "Arduino", "ESP32",
    "Raspberry Pi",
]


@pytest.mark.parametrize("skill", PARSER_SKILLS)
def test_every_parser_skill_is_detected(skill):
    assert skill in extract_skills(f"Experienced with {skill} projects.")


@pytest.mark.xfail(strict=True, reason=(
    "KNOWN DEFECT DEF-01: resume_parser.extract_skills reports 'C' when the "
    "text only contains 'C++' because its look-ahead does not exclude '+'. "
    "jd_matcher.py already handles this with [a-z0-9+#]."))
def test_cpp_does_not_imply_c():
    assert extract_skills("Experienced with C++ projects.") == ["C++"]


@pytest.mark.parametrize("skill", PARSER_SKILLS)
def test_parser_skill_not_found_inside_longer_word(skill):
    assert skill not in extract_skills(f"x{skill}x")


@pytest.mark.parametrize("skill", sorted(jd_matcher.KNOWN_SKILLS))
def test_every_jd_known_skill_is_detected(skill):
    assert skill in jd_matcher.extract_known_skills(f"need {skill} here")


@pytest.mark.parametrize("alias,canonical", sorted(jd_matcher.SKILL_CANONICAL.items()))
def test_every_alias_canonicalises(alias, canonical):
    assert jd_matcher.canonicalize_skill(alias) == canonical


@pytest.mark.parametrize("old,new", [
    ("react.js", "react"), ("node.js", "node"), ("express.js", "express"),
    ("restful api", "rest api"), ("restful apis", "rest apis"),
    ("front-end", "frontend"), ("back-end", "backend"),
    ("full-stack", "full stack"), ("fullstack", "full stack"),
    ("machine-learning", "machine learning"),
    ("deep-learning", "deep learning"),
    ("data-structures", "data structures"),
    ("object-oriented programming", "object oriented programming"),
    ("problem-solving", "problem solving"),
])
def test_jd_normalize_replacements(old, new):
    assert jd_matcher.normalize_text(f"a {old} b") == f"a {new} b"


def test_normalize_non_string_input():
    assert jd_matcher.normalize_text(123) == "123"


def test_meaningful_words_keeps_symbols_and_strips_punctuation():
    w = jd_matcher.extract_meaningful_words("c++, node.js! (python)")
    assert "c++" in w and "python" in w and "node" in w


def test_meaningful_words_min_length_boundary():
    w = jd_matcher.extract_meaningful_words("abc ab")
    assert w == {"abc"}


@pytest.mark.parametrize("word", ["verified", "mastering"])
def test_meaningful_words_drops_nothing_extra(word):
    assert word in jd_matcher.extract_meaningful_words(word)


class TestExactJDMessages:
    R = {"skills": ["Python", "React"]}

    def test_empty_jd_payload(self):
        assert jd_matcher.match_resume_to_jd(self.R, "") == {
            "jd_match_score": 0, "matched_keywords": [],
            "missing_keywords": [], "total_jd_keywords": 0,
            "recommendations": [
                "Add a job description to calculate JD compatibility."]}

    def test_none_jd_payload(self):
        assert jd_matcher.match_resume_to_jd(self.R, None)["jd_match_score"] == 0

    def test_exact_missing_recommendation(self):
        r = jd_matcher.match_resume_to_jd(self.R, "Python Docker")
        assert r["recommendations"][0] == (
            "Consider adding relevant skills from the job description that "
            "you genuinely have experience with: docker.")

    def test_exact_low_message(self):
        r = jd_matcher.match_resume_to_jd(self.R, "Docker AWS Linux")
        assert r["recommendations"][-1] == (
            "Your resume has a low keyword match with this job description. "
            "Consider tailoring your skills and project descriptions to the "
            "target role.")

    def test_exact_moderate_message(self):
        r = jd_matcher.match_resume_to_jd(self.R, "Python Docker")
        assert r["recommendations"][-1] == (
            "Your resume has a moderate match. Add relevant job-specific "
            "technologies and terminology where appropriate.")

    def test_exact_strong_message_and_no_missing_message(self):
        r = jd_matcher.match_resume_to_jd(self.R, "Python React")
        assert r["recommendations"] == [
            "Your resume has strong keyword alignment with this job description."]

    @pytest.mark.parametrize("jd,score,fragment", [
        ("Python Docker AWS Linux Java", 20, "low"),
        ("Python Docker Linux", 33, "low"),
        ("Python React Docker Linux", 50, "moderate"),
        ("Python React Docker", 67, "moderate"),
    ])
    def test_threshold_messages(self, jd, score, fragment):
        r = jd_matcher.match_resume_to_jd(self.R, jd)
        assert r["jd_match_score"] == score
        assert fragment in r["recommendations"][-1]

    def test_exactly_40_and_70_boundaries(self):
        five = {"skills": ["python", "react"]}
        r = jd_matcher.match_resume_to_jd(five, "python react docker aws linux")
        assert r["jd_match_score"] == 40
        assert "moderate" in r["recommendations"][-1]
        ten = {"skills": ["python", "react", "docker", "aws", "linux",
                          "java", "git"]}
        r = jd_matcher.match_resume_to_jd(
            ten, "python react docker aws linux java git go rust php")
        assert r["jd_match_score"] == 70
        assert "strong" in r["recommendations"][-1]

    def test_result_lists_are_sorted(self):
        r = jd_matcher.match_resume_to_jd(
            {"skills": ["react", "python"]}, "react python docker aws")
        assert r["matched_keywords"] == ["python", "react"]
        assert r["missing_keywords"] == ["aws", "docker"]


class TestExactSuggestions:
    FULL = {"contact": {"email": "a@b.c", "phone": "9", "linkedin": "x"},
            "summary": "s", "experience": "e", "projects": "p",
            "skills": list("abcde")}
    OK = {"content": 20}
    LONG = "word " * 300

    @pytest.mark.parametrize("patch,message", [
        ({"contact": {"phone": "9", "linkedin": "x"}},
         "Add a professional email address to your contact section."),
        ({"contact": {"email": "a", "linkedin": "x"}},
         "Consider adding a phone number to your contact information."),
        ({"contact": {"email": "a", "phone": "9"}},
         "Add a LinkedIn profile URL to strengthen your professional profile."),
        ({"summary": ""},
         "Add a concise professional summary tailored to your target role."),
        ({"experience": ""},
         "Add relevant work, internship, or practical experience."),
        ({"projects": ""},
         "Add relevant projects and describe your technical contributions."),
        ({"skills": list("abcd")},
         "Add more relevant technical skills that match your target role."),
    ])
    def test_exact_message(self, patch, message):
        r = {**self.FULL, **patch}
        assert generate_suggestions(r, self.LONG, self.OK) == [message]

    def test_content_message_and_threshold(self):
        msg = ("Use more action verbs and measurable achievements to "
               "demonstrate impact.")
        assert generate_suggestions(self.FULL, self.LONG, {"content": 11}) == [msg]
        assert generate_suggestions(self.FULL, self.LONG, {"content": 12}) == []

    def test_short_text_message_and_threshold(self):
        msg = "Add more relevant detail to your resume while keeping it concise."
        assert generate_suggestions(self.FULL, "w " * 249, self.OK) == [msg]
        assert generate_suggestions(self.FULL, "w " * 250, self.OK) == []

    def test_five_skills_is_enough(self):
        assert generate_suggestions(self.FULL, self.LONG, self.OK) == []


class TestContentScoreDetails:
    @pytest.mark.parametrize("word", [
        "developed", "implemented", "designed", "created", "built", "managed",
        "improved", "optimized", "analyzed", "engineered", "automated",
        "led", "achieved"])
    def test_each_action_word_counts(self, word):
        assert calculate_content_score(word) == 3
        assert calculate_content_score(word.upper()) == 3

    @pytest.mark.parametrize("text", [
        "40%", "5+", "5 users", "5 projects", "5 teams", "5 requests",
        "5 packets", "5 records", "5 seconds", "5 ms", "5 minutes", "5 hours"])
    def test_each_metric_pattern_counts(self, text):
        assert calculate_content_score(text) == 2

    def test_boundaries_word_count(self):
        assert calculate_content_score("w " * 149) == 0
        assert calculate_content_score("w " * 249) == 3
        assert calculate_content_score("w " * 399) == 5

    def test_boundaries_action_count(self):
        assert calculate_content_score("built " * 3) == 3
        assert calculate_content_score("built " * 4) == 5
        assert calculate_content_score("built " * 7) == 5
        assert calculate_content_score("built " * 8) == 7

    def test_boundaries_metric_count(self):
        assert calculate_content_score("1% 2%") == 4
        assert calculate_content_score("1% 2% 3%") == 4
        assert calculate_content_score("1% 2% 3% 4%") == 6


class TestAnalyzeDetails:
    def test_breakdown_percentages(self):
        resume = {"contact": {"name": "A", "email": "e"},   # 9/15 = 60
                  "summary": "s", "education": "e", "skills": ["a"] * 5,  # 15/25 = 60
                  "experience": "", "projects": ""}
        r = analyze_resume(resume, "built " * 4)            # content 5/20 = 25
        assert r["breakdown"] == {"contact": 60, "sections": 60,
                                  "skills": 56, "content": 25}

    def test_suggestions_are_included(self):
        r = analyze_resume({"contact": {}, "skills": []}, "")
        assert len(r["suggestions"]) == 9


def test_sections_ignore_headings_with_trailing_punctuation():
    s = extract_sections("Skills -\nPython\nProjects |\nApp")
    assert s["skills"] == "Python" and s["projects"] == "App"


def test_sections_multiline_content_joined_with_newline():
    assert extract_sections("Skills\nA\nB")["skills"] == "A\nB"
