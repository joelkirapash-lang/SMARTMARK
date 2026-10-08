import { useEffect, useState } from "react";
import { api } from "../api/client";
import { PageHeader, Card, Select, Button, ErrorBanner, EmptyState } from "../components/ui";

export default function MarksEntry() {
  const [grades, setGrades] = useState([]);
  const [streams, setStreams] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [exams, setExams] = useState([]);

  const [gradeId, setGradeId] = useState("");
  const [streamId, setStreamId] = useState("");
  const [subjectId, setSubjectId] = useState("");
  const [examId, setExamId] = useState("");

  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [savedAt, setSavedAt] = useState(null);

  useEffect(() => {
    api.get("/grades").then(setGrades);
    api.get("/subjects").then(setSubjects);
    api.get("/exams").then(setExams);
  }, []);

  useEffect(() => {
    if (gradeId) api.get(`/streams?grade_id=${gradeId}`).then(setStreams);
    else setStreams([]);
  }, [gradeId]);

  const ready = gradeId && subjectId && examId;

  useEffect(() => {
    if (!ready) { setRows([]); return; }
    setError("");
    const qs = new URLSearchParams({ exam_id: examId, grade_id: gradeId, subject_id: subjectId });
    if (streamId) qs.set("stream_id", streamId);
    api.get(`/marks/grid?${qs}`).then((d) => setRows(d.rows)).catch((e) => setError(e.message));
  }, [gradeId, streamId, subjectId, examId]);

  const updateScore = (studentId, value) => {
    setRows((rs) => rs.map((r) => (r.student_id === studentId ? { ...r, score: value } : r)));
  };

  const handlePaste = (startIndex) => (e) => {
    const text = e.clipboardData.getData("text");
    const values = text.split(/\r?\n/).map((v) => v.trim()).filter((v) => v !== "");
    if (values.length <= 1) return; // let default paste handle a single value
    e.preventDefault();
    setRows((rs) => {
      const next = [...rs];
      for (let i = 0; i < values.length && startIndex + i < next.length; i++) {
        next[startIndex + i] = { ...next[startIndex + i], score: values[i] };
      }
      return next;
    });
  };

  const save = async () => {
    setSaving(true);
    setError("");
    try {
      const res = await api.post("/marks/grid", {
        exam_id: examId, grade_id: gradeId, stream_id: streamId || null, subject_id: subjectId,
        rows: rows.map((r) => ({ student_id: r.student_id, score: r.score === "" ? null : r.score, max_score: r.max_score })),
      });
      if (res.errors?.length) {
        setError(res.errors.map((e) => e.error).join("; "));
      }
      setSavedAt(new Date());
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <PageHeader title="Marks Entry" subtitle="Select a class, exam and subject, then enter or paste scores" />
      <div className="p-8 space-y-4">
        <div className="grid grid-cols-4 gap-3">
          <Select label="Grade" value={gradeId} onChange={(e) => { setGradeId(e.target.value); setStreamId(""); }}>
            <option value="">Select grade…</option>
            {grades.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
          </Select>
          <Select label="Stream" value={streamId} onChange={(e) => setStreamId(e.target.value)} disabled={!streams.length}>
            <option value="">All streams</option>
            {streams.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </Select>
          <Select label="Exam" value={examId} onChange={(e) => setExamId(e.target.value)}>
            <option value="">Select exam…</option>
            {exams.map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}
          </Select>
          <Select label="Subject" value={subjectId} onChange={(e) => setSubjectId(e.target.value)}>
            <option value="">Select subject…</option>
            {subjects.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </Select>
        </div>

        <ErrorBanner message={error} />

        {!ready ? (
          <EmptyState title="Choose a grade, exam and subject" hint="The score grid will appear once all three are selected." />
        ) : (
          <Card className="p-0">
            <div className="px-5 py-3 border-b border-ink-100 flex items-center justify-between">
              <p className="text-sm text-slate-500">Tip: paste a column of scores from Excel directly into the first score box.</p>
              <Button onClick={save} disabled={saving}>{saving ? "Saving…" : "Save marks"}</Button>
            </div>
            {rows.length === 0 ? (
              <div className="p-5"><EmptyState title="No students in this class yet" /></div>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs uppercase tracking-wide text-slate-500 border-b border-ink-100">
                    <th className="px-5 py-2">Student</th>
                    <th className="py-2">Adm. No.</th>
                    <th className="py-2 w-32">Score</th>
                    <th className="py-2 w-24">Out of</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((r, i) => (
                    <tr key={r.student_id} className="border-b border-ink-100 last:border-0">
                      <td className="px-5 py-2">{r.student_name}</td>
                      <td className="py-2 text-slate-500">{r.admission_number}</td>
                      <td className="py-2">
                        <input
                          type="number"
                          className="w-24 rounded border border-ink-200 px-2 py-1 focus-ring"
                          value={r.score ?? ""}
                          onChange={(e) => updateScore(r.student_id, e.target.value)}
                          onPaste={handlePaste(i)}
                        />
                      </td>
                      <td className="py-2 text-slate-500">{r.max_score}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            {savedAt && <p className="px-5 py-2 text-xs text-slate-400">Saved {savedAt.toLocaleTimeString()}</p>}
          </Card>
        )}
      </div>
    </div>
  );
}
