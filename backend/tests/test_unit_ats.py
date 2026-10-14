"""Unit tests - app/services/ats_analyzer.py"""
import pytest

from app.services.ats_analyzer import (
    analyze_resume,
    calculate_contact_score,
    calculate_content_score,
    calculate_section_score,
    calculate_skills_score,
    generate_suggestions,
)

pytestmark = pytest.mark.unit


class TestContactScore:
    def test_full_contact_is_15(self):
        c = {"name": "A", "email": "a@b.c", "phone": "9876543210", "linkedin": "x"}
        assert calculate_contact_score(c) == 15

    def test_empty_is_zero(self):
        assert calculate_contact_score({}) == 0

    @pytest.mark.parametrize(
        "field,points",
        [("name", 5), ("email", 4), ("phone", 3), ("linkedin", 3), ("github", 3)],
    )
    def test_each_field_weight(self, field, points):
        assert calculate_contact_score({field: "value"}) == points

    def test_linkedin_and_github_count_once(self):
        assert calculate_contact_score({"linkedin": "x", "github": "y"}) == 3


class TestSectionScore:
    def test_all_sections_present_is_25(self):
        r = {k: "text" for k in
             ["summary", "education", "experience", "skills", "projects"]}
        assert calculate_section_score(r) == 25

    def test_blank_strings_do_not_count(self):
        assert calculate_section_score({"summary": "   ", "education": ""}) == 0

    def test_list_sections_count_when_non_empty(self):
        assert calculate_section_score({"skills": ["Python"]}) == 5
        assert calculate_section_score({"skills": []}) == 0

    def test_each_section_worth_5(self):
        assert calculate_section_score({"education": "x", "projects": "y"}) == 10


class TestSkillsScore:
    @pytest.mark.parametrize(
        "count,expected",
        [(0, 0), (1, 5), (2, 5), (3, 10), (4, 10), (5, 14), (6, 14),
         (7, 18), (9, 18), (10, 22), (14, 22), (15, 25), (40, 25)],
    )
    def test_threshold_boundaries(self, count, expected):
        assert calculate_skills_score(["s"] * count) == expected


class TestContentScore:
    def test_empty_text_scores_zero(self):
        assert calculate_content_score("") == 0

    def test_word_count_tiers(self):
        assert calculate_content_score("word " * 150) == 3
        assert calculate_content_score("word " * 250) == 5
        assert calculate_content_score("word " * 400) == 7

    def test_action_verbs_tiers(self):
        assert calculate_content_score("developed") == 3
        assert calculate_content_score("developed built designed created") == 5
        assert calculate_content_score(" ".join(["developed"] * 8)) == 7

    def test_metrics_tiers(self):
        assert calculate_content_score("improved by 40%") == 3 + 2
        assert calculate_content_score("40% and 50%") == 4
        assert calculate_content_score("10% 20% 30% 40%") == 6

    def test_score_capped_at_20(self):
        text = ("developed " * 10 + "10% 20% 30% 40% ") + "word " * 400
        assert calculate_content_score(text) == 20

    def test_action_verb_whole_word_only(self):
        assert calculate_content_score("redeveloped") == 0


class TestSuggestions:
    BREAKDOWN = {"contact": 15, "sections": 25, "skills": 25, "content": 20}

    def _full_resume(self):
        return {
            "contact": {"email": "a@b.c", "phone": "9", "linkedin": "x"},
            "summary": "s", "experience": "e", "projects": "p",
            "skills": ["a", "b", "c", "d", "e"],
        }

    def test_no_suggestions_for_complete_resume(self):
        assert generate_suggestions(
            self._full_resume(), "word " * 300, self.BREAKDOWN) == []

    def test_each_missing_field_gives_a_suggestion(self):
        s = generate_suggestions(
            {"contact": {}, "skills": []}, "", {"content": 0})
        assert len(s) == 9

    def test_few_skills_suggestion(self):
        r = self._full_resume()
        r["skills"] = ["a"]
        s = generate_suggestions(r, "word " * 300, self.BREAKDOWN)
        assert any("technical skills" in x for x in s)

    def test_low_content_score_suggestion(self):
        s = generate_suggestions(
            self._full_resume(), "word " * 300,
            {**self.BREAKDOWN, "content": 11})
        assert any("action verbs" in x for x in s)

    def test_short_resume_suggestion(self):
        s = generate_suggestions(self._full_resume(), "short", self.BREAKDOWN)
        assert any("more relevant detail" in x for x in s)


class TestAnalyzeResume:
    def test_empty_resume_is_zero(self):
        r = analyze_resume({"contact": {}, "skills": []}, "")
        assert r["ats_score"] == 0
        assert r["breakdown"] == {
            "contact": 0, "sections": 0, "skills": 0, "content": 0}

    def test_perfect_resume_is_100(self):
        resume = {
            "contact": {"name": "A", "email": "a@b.c",
                        "phone": "9", "linkedin": "x"},
            "summary": "s", "education": "e", "experience": "x",
            "projects": "p", "skills": ["s"] * 15,
        }
        text = ("developed " * 10 + "10% 20% 30% 40% ") + "word " * 400
        r = analyze_resume(resume, text)
        assert r["ats_score"] == 100
        assert all(v == 100 for v in r["breakdown"].values())

    def test_score_normalised_from_85(self):
        # contact 15 only -> 15/85 = 17.6 -> 18
        r = analyze_resume({"contact": {"name": "A", "email": "a@b.c",
                                        "phone": "9", "linkedin": "x"},
                            "skills": []}, "")
        assert r["ats_score"] == 18

    def test_result_shape(self):
        r = analyze_resume({"contact": {}, "skills": []}, "")
        assert set(r) == {"ats_score", "breakdown", "suggestions"}
