from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.jd_matcher import match_resume_to_jd


router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)


class JDMatchRequest(BaseModel):
    resume: dict
    job_description: str


@router.post("/jd-match")
async def jd_match(request: JDMatchRequest):
    """
    Match a parsed resume against a job description.
    """

    if not request.job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty.",
        )

    result = match_resume_to_jd(
        request.resume,
        request.job_description,
    )

    return result