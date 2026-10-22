import { useState } from "react";
import { api } from "../api";

function daysUntil(endDate) {
  const diff = Math.ceil((new Date(endDate) - new Date(new Date().toDateString())) / (1000 * 60 * 60 * 24));
  return diff;
}

function StatusPill({ student }) {
  if (student.certificate_sent) {
    return <span className="pill pill-sent">Certificate sent</span>;
  }
  if (student.last_send_error) {
    return <span className="pill pill-error" title={student.last_send_error}>Send failed</span>;
  }
  if (student.status === "completed") {
    return <span className="pill pill-pending">Pending send</span>;
  }
  const days = daysUntil(student.end_date);
  return <span className="pill pill-ongoing">{days > 0 ? `${days} day(s) left` : "Ongoing"}</span>;
}

// Converts an ISO datetime/date string to yyyy-mm-dd for <input type="date">
function toDateInputValue(value) {
  return value ? new Date(value).toISOString().slice(0, 10) : "";
}

function EditRow({ student, onSave, onCancel }) {
  const [form, setForm] = useState({
    name: student.name,
    phone_number: student.phone_number,
    course_name: student.course_name,
    domain: student.domain,
    start_date: toDateInputValue(student.start_date),
    end_date: toDateInputValue(student.end_date),
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      await onSave(form);
    } catch (err) {
      setError(err.message);
      setSaving(false);
    }
  }

  return (
    <tr className="edit-row">
      <td colSpan={6}>
        <div className="edit-grid">
          <input value={form.name} onChange={(e) => update("name", e.target.value)} placeholder="Name" />
          <input value={form.phone_number} onChange={(e) => update("phone_number", e.target.value)} placeholder="WhatsApp number" />
          <input value={form.course_name} onChange={(e) => update("course_name", e.target.value)} placeholder="Course" />
          <input value={form.domain} onChange={(e) => update("domain", e.target.value)} placeholder="Domain" />
          <input type="date" value={form.start_date} onChange={(e) => update("start_date", e.target.value)} />
          <input type="date" value={form.end_date} onChange={(e) => update("end_date", e.target.value)} />
          <div className="edit-actions">
            <button className="btn-primary btn-small" onClick={handleSave} disabled={saving}>
              {saving ? "Saving…" : "Save"}
            </button>
            <button className="btn-ghost" onClick={onCancel} disabled={saving}>Cancel</button>
          </div>
        </div>
        {error && <p className="error-text">{error}</p>}
      </td>
    </tr>
  );
}

export default function StudentTable({ students, onChanged }) {
  const [editingId, setEditingId] = useState(null);

  async function handleDelete(id) {
    if (!confirm("Remove this student's record?")) return;
    await api.deleteStudent(id);
    onChanged();
  }

  async function handleSaveEdit(id, updates) {
    // PATCH only sends changed fields; backend updates Postgres and returns the fresh row
    await api.updateStudent(id, updates);
    setEditingId(null);
    onChanged();
  }

  if (students.length === 0) {
    return <p className="empty-state">No students yet — add one above to get started.</p>;
  }

  return (
    <div className="panel table-wrap">
      <table>
        <thead>
          <tr>
            <th>Student</th>
            <th>Course / Domain</th>
            <th>Ends</th>
            <th>Status</th>
            <th>Certificate</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {students.map((s) =>
            editingId === s.id ? (
              <EditRow
                key={s.id}
                student={s}
                onSave={(updates) => handleSaveEdit(s.id, updates)}
                onCancel={() => setEditingId(null)}
              />
            ) : (
              <tr key={s.id}>
                <td>
                  <div className="student-name">{s.name}</div>
                  <div className="student-phone">+{s.phone_number}</div>
                </td>
                <td>
                  <div>{s.course_name}</div>
                  <div className="muted">{s.domain}</div>
                </td>
                <td>{new Date(s.end_date).toLocaleDateString()}</td>
                <td><StatusPill student={s} /></td>
                <td>
                  {s.certificate_generated ? (
                    <a className="link" href={api.certificateUrl(s.id)} target="_blank" rel="noreferrer">
                      Download PDF
                    </a>
                  ) : (
                    <span className="muted">Not generated</span>
                  )}
                </td>
                <td className="row-actions">
                  <button className="btn-ghost btn-edit" onClick={() => setEditingId(s.id)}>Edit</button>
                  <button className="btn-ghost" onClick={() => handleDelete(s.id)}>Remove</button>
                </td>
              </tr>
            )
          )}
        </tbody>
      </table>
    </div>
  );
}
