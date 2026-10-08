import { useEffect, useState } from "react";
import { api } from "../api/client";
import { PageHeader, Card, Input, Select, Button, Badge, ErrorBanner, EmptyState } from "../components/ui";

const STATUS_TONE = {
  SENT: "gold", PENDING: "slate", ACCEPTED: "green", EXPIRED: "red", CANCELLED: "red", FAILED: "red",
};

const emptyForm = {
  role: "TEACHER", first_name: "", second_name: "", other_name: "", gender: "",
  personal_email: "", phone_number: "",
  employee_id: "", home_grade_id: "", home_stream_id: "",
  admission_number: "", date_of_birth: "", grade_id: "", stream_id: "",
  guardian_name: "", guardian_phone: "", guardian_email: "",
};

export default function Invitations() {
  const [grades, setGrades] = useState([]);
  const [streams, setStreams] = useState([]);
  const [invitations, setInvitations] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const loadInvitations = () => api.get("/invitations").then(setInvitations);

  useEffect(() => {
    api.get("/grades").then(setGrades);
    loadInvitations();
  }, []);

  const relevantGradeId = form.role === "STUDENT" ? form.grade_id : form.home_grade_id;
  useEffect(() => {
    if (relevantGradeId) api.get(`/streams?grade_id=${relevantGradeId}`).then(setStreams);
    else setStreams([]);
  }, [relevantGradeId]);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await api.post("/invitations", form);
      setPreview(res.invitation);
      setForm(emptyForm);
      loadInvitations();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const resend = (id) => api.post(`/invitations/${id}/resend`, {}).then(loadInvitations);
  const cancel = (id) => api.post(`/invitations/${id}/cancel`, {}).then(loadInvitations);

  return (
    <div>
      <PageHeader title="Invite & Invitations" subtitle="Invite teachers, educators and students to activate their SmartMark accounts" />
      <div className="p-8 grid grid-cols-5 gap-6">
        <div className="col-span-2">
          <Card title="Send an invitation">
            <form onSubmit={submit} className="space-y-3">
              <ErrorBanner message={error} />
              <Select label="Invite as" value={form.role} onChange={set("role")}>
                <option value="TEACHER">Teacher</option>
                <option value="EDUCATOR">Educator</option>
                <option value="STUDENT">Student</option>
              </Select>

              <div className="grid grid-cols-2 gap-3">
                <Input label="First name" required value={form.first_name} onChange={set("first_name")} />
                <Input label="Second name" value={form.second_name} onChange={set("second_name")} />
              </div>
              <Input label="Other name" value={form.other_name} onChange={set("other_name")} />
              <Select label="Gender" value={form.gender} onChange={set("gender")}>
                <option value="">Prefer not to say</option>
                <option value="Female">Female</option>
                <option value="Male">Male</option>
              </Select>
              <Input label="Existing personal email" type="email" required value={form.personal_email} onChange={set("personal_email")} placeholder="their.email@gmail.com" />
              <Input label="Phone number" value={form.phone_number} onChange={set("phone_number")} />

              {(form.role === "TEACHER" || form.role === "EDUCATOR") && (
                <>
                  <Input label="Employee / teacher ID" value={form.employee_id} onChange={set("employee_id")} />
                  <Select label="Home grade" value={form.home_grade_id} onChange={set("home_grade_id")}>
                    <option value="">Select grade…</option>
                    {grades.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
                  </Select>
                  <Select label="Home stream" value={form.home_stream_id} onChange={set("home_stream_id")} disabled={!streams.length}>
                    <option value="">Select stream…</option>
                    {streams.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </Select>
                  <p className="text-xs text-slate-500">Subject assignments are set after activation, from the Teachers page.</p>
                </>
              )}

              {form.role === "STUDENT" && (
                <>
                  <Input label="Admission number" required value={form.admission_number} onChange={set("admission_number")} />
                  <Input label="Date of birth" type="date" value={form.date_of_birth} onChange={set("date_of_birth")} />
                  <Select label="Grade" required value={form.grade_id} onChange={set("grade_id")}>
                    <option value="">Select grade…</option>
                    {grades.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
                  </Select>
                  <Select label="Stream" value={form.stream_id} onChange={set("stream_id")} disabled={!streams.length}>
                    <option value="">Select stream…</option>
                    {streams.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </Select>
                  <Input label="Guardian name" value={form.guardian_name} onChange={set("guardian_name")} />
                  <Input label="Guardian phone" value={form.guardian_phone} onChange={set("guardian_phone")} />
                  <Input label="Guardian email" type="email" value={form.guardian_email} onChange={set("guardian_email")} />
                </>
              )}

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Sending…" : "Send invitation"}
              </Button>
            </form>
          </Card>

          {preview && (
            <Card title="Invitation sent" className="mt-4">
              <p className="text-sm text-slate-600">Generated SmartMark account:</p>
              <p className="text-sm font-medium text-ink-950 mt-1">{preview.smartmark_email}</p>
              <p className="text-xs text-slate-500 mt-2">Sent to {preview.personal_email}. Expires {new Date(preview.expires_at).toLocaleString()}.</p>
            </Card>
          )}
        </div>

        <div className="col-span-3">
          <Card title="All invitations" className="p-0">
            {invitations.length === 0 ? (
              <div className="p-5"><EmptyState title="No invitations yet" hint="Sent invitations will appear here with their status." /></div>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs uppercase tracking-wide text-slate-500 border-b border-ink-100">
                    <th className="px-5 py-2">Name</th>
                    <th className="py-2">Role</th>
                    <th className="py-2">Status</th>
                    <th className="py-2">Expires</th>
                    <th className="py-2 pr-5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {invitations.map((inv) => (
                    <tr key={inv.id} className="border-b border-ink-100 last:border-0">
                      <td className="px-5 py-3">
                        <p className="text-ink-950">{inv.recipient_name}</p>
                        <p className="text-xs text-slate-500">{inv.personal_email}</p>
                      </td>
                      <td className="py-3">{inv.role}</td>
                      <td className="py-3"><Badge tone={STATUS_TONE[inv.status] || "slate"}>{inv.status}</Badge></td>
                      <td className="py-3 text-xs text-slate-500">{new Date(inv.expires_at).toLocaleDateString()}</td>
                      <td className="py-3 pr-5 text-right space-x-2">
                        {inv.status !== "ACCEPTED" && inv.status !== "CANCELLED" && (
                          <>
                            <button onClick={() => resend(inv.id)} className="text-xs text-ink-900 underline">Resend</button>
                            <button onClick={() => cancel(inv.id)} className="text-xs text-red-600 underline">Cancel</button>
                          </>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
