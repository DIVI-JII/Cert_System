import base64
import os

import httpx

from ..config import settings


class WhatsAppSendError(Exception):
    pass


def send_certificate(phone_number: str, student_name: str, course_name: str, pdf_path: str) -> None:
    """
    Sends the certificate PDF to the student's WhatsApp number via the local
    Baileys microservice. Raises WhatsAppSendError on failure so the caller
    can record it and retry on the next scheduler run.
    """
    if not os.path.exists(pdf_path):
        raise WhatsAppSendError(f"Certificate file not found at {pdf_path}")

    with open(pdf_path, "rb") as f:
        file_b64 = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "phone_number": phone_number,  # digits only, country code included, no '+'
        "filename": os.path.basename(pdf_path),
        "file_base64": file_b64,
        "caption": (
            f"Congratulations {student_name}! 🎉\n\n"
            f"Please find attached your certificate of completion for *{course_name}*.\n\n"
            f"- {settings.COURSE_CENTER_NAME}"
        ),
    }

    try:
        response = httpx.post(
            f"{settings.WHATSAPP_SERVICE_URL}/send-document",
            json=payload,
            headers={"Authorization": f"Bearer {settings.WHATSAPP_SERVICE_TOKEN}"},
            timeout=60.0,
        )
    except httpx.RequestError as exc:
        raise WhatsAppSendError(f"Could not reach WhatsApp service: {exc}") from exc

    if response.status_code != 200:
        raise WhatsAppSendError(f"WhatsApp service returned {response.status_code}: {response.text}")

    data = response.json()
    if not data.get("success"):
        raise WhatsAppSendError(data.get("error", "Unknown error from WhatsApp service"))
