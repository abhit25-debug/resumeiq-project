# ResumeIQ – Live Demonstration Script (DA-3)

**Suggested duration:** 4–6 minutes  
**Repository:** https://github.com/abhit25-debug/resumeiq-project

## 1. Start the application

Open two terminals from the repository root.

**Terminal 1 – backend**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs` to show the FastAPI Swagger/OpenAPI interface and the available endpoints.

**Terminal 2 – frontend**
```powershell
cd frontend
npm run dev
```

Open the local Vite URL printed in the terminal, normally `http://localhost:5173`.

## 2. Demonstrate the main user flow

1. **Dashboard:** briefly introduce the dashboard and its summary cards.
2. **New Analysis:** open the analysis page and choose a text-based PDF resume. Explain that PDF and DOCX are supported and the upload limit is 10 MB.
3. **Job description:** paste a short target job description into the JD field.
4. **Analyze:** start the analysis and show the ATS compatibility score, JD match percentage, matched keywords, missing keywords, and improvement suggestions.
5. **DOCX support:** optionally repeat with a DOCX resume without a job description to show that ATS analysis can run independently.
6. **History and comparison:** open History, then Compare, and explain that the current prototype keeps analysis history in the browser session and compares the latest analyses.
7. **Input validation:** demonstrate the no-file validation message. If time permits, use the API docs to show invalid file-type or empty-JD responses.

## 3. Demonstrate testing and build evidence

From the `backend/` directory with the virtual environment activated:

```powershell
python -m pytest tests -v
python -m pytest tests --cov=app --cov-report=term-missing
```

For mutation results, if they have already been generated:

```powershell
python -m mutmut results
```

From the `frontend/` directory:

```powershell
npm run build
npm run lint
```

The submitted DA-3 evidence records **412 passed, 1 expected failure, and 1 warning**, with 99% line coverage. Mutation testing improved from 72.4% to 92.5% after adding targeted tests. Present these as the recorded results from the test run, and rerun the commands if you need to confirm the current environment.

## 4. Explain the design briefly

- **Frontend:** React + Vite.
- **Backend:** FastAPI REST API.
- **Parsing:** pypdf and python-docx extract resume text; parser rules and a controlled skill vocabulary structure the information.
- **Scoring:** the ATS analyser produces an explainable score and suggestions.
- **JD matching:** the matcher compares canonicalized skills/keywords and lists matches and gaps.
- **Testing/version management:** pytest covers unit, integration and regression behaviour; mutmut measures test-suite strength; Git/GitHub tracks code and design artifacts.

## 5. State limitations honestly

- Analysis history is session-only and is lost on refresh; persistent database storage is planned.
- Authentication, PDF report download, admin functions, and some advanced resume checks are planned rather than implemented.
- The test suite documents DEF-01: the parser may report `C` when a resume contains `C++`. It is an expected-failure test, not a fixed defect.

## Closing

“ResumeIQ helps job seekers understand their resume’s ATS-style score, identify job-description keyword gaps, and receive actionable improvement suggestions. The current prototype demonstrates the core analysis workflow, while the report documents the testing evidence and remaining planned features.”
