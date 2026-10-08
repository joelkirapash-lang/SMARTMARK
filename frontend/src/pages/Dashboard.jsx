import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import { PageHeader, Card, Select, EmptyState } from "../components/ui";

const COLORS = ["#C9A227", "#1E2E4F", "#3B5480", "#5B6472"];

export default function Dashboard() {
  const { user } = useAuth();
  const [exams, setExams] = useState([]);
  const [examId, setExamId] = useState("");
  const [priorExamId, setPriorExamId] = useState("");
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    api.get("/exams").then((data) => {
      setExams(data);
      if (data.length) setExamId(data[0].id);
      if (data.length > 1) setPriorExamId(data[1].id);
    });
  }, []);

  useEffect(() => {
    const qs = new URLSearchParams();
    if (examId) qs.set("exam_id", examId);
    if (priorExamId) qs.set("prior_exam_id", priorExamId);
    api.get(`/dashboard/summary?${qs.toString()}`).then(setSummary);
  }, [examId, priorExamId]);

  if (user.role === "STUDENT") {
    return (
      <div>
        <PageHeader title="Welcome back" subtitle={`${user.first_name} ${user.second_name || ""}`.trim()} />
        <div className="p-8">
          <EmptyState title="Your results will appear here" hint="Once your teachers publish an exam, your report card will be available in the Report Card section." />
        </div>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="An overview of your school's academic performance"
        actions={
          exams.length > 0 && (
            <div className="flex gap-2">
              <Select value={examId} onChange={(e) => setExamId(e.target.value)}>
                {exams.map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}
              </Select>
              <Select value={priorExamId} onChange={(e) => setPriorExamId(e.target.value)}>
                <option value="">Compare to…</option>
                {exams.filter((e) => e.id !== examId).map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}
              </Select>
            </div>
          )
        }
      />
      <div className="p-8 space-y-6">
        {exams.length === 0 && (
          <EmptyState title="No exams yet" hint="Create your first exam to start seeing dashboard stats." />
        )}

        {summary && (
          <>
            <div className="grid grid-cols-3 gap-4">
              <Card>
                <p className="text-xs uppercase tracking-wide text-slate-500">Students</p>
                <p className="font-display text-3xl text-ink-950 mt-1">{summary.student_count}</p>
              </Card>
              <Card>
                <p className="text-xs uppercase tracking-wide text-slate-500">Teachers</p>
                <p className="font-display text-3xl text-ink-950 mt-1">{summary.teacher_count}</p>
              </Card>
              <Card>
                <p className="text-xs uppercase tracking-wide text-slate-500">Grades</p>
                <p className="font-display text-3xl text-ink-950 mt-1">{summary.grade_count}</p>
              </Card>
            </div>

            {summary.subject_averages?.length > 0 && (
              <Card title="Subject averages">
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={summary.subject_averages}>
                    <XAxis dataKey="subject" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Bar dataKey="average" fill="#1E2E4F" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            )}

            <div className="grid grid-cols-2 gap-6">
              {summary.performance_distribution?.length > 0 && (
                <Card title="Performance level distribution">
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie data={summary.performance_distribution} dataKey="count" nameKey="band" outerRadius={80}>
                        {summary.performance_distribution.map((_, i) => (
                          <Cell key={i} fill={COLORS[i % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Card>
              )}

              {summary.most_improved?.length > 0 && (
                <Card title="Most improved students">
                  <table className="w-full text-sm">
                    <tbody>
                      {summary.most_improved.map((r) => (
                        <tr key={r.student_id} className="border-b border-ink-100 last:border-0">
                          <td className="py-2">{r.student_name}</td>
                          <td className="py-2 text-right font-medium text-green-700">+{r.delta}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </Card>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
