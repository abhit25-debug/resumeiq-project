"""Integration tests - HTTP API (router + parser + ATS analyzer + JD matcher)."""
import pytest

pytestmark = pytest.mark.integration


def _upload(client, path, name=None):
    with open(path, "rb") as fh:
        return client.post(
            "/resumes/upload", files={"file": (name or path.name, fh)})


class TestSystemEndpoints:
    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json() == {"message": "Welcome to ResumeIQ API", "status": "running"}

    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    def test_openapi_lists_all_routes(self, client):
        paths = client.get("/openapi.json").json()["paths"]
        assert "/resumes/upload" in paths
        assert "/analysis/jd-match" in paths

    def test_cors_allows_frontend_origin(self, client):
        r = client.options(
            "/resumes/upload",
            headers={"Origin": "http://localhost:5173",
                     "Access-Control-Request-Method": "POST"})
        assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"


class TestUploadPipeline:
    def test_pdf_upload_runs_full_pipeline(self, client, fixtures_dir):
        r = _upload(client, fixtures_dir / "sample_pdf_resume_a.pdf")
        assert r.status_code == 200
        body = r.json()
        assert body["file_type"] == "pdf"
        assert body["text_length"] > 0
        assert body["resume"]["contact"]["email"]
        assert body["resume"]["skills"]
        assert 0 <= body["ats_analysis"]["ats_score"] <= 100

    def test_docx_upload_runs_full_pipeline(self, client, fixtures_dir):
        r = _upload(client, fixtures_dir / "sample_docx_resume.docx")
        assert r.status_code == 200
        assert r.json()["file_type"] == "docx"

    def test_uploaded_file_is_saved_to_storage(self, client, fixtures_dir, tmp_path):
        _upload(client, fixtures_dir / "sample_pdf_resume_a.pdf")
        assert (tmp_path / "sample_pdf_resume_a.pdf").exists()

    def test_path_traversal_filename_is_neutralised(self, client, fixtures_dir, tmp_path):
        r = _upload(client, fixtures_dir / "sample_pdf_resume_a.pdf",
                    name="../../evil.pdf")
        assert r.status_code == 200
        assert r.json()["filename"] == "evil.pdf"
        assert (tmp_path / "evil.pdf").exists()

    def test_response_contains_parser_and_ats_output(self, client, fixtures_dir):
        body = _upload(client, fixtures_dir / "sample_pdf_resume_b.pdf").json()
        assert set(body["resume"]) == {
            "contact", "summary", "education", "experience", "skills", "projects"}
        assert set(body["ats_analysis"]) == {"ats_score", "breakdown", "suggestions"}


class TestUploadValidation:
    def test_unsupported_extension_rejected(self, client):
        r = client.post("/resumes/upload", files={"file": ("a.txt", b"hello")})
        assert r.status_code == 400
        assert "PDF and DOCX" in r.json()["detail"]

    def test_file_over_10mb_rejected(self, client):
        big = b"0" * (10 * 1024 * 1024 + 1)
        r = client.post("/resumes/upload", files={"file": ("big.pdf", big)})
        assert r.status_code == 400
        assert "10 MB" in r.json()["detail"]

    def test_missing_file_field_rejected(self, client):
        assert client.post("/resumes/upload").status_code == 422

    def test_image_only_docx_has_no_text(self, client, tmp_path):
        from docx import Document
        p = tmp_path / "empty.docx"
        Document().save(p)
        r = _upload(client, p)
        assert r.status_code == 400
        assert "Could not extract" in r.json()["detail"]


class TestJDMatchEndpoint:
    RESUME = {"skills": ["Python", "React"], "projects": "Built REST APIs"}

    def test_jd_match_success(self, client):
        r = client.post("/analysis/jd-match", json={
            "resume": self.RESUME,
            "job_description": "Python, React and Docker"})
        assert r.status_code == 200
        assert r.json()["jd_match_score"] == 67
        assert r.json()["missing_keywords"] == ["docker"]

    def test_empty_jd_is_400(self, client):
        r = client.post("/analysis/jd-match", json={
            "resume": self.RESUME, "job_description": "   "})
        assert r.status_code == 400
        assert "cannot be empty" in r.json()["detail"]

    def test_missing_body_fields_is_422(self, client):
        assert client.post("/analysis/jd-match", json={}).status_code == 422


class TestEndToEndFlow:
    """Mirrors what the React frontend does: upload, then JD-match."""

    def test_upload_then_jd_match(self, client, fixtures_dir):
        up = _upload(client, fixtures_dir / "sample_pdf_resume_a.pdf").json()
        jd = client.post("/analysis/jd-match", json={
            "resume": up["resume"],
            "job_description": "Looking for Python, React, Docker, SQL and AWS"})
        assert jd.status_code == 200
        body = jd.json()
        assert body["total_jd_keywords"] == 5
        assert "aws" in body["missing_keywords"]
        assert {"python", "react", "docker", "sql"} <= set(body["matched_keywords"])
        assert body["jd_match_score"] == 80
