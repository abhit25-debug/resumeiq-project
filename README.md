# ResumeIQ – AI-Powered Resume Analyser & Career Insights

ResumeIQ is an AI-powered resume analysis platform designed to help job seekers understand how their resume performs against ATS (Applicant Tracking Systems) and specific job descriptions.

## Project Overview

Users can upload a PDF/DOCX resume and receive resume-analysis insights such as an ATS compatibility score, extracted skills, formatting issues, job-description matching, missing keywords, and improvement suggestions. The project also includes resume history and version-comparison functionality in the current frontend prototype.

## Core Goals

- Resume upload and parsing
- ATS compatibility scoring
- Resume formatting checks
- Skill extraction and gap analysis
- Job-description matching
- Keyword optimization suggestions
- Analysis history and resume-version comparison
- Authentication and personalization
- Administrative review and analytics

## Technology Stack

### Frontend
- React
- Vite
- JavaScript
- CSS

### Backend
- Python
- FastAPI
- spaCy / NLP-based resume processing
- PostgreSQL planned for persistent storage

### Development & Deployment
- Git / GitHub
- Docker / Docker Compose planned for local orchestration
- Vercel for frontend deployment (planned)
- Render or Railway for backend/database deployment (planned)

## Repository Structure

```text
resumeiq-project/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   └── services/
│   ├── uploads/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── docs/
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 25 User Stories

The following 25 user stories are tracked as GitHub Issues and form the project's functional backlog.

| ID | User Story | Actor | Category |
|---|---|---|---|
| US-01 | Upload a resume file (PDF/DOCX) | Learner | Upload |
| US-02 | Parse resume into structured sections | System | Parsing |
| US-03 | View overall ATS compatibility score | Learner | Scoring |
| US-04 | See flagged formatting issues (tables, images, columns) | Learner | Scoring |
| US-05 | See extracted skills list | Learner | Parsing |
| US-06 | See contact-info completeness check | Learner | Parsing |
| US-07 | See work experience duration summary | Learner | Parsing |
| US-08 | Paste or upload a target job description (JD) | Learner | Matching |
| US-09 | View match percentage between resume and JD | Learner | Matching |
| US-10 | View missing keywords compared to JD | Learner | Matching |
| US-11 | Get suggestions to improve keyword match | Learner | Suggestions |
| US-12 | View an overall improvement suggestions summary | Learner | Suggestions |
| US-13 | View section-wise score breakdown | Learner | Scoring |
| US-14 | Save an analysis result to history | Learner | Dashboard |
| US-15 | View history of past resume analyses | Learner | Dashboard |
| US-16 | Compare scores between two resume versions | Learner | Dashboard |
| US-17 | Delete a saved resume/analysis | Learner | Dashboard |
| US-18 | Download the analysis report as PDF | Learner | Reporting |
| US-19 | Sign up / log in with email | Learner | Auth |
| US-20 | Log in with Google | Learner | Auth |
| US-21 | Reset a forgotten password | Learner | Auth |
| US-22 | Select a target industry/role for tailored analysis | Learner | Personalization |
| US-23 | Admin reviews flagged/low-quality parses | Admin | Admin Operations |
| US-24 | Admin updates the skills/keyword dictionary | Admin | Admin Operations |
| US-25 | Admin views platform usage analytics | Admin | Admin Operations |

## Current Development Status

The repository currently contains the React/Vite frontend prototype, FastAPI backend structure, resume-analysis services, JD matching service, and the GitHub issue backlog. Some planned requirements are intentionally left for subsequent development iterations.

## Development Workflow

The project follows a GitHub Flow-style workflow:

- `main` is the stable branch.
- New work can be developed on `feature/<short-description>` branches.
- Changes should be committed with clear messages.
- Completed features can be merged into `main` through pull requests.

## Planned Next Steps

1. Complete and verify backend dependencies and configuration.
2. Test the complete resume-upload → parsing → ATS-analysis → JD-matching flow.
3. Add persistent database-backed analysis history.
4. Implement authentication and profile persistence.
5. Add PDF report generation.
6. Complete remaining admin and personalization features.
7. Finalize Docker and deployment configuration.

## Project Vision

ResumeIQ aims to become a simple, free tool that helps job seekers understand their resume performance against ATS systems and target roles, while providing a clear and actionable checklist for improvement.
