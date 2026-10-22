const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  listStudents: () => request("/api/students"),
  createStudent: (data) => request("/api/students", { method: "POST", body: JSON.stringify(data) }),
  updateStudent: (id, data) => request(`/api/students/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteStudent: (id) => request(`/api/students/${id}`, { method: "DELETE" }),
  runDailyCheck: () => request("/api/students/run-daily-check", { method: "POST" }),
  certificateUrl: (id) => `${BASE_URL}/api/students/${id}/certificate`,
};
