# Automatic Certificate Generator

A dashboard for a course center to manage students and automatically issue &
deliver completion certificates over WhatsApp on the student's end date.

## How it works

```
┌─────────────┐      ┌───────────────────┐      ┌────────────────────┐
│   React     │◄────►│   FastAPI backend │◄────►│  PostgreSQL         │
│  Dashboard  │      │  (students API,   │      │  (students table)   │
└─────────────┘      │  certificate PDF, │      └────────────────────┘
                      │  daily scheduler) │
                      └─────────┬─────────┘
                                │ HTTP (local)
                                ▼
                      ┌───────────────────┐      ┌────────────────────┐
                      │  Node.js service  │◄────►│  WhatsApp (Baileys) │
                      │  (Baileys)        │      │  course center #    │
                      └───────────────────┘      └────────────────────┘
```

1. Admin adds a student (name, WhatsApp number, course, domain, start date, end date) in the dashboard.
2. A background scheduler in the FastAPI backend runs once a day (default 9:00 AM IST, configurable). It finds every student whose `end_date` is today and who hasn't been sent a certificate yet.
3. For each one it generates a certificate PDF (ReportLab), then calls the Node.js/Baileys microservice to send that PDF as a WhatsApp document from the course center's number.
4. On success, the database is updated (`certificate_sent = true`, timestamp recorded) so the dashboard reflects it immediately. On failure (e.g. WhatsApp temporarily disconnected), the error is recorded and the student is retried automatically on the next run since `certificate_sent` is still `false`.
5. The dashboard lists every student with live status (ongoing / awaiting send / sent / failed) and a download link for the generated PDF.

## Why two backend services (FastAPI + Node)?

Baileys, the library used to send WhatsApp messages from an ordinary phone
number for free, only exists for Node.js. Rather than switching the whole
project to Node, the small WhatsApp-sending piece is isolated in its own
service that the Python backend calls over HTTP. If you later move to
Meta's official WhatsApp Cloud API (recommended for real production use —
see "Going to real production" below), you only need to replace
`backend/app/services/whatsapp_client.py`; nothing else changes.

## Project structure

```
certificate-generator/
├── backend/            FastAPI app, PostgreSQL models, scheduler, PDF generation
├── whatsapp-service/   Node.js + Baileys microservice that sends WhatsApp messages
├── frontend/           React admin dashboard (Vite)
└── docker-compose.yml  Runs Postgres + both backend services together
```

## Running it locally

### Option A — Docker Compose (recommended)

```bash
docker compose up --build
```

Then, the **first time only**, watch the WhatsApp service logs and scan the QR code with the course center's phone (WhatsApp app → Linked Devices → Link a device):

```bash
docker compose logs -f whatsapp-service
```

The session is saved in a Docker volume, so you won't need to scan again unless you log out.

Then run the frontend separately (Compose doesn't build it, since you'll be actively developing it):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

### Option B — Run everything manually

**1. PostgreSQL** — create a database named `certificate_db` (or update `DATABASE_URL`).

**2. WhatsApp microservice**
```bash
cd whatsapp-service
cp .env.example .env      # edit WHATSAPP_SERVICE_TOKEN to a random string
npm install
npm start
```
Scan the QR code that appears in the terminal with the course center's WhatsApp.

**3. Backend**
```bash
cd backend
cp .env.example .env      # make sure WHATSAPP_SERVICE_TOKEN matches the one above
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs available at http://localhost:8000/docs

**4. Frontend**
```bash
cd frontend
npm install
npm run dev
```

## Testing the automation without waiting for a real end date

- Add a student with `end_date` set to today.
- Click **"Run today's check now"** in the dashboard header (calls `POST /api/students/run-daily-check`), which runs the exact same job the scheduler runs automatically every day.
- Check the course center's WhatsApp — the certificate should arrive as a PDF document — and confirm the dashboard now shows "Certificate sent".

## Important operational notes

- **Phone number format**: store numbers as country code + number with no `+`, spaces, or leading zero (e.g. `919876543210` for an Indian number). The form validates this.
- **Baileys and WhatsApp's terms**: Baileys is an unofficial client. It's the right tool for a prototype or a small operation, but WhatsApp can rate-limit or ban numbers that send a lot of automated messages. Keep sending volumes modest, and avoid sending identical messages to many numbers back-to-back.
- **Retries**: a student is only ever marked `certificate_sent = true` after a confirmed successful send, so any failure (WhatsApp disconnected, invalid number, network issue) is automatically retried the next day. You can also see the specific error on the dashboard.
- **Idempotency**: the certificate PDF is generated once and reused — the job checks `certificate_file_path` before regenerating.

## Going to real production

For a course center that will run this long-term and at real scale, consider:

1. **Switch to the official WhatsApp Cloud API** (Meta) instead of Baileys — no ban risk, an official business-verified number, and a stable SLA. Only `whatsapp_client.py` needs to change; the API contract (`phone_number`, PDF, caption) stays the same.
2. **Authentication** on the dashboard itself (this scaffold has none — add login for the admin, e.g. via FastAPI's OAuth2/JWT support, before exposing it beyond your own machine).
3. **Move certificate storage to S3 or similar** instead of local disk, so it survives redeploys and scales across multiple backend instances.
4. **Add a message-queue-backed retry policy** (e.g. Celery + Redis) instead of a simple daily cron if you want faster retries than "once a day."
5. **Backups** for the PostgreSQL database.
