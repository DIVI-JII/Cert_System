import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Date, DateTime, Boolean, Enum, Text
from sqlalchemy.dialects.postgresql import UUID

from .database import Base


class StudentStatus(str, enum.Enum):
    ongoing = "ongoing"
    completed = "completed"


class Student(Base):
    __tablename__ = "students"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, nullable=False)
    # Full international format e.g. 919876543210 (country code, no +, no spaces)
    phone_number = Column(String, nullable=False)

    course_name = Column(String, nullable=False)
    domain = Column(String, nullable=False)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    status = Column(Enum(StudentStatus), default=StudentStatus.ongoing, nullable=False)

    certificate_generated = Column(Boolean, default=False, nullable=False)
    certificate_sent = Column(Boolean, default=False, nullable=False)
    certificate_sent_at = Column(DateTime, nullable=True)
    certificate_file_path = Column(String, nullable=True)

    # Records the reason if an automatic send attempt failed, shown on dashboard
    last_send_error = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
