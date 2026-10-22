import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .models import StudentStatus


class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    phone_number: str = Field(..., description="International format digits only, e.g. 919876543210")
    course_name: str = Field(..., min_length=1, max_length=200)
    domain: str = Field(..., min_length=1, max_length=200)
    start_date: date
    end_date: date

    @field_validator("phone_number")
    @classmethod
    def clean_phone(cls, v: str) -> str:
        digits = "".join(ch for ch in v if ch.isdigit())
        if len(digits) < 10:
            raise ValueError("phone_number must include country code and be at least 10 digits")
        return digits

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, v: date, info):
        start = info.data.get("start_date")
        if start and v < start:
            raise ValueError("end_date cannot be before start_date")
        return v


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    course_name: Optional[str] = None
    domain: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @field_validator("phone_number")
    @classmethod
    def clean_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        digits = "".join(ch for ch in v if ch.isdigit())
        if len(digits) < 10:
            raise ValueError("phone_number must include country code and be at least 10 digits")
        return digits


class StudentOut(StudentBase):
    id: uuid.UUID
    status: StudentStatus
    certificate_generated: bool
    certificate_sent: bool
    certificate_sent_at: Optional[datetime] = None
    certificate_file_path: Optional[str] = None
    last_send_error: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
