"""Regression tests - golden values captured from verified runs.

If any of these fail after a code change, scoring behaviour has changed
and the change must be reviewed deliberately (and the golden value
updated only if the change is intended).
"""
import pytest

pytestmark = pytest.mark.regression

GOLDEN = {
    "sample_pdf_resume_a.pdf": dict(
        file_type="pdf", score=86, name="ABHINAV SINGH",
        email="abhinavakhil25@gmail.com", skill_count=22,
        breakdown={"contact": 100, "sections": 60, "skills": 100, "content": 90}),
    "sample_pdf_resume_b.pdf": dict(
        file_type="pdf", score=94, name="DEVANSH KALWANI",
        email="devanshkalwani2010@gmail.com", skill_count=24,
        breakdown={"contact": 100, "sections": 80, "skills": 100, "content": 100}),
    "sample_docx_resume.docx": dict(
        file_type="docx", score=75, name="ABHINAV SINGH",
        email=None, skill_count=20,
        breakdown={"contact": 53, "sections": 60, "skills": 100, "content": 80}),
}


@pytest.fixture(params=sorted(GOLDEN))
def result(request, client, fixtures_dir):
    name = request.param
    with open(fixtures_dir / name, "rb") as fh:
        body = client.post("/resumes/upload", files={"file": (name, fh)}).json()
    return GOLDEN[name], body


def test_ats_score_unchanged(result):
    expected, body = result
    assert body["ats_analysis"]["ats_score"] == expected["score"]


def test_ats_breakdown_unchanged(result):
    expected, body = result
    assert body["ats_analysis"]["breakdown"] == expected["breakdown"]


def test_contact_extraction_unchanged(result):
    expected, body = result
    assert body["resume"]["contact"]["name"] == expected["name"]
    assert body["resume"]["contact"]["email"] == expected["email"]


def test_skill_count_unchanged(result):
    expected, body = result
    assert len(body["resume"]["skills"]) == expected["skill_count"]


def test_file_type_unchanged(result):
    expected, body = result
    assert body["file_type"] == expected["file_type"]


# ---- Known tricky cases that must keep working (edge-case regressions) ----

def test_c_is_not_matched_inside_other_words():
    from app.services.resume_parser import extract_skills
    assert "C" not in extract_skills("Cooperation and Machine")


def test_cpp_special_characters_escaped():
    from app.services.resume_parser import extract_skills
    assert "C++" in extract_skills("Proficient in C++")


def test_api_aliases_collapse_to_one_keyword():
    from app.services.jd_matcher import extract_canonical_skills
    assert extract_canonical_skills("api APIs REST rest api REST APIs") == {"rest api"}


def test_dsa_recognised_when_split_in_resume():
    from app.services.jd_matcher import keyword_in_resume
    assert keyword_in_resume("data structures and algorithms",
                             "Skills: Data Structures, Algorithms")


def test_scores_never_exceed_100(client, fixtures_dir):
    for name in GOLDEN:
        with open(fixtures_dir / name, "rb") as fh:
            s = client.post("/resumes/upload",
                            files={"file": (name, fh)}).json()["ats_analysis"]
        assert 0 <= s["ats_score"] <= 100
