import os
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from authlib.integrations.flask_client import OAuth
from flask import Flask, request, jsonify, render_template, flash
from flask import send_file, session, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from uuid import uuid4

from pdf_generator import generate_pdf
from resume_builder import validate_form_data, format_resume_data, build_parsed_data, refine_for_ats, generate_resume_pdf
from resume_parser import parse_resume
from skill_matcher import match_skills
from role_predictor import predict_role
from ats_scorer import calculate_ats_score
from career_recommender import recommend_career
from database import connect_db, create_users_table
from database import create_analysis_table
from jd_matcher import match_jd
from email_sender import send_email
from resume_insights import analyze_resume_insights
from resume_suggestions import generate_suggestions
from multi_role_predictor import predict_multiple_roles
from compare_pdf_generator import generate_comparison_pdf


# ── Flask App ──
app = Flask(__name__)

# ProxyFix: trust X-Forwarded-* headers from reverse proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# SECRET_KEY: require from env in production, fallback only for local dev
_env = os.getenv("FLASK_ENV", "development")
if _env == "production" and not os.getenv("SECRET_KEY"):
    raise RuntimeError("SECRET_KEY must be set in production!")
app.secret_key = os.getenv("SECRET_KEY", "dev-fallback-key-change-me")

# ── Session Security ──
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
if _env == "production":
    app.config["SESSION_COOKIE_SECURE"] = True

# ── CSRF Protection ──
csrf = CSRFProtect(app)

# ── Logging ──
os.makedirs("logs", exist_ok=True)

file_handler = RotatingFileHandler(
    "logs/app.log", maxBytes=5_000_000, backupCount=5
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
))

error_handler = RotatingFileHandler(
    "logs/error.log", maxBytes=5_000_000, backupCount=3
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s\n%(pathname)s:%(lineno)d"
))

app.logger.addHandler(file_handler)
app.logger.addHandler(error_handler)
app.logger.setLevel(logging.INFO)
app.logger.info("Nexus CV starting up...")

# ── Rate Limiting ──
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://"
)



oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

microsoft = oauth.register(
    name='microsoft',
    client_id=os.getenv("MICROSOFT_CLIENT_ID"),
    client_secret=os.getenv("MICROSOFT_CLIENT_SECRET"),
    authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
    api_base_url='https://graph.microsoft.com/v1.0/',
    client_kwargs={'scope': 'User.Read'},
)

UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "reports"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["REPORT_FOLDER"] = REPORT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# ── Initialize database tables (once) ──
create_users_table()
create_analysis_table()

# ------------------------
# WEBSITE ROUTES
# ------------------------

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/upload-page", methods=["GET"])
def upload_page():
    if "user" not in session:
        return redirect("/login")
    return render_template("upload.html")

@app.route("/analyze", methods=["POST"])
@limiter.limit("10/minute")
def analyze():
    if "user" not in session:
        return redirect("/login")
    
    file = request.files["resume"]
    path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(path)

    parsed_data = parse_resume(path)
    resume_text = parsed_data["text"]
    insights = analyze_resume_insights(resume_text, parsed_data["skills"])
    # MULTI-ROLE PREDICTION
    multi_roles = predict_multiple_roles(parsed_data["skills"])

    primary_role = multi_roles[0]["role"]   # top-ranked role
    role = primary_role
    ats_result = calculate_ats_score(parsed_data, role)
    jd_result = {
        "match_percentage": 0,
        "matched_skills": [],
        "missing_keywords": []
    }
    job_description = request.form.get("job_description", None)
    if job_description:
        jd_result = match_jd(parsed_data["skills"], job_description)

    career = recommend_career(ats_result, role, parsed_data["skills"], insights=insights, jd_result=jd_result)

    suggestions = generate_suggestions(insights, ats_result["missing_skills"], jd_result)
    pdf_filename = f"analysis_{session['user']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex}.pdf"
    pdf_path = os.path.join(app.config["REPORT_FOLDER"], pdf_filename)

    generate_pdf(
        {
            "role": role,
            "ats_score": ats_result["ats_score"],
            "matched_skills": ats_result["matched_skills"],
            "missing_skills": ats_result["missing_skills"],
            "missing_classified": ats_result["missing_classified"],
            "roadmap": career.get("roadmap", {}),
            "ats_breakdown": {
                "skill_score": ats_result["skill_score"],
                "keyword_score": ats_result["keyword_score"],
                "completeness_score": ats_result["completeness_score"]
            },
            "jd_result": jd_result,
            "insights": insights,
            "suggestions": suggestions
        },
        pdf_path
    )

    send_email(session["email"], pdf_path)
    session["last_pdf"] = pdf_path

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO analysis (username, role, ats_score, date, pdf_path) VALUES (?, ?, ?, ?, ?)",
        (
            session["user"],
            role,
            ats_result["ats_score"],
            datetime.now().strftime("%d-%m-%Y %H:%M"),
            pdf_path
        )
    )

    conn.commit()
    conn.close()

    session["last_result"] = {
        "role": role,
        "roles": multi_roles,
        "ats_score": ats_result["ats_score"],
        "matched_skills": ats_result["matched_skills"],
        "missing_skills": ats_result["missing_skills"],
        "missing_classified": ats_result["missing_classified"],
        "roadmap": career.get("roadmap", {}),
        "ats_breakdown": {
            "skill_score": ats_result["skill_score"],
            "keyword_score": ats_result["keyword_score"],
            "completeness_score": ats_result["completeness_score"]
        }
    }

    return render_template(
        "result.html",
        role=role,
        roles=multi_roles,
        ats_score=ats_result["ats_score"],
        matched_skills=ats_result["matched_skills"],
        missing_skills=ats_result["missing_skills"],
        missing_classified=ats_result["missing_classified"],
        roadmap=career.get("roadmap", {}),
        jd_result=jd_result,
        insights=insights,
        suggestions=suggestions,
        ats_breakdown={
            "skill": ats_result["skill_score"],
            "keyword": ats_result["keyword_score"],
            "completeness": ats_result["completeness_score"]
        }
    )

@app.route("/compare-analyze", methods=["POST"])
@limiter.limit("5/minute")
def compare_analyze():
    if "user" not in session:
        return redirect("/login")

    resume1 = request.files.get("resume_v1")
    resume2 = request.files.get("resume_v2")

    if not resume1 or not resume2:
        return redirect("/compare-resume")

    from uuid import uuid4

    path1 = os.path.join(
        app.config["UPLOAD_FOLDER"],
        f"v1_{uuid4().hex}_{resume1.filename}"
    )
    path2 = os.path.join(
        app.config["UPLOAD_FOLDER"],
        f"v2_{uuid4().hex}_{resume2.filename}"
    )

    resume1.save(path1)
    resume2.save(path2)

    parsed1 = parse_resume(path1)
    parsed2 = parse_resume(path2)

    role = predict_multiple_roles(parsed2["skills"])[0]["role"]

    ats1 = calculate_ats_score(parsed1, role)
    ats2 = calculate_ats_score(parsed2, role)

    job_description = request.form.get("job_description")
    jd1 = jd2 = None

    if job_description:
        jd1 = match_jd(parsed1["skills"], job_description)
        jd2 = match_jd(parsed2["skills"], job_description)

    skills1 = set(s.lower() for s in parsed1["skills"])
    skills2 = set(s.lower() for s in parsed2["skills"])

    # Build AI summary based on actual diff data
    change = ats2["ats_score"] - ats1["ats_score"]
    added = list(skills2 - skills1)
    removed = list(skills1 - skills2)

    if change > 0:
        ai_summary = (
            f"Your updated resume shows a +{change} point ATS improvement for the {role} role. "
        )
        if added:
            ai_summary += f"Skills gained ({', '.join(added[:4])}) strengthened your profile. "
        if removed:
            ai_summary += f"Note: you removed {', '.join(removed[:3])} — verify these aren't critical for your target role. "
        ai_summary += "Continue optimizing keyword coverage and quantifying achievements."
    elif change < 0:
        ai_summary = (
            f"Your ATS score decreased by {abs(change)} points for the {role} role. "
        )
        if removed:
            ai_summary += f"Removing {', '.join(removed[:3])} likely contributed to the decline. "
        if added:
            ai_summary += f"Despite adding {', '.join(added[:3])}, the net impact was negative. "
        ai_summary += "Consider restoring key role-specific skills and improving keyword density."
    else:
        ai_summary = (
            f"Both resume versions score equally for the {role} role. "
        )
        if added and removed:
            ai_summary += f"You swapped {', '.join(removed[:2])} for {', '.join(added[:2])}. "
        ai_summary += "Try adding quantified achievements and role-specific keywords to improve."

    comparison = {
        "role": role,
        "ats_before": ats1["ats_score"],
        "ats_after": ats2["ats_score"],
        "ats_change": change,
        "skills_added": added,
        "skills_removed": removed,
        "jd_before": jd1,
        "jd_after": jd2,
        "ai_summary": ai_summary
    }

    # Generate comparison PDF (always — needed for download)
    cmp_pdf_name = f"compare_{session['user']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex}.pdf"
    cmp_pdf_path = os.path.join(app.config["REPORT_FOLDER"], cmp_pdf_name)
    generate_comparison_pdf(comparison, cmp_pdf_path)
    session["compare_pdf_path"] = cmp_pdf_path

    # Auto-email comparison report
    try:
        change = comparison["ats_change"]
        if change > 0:
            change_msg = f"Your ATS score improved by {change} points."
        elif change < 0:
            change_msg = f"Your ATS score decreased by {abs(change)} points."
        else:
            change_msg = "Your ATS score remained unchanged."

        send_email(
            session["email"],
            cmp_pdf_path,
            subject="Your Resume Comparison Report \u2014 Nexus CV",
            body=(
                f"Hello,\n\n"
                f"Your resume comparison report for the {role} role is attached.\n\n"
                f"ATS Score: {comparison['ats_before']} \u2192 {comparison['ats_after']}\n"
                f"{change_msg}\n\n"
                f"Review the attached PDF for full details on skills added, "
                f"removed, and overall improvement.\n\n"
                f"Best regards,\nNexus CV Team"
            ),
            attachment_name="Resume_Comparison_Report.pdf"
        )
    except Exception as e:
        logging.error(f"Failed to send comparison email: {e}")

    return render_template("compare_result.html", comparison=comparison)


@app.route("/download-compare-report")
def download_compare_report():
    if "compare_pdf_path" not in session:
        return redirect("/")
    return send_file(session["compare_pdf_path"], as_attachment=True)

@app.route("/download-pdf")
def download_pdf():
    if "last_pdf" not in session:
        return redirect("/")

    return send_file(session["last_pdf"], as_attachment=True)


@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT role, ats_score, date, pdf_path FROM analysis WHERE username=? ORDER BY id DESC",
        (session["user"],)
    )
    records = cur.fetchall()
    conn.close()

    return render_template("history.html", records=records)

# ------------------------
# API ROUTES (Postman)
# ------------------------
@app.route("/compare-resume", methods=["GET"])
def compare_resume():
    if "user" not in session:
        return redirect("/login")

    return render_template("compare.html")

@app.route("/match", methods=["POST"])
def match():
    data = request.json
    return jsonify(match_skills(data["skills"], data["job_role"]))


@app.route("/predict-role", methods=["POST"])
def predict():
    data = request.json
    return jsonify({"predicted_role": predict_role(data["skills"])})


@app.route("/ats-score", methods=["POST"])
def ats_score():
    data = request.json
    return jsonify(calculate_ats_score(data["parsed_data"], data["job_role"]))


@app.route("/career-recommendation", methods=["POST"])
def career():
    data = request.json
    return jsonify(recommend_career(data["ats_result"], data["job_role"]))


@app.route("/download-history-pdf")
def download_history_pdf():
    if "user" not in session:
        return redirect("/login")

    pdf_path = request.args.get("path")

    if not pdf_path or not os.path.exists(pdf_path):
        return "File not found", 404

    # Security: prevent path traversal — only serve files from REPORT_FOLDER
    real_path = os.path.realpath(pdf_path)
    real_report_dir = os.path.realpath(app.config["REPORT_FOLDER"])
    if not real_path.startswith(real_report_dir):
        return "Access denied", 403

    return send_file(pdf_path, as_attachment=True)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        conn = connect_db()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            conn.commit()
        except:
            return "Username already exists"
        finally:
            conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT username, email, password FROM users WHERE username=? ",
            (username,)
        )
        user = cur.fetchone()
        conn.close()

        if user and user[2] == password:
            session["user"] = user[0]
            session["email"] = user[1]
            return redirect("/")
        else:
            return "Invalid credentials"

    return render_template("login.html")

@app.route("/login/google")
def login_google():
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/login/google/callback")
def google_callback():
    token = google.authorize_access_token()
    user_info = google.get(
        "https://openidconnect.googleapis.com/v1/userinfo"
    ).json()


    email = user_info["email"]
    name = user_info.get("name", email)

    # Auto-register user if not exists
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT username FROM users WHERE email=?", (email,))
    user = cur.fetchone()

    if not user:
        cur.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (name, email, "GOOGLE_OAUTH")
        )
        conn.commit()

    conn.close()

    session["user"] = name
    session["email"] = email

    return redirect("/")

@app.route("/login/microsoft")
def login_microsoft():
    redirect_uri = url_for('microsoft_callback', _external=True)
    return microsoft.authorize_redirect(redirect_uri)

@app.route("/login/microsoft/callback")
def microsoft_callback():
    token = microsoft.authorize_access_token()
    user_info = microsoft.get('me').json()

    email = user_info.get("mail") or user_info.get("userPrincipalName")
    name = user_info.get("displayName", email)

    session["user"] = name
    session["email"] = email

    return redirect("/")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ------------------------
# RESUME BUILDER ROUTES
# ------------------------

@app.route("/resume-builder", methods=["GET"])
def resume_builder_page():
    if "user" not in session:
        return redirect("/login")

    # Pre-fill form if editing
    builder_data = session.get("resume_builder_data", {})
    prefill = builder_data.get("resume_data", {})
    return render_template("resume_builder.html", prefill=prefill)


@app.route("/generate-resume", methods=["POST"])
@limiter.limit("5/minute")
def generate_resume():
    if "user" not in session:
        return redirect("/login")

    # Validate form
    is_valid, error_msg = validate_form_data(request.form)
    if not is_valid:
        flash(error_msg, "error")
        return redirect("/resume-builder")

    # Format resume data
    resume_data = format_resume_data(request.form)

    # Determine target role
    target_role = resume_data.get("target_role", "")
    if not target_role:
        # Predict role from skills
        roles = predict_multiple_roles(resume_data["skills_list"])
        target_role = roles[0]["role"] if roles else "Software Engineer"

    # Run ATS scoring + refinement (max 2 attempts)
    from multi_role_predictor import ROLE_SKILLS
    resume_data, ats_result = refine_for_ats(
        resume_data, target_role, calculate_ats_score, ROLE_SKILLS
    )

    # Generate PDF
    resume_data["ats_score"] = ats_result["ats_score"]  # for AI Optimization Summary in PDF
    pdf_filename = f"generated_{session['user']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex}.pdf"
    pdf_path = os.path.join(app.config["REPORT_FOLDER"], pdf_filename)
    generate_resume_pdf(resume_data, pdf_path)

    # Auto-email generated resume to user
    try:
        send_email(
            session["email"],
            pdf_path,
            subject="Your Generated Resume \u2014 Nexus CV",
            body=(
                f"Hello {resume_data.get('full_name', '')},\n\n"
                f"Your resume has been generated and optimized for the "
                f"{target_role} role.\n\n"
                f"ATS Score: {ats_result['ats_score']}\n\n"
                f"Your resume PDF is attached. You can also download it "
                f"from your Nexus CV dashboard.\n\n"
                f"Best regards,\nNexus CV Team"
            ),
            attachment_name="Generated_Resume.pdf"
        )
    except Exception as e:
        logging.error(f"Failed to send builder email: {e}")

    # Store in session under single key
    session["resume_builder_data"] = {
        "resume_data": resume_data,
        "ats_score": ats_result["ats_score"],
        "ats_result": {
            "skill_score": ats_result["skill_score"],
            "keyword_score": ats_result["keyword_score"],
            "completeness_score": ats_result["completeness_score"],
            "matched_skills": ats_result["matched_skills"],
            "missing_skills": ats_result["missing_skills"]
        },
        "target_role": target_role,
        "pdf_path": pdf_path
    }

    return redirect("/resume-preview")


@app.route("/resume-preview", methods=["GET"])
def resume_preview():
    if "user" not in session:
        return redirect("/login")

    builder_data = session.get("resume_builder_data")
    if not builder_data:
        return redirect("/resume-builder")

    return render_template(
        "resume_preview.html",
        resume=builder_data["resume_data"],
        ats_score=builder_data["ats_score"],
        ats_result=builder_data["ats_result"],
        target_role=builder_data["target_role"]
    )


@app.route("/download-resume")
def download_resume():
    if "user" not in session:
        return redirect("/login")

    builder_data = session.get("resume_builder_data")
    if not builder_data or not builder_data.get("pdf_path"):
        return redirect("/resume-builder")

    pdf_path = builder_data["pdf_path"]
    if not os.path.exists(pdf_path):
        flash("Generated resume file not found. Please regenerate.", "error")
        return redirect("/resume-builder")

    # Clear builder session data after download
    session.pop("resume_builder_data", None)

    return send_file(pdf_path, as_attachment=True)


@app.route("/edit-resume")
def edit_resume():
    if "user" not in session:
        return redirect("/login")
    return redirect("/resume-builder")


# ------------------------
# SECURITY HEADERS
# ------------------------

@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if os.getenv("FLASK_ENV") == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self'"
        )
    # Cache static assets (CSS, JS, images, fonts)
    if response.content_type:
        ct = response.content_type
        if any(t in ct for t in ["text/css", "javascript", "image/", "font/"]):
            response.headers["Cache-Control"] = "public, max-age=86400"
    return response


# ------------------------
# ERROR HANDLERS
# ------------------------

@app.errorhandler(404)
def page_not_found(e):
    app.logger.warning("404 Not Found: %s", request.url)
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error("500 Internal Server Error: %s", e)
    return render_template("500.html"), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    app.logger.warning("Rate limit exceeded: %s from %s", request.url, request.remote_addr)
    return jsonify(error="Rate limit exceeded. Please try again later."), 429


# ------------------------
# BACKGROUND CLEANUP JOB
# ------------------------

def _start_cleanup_scheduler():
    """Start APScheduler background job for file cleanup.
    Uses job ID + replace_existing to prevent duplicate jobs on reload."""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from cleanup import cleanup_old_files
        scheduler = BackgroundScheduler(daemon=True)
        scheduler.add_job(
            cleanup_old_files,
            "interval",
            hours=6,
            id="nexuscv_cleanup",
            replace_existing=True
        )
        scheduler.start()
        app.logger.info("Cleanup scheduler started (every 6 hours)")
    except ImportError:
        app.logger.warning("APScheduler not installed, skipping cleanup background job")


# ------------------------
# RUN APP
# ------------------------

if __name__ == "__main__":
    _start_cleanup_scheduler()
    app.run(host="0.0.0.0", port=5000, debug=False)
