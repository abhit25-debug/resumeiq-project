"""Unit tests - app/services/resume_parser.py"""
import pytest

from app.services.resume_parser import (
    detect_section,
    extract_contact_info,
    extract_sections,
    extract_skills,
    normalize_text,
    parse_resume,
)

pytestmark = pytest.mark.unit

SAMPLE = """Jane Doe
jane.doe@example.com | +91 9876543210
linkedin.com/in/janedoe | github.com/janedoe

Summary
Motivated engineer.

Education
VIT Chennai 2024 - 2028

Experience
Intern at Acme

Skills
Python, React, Docker

Projects
ResumeIQ analyzer
"""


class TestNormalizeText:
    def test_collapses_spaces_and_tabs(self):
        assert normalize_text("a   b\t\tc") == "a b c"

    def test_collapses_blank_lines(self):
        assert normalize_text("a\n\n\n\nb") == "a\n\nb"

    def test_converts_carriage_returns(self):
        assert normalize_text("a\rb") == "a\nb"

    def test_strips_edges(self):
        assert normalize_text("  hi  ") == "hi"


class TestDetectSection:
    @pytest.mark.parametrize(
        "line,expected",
        [
            ("Skills", "skills"),
            ("SKILLS", "skills"),
            ("Skills:", "skills"),
            ("Technical Skills", "skills"),
            ("Professional Experience", "experience"),
            ("Education", "education"),
            ("Academic Projects", "projects"),
            ("Career Objective", "summary"),
        ],
    )
    def test_known_headings(self, line, expected):
        assert detect_section(line) == expected

    @pytest.mark.parametrize("line", ["Hobbies", "Python developer", ""])
    def test_unknown_lines_return_none(self, line):
        assert detect_section(line) is None


class TestExtractSections:
    def test_all_five_sections_found(self):
        s = extract_sections(SAMPLE)
        assert s["summary"] == "Motivated engineer."
        assert "VIT Chennai" in s["education"]
        assert s["experience"] == "Intern at Acme"
        assert s["skills"] == "Python, React, Docker"
        assert s["projects"] == "ResumeIQ analyzer"

    def test_missing_sections_are_empty_strings(self):
        s = extract_sections("Skills\nPython")
        assert s["summary"] == ""
        assert s["experience"] == ""

    def test_text_before_first_heading_is_ignored(self):
        s = extract_sections("Some header\nSkills\nPython")
        assert "Some header" not in s["skills"]


class TestExtractContactInfo:
    def test_full_contact_block(self):
        c = extract_contact_info(SAMPLE)
        assert c["name"] == "Jane Doe"
        assert c["email"] == "jane.doe@example.com"
        assert c["phone"] == "+91 9876543210"
        assert c["linkedin"] == "linkedin.com/in/janedoe"
        assert c["github"] == "github.com/janedoe"

    def test_missing_fields_are_none(self):
        c = extract_contact_info("Jane Doe\nno contact here")
        assert c["email"] is None
        assert c["phone"] is None
        assert c["linkedin"] is None
        assert c["github"] is None

    @pytest.mark.parametrize("heading", ["Resume", "Curriculum Vitae", "CV"])
    def test_heading_is_not_used_as_name(self, heading):
        assert extract_contact_info(f"{heading}\nx@y.com")["name"] is None

    def test_long_first_line_is_not_a_name(self):
        line = "one two three four five six"
        assert extract_contact_info(line)["name"] is None

    def test_first_line_with_email_is_not_a_name(self):
        assert extract_contact_info("jane@x.com")["name"] is None

    def test_phone_without_country_code(self):
        assert extract_contact_info("x\n9876543210")["phone"] == "9876543210"

    def test_invalid_indian_phone_rejected(self):
        assert extract_contact_info("x\n1234567890")["phone"] is None

    def test_empty_text(self):
        assert extract_contact_info("")["name"] is None


class TestExtractSkills:
    def test_detects_known_skills(self):
        assert extract_skills("Python and Docker") == ["Docker", "Python"]

    def test_case_insensitive(self):
        assert "Python" in extract_skills("PYTHON")

    def test_cpp_and_c_are_distinct(self):
        assert "C++" in extract_skills("C++")
        assert "C" in extract_skills("I know C and Java")

    def test_whole_word_only(self):
        # "Javascripting" must not match JavaScript; "Cooperation" must not match C
        assert extract_skills("Javascripting Cooperation") == []

    def test_result_sorted_and_unique(self):
        r = extract_skills("react REACT Python python")
        assert r == sorted(set(r))

    def test_no_skills(self):
        assert extract_skills("nothing relevant") == []


class TestParseResume:
    def test_returns_expected_keys(self):
        r = parse_resume(SAMPLE)
        assert set(r) == {
            "contact", "summary", "education",
            "experience", "skills", "projects",
        }

    def test_skills_are_a_list(self):
        r = parse_resume(SAMPLE)
        assert isinstance(r["skills"], list)
        assert {"Python", "React", "Docker"} <= set(r["skills"])
