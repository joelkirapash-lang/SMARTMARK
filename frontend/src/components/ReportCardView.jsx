import { Badge } from "./ui";

export default function ReportCardView({ data }) {
  if (!data) return null;
  const { school, student, exam, subjects, total, average } = data;

  return (
    <div className="print-sheet bg-white border border-ink-100 rounded-lg max-w-2xl mx-auto p-10">
      <div className="flex items-start justify-between border-b border-ink-200 pb-6 mb-6">
        <div>
          <p className="font-display text-2xl text-ink-950">{school.name}</p>
          {school.motto && <p className="text-sm text-slate-500 italic">{school.motto}</p>}
          {school.address && <p className="text-xs text-slate-500 mt-1">{school.address}</p>}
        </div>
        {school.crest_url && <img src={school.crest_url} alt="" className="w-16 h-16 object-contain" />}
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6 text-sm">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">Student</p>
          <p className="text-ink-950 font-medium">{student.name}</p>
          {student.admission_number && <p className="text-slate-500">Adm. No. {student.admission_number}</p>}
        </div>
        <div className="text-right">
          <p className="text-xs uppercase tracking-wide text-slate-500">Examination</p>
          <p className="text-ink-950 font-medium">{exam.name}</p>
          {exam.term && <p className="text-slate-500">{exam.term}</p>}
        </div>
      </div>

      <table className="w-full text-sm mb-6">
        <thead>
          <tr className="border-b border-ink-200 text-left text-xs uppercase tracking-wide text-slate-500">
            <th className="py-2">Subject</th>
            <th className="py-2 text-right">Score</th>
            <th className="py-2 text-right">Level</th>
            <th className="py-2">Remark</th>
          </tr>
        </thead>
        <tbody>
          {subjects.map((s, i) => (
            <tr key={i} className="border-b border-ink-100">
              <td className="py-2">{s.subject}</td>
              <td className="py-2 text-right">{s.score ?? "—"} / {s.max_score}</td>
              <td className="py-2 text-right">{s.band ? <Badge tone="gold">{s.band}</Badge> : "—"}</td>
              <td className="py-2 text-slate-500">{s.remark || ""}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="flex justify-end gap-8 text-sm mb-10">
        <div><span className="text-slate-500 mr-2">Total</span><span className="font-medium text-ink-950">{total}</span></div>
        <div><span className="text-slate-500 mr-2">Average</span><span className="font-medium text-ink-950">{average ?? "—"}</span></div>
      </div>

      <div className="grid grid-cols-2 gap-10 text-xs text-slate-500 pt-10">
        <div className="border-t border-ink-300 pt-2">Class Teacher's Signature</div>
        <div className="border-t border-ink-300 pt-2">Principal's Signature / Stamp</div>
      </div>

      {school.footer && <p className="text-xs text-slate-400 mt-8 text-center">{school.footer}</p>}
    </div>
  );
}
