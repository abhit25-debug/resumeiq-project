const API_BASE_URL = "http://localhost:8000";

export async function uploadResume(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/resumes/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to upload resume");
  }

  return response.json();
}

export async function matchResumeToJD(resume, jobDescription) {
  const response = await fetch(`${API_BASE_URL}/analysis/jd-match`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      resume,
      job_description: jobDescription,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Failed to analyze job description");
  }

  return response.json();
}