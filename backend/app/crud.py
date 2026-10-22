import uuid
from datetime import date

from sqlalchemy.orm import Session

from . import models, schemas


def create_student(db: Session, student: schemas.StudentCreate) -> models.Student:
    db_student = models.Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def get_students(db: Session):
    return db.query(models.Student).order_by(models.Student.end_date.asc()).all()


def get_student(db: Session, student_id: uuid.UUID):
    return db.query(models.Student).filter(models.Student.id == student_id).first()


def update_student(db: Session, student_id: uuid.UUID, updates: schemas.StudentUpdate):
    db_student = get_student(db, student_id)
    if not db_student:
        return None
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_student, field, value)
    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, student_id: uuid.UUID) -> bool:
    db_student = get_student(db, student_id)
    if not db_student:
        return False
    db.delete(db_student)
    db.commit()
    return True


def get_students_due_today(db: Session, today: date = None):
    """Students whose end_date is today and who have not yet been sent a certificate."""
    today = today or date.today()
    return (
        db.query(models.Student)
        .filter(models.Student.end_date == today)
        .filter(models.Student.certificate_sent.is_(False))
        .all()
    )


def mark_completed(db: Session, student: models.Student):
    student.status = models.StudentStatus.completed
    db.commit()


def mark_certificate_generated(db: Session, student: models.Student, file_path: str):
    student.certificate_generated = True
    student.certificate_file_path = file_path
    db.commit()


def mark_certificate_sent(db: Session, student: models.Student):
    from datetime import datetime

    student.certificate_sent = True
    student.certificate_sent_at = datetime.utcnow()
    student.last_send_error = None
    db.commit()


def record_send_error(db: Session, student: models.Student, error: str):
    student.last_send_error = error
    db.commit()
