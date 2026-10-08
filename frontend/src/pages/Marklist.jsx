import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { PageHeader, Card, Select, Button, EmptyState } from "../components/ui";

export default function Marklist() {
  const [grades, setGrades] = useState([]);
  const [streams, setStreams] = useState([]);
  const [exams, setExams] = useState([]);
  const [gradeId, setGradeId] = useState("");
  const [streamId, setStreamId] = useState("");
  const [examId, setExamId] = useState("");
  const [marklist, setMarklist] = useState(null);

  useEffect(() => {
    api.get("/grades").then(setGrades);
    api.get("/exams").then(setExams);
  }, []);

  useEffect(() => {
    if (gradeId) api.get(`/streams?grade_id=${gradeId}`).then(setStreams);
    else setStreams([]);
  }, [gradeId]);

  useEffect(() => {
    if (gradeId && examId) {
      const qs = new URLSearchParams({ exam_id: examId, grade_id: gradeId });
      if (streamId) qs.set("stream_id", streamId);
      api.get(`/marklist?${qs}`).then((d) => setMarklist(d.marklist));
    } else {
      setMarklist(null);
    }
  }, [gradeId, streamId, examId]);

  const exportUrl = () => {
    const qs = new URLSearchParams({ exam_id: examId, grade_id: gradeId });
    if (streamId) qs.set("stream_id", streamId);
    return api.downloadUrl(`/marklist/export?${qs}`);
  };

  return (
    <div>
      <PageHeader
        title="Marklists"
        subtitle="Ranked class marklist per grade, stream and exam"
        actions={
          marklist && (
            <>
              <Button variant="outline" onClick={() => window.print()}>Print</Button>
              <a href={exportUrl()}><Button variant="gold">Export Excel</Button></a>
            </>
          )
        }
      />
      <div className="p-8 space-y-4">
        <div className="grid grid-cols-3 gap-3 no-print">
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
        </div>

        {!marklist ? (
          <EmptyState title="Choose a grade and exam" hint="The ranked marklist will appear here." />
        ) : marklist.length === 0 ? (
          <EmptyState title="No students or marks found for this selection" />
        ) : (
          <Card className="p-0 print-sheet">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wide text-slate-500 border-b border-ink-100">
                  <th className="px-5 py-2">Pos.</th>
                  <th className="py-2">Student</th>
                  <th className="py-2">Adm. No.</th>
                  <th className="py-2 text-right">Total</th>
                  <th className="py-2 text-right">Average</th>
                  <th className="py-2 pr-5 text-right no-print">Report Card</th>
                </tr>
              </thead>
              <tbody>
                {marklist.map((r) => (
                  <tr key={r.student_id} className="border-b border-ink-100 last:border-0">
                    <td className="px-5 py-2 font-medium text-ink-950">{r.position}</td>
                    <td className="py-2">{r.student_name}</td>
                    <td className="py-2 text-slate-500">{r.admission_number}</td>
                    <td className="py-2 text-right">{r.total}</td>
                    <td className="py-2 text-right">{r.average ?? "—"}</td>
                    <td className="py-2 pr-5 text-right no-print">
                      <Link to={`/app/report-card?student_id=${r.student_id}&exam_id=${examId}`} className="text-xs text-ink-900 underline">
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        )}
      </div>
    </div>
  );
}
