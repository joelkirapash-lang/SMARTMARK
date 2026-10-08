import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import ReportCardView from "../components/ReportCardView";
import { PageHeader, Button, Select, EmptyState } from "../components/ui";

export default function ReportCard() {
  const { user } = useAuth();
  const [params] = useSearchParams();
  const [studentId, setStudentId] = useState(params.get("student_id") || (user.role === "STUDENT" ? user.id : ""));
  const [examId, setExamId] = useState(params.get("exam_id") || "");
  const [exams, setExams] = useState([]);
  const [data, setData] = useState(null);
  const [shareUrl, setShareUrl] = useState(null);
  const [orientation, setOrientation] = useState("portrait");

  useEffect(() => { api.get("/exams").then(setExams); }, []);

  useEffect(() => {
    if (studentId && examId) {
      api.get(`/reports/card?student_id=${studentId}&exam_id=${examId}`).then(setData).catch(() => setData(null));
    }
  }, [studentId, examId]);

  const generateShareLink = async () => {
    const res = await api.post("/reports/share-link", { student_id: studentId, exam_id: examId });
    setShareUrl(res.url);
  };

  return (
    <div>
      <PageHeader
        title="Report Card"
        subtitle="Individual printable report card"
        actions={
          data && (
            <>
              <Button variant="outline" onClick={() => setOrientation((o) => (o === "portrait" ? "landscape" : "portrait"))}>
                {orientation === "portrait" ? "Landscape" : "Portrait"}
              </Button>
              {user.role === "SCHOOL_ADMIN" && <Button variant="outline" onClick={generateShareLink}>Get parent link</Button>}
              <Button onClick={() => window.print()}>Print / Save as PDF</Button>
            </>
          )
        }
      />
      <div className="p-8 space-y-4">
        {user.role !== "STUDENT" && (
          <div className="grid grid-cols-2 gap-3 max-w-md no-print">
            <input
              className="rounded-md border border-ink-200 px-3 py-2 text-sm focus-ring"
              placeholder="Student ID"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
            />
            <Select value={examId} onChange={(e) => setExamId(e.target.value)}>
              <option value="">Select exam…</option>
              {exams.map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}
            </Select>
          </div>
        )}

        {shareUrl && (
          <div className="bg-gold-500/10 border border-gold-500/30 rounded-md px-4 py-3 text-sm no-print">
            Parent link (valid 30 days): <a href={shareUrl} className="underline" target="_blank" rel="noreferrer">{shareUrl}</a>
          </div>
        )}

        {!data ? (
          <EmptyState title="Select a student and exam" hint="Their report card will appear here." />
        ) : (
          <div className={orientation === "landscape" ? "rotate-0" : ""}>
            <ReportCardView data={data} />
          </div>
        )}
      </div>
    </div>
  );
}
