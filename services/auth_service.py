"""
Local profile data models for the Sehat Saathi prototype.

These models do not authenticate users, verify ABHA IDs or clinician credentials,
or enforce role-based access control.
"""

import uuid
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    google_id: Optional[str] = None
    email: Optional[str] = None
    name: str = ""
    role: str = "patient"  # "patient", "doctor", "staff"
    phone: Optional[str] = None
    abha_id: Optional[str] = None  # Ayushman Bharat Health Account ID
    profile_pic: Optional[str] = None
    created_at: Optional[str] = None

    # Doctor-specific profile fields
    medical_license_no: Optional[str] = None  # NMC / State Medical Council Registration No.
    specialization: Optional[str] = None      # e.g., General Medicine, Cardiology, Pediatrics
    hospital_clinic: Optional[str] = None     # Hospital, CHC or Clinic affiliation
    qualification: Optional[str] = None       # MBBS, MD, MS, DNB

    # Staff-specific profile fields (Nurse, Pharmacist, Lab Technician, ASHA)
    staff_designation: Optional[str] = None   # Staff Nurse, Pharmacist, ASHA, ANM, Lab Tech
    employee_id: Optional[str] = None         # Hospital Staff / Employee Code
    department_ward: Optional[str] = None     # Ward, OPD, Emergency, PHC Unit

    # Patient-specific profile fields
    age: Optional[int] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None
    address: Optional[str] = None


class AuthService:
    """
    Creates local prototype profiles. It does not provide authentication or RBAC.
    """

    @classmethod
    def get_google_auth_url(cls, redirect_uri: str, client_id: Optional[str] = None) -> str:
        """
        Fail closed until a complete OAuth callback/session flow is implemented.
        """
        raise RuntimeError(
            "Google sign-in is not implemented: this prototype has no OAuth callback, "
            "state validation, token verification, or secure session management."
        )

    @classmethod
    def create_google_demo_user(cls, role: str = "patient") -> User:
        """
        Returns a synthetic sample profile for tests; it is not authenticated.
        """
        if role == "doctor":
            return User(
                id="doc_aiims_001",
                google_id="google_sub_10928374",
                email="dr.aditi.sharma@aiims.gov.in",
                name="डॉ. अदिति शर्मा (Dr. Aditi Sharma, MD)",
                role="doctor",
                phone="9876543210",
                abha_id="12-3456-7890-1234",
                medical_license_no="MCI-2014-98421",
                specialization="General Medicine (MD)",
                hospital_clinic="नीमराना सामुदायिक स्वास्थ्य केंद्र (CHC)",
                qualification="MBBS, MD (Medicine)",
                profile_pic="👨‍⚕️"
            )
        elif role == "staff":
            return User(
                id="staff_phc_002",
                google_id="google_sub_20394819",
                email="priya.nurse@phc.mohfw.in",
                name="प्रिया वर्मा (Priya Verma - PHC Staff)",
                role="staff",
                phone="9811223344",
                abha_id="14-9876-5432-1098",
                staff_designation="सीनियर स्टाफ नर्स (Senior Staff Nurse)",
                employee_id="EMP-PHC-8819",
                department_ward="ओपीडी व मातृ स्वास्थ्य वार्ड (OPD & Maternal Ward)",
                hospital_clinic="सामुदायिक स्वास्थ्य केंद्र (CHC)",
                profile_pic="🏥"
            )
        else:
            return User(
                id="patient_demo_003",
                google_id="google_sub_30495821",
                email="ramesh.kumar1965@gmail.com",
                name="रमेश कुमार (Ramesh Kumar)",
                role="patient",
                phone="9123456789",
                abha_id="91-1234-5678-9012",
                age=58,
                gender="पुरुष (Male)",
                blood_group="B+",
                emergency_contact="9876500000",
                address="ग्राम नीमराना, अलवर",
                profile_pic="👤"
            )

    @classmethod
    def create_blank_user(cls, role: str = "patient") -> User:
        """
        Creates a blank new user without any pre-existing fake data, ready to collect user data.
        """
        return User(
            id=f"user_{uuid.uuid4().hex[:8]}",
            name="",
            role=role,
            profile_pic="👨‍⚕️" if role == "doctor" else ("🏥" if role == "staff" else "👤")
        )

    @classmethod
    def create_custom_user(
        cls,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        abha_id: Optional[str] = None,
        role: str = "patient",
        medical_license_no: Optional[str] = None,
        specialization: Optional[str] = None,
        hospital_clinic: Optional[str] = None,
        qualification: Optional[str] = None,
        staff_designation: Optional[str] = None,
        employee_id: Optional[str] = None,
        department_ward: Optional[str] = None,
        age: Optional[int] = None,
        gender: Optional[str] = None,
        blood_group: Optional[str] = None,
        emergency_contact: Optional[str] = None,
        address: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> User:
        """
        Creates a local profile record with role-specific fields; it does not register or authenticate a user.
        """
        default_name = "डॉक्टर (Doctor)" if role == "doctor" else ("स्वास्थ्य स्टाफ (Staff)" if role == "staff" else "मरीज (Patient)")
        final_name = name.strip() if (name and name.strip()) else default_name
        return User(
            id=user_id or str(uuid.uuid4())[:8],
            email=email,
            name=final_name,
            role=role,
            phone=phone,
            abha_id=abha_id,
            profile_pic="👨‍⚕️" if role == "doctor" else ("🏥" if role == "staff" else "👤"),
            medical_license_no=medical_license_no,
            specialization=specialization,
            hospital_clinic=hospital_clinic,
            qualification=qualification,
            staff_designation=staff_designation,
            employee_id=employee_id,
            department_ward=department_ward,
            age=age,
            gender=gender,
            blood_group=blood_group,
            emergency_contact=emergency_contact,
            address=address
        )
