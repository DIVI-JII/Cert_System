import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # PostgreSQL connection string
    # Example: postgresql://postgres:password@localhost:5432/certificate_db
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:password@localhost:5432/certificate_db"
    )

    # Where the Node.js Baileys microservice is running
    WHATSAPP_SERVICE_URL: str = os.getenv("WHATSAPP_SERVICE_URL", "http://localhost:4001")

    # Shared secret so only our backend can call the whatsapp microservice
    WHATSAPP_SERVICE_TOKEN: str = os.getenv("WHATSAPP_SERVICE_TOKEN", "change-me")

    # Course center identity, printed on the certificate
    COURSE_CENTER_NAME: str = os.getenv("COURSE_CENTER_NAME", "Your Course Center")

    # Certificate signatory block
    SIGNATORY_NAME: str = os.getenv("SIGNATORY_NAME", "Divya")
    SIGNATORY_TITLE: str = os.getenv("SIGNATORY_TITLE", "Program Coordinator")

    # Footer contact strip on the certificate (leave blank to omit a line)
    COURSE_CENTER_EMAIL: str = os.getenv("COURSE_CENTER_EMAIL", "")
    COURSE_CENTER_PHONE: str = os.getenv("COURSE_CENTER_PHONE", "")
    COURSE_CENTER_WEBSITE: str = os.getenv("COURSE_CENTER_WEBSITE", "")
    COURSE_CENTER_ADDRESS: str = os.getenv("COURSE_CENTER_ADDRESS", "")

    # Folder where generated certificate PDFs are stored
    CERTIFICATES_DIR: str = os.getenv(
        "CERTIFICATES_DIR", os.path.join(os.path.dirname(__file__), "..", "generated_certificates")
    )

    # Time (24h, server timezone) the daily job runs, "HH:MM"
    DAILY_JOB_TIME: str = os.getenv("DAILY_JOB_TIME", "09:00")

    # CORS - the frontend origin allowed to call this API
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


settings = Settings()
os.makedirs(settings.CERTIFICATES_DIR, exist_ok=True)