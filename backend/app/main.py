from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import resumes
from app.routers import analysis

app = FastAPI(
    title="ResumeIQ API",
    description="AI-powered Resume Analyzer and Career Insights API",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(resumes.router)
app.include_router(analysis.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to ResumeIQ API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ResumeIQ Backend",
    }