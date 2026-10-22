import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from . import crud
from .config import settings
from .database import SessionLocal
from .services.certificate_gen import generate_certificate
from .services.whatsapp_client import send_certificate, WhatsAppSendError

logger = logging.getLogger("certificate_scheduler")


def run_daily_certificate_job():
    """
    Core automation:
    1. Find students whose end_date == today and who haven't been sent a certificate yet.
    2. Generate the certificate PDF (if not already generated).
    3. Send it over WhatsApp from the course center's number.
    4. Update the database so the dashboard reflects the new status.

    Safe to re-run: it only ever acts on students where certificate_sent is False,
    so a retry after a failure will pick up exactly where it left off.
    """
    db = SessionLocal()
    try:
        due_students = crud.get_students_due_today(db)
        logger.info("Certificate job: %d student(s) due today", len(due_students))

        for student in due_students:
            try:
                crud.mark_completed(db, student)

                pdf_path = student.certificate_file_path
                if not pdf_path:
                    pdf_path = generate_certificate(
                        student_id=str(student.id),
                        student_name=student.name,
                        course_name=student.course_name,
                        domain=student.domain,
                        start_date=student.start_date,
                        end_date=student.end_date,
                    )
                    crud.mark_certificate_generated(db, student, pdf_path)

                send_certificate(
                    phone_number=student.phone_number,
                    student_name=student.name,
                    course_name=student.course_name,
                    pdf_path=pdf_path,
                )

                crud.mark_certificate_sent(db, student)
                logger.info("Certificate sent to %s (%s)", student.name, student.phone_number)

            except WhatsAppSendError as exc:
                crud.record_send_error(db, student, str(exc))
                logger.error("Failed to send certificate to %s: %s", student.name, exc)
            except Exception as exc:  # noqa: BLE001 - keep the loop going for other students
                crud.record_send_error(db, student, f"Unexpected error: {exc}")
                logger.exception("Unexpected error processing student %s", student.id)
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    hour, minute = settings.DAILY_JOB_TIME.split(":")
    scheduler.add_job(
        run_daily_certificate_job,
        trigger=CronTrigger(hour=int(hour), minute=int(minute)),
        id="daily_certificate_job",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started, daily job set for %s IST", settings.DAILY_JOB_TIME)
    return scheduler
