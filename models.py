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
    role = StringField(default="student", choices=["student", "alumni", "superadmin", "fee", "scholarship"])
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


class FeeApplication(Document):
    application_id = StringField(required=True, unique=True, index=True)
    today_date = StringField(required=True)
    name = StringField(required=True)
    father_name = StringField(required=True)
    cnic = StringField(required=True)
    email = StringField(required=True)
    matric_roll = StringField(required=True)
    contact = StringField(required=True)
    whatsapp = StringField(required=True)
    city = StringField(required=True)
    institute_name = StringField(required=True)
    degree = StringField(required=True)
    applying_for = ListField(StringField(), required=True)
    current_semester = StringField(required=True)
    last_date = StringField(required=True)
    account_holder = StringField(required=True)
    iban = StringField(required=True)
    siblings = IntField(required=True)
    income = FloatField(required=True)
    # File Paths
    fee_voucher_path = StringField(required=True)
    contribution_slip_path = StringField(required=True)
    result_path = StringField(required=True)
    cheque_book_path = StringField() 
    status = StringField(default="Pending")
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'fee_applications',
        'indexes': ['application_id', 'cnic', 'status']
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


class ScholarshipApplication(Document):
    application_id = StringField(required=True, unique=True, index=True)
    name = StringField(required=True)
    gender = StringField(required=True)
    dob = StringField()
    cnic = StringField(required=True, unique=True, max_length=13)
    email = StringField(required=True)
    father_name = StringField(required=True)
    father_cnic = StringField(required=True, max_length=13)
    address = StringField(required=True)
    city = StringField(required=True)
    campus = StringField(required=True)
    phone = StringField(required=True)
    whatsapp = StringField(required=True)
    emergency_contact = StringField(required=True)
    emergency_phone = StringField(required=True)
    applicable_option = StringField(required=True)
    currently_working = StringField(required=True)
    previously_applied = StringField(required=True)
    school_name = StringField(required=True)
    school_location = StringField(required=True)
    years_in_tcf = IntField(required=True)
    matric_year = IntField(required=True)
    matric_roll = StringField(required=True)
    faculty = StringField(required=True)
    matric_percentage = FloatField(required=True)
    matric_grade = StringField(required=True)
    last_qualification = StringField(required=True)
    earning_members = IntField(required=True)
    siblings_in_uni = IntField(required=True)
    household_members = IntField(required=True)
    house_type = StringField(required=True)
    rent_amount = FloatField()
    transport = FloatField(required=True)
    medical = FloatField(required=True)
    gas_bill = FloatField(required=True)
    electricity = FloatField(required=True)
    water = FloatField(required=True)
    grocery = FloatField(required=True)
    loan = FloatField()
    other_expense = FloatField()
    total_expense = FloatField(required=True)
    contribution_amount = FloatField(required=True)
    degree_plan_a = StringField(required=True)
    reason_plan_a = StringField(required=True)
    industry_plan_a = StringField(required=True)
    uni1_plan_a = StringField(required=True)
    uni2_plan_a = StringField(required=True)
    uni3_plan_a = StringField(required=True)
    degree_plan_b = StringField(required=True)
    reason_plan_b = StringField(required=True)
    industry_plan_b = StringField(required=True)
    uni1_plan_b = StringField(required=True)
    uni2_plan_b = StringField(required=True)
    uni3_plan_b = StringField(required=True)
    cnic_file = StringField()
    father_cnic_file = StringField()
    photo = StringField()
    matric_marksheet = StringField()
    utility_bills = StringField()
    other_docs = StringField()
    status = StringField(default="Pending")
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'scholarship_applications',
        'indexes': ['application_id', 'cnic', 'status']
    }


# ===================== Pydantic Schemas =====================

class ComplaintCreate(BaseModel):
    text: str = Field(..., min_length=10, max_length=5000)

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