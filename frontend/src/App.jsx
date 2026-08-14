import { useState, useRef } from "react";
import "./App.css";
import { uploadResume, matchResumeToJD } from "./api";


function App() {
  const [page, setPage] = useState("dashboard");

  // Latest analysis result
  const [analysisResult, setAnalysisResult] = useState(null);

  // Number of resumes analyzed
  const [analysisCount, setAnalysisCount] = useState(0);

  // Store all analyses during the current session
  const [analysisHistory, setAnalysisHistory] = useState([]);


  const navItems = [
    {
      id: "dashboard",
      label: "Dashboard",
      icon: "⌂",
    },
    {
      id: "analysis",
      label: "New Analysis",
      icon: "＋",
    },
    {
      id: "history",
      label: "History",
      icon: "◷",
    },
    {
      id: "compare",
      label: "Compare",
      icon: "⇄",
    },
    {
      id: "profile",
      label: "Profile",
      icon: "○",
    },
  ];


  return (
    <div className="app">

      {/* =========================
          SIDEBAR
      ========================== */}

      <aside className="sidebar">

        <div className="brand">

          <div className="brand-logo">
            R
          </div>

          <div>
            <h2>ResumeIQ</h2>
            <span>AI Resume Analyzer</span>
          </div>

        </div>


        <nav>

          {navItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${
                page === item.id ? "active" : ""
              }`}
              onClick={() => setPage(item.id)}
            >

              <span className="nav-icon">
                {item.icon}
              </span>

              {item.label}

            </button>
          ))}

        </nav>


        <div className="sidebar-bottom">

          <div className="tips">

            <strong>
              💡 Resume Tip
            </strong>

            <p>
              Use measurable achievements instead of generic
              responsibilities.
            </p>

          </div>


          <button className="logout">
            ↪ Logout
          </button>

        </div>

      </aside>


      {/* =========================
          MAIN CONTENT
      ========================== */}

      <main className="main">

        {/* TOP BAR */}

        <header className="topbar">

          <div>

            <p className="eyebrow">
              AI-powered career insights
            </p>

            <h1>
              Welcome back, <span>Abhinav</span> 👋
            </h1>

          </div>


          <div className="profile">

            <div className="avatar">
              AS
            </div>

            <div>

              <strong>
                Abhinav Singh
              </strong>

              <small>
                Student
              </small>

            </div>

          </div>

        </header>


        {/* =========================
            PAGES
        ========================== */}

        {page === "dashboard" && (
          <Dashboard
            setPage={setPage}
            analysisResult={analysisResult}
            analysisCount={analysisCount}
            analysisHistory={analysisHistory}
          />
        )}


        {page === "analysis" && (
          <Analysis
            analysisResult={analysisResult}
            setAnalysisResult={setAnalysisResult}
            setAnalysisCount={setAnalysisCount}
            setAnalysisHistory={setAnalysisHistory}
            setPage={setPage}
          />
        )}


        {page === "history" && (
          <History
            analysisHistory={analysisHistory}
          />
        )}


        {page === "compare" && (
          <Compare
            analysisHistory={analysisHistory}
          />
        )}


        {page === "profile" && (
          <Profile />
        )}

      </main>

    </div>
  );
}


/* =====================================================
   DASHBOARD
===================================================== */

function Dashboard({
  setPage,
  analysisResult,
  analysisCount,
  analysisHistory,
}) {

  /*
   * Latest ATS score
   */

  const latestAtsScore =
    analysisResult?.ats_analysis?.ats_score ??
    analysisResult?.ats_score ??
    0;


  /*
   * Latest JD score
   */

  const latestJdScore =
    analysisResult?.jd_match_score ??
    analysisResult?.ats_analysis?.jd_match_score ??
    0;


  /*
   * Best ATS score from all analyzed resumes
   */

  const bestAtsScore =
    analysisHistory.length > 0
      ? Math.max(
          ...analysisHistory.map(
            (item) => item.atsScore
          )
        )
      : 0;


  /*
   * Number of suggestions / improvements
   */

  const improvements =
    analysisResult?.ats_analysis?.suggestions?.length ??
    analysisResult?.ats_analysis?.recommendations?.length ??
    0;


  return (
    <>

      {/* =========================
          HERO
      ========================== */}

      <section className="hero">

        <div>

          <p className="hero-label">
            RESUME HEALTH CHECK
          </p>

          <h2>
            Make your resume
            <br />
            ready for the next opportunity.
          </h2>

          <p>
            Upload your resume and ResumeIQ will analyze its
            ATS compatibility, skills, formatting, and
            job-description match.
          </p>

          <button
            className="primary-btn"
            onClick={() => setPage("analysis")}
          >
            Analyze a Resume →
          </button>

        </div>


        <div className="score-preview">

          <div className="score-circle">

            <strong>
              {analysisResult
                ? latestAtsScore
                : "—"}
            </strong>

            <span>
              ATS Score
            </span>

          </div>


          <p>
            {analysisResult
              ? "Your latest resume analysis."
              : "Analyze a resume to see your score."}
          </p>

        </div>

      </section>


      {/* =========================
          STATISTICS
      ========================== */}

      <section className="stats">

        <Stat
          title="Resumes Analyzed"
          value={analysisCount}
        />


        <Stat
          title="Best ATS Score"
          value={
            analysisHistory.length > 0
              ? `${bestAtsScore}%`
              : "—"
          }
        />


        <Stat
          title="JD Match"
          value={
            analysisResult
              ? `${latestJdScore}%`
              : "—"
          }
        />


        <Stat
          title="Improvements"
          value={
            analysisResult
              ? improvements
              : "—"
          }
        />

      </section>


      {/* =========================
          LATEST RESULT
      ========================== */}

      {analysisResult && (

        <section className="card analysis-result-card">

          <div className="card-heading">

            <div>

              <p className="eyebrow">
                LATEST RESULT
              </p>

              <h3>
                {analysisResult.filename}
              </h3>

            </div>


            <span className="score-badge">
              {latestAtsScore}%
            </span>

          </div>


          <p>
            Resume successfully uploaded and analyzed
            by ResumeIQ.
          </p>


          {/* Suggestions */}

          {analysisResult.ats_analysis?.suggestions?.length > 0 && (

            <div>

              <h4>
                Suggestions
              </h4>

              <ul>

                {analysisResult.ats_analysis.suggestions.map(
                  (suggestion, index) => (

                    <li key={index}>
                      {suggestion}
                    </li>

                  )
                )}

              </ul>

            </div>

          )}

        </section>

      )}


      {/* =========================
          CONTENT GRID
      ========================== */}

      <section className="content-grid">


        {/* UPLOAD CARD */}

        <div className="card upload-card">

          <div className="card-heading">

            <div>

              <p className="eyebrow">
                GET STARTED
              </p>

              <h3>
                Analyze your resume
              </h3>

            </div>

            <span className="card-icon">
              ↑
            </span>

          </div>


          <div className="dropzone">

            <div className="upload-icon">
              ↑
            </div>

            <h4>
              Drop your resume here
            </h4>

            <p>
              PDF or DOCX · Maximum 10 MB
            </p>

            <button
              onClick={() => setPage("analysis")}
            >
              Choose File
            </button>

          </div>

        </div>


        {/* RECENT ANALYSES */}

        <div className="card">

          <div className="card-heading">

            <div>

              <p className="eyebrow">
                RECENT
              </p>

              <h3>
                Recent Analyses
              </h3>

            </div>


            <button
              className="text-btn"
              onClick={() => setPage("history")}
            >
              View all →
            </button>

          </div>


          {analysisHistory.length === 0 ? (

            <div className="empty-state">

              <p>
                No resumes analyzed yet.
              </p>

              <button
                className="text-btn"
                onClick={() => setPage("analysis")}
              >
                Analyze your first resume →
              </button>

            </div>

          ) : (

            analysisHistory
              .slice(0, 5)
              .map((item, index) => (

                <RecentFile
                  key={`${item.filename}-${item.timestamp}-${index}`}
                  name={item.filename}
                  score={`${item.atsScore}%`}
                  type={item.fileType}
                />

              ))

          )}

        </div>

      </section>

    </>
  );
}


/* =====================================================
   STAT
===================================================== */

function Stat({
  title,
  value,
}) {

  return (

    <div className="stat-card">

      <span>
        {title}
      </span>

      <strong>
        {value}
      </strong>

    </div>

  );
}


/* =====================================================
   RECENT FILE
===================================================== */

function RecentFile({
  name,
  score,
  type = "pdf",
}) {

  return (

    <div className="recent-file">

      <div className="file-icon">
        {type?.toUpperCase() || "PDF"}
      </div>


      <div className="file-info">

        <strong>
          {name}
        </strong>

        <small>
          Analyzed recently
        </small>

      </div>


      <span className="score-badge">
        {score}
      </span>

    </div>

  );
}


/* =====================================================
   NEW ANALYSIS
===================================================== */

function Analysis({
  analysisResult,
  setAnalysisResult,
  setAnalysisCount,
  setAnalysisHistory,
  setPage,
}) {

  const [file, setFile] = useState(null);

  const [jobDescription, setJobDescription] =
    useState("");

  const [targetRole, setTargetRole] =
    useState("");


  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");


  const fileInputRef =
    useRef(null);


  /* =========================
     FILE SELECTION
  ========================== */

  function handleFileChange(event) {

    const selectedFile =
      event.target.files?.[0];


    if (!selectedFile) {
      return;
    }


    const allowedTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];


    const maxSize =
      10 * 1024 * 1024;


    if (!allowedTypes.includes(selectedFile.type)) {

      setError(
        "Please select a PDF or DOCX file."
      );

      setFile(null);

      return;
    }


    if (selectedFile.size > maxSize) {

      setError(
        "File size must be less than 10 MB."
      );

      setFile(null);

      return;
    }


    setError("");
    setSuccess("");
    setFile(selectedFile);

  }


  /* =========================
     ANALYZE RESUME
  ========================== */

  async function handleAnalyze() {

    if (!file) {

      setError(
        "Please choose a resume first."
      );

      return;
    }


    setLoading(true);
    setError("");
    setSuccess("");


    try {

      /* --------------------------------
         STEP 1: UPLOAD RESUME
      -------------------------------- */

      const resumeResponse =
        await uploadResume(file);


      let finalResult = {
        ...resumeResponse,
      };


      /* --------------------------------
         STEP 2: JOB DESCRIPTION MATCHING
      -------------------------------- */

      if (jobDescription.trim()) {

        const jdResponse =
          await matchResumeToJD(
            resumeResponse.resume,
            jobDescription
          );


        finalResult = {

          ...resumeResponse,

          jd_match_score:
            jdResponse.jd_match_score,

          matched_keywords:
            jdResponse.matched_keywords,

          missing_keywords:
            jdResponse.missing_keywords,

          total_jd_keywords:
            jdResponse.total_jd_keywords,

          jd_recommendations:
            jdResponse.recommendations,

        };

      } else {

        /*
         * No JD was provided.
         * Keep JD score at 0.
         */

        finalResult = {

          ...resumeResponse,

          jd_match_score: 0,

          matched_keywords: [],

          missing_keywords: [],

          total_jd_keywords: 0,

          jd_recommendations: [],

        };

      }


      /* --------------------------------
         STEP 3: SAVE LATEST RESULT
      -------------------------------- */

      setAnalysisResult(finalResult);


      /* --------------------------------
         STEP 4: UPDATE COUNT
      -------------------------------- */

      setAnalysisCount(
        (previous) => previous + 1
      );


      /* --------------------------------
         STEP 5: ADD TO HISTORY
      -------------------------------- */

      const atsScore =
        finalResult?.ats_analysis?.ats_score ??
        finalResult?.ats_score ??
        0;


      const jdScore =
        finalResult?.jd_match_score ??
        0;


      const suggestions =
        finalResult?.ats_analysis?.suggestions ??
        finalResult?.ats_analysis?.recommendations ??
        [];


      const historyItem = {

        filename:
          finalResult.filename ||
          file.name,

        fileType:
          finalResult.file_type ||
          file.name.split(".").pop(),

        atsScore:
          atsScore,

        jdScore:
          jdScore,

        suggestions:
          suggestions,

        targetRole:
          targetRole,

        timestamp:
          Date.now(),

      };


      setAnalysisHistory(
        (previousHistory) => [
          historyItem,
          ...previousHistory,
        ]
      );


      setSuccess(
        "Resume analyzed successfully!"
      );

    } catch (err) {

      console.error(err);


      setError(
        err?.message ||
        "Something went wrong while analyzing the resume."
      );

    } finally {

      setLoading(false);

    }

  }


  return (

    <section>

      {/* =========================
          PAGE HEADING
      ========================== */}

      <div className="page-heading">

        <p className="eyebrow">
          NEW ANALYSIS
        </p>

        <h2>
          Analyze your resume
        </h2>

        <p>
          Upload a PDF or DOCX resume and
          optionally provide a target role.
        </p>

      </div>


      <div className="card large-card">


        {/* =========================
            FILE UPLOAD
        ========================== */}

        <div className="dropzone large-dropzone">

          <div className="upload-icon">
            ↑
          </div>


          <h3>

            {file
              ? file.name
              : "Drag & drop your resume here"}

          </h3>


          <p>

            {file
              ? `${(
                  file.size /
                  1024 /
                  1024
                ).toFixed(2)} MB`
              : "Supported formats: PDF, DOCX"}

          </p>


          <button
            type="button"
            onClick={() =>
              fileInputRef.current?.click()
            }
          >
            Browse File
          </button>


          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileChange}
            style={{
              display: "none",
            }}
          />

        </div>


        {/* =========================
            TARGET ROLE
        ========================== */}

        <label>
          Target role
        </label>


        <input
          className="input"
          value={targetRole}
          onChange={(event) =>
            setTargetRole(
              event.target.value
            )
          }
          placeholder="e.g. Software Engineer, Data Analyst..."
        />


        {/* =========================
            JOB DESCRIPTION
        ========================== */}

        <label>

          Job Description{" "}

          <span>
            (optional)
          </span>

        </label>


        <textarea
          className="input textarea"
          value={jobDescription}
          onChange={(event) =>
            setJobDescription(
              event.target.value
            )
          }
          placeholder="Paste the target job description here..."
        />


        {/* =========================
            ERROR
        ========================== */}

        {error && (

          <div className="error-message">
            {error}
          </div>

        )}


        {/* =========================
            SUCCESS
        ========================== */}

        {success && (

          <div className="success-message">
            {success}
          </div>

        )}


        {/* =========================
            ANALYZE BUTTON
        ========================== */}

        <button
          className="primary-btn full"
          onClick={handleAnalyze}
          disabled={loading}
        >

          {loading
            ? "Analyzing..."
            : "Analyze Resume"}

        </button>


        {/* =========================
            RESULT
        ========================== */}

        {analysisResult && (

          <div className="analysis-summary">

            <h3>
              Analysis Complete
            </h3>


            {/* ATS */}

            <p>

              ATS Score:{" "}

              <strong>

                {analysisResult
                  .ats_analysis
                  ?.ats_score ??
                  analysisResult
                  ?.ats_score ??
                  "N/A"}

                %

              </strong>

            </p>


            {/* JD MATCH */}

            {analysisResult.jd_match_score !==
              undefined && (

              <p>

                JD Match:{" "}

                <strong>
                  {analysisResult.jd_match_score}%
                </strong>

              </p>

            )}


            {/* MATCHED KEYWORDS */}

            {analysisResult.matched_keywords?.length >
              0 && (

              <div>

                <h4>
                  Matched Keywords
                </h4>

                <p>
                  {analysisResult.matched_keywords.join(
                    ", "
                  )}
                </p>

              </div>

            )}


            {/* MISSING KEYWORDS */}

            {analysisResult.missing_keywords?.length >
              0 && (

              <div>

                <h4>
                  Missing Keywords
                </h4>

                <p>
                  {analysisResult.missing_keywords.join(
                    ", "
                  )}
                </p>

              </div>

            )}


            {/* RECOMMENDATIONS */}

            {analysisResult.jd_recommendations
              ?.length > 0 && (

              <div>

                <h4>
                  JD Recommendations
                </h4>

                <ul>

                  {analysisResult.jd_recommendations.map(
                    (recommendation, index) => (

                      <li key={index}>
                        {recommendation}
                      </li>

                    )
                  )}

                </ul>

              </div>

            )}


            <button
              className="text-btn"
              onClick={() =>
                setPage("dashboard")
              }
            >
              View Dashboard →
            </button>

          </div>

        )}

      </div>

    </section>

  );
}


/* =====================================================
   HISTORY
===================================================== */

function History({
  analysisHistory,
}) {

  return (

    <section>

      <div className="page-heading">

        <p className="eyebrow">
          YOUR RESUMES
        </p>

        <h2>
          Analysis History
        </h2>

        <p>
          Track how your resume improves over time.
        </p>

      </div>


      <div className="card">

        {analysisHistory.length === 0 ? (

          <div className="empty-state">

            <h3>
              No analysis history yet
            </h3>

            <p>
              Analyze your first resume to see
              your results here.
            </p>

          </div>

        ) : (

          analysisHistory.map(
            (item, index) => (

              <div
                key={`${item.filename}-${item.timestamp}-${index}`}
              >

                <RecentFile
                  name={item.filename}
                  score={`${item.atsScore}%`}
                  type={item.fileType}
                />


                <div
                  style={{
                    padding:
                      "0 0 16px 0",
                    fontSize:
                      "14px",
                    color:
                      "#777",
                  }}
                >

                  JD Match:{" "}

                  <strong>
                    {item.jdScore}%
                  </strong>

                  {item.targetRole && (
                    <>
                      {" "}· Target Role:{" "}
                      <strong>
                        {item.targetRole}
                      </strong>
                    </>
                  )}

                </div>

              </div>

            )
          )

        )}

      </div>

    </section>

  );
}


/* =====================================================
   COMPARE
===================================================== */

function Compare({
  analysisHistory,
}) {

  /*
   * Need at least 2 resumes to compare
   */

  if (analysisHistory.length < 2) {

    return (

      <section>

        <div className="page-heading">

          <p className="eyebrow">
            VERSION COMPARISON
          </p>

          <h2>
            Compare Resume Versions
          </h2>

          <p>
            Analyze at least two resumes to
            compare their performance.
          </p>

        </div>


        <div className="card">

          <h3>
            Not enough resumes
          </h3>

          <p>
            You currently have{" "}
            {analysisHistory.length}{" "}
            analyzed resume
            {analysisHistory.length === 1
              ? ""
              : "s"}.
          </p>

          <p>
            Analyze another resume to
            enable comparison.
          </p>

        </div>

      </section>

    );
  }


  /*
   * Latest two analyses
   */

  const latest =
    analysisHistory[0];

  const previous =
    analysisHistory[1];


  const difference =
    latest.atsScore -
    previous.atsScore;


  return (

    <section>

      <div className="page-heading">

        <p className="eyebrow">
          VERSION COMPARISON
        </p>

        <h2>
          Compare Resume Versions
        </h2>

        <p>
          See whether your resume improvements
          are actually working.
        </p>

      </div>


      <div className="compare-grid">


        {/* PREVIOUS */}

        <div className="card">

          <span>
            Previous Version
          </span>

          <h3>
            {previous.atsScore}%
          </h3>

          <p>
            {previous.filename}
          </p>

          <small>
            JD Match: {previous.jdScore}%
          </small>

        </div>


        {/* ARROW */}

        <div className="compare-arrow">
          →
        </div>


        {/* LATEST */}

        <div className="card">

          <span>
            Latest Version
          </span>

          <h3 className="success">
            {latest.atsScore}%
          </h3>

          <p>
            {latest.filename}
          </p>

          <small>
            JD Match: {latest.jdScore}%
          </small>

        </div>

      </div>


      {/* IMPROVEMENT */}

      <div className="card">

        <h3>
          ATS Score Change
        </h3>

        <p>

          {difference > 0
            ? `Your ATS score improved by ${difference} points.`
            : difference < 0
            ? `Your ATS score decreased by ${Math.abs(
                difference
              )} points.`
            : "Your ATS score stayed the same."}

        </p>

      </div>

    </section>

  );
}


/* =====================================================
   PROFILE
===================================================== */

function Profile() {

  return (

    <section>

      <div className="page-heading">

        <p className="eyebrow">
          ACCOUNT
        </p>

        <h2>
          Your Profile
        </h2>

        <p>
          Manage your ResumeIQ preferences.
        </p>

      </div>


      <div className="card profile-card">

        <div className="big-avatar">
          AS
        </div>


        <h3>
          Abhinav Singh
        </h3>


        <p>
          24BRS1404
        </p>


        <label>
          Target Role
        </label>


        <input
          className="input"
          placeholder="Software Engineer"
        />


        <button className="primary-btn">
          Save Changes
        </button>

      </div>

    </section>

  );
}


export default App;