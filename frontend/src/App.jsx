import { useEffect, useState, useCallback } from "react";
import { api } from "./api";
import StudentForm from "./components/StudentForm";
import StudentTable from "./components/StudentTable";

export default function App() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [banner, setBanner] = useState(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.listStudents();
      setStudents(data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function handleAdd(data) {
    await api.createStudent(data);
    await refresh();
  }

  async function handleRunCheck() {
    setBanner("Running today's certificate check…");
    try {
      await api.runDailyCheck();
      await refresh();
      setBanner("Daily check complete.");
    } catch (err) {
      setBanner(`Check failed: ${err.message}`);
    } finally {
      setTimeout(() => setBanner(null), 4000);
    }
  }

  const sentCount = students.filter((s) => s.certificate_sent).length;
  const pendingCount = students.filter((s) => s.status === "completed" && !s.certificate_sent).length;

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Course Center Admin</p>
          <h1>Certificate Desk</h1>
        </div>
        <button className="btn-secondary" onClick={handleRunCheck}>Run today's check now</button>
      </header>

      {banner && <div className="banner">{banner}</div>}

      <section className="stats-row">
        <div className="stat-card">
          <span className="stat-number">{students.length}</span>
          <span className="stat-label">Total students</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">{sentCount}</span>
          <span className="stat-label">Certificates sent</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">{pendingCount}</span>
          <span className="stat-label">Awaiting send</span>
        </div>
      </section>

      <section>
        <h2 className="section-title">Add a student</h2>
        <StudentForm onSubmit={handleAdd} />
      </section>

      <section>
        <h2 className="section-title">Students</h2>
        {loading ? <p className="muted">Loading…</p> : <StudentTable students={students} onChanged={refresh} />}
      </section>
    </div>
  );
}
