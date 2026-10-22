import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..scheduler import run_daily_certificate_job

router = APIRouter(prefix="/api/students", tags=["students"])


@router.post("", response_model=schemas.StudentOut, status_code=201)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    return crud.create_student(db, student)


@router.get("", response_model=list[schemas.StudentOut])
def list_students(db: Session = Depends(get_db)):
    return crud.get_students(db)


@router.get("/{student_id}", response_model=schemas.StudentOut)
def get_student(student_id: uuid.UUID, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.patch("/{student_id}", response_model=schemas.StudentOut)
def update_student(student_id: uuid.UUID, updates: schemas.StudentUpdate, db: Session = Depends(get_db)):
    student = crud.update_student(db, student_id, updates)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.delete("/{student_id}", status_code=204)
def delete_student(student_id: uuid.UUID, db: Session = Depends(get_db)):
    if not crud.delete_student(db, student_id):
        raise HTTPException(status_code=404, detail="Student not found")


@router.get("/{student_id}/certificate")
def download_certificate(student_id: uuid.UUID, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if not student or not student.certificate_file_path:
        raise HTTPException(status_code=404, detail="Certificate not generated yet")
    return FileResponse(
        student.certificate_file_path,
        media_type="application/pdf",
        filename=f"{student.name.replace(' ', '_')}_certificate.pdf",
    )


@router.post("/run-daily-check", status_code=202)
def trigger_daily_check_manually():
    """
    Lets the admin manually trigger the same job the scheduler runs every day —
    useful for testing, or for catching up if the server was down at the
    scheduled time.
    """
    run_daily_certificate_job()
    return {"message": "Daily certificate check executed"}
