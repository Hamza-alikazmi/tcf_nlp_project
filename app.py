from fastapi import FastAPI, Request, HTTPException, Form, File, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime
from contextlib import asynccontextmanager
from typing import List, Optional

import pandas as pd
import numpy as np
import os
import shutil

from jose import JWTError, jwt
from fastapi import Depends, Cookie

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# MongoDB
from database import init_mongodb, close_mongodb,DB_NAME 
from models import (
    Complaint, ComplaintCreate, QueryRequest, FeeApplication,
    User, StudentRegistration, ScholarshipApplication, SignupRequest   
    )


# Secret key to sign JWT - Keep this private!
SECRET_KEY = "TCF_SUPER_SECRET_KEY_2026" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Helper to create tokens
def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Middleware/Dependency to verify token and role
async def get_current_user_role(access_token: Optional[str] = Cookie(None)):
    if not access_token:
        return None
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        role: str = payload.get("role")
        if role is None:
            return None
        return role
    except JWTError:
        return None

# ==========================
# Lifespan Management
# ==========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_mongodb()
    print("✅ MongoDB Connected")
    yield
    close_mongodb()
    print("✅ MongoDB Connection Closed")
db = DB_NAME 

app = FastAPI(title="TCF NLP Project Backend", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def role_required(allowed_roles: list):
    async def dependency(role: str = Depends(get_current_user_role)):
        if not role:
            return "<script> alert('Please Login First'); window.href.location='/';</script>"
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Unauthorized Access")
        return role
    return Depends(dependency)

# Example: Protecting the Admin Dashboard
@app.get("/admin/dashboard")
async def admin_dashboard(request: Request, role: str = role_required(["admin"])):
    return templates.TemplateResponse("admin-dashboard.html", {"request": request, "role": role})


@app.middleware("http")
async def add_auth_state(request: Request, call_next):
    token = request.cookies.get("access_token")
    role = None
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            role = payload.get("role")
        except:
            pass
    request.state.user_role = role
    response = await call_next(request)
    return response

# Inject role into all templates automatically
@app.get("/context_data") # This is a helper for Jinja
def inject_role(request: Request):
    return {"user_role": getattr(request.state, "user_role", None)}

templates.env.globals.update(inject_role=inject_role)

def role_required(allowed_roles: list):
    async def dependency(role: str = Depends(get_current_user_role)):
        if not role:
            raise HTTPException(status_code=401, detail="Please login first")
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Unauthorized Access")
        return role
    return Depends(dependency)

# Example: Protecting the Admin Dashboard
@app.get("/admin/dashboard")
async def admin_dashboard(request: Request, role: str = role_required(["admin"])):
    return templates.TemplateResponse("admin-dashboard.html", {"request": request, "role": role})

# Example: Protecting Student Form
@app.get("/scholarship-form")
async def scholarship_page(request: Request, role: str = role_required(["student", "user"])):
    return templates.TemplateResponse("scholarship-form.html", {"request": request, "role": role})


# Example: Protecting Student Form
@app.get("/scholarship-form")
async def scholarship_page(request: Request, role: str = role_required(["student", "user"])):
    return templates.TemplateResponse("scholarship-form.html", {"request": request, "role": role})

# ==========================
# Pydantic Models
# ==========================
class AdminUpdate(BaseModel):
    complaint_id: str
    status: Optional[str] = None
    resolution: Optional[str] = None


class LoginRequest(BaseModel):
    cnic: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    redirect: Optional[str] = None
    role: Optional[str] = None


class RegistrationRequest(BaseModel):
    todayDate: str
    alumni: str
    fatherName: str
    dob: str
    gender: str
    cnic: str
    metricRoll: str
    schoolName: str
    campusName: str
    area: str
    regionName: str
    homeAddress: str
    homeCity: str
    personalMobile: str
    parentMobile: str
    metricStatus: str
    matricYear: int
    interEnrollment: str
    enrollDate: str
    faculty: str
    collegeName: str
    collegeType: str
    interSupport: str
    studyUniversity: str


# ==========================
# Load ML Models & Datasets
# ==========================
model = SentenceTransformer('all-MiniLM-L6-v2')
sentiment_model = SentimentIntensityAnalyzer()

try:
    complaints_df = pd.read_excel("datas.xlsx")
    queries_df = pd.read_excel("queries.xlsx")
    complaint_embeddings = model.encode(complaints_df["text"].tolist())
    query_embeddings = model.encode(queries_df["question"].tolist())
    print("✅ Datasets and embeddings loaded successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not load datasets. Error: {e}")
    complaints_df = pd.DataFrame(columns=["text", "department"])
    queries_df = pd.DataFrame(columns=["question", "answer"])
    complaint_embeddings = np.array([])
    query_embeddings = np.array([])


# ==========================
# Keywords
# ==========================
department_keywords = {
    "IT": ["internet", "wifi", "system", "network", "computer", "server", "login", "software", "hardware", "email"],
    "HR": ["salary", "leave", "payroll", "bonus", "increment", "promotion", "hr", "hiring", "recruitment", "attendance"],
    "Admin": ["clean", "maintenance", "facility", "office", "equipment", "furniture", "repair", "housekeeping"],
    "Fee": ["fee", "payment", "tuition", "invoice", "billing", "account", "refund", "receipt", "transaction"]
}

high_priority_keywords = [
    "urgent", "immediately", "emergency", "asap", "critical", "important",
    "stop", "breakdown", "tomorrow", "today", "last date", "again", "deadline",
    "immediate", "attention", "serious", "severe", "crisis"
]

normal_priority_keywords = [
    "soon", "quick", "moderate", "request", "issue", "problem",
    "attention", "follow up", "need", "required", "pending"
]

low_priority_keywords = [
    "whenever", "low", "minor", "later", "not urgent", "no hurry",
    "general", "inquiry", "question", "suggestion", "feedback"
]


# ==========================
# Helper Functions
# ==========================
def generate_complaint_id():
    count = Complaint.objects.count() + 1
    return f"CMP-2026-{str(count).zfill(5)}"


def detect_department(text: str) -> str:
    if not text or not isinstance(text, str):
        return "Admin"
    text_lower = text.lower()
    for dept, keywords in department_keywords.items():
        for word in keywords:
            if word in text_lower:
                return dept
    try:
        if len(complaint_embeddings) > 0:
            emb = model.encode([text])
            scores = cosine_similarity(emb, complaint_embeddings)
            idx = scores.argmax()
            return complaints_df.iloc[idx]["department"]
    except:
        pass
    return "Admin"


def detect_sentiment(text: str) -> str:
    if not text or not isinstance(text, str):
        return "Neutral"
    try:
        score = sentiment_model.polarity_scores(text)["compound"]
        if score >= 0.05:
            return "Positive"
        elif score <= -0.05:
            return "Negative"
        return "Neutral"
    except:
        return "Neutral"


def detect_priority(text: str) -> str:
    if not text or not isinstance(text, str):
        return "NORMAL"
    text_lower = text.lower()
    for word in high_priority_keywords:
        if word in text_lower:
            return "HIGH"
    for word in normal_priority_keywords:
        if word in text_lower:
            return "NORMAL"
    for word in low_priority_keywords:
        if word in text_lower:
            return "LOW"
    try:
        score = sentiment_model.polarity_scores(text)["compound"]
        if score < -0.3:
            return "HIGH"
        elif score < 0:
            return "NORMAL"
    except:
        pass
    return "NORMAL"


# ==========================
# Auto-Learning Functions
# ==========================
def retrain_model():
    try:
        if os.path.exists("resolved_complaints.csv"):
            df = pd.read_csv("resolved_complaints.csv")
            global complaint_embeddings, complaints_df
            complaints_df = pd.concat([complaints_df, df[["text", "department"]]], ignore_index=True)
            complaint_embeddings = model.encode(complaints_df["text"].tolist())
            print("✅ Model retrained with resolved complaints")
    except Exception as e:
        print(f"Error retraining model: {e}")


def update_priority_keywords():
    try:
        if os.path.exists("resolved_complaints.csv"):
            df = pd.read_csv("resolved_complaints.csv")
            global high_priority_keywords, normal_priority_keywords, low_priority_keywords
            high_words = []
            normal_words = []
            low_words = []
            for _, row in df.iterrows():
                words = str(row["text"]).lower().split()
                if row.get("priority") == "HIGH":
                    high_words.extend(words)
                elif row.get("priority") == "NORMAL":
                    normal_words.extend(words)
                elif row.get("priority") == "LOW":
                    low_words.extend(words)

            stop_words = {"the", "a", "an", "is", "are", "was", "were", "i", "my", "me", "to", "for", "in", "on", "at", "and", "of"}

            def extract_top(word_list, existing):
                if not word_list:
                    return existing
                counts = pd.Series(word_list).value_counts()
                counts = counts[~counts.index.isin(stop_words)]
                new_words = counts.head(10).index.tolist()
                return list(set(existing + new_words))

            high_priority_keywords = extract_top(high_words, high_priority_keywords)
            normal_priority_keywords = extract_top(normal_words, normal_priority_keywords)
            low_priority_keywords = extract_top(low_words, low_priority_keywords)
            print("✅ Priority keywords updated from resolved data")
    except Exception as e:
        print(f"Error updating priority keywords: {e}")


def save_resolved_complaint(complaint):
    try:
        entry = {
            "text": complaint.text,
            "department": complaint.department,
            "priority": complaint.priority,
            "resolution": complaint.resolution or ""
        }
        df = pd.DataFrame([entry])
        if not os.path.exists("resolved_complaints.csv"):
            df.to_csv("resolved_complaints.csv", index=False)
        else:
            df.to_csv("resolved_complaints.csv", mode="a", index=False, header=False)
        print(f"✅ Resolved complaint saved: {complaint.complaint_id}")
    except Exception as e:
        print(f"Error saving resolved complaint: {e}")


# ==========================
# Routes
# ==========================
# ==========================
# Frontend Page Routes (GET)
# ==========================

@app.get("/")
def index_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/home")
def home_page(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")

@app.get("/about")
def about_page(request: Request):
    return templates.TemplateResponse(request=request, name="about.html")

@app.get("/contact")
def contact_page(request: Request):
    return templates.TemplateResponse(request=request, name="contact.html")

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse(request=request, name="signup.html")

@app.get("/success-stories")
def success_stories_page(request: Request):
    return templates.TemplateResponse(request=request, name="success-stories.html")

@app.get("/guide")
def guide_page(request: Request):
    return templates.TemplateResponse(request=request, name="guide.html")

@app.get("/query-page")
def query_page(request: Request):
    return templates.TemplateResponse(request=request, name="query.html")

# ==========================
# Forms Routes (GET)
# ==========================

@app.get("/reg-form")
def registration_form_page(request: Request,role: str = role_required(["admin"])):
    return templates.TemplateResponse(request=request, name="reg-form.html", context={"role": role})

@app.get("/fee-form")
def fee_form_page(request: Request):
    return templates.TemplateResponse(request=request, name="fee-form.html")

@app.get("/scholarship-form")
def scholarship_form_page(request: Request):
    return templates.TemplateResponse(request=request, name="scholarship-form.html")

# ==========================
# Dashboard Routes (GET)
# ==========================

@app.get("/admin")
async def admin_login_page(request: Request, page: int = 1):
    # Number of complaints per page
    per_page = 10
    
    # Calculate skip value
    skip = (page - 1) * per_page
    
    # Get total count for pagination logic
    total_count = Complaint.objects.count()
    
    # Fetch only the specific page using skip and limit
    complaints_list = Complaint.objects().order_by('-created_at').skip(skip).limit(per_page)
    
    # Calculate total pages
    total_pages = (total_count + per_page - 1) // per_page

    return templates.TemplateResponse(
        request=request,
        name="admin.html", 
        context={
            "request": request, 
            "complaints": complaints_list,
            "current_page": page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    )

@app.get("/student/dashboard")
def dashboard_page(request: Request, role: str = role_required(["student", "user"])):
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"role": role})

@app.get("/admin/dashboard")
def alt_admin_dashboard_page(request: Request):
    return templates.TemplateResponse(request=request, name="admin-dashboard.html")

@app.get("/alumni/dashboard")
def alumni_dashboard_page(request: Request):
    return templates.TemplateResponse(request=request, name="alumni-dashboard.html")

@app.post("/complaint")
def submit_complaint(payload: ComplaintCreate):
    department = detect_department(payload.text)
    sentiment = detect_sentiment(payload.text)
    priority = detect_priority(payload.text)
    complaint_id = generate_complaint_id()

    new_complaint = Complaint(
        complaint_id=complaint_id,
        text=payload.text,
        department=department,
        sentiment=sentiment,
        priority=priority,
        status="Pending"
    )
    new_complaint.save()

    return {
        "message": f"Your Complaint has been forwarded to {department} Department. Your Complaint ID is {complaint_id}.",
        "complaint_id": complaint_id,
        "department": department,
        "priority": priority,
        "sentiment": sentiment
    }


@app.get("/track/{complaint_id}")
def track(complaint_id: str):
    complaint = Complaint.objects(complaint_id=complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return {
        "complaint_id": complaint.complaint_id,
        "text": complaint.text,
        "department": complaint.department,
        "status": complaint.status,
        "resolution": complaint.resolution,
        "priority": complaint.priority,
        "sentiment": complaint.sentiment,
        "resolved_at": str(complaint.resolved_at) if complaint.resolved_at else None
    }


@app.post("/admin/update")
def update(payload: AdminUpdate):
    complaint = Complaint.objects(complaint_id=payload.complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if payload.status:
        complaint.status = payload.status
    if payload.resolution:
        complaint.resolution = payload.resolution

    if complaint.status == "Resolved" and not complaint.resolved_at:
        complaint.resolved_at = datetime.utcnow()
        save_resolved_complaint(complaint)
        retrain_model()
        update_priority_keywords()

    complaint.save()
    return {"message": "Complaint updated successfully"}

@app.get("/admin/data")
def admin_data():
    complaints = Complaint.objects()
    dept_counts = {}
    priority_counts = {"HIGH": 0, "NORMAL": 0, "LOW": 0}
    status_counts = {"Pending": 0, "In Progress": 0, "Resolved": 0}

    for c in complaints:
        dept_counts[c.department] = dept_counts.get(c.department, 0) + 1
        priority_counts[c.priority] = priority_counts.get(c.priority, 0) + 1
        status_counts[c.status] = status_counts.get(c.status, 0) + 1

    return {
        "departments": {"labels": list(dept_counts.keys()), "counts": list(dept_counts.values())},
        "priority": {"labels": list(priority_counts.keys()), "counts": list(priority_counts.values())},
        "status": {"labels": list(status_counts.keys()), "counts": list(status_counts.values())}
    }


@app.get("/admin/complaints")
def get_all_complaints():
    complaints = Complaint.objects()
    return [
        {
            "complaint_id": c.complaint_id,
            "text": c.text,
            "department": c.department,
            "status": c.status,
            "priority": c.priority,
            "sentiment": c.sentiment,
            "resolved_at": str(c.resolved_at) if c.resolved_at else None
        }
        for c in complaints
    ]


@app.post("/query")
def query(payload: QueryRequest):
    if len(query_embeddings) == 0:
        return JSONResponse(status_code=503, content={"answer": "Query system not ready", "confidence": 0.0})
    try:
        emb = model.encode([payload.question])
        scores = cosine_similarity(emb, query_embeddings)
        idx = np.argmax(scores)
        confidence = float(scores[0][idx])

        if confidence > 0.4:
            answer = queries_df.iloc[idx]["answer"]
        else:
            answer = "Sorry, I don't have an answer for that question. Please contact the support team."

        return {"answer": answer, "confidence": confidence}
    except Exception as e:
        return JSONResponse(status_code=500, content={"answer": "Error processing query", "confidence": 0.0})


# ==========================
# FEE APPLICATION
# ==========================
@app.post("/fee")
async def submit_fee_application(
    todayDate: str = Form(...),
    name: str = Form(...),
    fatherName: str = Form(...),
    cnic: str = Form(...),
    email: str = Form(...),
    matricRoll: str = Form(...),
    contact: str = Form(...),
    whatsapp: str = Form(...),
    city: str = Form(...),
    instituteName: str = Form(...),
    degree: str = Form(...),
    applyingFor: List[str] = Form(...),
    currentSemester: str = Form(...),
    lastDate: str = Form(...),
    accountHolder: str = Form(...),
    iban: str = Form(...),
    siblings: int = Form(...),
    income: float = Form(...),
    feeVoucher: UploadFile = File(...),
    contributionSlip: UploadFile = File(...),
    result: UploadFile = File(...),
    chequeBook: Optional[UploadFile] = File(None)
):
    try:
        count = FeeApplication.objects.count() + 1
        app_id = f"FEE-2026-{str(count).zfill(5)}"

        def save_upload(file_obj: UploadFile, prefix: str):
            if not file_obj or not file_obj.filename:
                return None
            ext = os.path.splitext(file_obj.filename)[1]
            filename = f"{app_id}_{prefix}{ext}"
            filepath = os.path.join("uploads", filename)
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file_obj.file, buffer)
            return filepath

        voucher_path = save_upload(feeVoucher, "voucher")
        slip_path = save_upload(contributionSlip, "slip")
        result_path = save_upload(result, "result")
        cheque_path = save_upload(chequeBook, "cheque") if chequeBook else None

        application = FeeApplication(
            application_id=app_id,
            today_date=todayDate,
            name=name,
            father_name=fatherName,
            cnic=cnic,
            email=email,
            matric_roll=matricRoll,
            contact=contact,
            whatsapp=whatsapp,
            city=city,
            institute_name=instituteName,
            degree=degree,
            applying_for=applyingFor,
            current_semester=currentSemester,
            last_date=lastDate,
            account_holder=accountHolder,
            iban=iban,
            siblings=siblings,
            income=income,
            fee_voucher_path=voucher_path,
            contribution_slip_path=slip_path,
            result_path=result_path,
            cheque_book_path=cheque_path
        )
        application.save()

        return HTMLResponse(f"""
            <div style="color: #155724; padding: 20px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; text-align: center;">
                <h3>✅ Application Submitted Successfully!</h3>
                <p><strong>Tracking ID:</strong> {app_id}</p>
                <p>We will review your application and contact you soon.</p>
            </div>
        """)
    except Exception as e:
        print(f"Fee Submission Error: {e}")
        return HTMLResponse(f"""
            <div style="color: #721c24; padding: 20px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 8px; text-align: center;">
                <h3>❌ Submission Failed</h3>
                <p>Please try again. If the problem persists, contact support.</p>
            </div>
        """, status_code=500)


# ==========================
# AUTHENTICATION
# ==========================
@app.post("/api/login", response_model=LoginResponse)
async def login(payload: LoginRequest, response: JSONResponse):
    user = User.objects(cnic=payload.cnic).first()
    if not user or not pwd_context.verify(payload.password, user.password):
        return LoginResponse(success=False, message="Invalid credentials")

    # Create token containing Role and CNIC
    token = create_access_token(data={"sub": user.cnic, "role": user.role})

    # Set token in an HttpOnly cookie
    response = JSONResponse(content={
        "success": True,
        "message": "Welcome back!",
        "redirect": "/admin/dashboard" if user.role == "admin" else "/student/dashboard",
        "role": user.role
    })
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax")
    return response

# ==========================
# STUDENT REGISTRATION (Alumni)
# ==========================
@app.post("/register")
async def register_student(payload: RegistrationRequest):
    try:
        if StudentRegistration.objects(cnic=payload.cnic).first():
            return HTMLResponse("""
                <div style="color:#721c24;padding:30px;background:#f8d7da;border-radius:10px;text-align:center;margin:50px auto;max-width:600px;">
                    <h2>Registration Failed</h2>
                    <p>This CNIC is already registered.</p>
                    <a href="/" style="color:#667eea;">← Back to Form</a>
                </div>
            """, status_code=400)

        count = StudentRegistration.objects.count() + 1
        reg_id = f"REG-2026-{str(count).zfill(5)}"

        StudentRegistration(
            registration_id=reg_id,
            today_date=payload.todayDate,
            alumni_name=payload.alumni,
            father_name=payload.fatherName,
            dob=payload.dob,
            gender=payload.gender,
            cnic=payload.cnic,
            metric_roll=payload.metricRoll,
            school_name=payload.schoolName,
            campus_name=payload.campusName,
            area=payload.area,
            region_name=payload.regionName,
            home_address=payload.homeAddress,
            home_city=payload.homeCity,
            personal_mobile=payload.personalMobile,
            parent_mobile=payload.parentMobile,
            metric_status=payload.metricStatus,
            matric_year=payload.matricYear,
            inter_enrollment=payload.interEnrollment,
            enroll_date=payload.enrollDate,
            faculty=payload.faculty,
            college_name=payload.collegeName,
            college_type=payload.collegeType,
            inter_support=payload.interSupport,
            study_university=payload.studyUniversity,
            status="Pending"
        ).save()

        return HTMLResponse(f"""
            <div style="color:#155724;padding:30px;background:#d4edda;border-radius:10px;text-align:center;margin:40px auto;max-width:700px;">
                <h2>Registration Successful!</h2>
                <h3>Registration ID: <strong>{reg_id}</strong></h3>
                <p>Your application has been submitted successfully.</p>
                <a href="/" style="background:#667eea;color:white;padding:12px 25px;text-decoration:none;border-radius:6px;">← Back to Home</a>
            </div>
        """)
    except Exception as e:
        print(f"Registration Error: {e}")
        return HTMLResponse("""
            <div style="color:#721c24;padding:30px;background:#f8d7da;border-radius:10px;text-align:center;margin:50px auto;">
                <h2>Registration Failed</h2>
                <p>Please try again later.</p>
                <a href="/" style="color:#667eea;">← Back</a>
            </div>
        """, status_code=500)


# ==========================
# ALUMNI MANAGEMENT API (for your Alumni HTML)
# ==========================
@app.get("/register/all")
def get_all_registrations():
    registrations = StudentRegistration.objects().order_by('-created_at')
    return {"registrations": [r.to_mongo().to_dict() for r in registrations]}


@app.get("/register/cnic/{cnic}")
def get_by_cnic(cnic: str):
    reg = StudentRegistration.objects(cnic=cnic).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"registration": reg.to_mongo().to_dict()}


@app.put("/register/cnic/{cnic}")
async def update_by_cnic(cnic: str, payload: RegistrationRequest):
    reg = StudentRegistration.objects(cnic=cnic).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Record not found")
    # Update logic (add fields as needed)
    reg.save()
    return {"message": "Record updated successfully"}


@app.delete("/register/cnic/{cnic}")
def delete_by_cnic(cnic: str):
    reg = StudentRegistration.objects(cnic=cnic).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Record not found")
    reg.delete()
    return {"message": "Record deleted successfully"}


# ==========================
# QARZ-E-HASNA SCHOLARSHIP
# ==========================
@app.post("/scholarship")
async def submit_scholarship_application(
    name: str = Form(...),
    gender: str = Form(...),
    dob: str = Form(...),
    cnic: str = Form(...),
    email: str = Form(...),
    fatherName: str = Form(...),
    fatherCnic: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    campus: str = Form(...),
    phone: str = Form(...),
    whatsapp: str = Form(...),
    emergencyContact: str = Form(...),
    emergencyPhone: str = Form(...),
    applicableOption: str = Form(...),
    working: str = Form(...),
    previousApply: str = Form(...),
    schoolName: str = Form(...),
    schoolLocation: str = Form(...),
    yearsInTcf: int = Form(...),
    matricYear: int = Form(...),
    matricRoll: str = Form(...),
    faculty: str = Form(...),
    matricPercentage: float = Form(...),
    matricGrade: str = Form(...),
    lastQualification: str = Form(...),
    earningMembers: int = Form(...),
    siblingsInUni: int = Form(...),
    householdMembers: int = Form(...),
    house: str = Form(...),
    transport: float = Form(...),
    medical: float = Form(...),
    gasBill: float = Form(...),
    electricity: float = Form(...),
    water: float = Form(...),
    grocery: float = Form(...),
    totalExpense: float = Form(...),
    contributionAmount: float = Form(...),
    degreePlanA: str = Form(...),
    reasonPlanA: str = Form(...),
    # Add other Plan A/B fields if needed
    cnicFile: UploadFile = File(...),
    fatherCnicFile: UploadFile = File(...),
    photo: UploadFile = File(...),
    matricMarksheet: UploadFile = File(...),
    utilityBills: UploadFile = File(...),
    otherDocs: Optional[UploadFile] = File(None)
):
    try:
        count = ScholarshipApplication.objects.count() + 1
        app_id = f"QEH-2026-{str(count).zfill(5)}"

        def save_file(file: UploadFile, prefix: str):
            if not file or not file.filename:
                return None
            ext = os.path.splitext(file.filename)[1]
            filename = f"{app_id}_{prefix}{ext}"
            filepath = os.path.join("uploads", filename)
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return filepath

        cnic_path = save_file(cnicFile, "cnic")
        father_cnic_path = save_file(fatherCnicFile, "father_cnic")
        photo_path = save_file(photo, "photo")
        matric_path = save_file(matricMarksheet, "matric")
        utility_path = save_file(utilityBills, "utility")
        other_path = save_file(otherDocs, "other") if otherDocs else None

        ScholarshipApplication(
            application_id=app_id,
            name=name,
            gender=gender,
            dob=dob,
            cnic=cnic,
            email=email,
            father_name=fatherName,
            father_cnic=fatherCnic,
            address=address,
            city=city,
            campus=campus,
            phone=phone,
            whatsapp=whatsapp,
            emergency_contact=emergencyContact,
            emergency_phone=emergencyPhone,
            applicable_option=applicableOption,
            currently_working=working,
            previously_applied=previousApply,
            school_name=schoolName,
            school_location=schoolLocation,
            years_in_tcf=yearsInTcf,
            matric_year=matricYear,
            matric_roll=matricRoll,
            faculty=faculty,
            matric_percentage=matricPercentage,
            matric_grade=matricGrade,
            last_qualification=lastQualification,
            earning_members=earningMembers,
            siblings_in_uni=siblingsInUni,
            household_members=householdMembers,
            house_type=house,
            transport=transport,
            medical=medical,
            gas_bill=gasBill,
            electricity=electricity,
            water=water,
            grocery=grocery,
            total_expense=totalExpense,
            contribution_amount=contributionAmount,
            degree_plan_a=degreePlanA,
            reason_plan_a=reasonPlanA,
            cnic_file=cnic_path,
            father_cnic_file=father_cnic_path,
            photo=photo_path,
            matric_marksheet=matric_path,
            utility_bills=utility_path,
            other_docs=other_path,
            status="Pending"
        ).save()

        return JSONResponse({"success": True, "message": f"Application submitted successfully! Your ID is {app_id}"})

    except Exception as e:
        print(f"Scholarship Error: {e}")
        return JSONResponse({"success": False, "message": "Failed to submit application"}, status_code=500)


# ==========================
# NEW: USER SIGNUP 
# ==========================
@app.post("/api/signin-data")
async def user_signup(payload: SignupRequest):
    try:
        # 1. Structural & Data Validation
        if len(payload.cnic) != 13 or not payload.cnic.isdigit():
            return {"success": False, "message": "CNIC must be exactly 13 digits."}

        if payload.password != payload.confirmPassword:
            return {"success": False, "message": "Passwords do not match."}

        if len(payload.password) < 8:
            return {"success": False, "message": "Password must be at least 8 characters."}

        # 2. Duplicate Check
        if User.objects(cnic=payload.cnic).first():
            return {"success": False, "message": "An account with this CNIC already exists."}

        # 3. Secure Password Hashing
        hashed_password = pwd_context.hash(payload.password)

        # 4. Persistence
        # Note: 'role' must be one of ['student', 'alumni', 'superadmin', 'fee', 'scholarship']
        # 'type' defaults to 'user' in your model definition.
        user = User(
            cnic=payload.cnic,
            email=payload.email,
            password=hashed_password,
            full_name=payload.full_name,  # Now correctly capturing the name from frontend
            role="student"                # Assigned 'student' as default valid role
        )
        user.save()

        # 5. Logging the event
        try:
            SystemLog(
                event="User Registration",
                event_type="AUTH",
                details=f"New user registered with CNIC: {payload.cnic}"
            ).save()
        except:
            pass # Don't block registration if logging fails

        return {
            "success": True,
            "message": "Account created successfully! You can now login."
        }

    except Exception as e:
        print(f"Signup Error: {e}")
        return {"success": False, "message": "Server error. Please try again later."}


@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": str(datetime.utcnow())}

@app.get("/logout")
async def logout():
    response = HTMLResponse(content="<script>window.location.href='/login';</script>")
    response.delete_cookie("access_token")
    return response

# Initialize resolved complaints file
if not os.path.exists("resolved_complaints.csv"):
    pd.DataFrame(columns=["text", "department", "priority", "resolution"]).to_csv("resolved_complaints.csv", index=False)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)