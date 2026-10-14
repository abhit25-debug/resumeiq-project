"""Unit tests - app/services/jd_matcher.py"""
import pytest

from app.services.jd_matcher import (
    canonicalize_skill,
    extract_canonical_skills,
    extract_known_skills,
    extract_meaningful_words,
    keyword_in_resume,
    match_resume_to_jd,
    normalize_text,
    resume_to_text,
)

pytestmark = pytest.mark.unit


class TestNormalize:
    def test_lowercases(self):
        assert normalize_text("PYTHON") == "python"

    def test_aliases_replaced(self):
        assert normalize_text("React.js and Node.js") == "react and node"
        assert normalize_text("Full-Stack Front-End") == "full stack frontend"

    def test_empty_inputs(self):
        assert normalize_text("") == ""
        assert normalize_text(None) == ""


class TestCanonicalize:
    @pytest.mark.parametrize(
        "raw,canonical",
        [("APIs", "rest api"), ("REST", "rest api"), ("Node.js", "node"),
         ("sklearn", "scikit-learn"), ("AI", "artificial intelligence"),
         ("OOP", "object oriented programming"), ("python", "python")],
    )
    def test_aliases(self, raw, canonical):
        assert canonicalize_skill(raw) == canonical


class TestResumeToText:
    def test_flattens_nested_structures(self):
        r = {"a": "x", "b": ["y", {"c": "z"}], "d": None}
        out = resume_to_text(r)
        assert "x" in out and "y" in out and "z" in out

    def test_none_and_string(self):
        assert resume_to_text(None) == ""
        assert resume_to_text("abc") == "abc"

    def test_non_string_scalar(self):
        assert resume_to_text(42) == "42"


class TestExtractSkills:
    def test_known_skills_found(self):
        assert {"python", "docker"} <= extract_known_skills("Python and Docker")

    def test_cplusplus_not_confused_with_c(self):
        found = extract_known_skills("We need c++")
        assert "c++" in found and "c" not in found

    def test_canonical_merges_aliases(self):
        assert extract_canonical_skills("REST APIs and APIs") == {"rest api"}

    def test_unknown_words_ignored(self):
        assert extract_known_skills("bake bread") == set()


class TestMeaningfulWords:
    def test_stop_words_removed(self):
        w = extract_meaningful_words("the python and the team")
        assert w == {"python"}

    def test_short_words_removed(self):
        assert "go" not in extract_meaningful_words("go to it")


class TestKeywordInResume:
    def test_direct_hit(self):
        assert keyword_in_resume("python", "I use Python daily")

    def test_alias_hit(self):
        assert keyword_in_resume("rest api", "built RESTful APIs")

    def test_miss(self):
        assert not keyword_in_resume("docker", "I use Python")

    def test_dsa_needs_both_parts(self):
        assert keyword_in_resume(
            "data structures and algorithms", "Data Structures, Algorithms")
        assert not keyword_in_resume(
            "data structures and algorithms", "Data Structures only")

    def test_whole_word_boundaries(self):
        assert not keyword_in_resume("java", "javascript")


class TestMatchResumeToJD:
    RESUME = {"skills": ["Python", "React"]}

    def test_empty_jd(self):
        r = match_resume_to_jd(self.RESUME, "   ")
        assert r["jd_match_score"] == 0
        assert r["total_jd_keywords"] == 0

    def test_partial_match_score(self):
        r = match_resume_to_jd(
            self.RESUME, "Python, React, Docker and REST APIs")
        assert r["jd_match_score"] == 50
        assert r["matched_keywords"] == ["python", "react"]
        assert r["missing_keywords"] == ["docker", "rest api"]
        assert r["total_jd_keywords"] == 4

    def test_full_match_is_100_and_strong_message(self):
        r = match_resume_to_jd(self.RESUME, "Python and React")
        assert r["jd_match_score"] == 100
        assert any("strong" in x for x in r["recommendations"])

    def test_zero_match_low_message(self):
        r = match_resume_to_jd(self.RESUME, "Docker Kubernetes AWS")
        assert r["jd_match_score"] == 0
        assert any("low keyword match" in x for x in r["recommendations"])

    def test_moderate_message(self):
        r = match_resume_to_jd(self.RESUME, "Python and Docker")
        assert r["jd_match_score"] == 50
        assert any("moderate" in x for x in r["recommendations"])

    def test_jd_without_known_skills(self):
        r = match_resume_to_jd(self.RESUME, "We bake bread")
        assert r["jd_match_score"] == 0
        assert r["total_jd_keywords"] == 0

    def test_missing_keyword_recommendation_capped_at_8(self):
        jd = "java go rust php kotlin swift angular vue docker kubernetes"
        r = match_resume_to_jd({"skills": []}, jd)
        text = r["recommendations"][0]
        assert text.count(",") == 7
