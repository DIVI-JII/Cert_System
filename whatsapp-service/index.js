/**
 * WhatsApp sending microservice for the Automatic Certificate Generator.
 *
 * Uses Baileys (unofficial WhatsApp Web multi-device protocol) to log in as
 * the course center's own WhatsApp number, then exposes a small local HTTP
 * API that the Python/FastAPI backend calls to deliver certificate PDFs.
 *
 * First run: a QR code prints in this terminal. Scan it with the course
 * center's WhatsApp app (Linked Devices > Link a device). After that, login
 * session is cached in ./auth_session so you won't need to scan again unless
 * you log out or the session expires.
 */

require("dotenv").config();

const express = require("express");
const qrcode = require("qrcode-terminal");
const pino = require("pino");
const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
} = require("@whiskeysockets/baileys");

const PORT = process.env.PORT || 4001;
const AUTH_TOKEN = process.env.WHATSAPP_SERVICE_TOKEN || "change-me";
const AUTH_FOLDER = process.env.AUTH_FOLDER || "./auth_session";

const logger = pino({ level: process.env.LOG_LEVEL || "info" });

let sock = null;
let isReady = false;

async function connectToWhatsApp() {
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_FOLDER);
  const { version } = await fetchLatestBaileysVersion();

  sock = makeWASocket({
    version,
    auth: state,
    logger: pino({ level: "silent" }), // keep Baileys' internal logs quiet
    printQRInTerminal: false,
  });

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("connection.update", (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      logger.info("Scan this QR code with the course center's WhatsApp (Linked Devices):");
      qrcode.generate(qr, { small: true });
    }

    if (connection === "open") {
      isReady = true;
      logger.info("WhatsApp connected successfully.");
    }

    if (connection === "close") {
      isReady = false;
      const statusCode = lastDisconnect?.error?.output?.statusCode;
      const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
      logger.warn(`Connection closed (code ${statusCode}). Reconnecting: ${shouldReconnect}`);
      if (shouldReconnect) {
        connectToWhatsApp();
      } else {
        logger.error("Logged out. Delete the auth_session folder and restart to re-link.");
      }
    }
  });
}

function requireAuth(req, res, next) {
  const header = req.headers.authorization || "";
  const token = header.replace("Bearer ", "");
  if (token !== AUTH_TOKEN) {
    return res.status(401).json({ success: false, error: "Unauthorized" });
  }
  next();
}

function toJid(phoneNumber) {
  const digits = phoneNumber.replace(/\D/g, "");
  return `${digits}@s.whatsapp.net`;
}

const app = express();
app.use(express.json({ limit: "15mb" })); // certificates are small PDFs, generous headroom

app.get("/health", (req, res) => {
  res.json({ success: true, whatsapp_ready: isReady });
});

app.post("/send-document", requireAuth, async (req, res) => {
  const { phone_number, filename, file_base64, caption } = req.body || {};

  if (!phone_number || !file_base64) {
    return res.status(400).json({ success: false, error: "phone_number and file_base64 are required" });
  }
  if (!isReady) {
    return res.status(503).json({ success: false, error: "WhatsApp is not connected yet. Scan the QR code and retry." });
  }

  try {
    const jid = toJid(phone_number);
    const buffer = Buffer.from(file_base64, "base64");

    // Confirm this number actually exists on WhatsApp before sending
    const [result] = await sock.onWhatsApp(jid);
    if (!result?.exists) {
      return res.status(422).json({ success: false, error: `${phone_number} is not a valid WhatsApp number` });
    }

    await sock.sendMessage(jid, {
      document: buffer,
      fileName: filename || "certificate.pdf",
      mimetype: "application/pdf",
      caption: caption || "",
    });

    logger.info(`Certificate sent to ${phone_number}`);
    res.json({ success: true });
  } catch (err) {
    logger.error(err, "Failed to send document");
    res.status(500).json({ success: false, error: err.message });
  }
});

app.listen(PORT, () => {
  logger.info(`WhatsApp microservice listening on port ${PORT}`);
  connectToWhatsApp();
});
