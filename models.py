from mongoengine import Document, StringField, IntField, DateTimeField, ListField, FloatField
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

# ===================== MongoDB Documents =====================

class User(Document):
    cnic = StringField(unique=True, required=True, max_length=13)
    password = StringField(required=True)
    full_name = StringField(required=True)
    email = StringField(required=True)
    type = StringField(default="user", choices=["user", "admin"])
    role = StringField(default="student", choices=["student", "alumni", "superadmin", "fee", "scholarship","genadmin"])
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'users'}


class Complaint(Document):
    complaint_id = StringField(unique=True, sparse=True) 
    text = StringField()
    department = StringField()
    priority = StringField()
    sentiment = StringField()
    status = StringField(default="Pending")
    resolution = StringField()
    resolved_at = StringField() # Kept as String to match your logic
    created_at = StringField()  # Kept as String to match your logic
    time = StringField()

    meta = {'collection': 'complaints'}                                                                         

from mongoengine import Document, StringField, IntField, FloatField, DateTimeField, ListField, EmailField
from datetime import datetime

class FeeApplication(Document):
    # System Fields
    application_id = StringField(required=True, unique=True, index=True)
    status = StringField(default="Pending", choices=["Pending", "In Review", "Approved", "Rejected"])
    created_at = DateTimeField(default=datetime.utcnow)

    # Basic Info (Matches Frontend names)
    today_date = StringField(required=True)
    name = StringField(required=True)
    father_name = StringField(required=True)
    cnic = StringField(required=True, max_length=13) # No unique=True here to allow multiple sem applications if needed, or keep unique if 1 app per student
    email = EmailField(required=True)
    matric_roll = StringField(required=True)
    contact = StringField(required=True, max_length=11)
    whatsapp = StringField(required=True, max_length=11)
    city = StringField(required=True)

    # Academic Info
    institute_name = StringField(required=True)
    degree = StringField(required=True)
    current_semester = StringField(required=True)
    last_date = StringField(required=True)

    # Application Details
    # ListField is crucial because user can select multiple (Semester + Hostel etc.)
    applying_for = ListField(StringField(), required=True) 
    
    # Financial & Banking
    account_holder = StringField(required=True)
    iban = StringField(required=True)
    siblings = IntField(required=True, min_value=0)
    income = FloatField(required=True, min_value=0.0)

    # Storage paths for uploaded files
    fee_voucher_path = StringField(required=True)
    contribution_slip_path = StringField(required=True)
    result_path = StringField(required=True)
    cheque_book_path = StringField() # Optional

    meta = {
        'collection': 'fee_applications',
        'indexes': [
            'application_id', 
            'cnic', 
            'status',
            'created_at'
        ],
        'ordering': ['-created_at'] # Latest applications top par aayengi
    }

class StudentRegistration(Document):
    registration_id = StringField(required=True, unique=True, index=True)
    today_date = StringField()
    alumni_name = StringField(required=True)
    father_name = StringField(required=True)
    dob = StringField()
    gender = StringField()
    cnic = StringField(unique=True, required=True, max_length=13)
    metric_roll = StringField()
    school_name = StringField()
    campus_name = StringField()
    area = StringField()
    region_name = StringField()
    home_address = StringField()
    home_city = StringField()
    personal_mobile = StringField()
    parent_mobile = StringField()
    metric_status = StringField()
    matric_year = IntField()
    inter_enrollment = StringField()
    enroll_date = StringField()
    faculty = StringField()
    college_name = StringField()
    college_type = StringField()
    inter_support = StringField()
    study_university = StringField()
    status = StringField(default="Pending")
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'student_registrations',
        'indexes': ['registration_id', 'cnic', 'status']
    }


class Feedback(Document):
    complaint_id = StringField(required=True, index=True)
    rating = IntField(required=True, min_value=1, max_value=5)
    comment = StringField()
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'feedback',
        'indexes': ['complaint_id']
    }


class SystemLog(Document):
    event = StringField(required=True)
    event_type = StringField()
    details = StringField()
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'logs',
        'indexes': ['created_at']
    }

from mongoengine import Document, StringField, IntField, FloatField, DateTimeField, EmailField
from datetime import datetime

class ScholarshipApplication(Document):
    # System Fields
    application_id = StringField(required=True, unique=True, index=True)
    status = StringField(default="Pending", choices=["Pending", "In Review", "Approved", "Rejected"])
    created_at = DateTimeField(default=datetime.utcnow)

    # Personal Information
    name = StringField(required=True)
    gender = StringField(required=True, choices=["male", "female", "other"])
    dob = StringField()
    cnic = StringField(required=True, unique=True, max_length=13, min_length=13)
    email = EmailField(required=True)
    father_name = StringField(required=True)
    father_cnic = StringField(required=True, max_length=13)
    address = StringField(required=True)
    city = StringField(required=True)
    campus = StringField(required=True)
    phone = StringField(required=True, max_length=11)
    whatsapp = StringField(required=True, max_length=11)
    emergency_contact = StringField(required=True)
    emergency_phone = StringField(required=True, max_length=11)

    # Education Background
    applicable_option = StringField(required=True)
    currently_working = StringField(required=True)
    previously_applied = StringField(required=True)
    school_name = StringField(required=True)
    school_location = StringField(required=True)
    years_in_tcf = IntField(required=True)
    matric_year = IntField(required=True)
    matric_roll = StringField(required=True)
    faculty = StringField(required=True)
    matric_percentage = FloatField(required=True, min_value=0, max_value=100)
    matric_grade = StringField(required=True)
    last_qualification = StringField(required=True)

    # Household & Financials
    earning_members = IntField(required=True, default=0)
    siblings_in_uni = IntField(required=True, default=0)
    household_members = IntField(required=True, default=0)
    house_type = StringField(required=True)
    rent_amount = FloatField(default=0.0)
    transport = FloatField(required=True, default=0.0)
    medical = FloatField(required=True, default=0.0)
    gas_bill = FloatField(required=True, default=0.0)
    electricity = FloatField(required=True, default=0.0)
    water = FloatField(required=True, default=0.0)
    grocery = FloatField(required=True, default=0.0)
    loan = FloatField(default=0.0)
    other_expense = FloatField(default=0.0)
    total_expense = FloatField(required=True)
    contribution_amount = FloatField(required=True)

    # Tertiary Education Plans (Plan A)
    degree_plan_a = StringField(required=True)
    reason_plan_a = StringField(required=True)
    industry_plan_a = StringField(required=True)
    uni1_plan_a = StringField(required=True)
    uni2_plan_a = StringField(required=True)
    uni3_plan_a = StringField(required=True)

    # Tertiary Education Plans (Plan B)
    degree_plan_b = StringField(required=True)
    reason_plan_b = StringField(required=True)
    industry_plan_b = StringField(required=True)
    uni1_plan_b = StringField(required=True)
    uni2_plan_b = StringField(required=True)
    uni3_plan_b = StringField(required=True)

    # File Paths (Storage path of uploaded files)
    cnic_file = StringField()
    father_cnic_file = StringField()
    photo = StringField()
    matric_marksheet = StringField()
    utility_bills = StringField()
    other_docs = StringField()

    meta = {
        'collection': 'scholarship_applications',
        'indexes': [
            'application_id', 
            'cnic', 
            'status',
            'created_at' # New index for sorting by date
        ],
        'ordering': ['-created_at'] # Default sorting: Latest first
    }

# ===================== Pydantic Schemas =====================

class ComplaintCreate(BaseModel):
    text: str = Field(..., min_length=10, max_length=5000)
    cnic: str  # Mandatory for official complaints
    department: Optional[str] = None

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

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)

class SignupRequest(BaseModel):
    full_name: str # Added this - mechanical necessity for User Document
    cnic: str
    email: str
    password: str
    confirmPassword: str

class StaffCreateRequest(BaseModel):
    full_name: str
    cnic: str
    email: str
    password: str
    role: str

class StaffDeleteRequest(BaseModel):
    cnic: str

# Add this Document to your MongoDB sections in models.py
class QueryTicket(Document):
    query_no = StringField(required=True, unique=True, index=True)
    cnic = StringField(required=True)
    query = StringField(required=True)
    department = StringField(required=True)
    status = StringField(default="forwarded", choices=["forwarded", "responded"])
    response = StringField()
    confidence = FloatField()
    createdAt = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'query_tickets',
        'indexes': ['query_no', 'department', 'status'],
        'ordering': ['-createdAt']
    }

# Add this to your Pydantic schemas section in models.py
class QueryTicketUpdate(BaseModel):
    cnic: str
    query: str
    department: str
    response: Optional[str] = ""
    status: str