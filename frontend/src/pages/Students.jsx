import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import { PageHeader, Card, Select, Button, Badge, EmptyState, Input } from "../components/ui";

export default function Students() {
  const [grades, setGrades] = useState([]);
  const [streams, setStreams] = useState([]);
  const [students, setStudents] = useState([]);
  const [gradeId, setGradeId] = useState("");
  const [streamId, setStreamId] = useState("");
  const [search, setSearch] = useState("");
  const [importResult, setImportResult] = useState(null);
  const fileRef = useRef();

  useEffect(() => { api.get("/grades").then(setGrades); }, []);
  useEffect(() => {
    if (gradeId) api.get(`/streams?grade_id=${gradeId}`).then(setStreams);
    else setStreams([]);
  }, [gradeId]);

  const load = () => {
    const qs = new URLSearchParams();
    if (gradeId) qs.set("grade_id", gradeId);
    if (streamId) qs.set("stream_id", streamId);
    if (search) qs.set("search", search);
    api.get(`/students?${qs.toString()}`).then(setStudents);
  };
  useEffect(load, [gradeId, streamId, search]);

  const importCsv = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    const res = await api.postForm("/students/bulk-import", formData);
    setImportResult(res);
    load();
    fileRef.current.value = "";
  };

  return (
    <div>
      <PageHeader
        title="Students"
        subtitle="Manage learners and bulk-import class rosters"
        actions={
          <>
            <input type="file" accept=".csv" ref={fileRef} onChange={importCsv} className="hidden" id="csv-input" />
            <Button variant="gold" onClick={() => fileRef.current.click()}>Bulk import CSV</Button>
          </>
        }
      />
      <div className="p-8 space-y-4">
        {importResult && (
          <Card title="Import result">
            <p className="text-sm text-green-700">{importResult.created.length} student(s) created.</p>
            {importResult.errors.length > 0 && (
              <ul className="text-sm text-red-600 mt-2 list-disc pl-5">
                {importResult.errors.map((e, i) => <li key={i}>Row {e.row}: {e.error}</li>)}
              </ul>
            )}
          </Card>
        )}

        <div className="flex gap-3">
          <Select value={gradeId} onChange={(e) => { setGradeId(e.target.value); setStreamId(""); }}>
            <option value="">All grades</option>
            {grades.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
          </Select>
          <Select value={streamId} onChange={(e) => setStreamId(e.target.value)} disabled={!streams.length}>
            <option value="">All streams</option>
            {streams.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </Select>
          <Input placeholder="Search by name or admission no." value={search} onChange={(e) => setSearch(e.target.value)} className="max-w-xs" />
        </div>

        <Card className="p-0">
          {students.length === 0 ? (
            <div className="p-5"><EmptyState title="No students found" hint="Invite students individually, or bulk-import a CSV roster." /></div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wide text-slate-500 border-b border-ink-100">
                  <th className="px-5 py-2">Name</th>
                  <th className="py-2">Admission No.</th>
                  <th className="py-2">Status</th>
                  <th className="py-2 pr-5">SmartMark email</th>
                </tr>
              </thead>
              <tbody>
                {students.map((s) => (
                  <tr key={s.id} className="border-b border-ink-100 last:border-0">
                    <td className="px-5 py-3">{s.first_name} {s.second_name}</td>
                    <td className="py-3">{s.admission_number || "—"}</td>
                    <td className="py-3"><Badge tone={s.status === "ACTIVE" ? "green" : "slate"}>{s.status}</Badge></td>
                    <td className="py-3 pr-5 text-xs text-slate-500">{s.smartmark_email}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Card>

        <Card title="CSV format">
          <p className="text-xs text-slate-500">
            Columns: first_name, second_name, other_name, admission_number, gender, date_of_birth (YYYY-MM-DD),
            personal_email, phone_number, grade_id, stream_id, guardian_name, guardian_phone, guardian_email.
            Find grade_id/stream_id values on the Grades, Streams &amp; Subjects page.
          </p>
        </Card>
      </div>
    </div>
  );
}
