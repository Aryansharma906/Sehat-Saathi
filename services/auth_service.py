"""
Authentication & Identity Service for Sehat Saathi
Supports Google Sign-In (OAuth 2.0), ABHA ID / Phone login, and Role-Based Access Control (RBAC)
for Patients, Doctors, and Hospital/PHC Staff.
"""

import os
import uuid
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    google_id: Optional[str] = None
    email: Optional[str] = None
    name: str = "अतिथि मरीज (Guest Patient)"
    role: str = "patient"  # "patient", "doctor", "staff"
    phone: Optional[str] = None
    abha_id: Optional[str] = None  # Ayushman Bharat Health Account ID
    profile_pic: Optional[str] = None
    created_at: Optional[str] = None


class AuthService:
    """
    Manages user authentication, Google Sign-In, and RBAC permissions.
    """

    GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"

    @classmethod
    def get_google_auth_url(cls, redirect_uri: str, client_id: Optional[str] = None) -> str:
        """
        Builds Google OAuth 2.0 authorization URL.
        """
        cid = client_id or os.environ.get("GOOGLE_CLIENT_ID", "DEMO_GOOGLE_CLIENT_ID.apps.googleusercontent.com")
        scope = "openid%20email%20profile"
        state = str(uuid.uuid4())
        return (
            f"{cls.GOOGLE_AUTH_ENDPOINT}?"
            f"client_id={cid}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope={scope}&"
            f"state={state}&"
            f"access_type=offline"
        )

    @classmethod
    def create_google_demo_user(cls, role: str = "patient") -> User:
        """
        Creates an authenticated Google profile for instant testing and demonstration.
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
                profile_pic="🏥"
            )
        else:
            return User(
                id="patient_demo_003",
                google_id="google_sub_30495821",
                email="ramesh.kumar1965@gmail.com",
                name="रमेश कुमार (Ramesh Kumar - 58 yrs)",
                role="patient",
                phone="9123456789",
                abha_id="91-1234-5678-9012",
                profile_pic="👤"
            )

    @classmethod
    def create_custom_user(cls, name: str, email: Optional[str], phone: Optional[str], abha_id: Optional[str], role: str = "patient") -> User:
        """
        Creates a custom registered user profile with ABHA / Phone credentials.
        """
        return User(
            id=str(uuid.uuid4())[:8],
            email=email,
            name=name.strip() if name and name.strip() else "मरीज (Patient)",
            role=role,
            phone=phone,
            abha_id=abha_id,
            profile_pic="👨‍⚕️" if role == "doctor" else ("🏥" if role == "staff" else "👤")
        )
