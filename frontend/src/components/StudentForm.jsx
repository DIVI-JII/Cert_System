import { useState } from "react";

const empty = {
  name: "",
  phone_number: "",
  course_name: "",
  domain: "",
  start_date: "",
  end_date: "",
};

export default function StudentForm({ onSubmit }) {
  const [form, setForm] = useState(empty);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await onSubmit(form);
      setForm(empty);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="panel form-grid" onSubmit={handleSubmit}>
      <div className="field">
        <label>Student name</label>
        <input required value={form.name} onChange={(e) => update("name", e.target.value)} placeholder="Ananya Rao" />
      </div>
      <div className="field">
        <label>WhatsApp number</label>
        <input
          required
          value={form.phone_number}
          onChange={(e) => update("phone_number", e.target.value)}
          placeholder="919876543210 (with country code)"
        />
      </div>
      <div className="field">
        <label>Course</label>
        <input required value={form.course_name} onChange={(e) => update("course_name", e.target.value)} placeholder="Full Stack Web Development" />
      </div>
      <div className="field">
        <label>Domain</label>
        <input required value={form.domain} onChange={(e) => update("domain", e.target.value)} placeholder="Software Engineering" />
      </div>
      <div className="field">
        <label>Start date</label>
        <input required type="date" value={form.start_date} onChange={(e) => update("start_date", e.target.value)} />
      </div>
      <div className="field">
        <label>End date</label>
        <input required type="date" value={form.end_date} onChange={(e) => update("end_date", e.target.value)} />
      </div>

      {error && <p className="error-text">{error}</p>}

      <button type="submit" className="btn-primary" disabled={submitting}>
        {submitting ? "Adding…" : "Add student"}
      </button>
    </form>
  );
}
