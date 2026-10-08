import { useEffect, useState } from "react";
import { api } from "../api/client";
import { PageHeader, Card, Input, Select, Button, ErrorBanner, EmptyState } from "../components/ui";

export default function Academics() {
  const [grades, setGrades] = useState([]);
  const [streams, setStreams] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [bands, setBands] = useState([]);
  const [error, setError] = useState("");

  const [gradeName, setGradeName] = useState("");
  const [gradeOrder, setGradeOrder] = useState(0);
  const [streamName, setStreamName] = useState("");
  const [streamGradeId, setStreamGradeId] = useState("");
  const [subjectName, setSubjectName] = useState("");
  const [subjectCode, setSubjectCode] = useState("");
  const [band, setBand] = useState({ code: "", label: "", min_score: "", max_score: "", color: "#C9A227" });

  const load = () => {
    api.get("/grades").then(setGrades);
    api.get("/streams").then(setStreams);
    api.get("/subjects").then(setSubjects);
    api.get("/performance-bands").then(setBands);
  };
  useEffect(load, []);

  const addGrade = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/grades", { name: gradeName, order_index: Number(gradeOrder) || 0 });
      setGradeName(""); setGradeOrder(0);
      load();
    } catch (err) { setError(err.message); }
  };

  const addStream = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/streams", { name: streamName, grade_id: streamGradeId });
      setStreamName("");
      load();
    } catch (err) { setError(err.message); }
  };

  const addSubject = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/subjects", { name: subjectName, code: subjectCode });
      setSubjectName(""); setSubjectCode("");
      load();
    } catch (err) { setError(err.message); }
  };

  const addBand = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/performance-bands", {
        ...band, min_score: Number(band.min_score), max_score: Number(band.max_score),
      });
      setBand({ code: "", label: "", min_score: "", max_score: "", color: "#C9A227" });
      load();
    } catch (err) { setError(err.message); }
  };

  const streamsByGrade = (gradeId) => streams.filter((s) => s.grade_id === gradeId);

  return (
    <div>
      <PageHeader title="Grades, Streams & Subjects" subtitle="Set up your CBC structure — nothing is pre-loaded, configure it your way" />
      <div className="p-8 space-y-6">
        <ErrorBanner message={error} />
        <div className="grid grid-cols-2 gap-6">
          <Card title="Grades (e.g. Playgroup, PP1, Grade 4)">
            <form onSubmit={addGrade} className="flex gap-2 mb-4">
              <Input placeholder="Grade name" value={gradeName} onChange={(e) => setGradeName(e.target.value)} required />
              <Input placeholder="Order" type="number" className="w-20" value={gradeOrder} onChange={(e) => setGradeOrder(e.target.value)} />
              <Button type="submit">Add</Button>
            </form>
            {grades.length === 0 ? <EmptyState title="No grades yet" hint="Add your first grade above." /> : (
              <ul className="divide-y divide-ink-100">
                {grades.sort((a,b)=>a.order_index-b.order_index).map((g) => (
                  <li key={g.id} className="py-2 flex justify-between text-sm">
                    <span>{g.name}</span>
                    <span className="text-slate-400">{streamsByGrade(g.id).length} stream(s)</span>
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Card title="Streams">
            <form onSubmit={addStream} className="space-y-2 mb-4">
              <Select value={streamGradeId} onChange={(e) => setStreamGradeId(e.target.value)} required>
                <option value="">Select grade…</option>
                {grades.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
              </Select>
              <div className="flex gap-2">
                <Input placeholder="Stream name, e.g. Stream A" value={streamName} onChange={(e) => setStreamName(e.target.value)} required />
                <Button type="submit">Add</Button>
              </div>
            </form>
            {streams.length === 0 ? <EmptyState title="No streams yet" /> : (
              <ul className="divide-y divide-ink-100">
                {streams.map((s) => (
                  <li key={s.id} className="py-2 text-sm flex justify-between">
                    <span>{s.name}</span>
                    <span className="text-slate-400">{grades.find((g) => g.id === s.grade_id)?.name}</span>
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Card title="Subjects">
            <form onSubmit={addSubject} className="flex gap-2 mb-4">
              <Input placeholder="Subject name" value={subjectName} onChange={(e) => setSubjectName(e.target.value)} required />
              <Input placeholder="Code" className="w-24" value={subjectCode} onChange={(e) => setSubjectCode(e.target.value)} required />
              <Button type="submit">Add</Button>
            </form>
            {subjects.length === 0 ? <EmptyState title="No subjects yet" /> : (
              <ul className="divide-y divide-ink-100">
                {subjects.map((s) => (
                  <li key={s.id} className="py-2 text-sm flex justify-between">
                    <span>{s.name}</span><span className="text-slate-400">{s.code}</span>
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Card title="Performance bands (BE / AE / ME / EE)">
            <form onSubmit={addBand} className="grid grid-cols-2 gap-2 mb-4">
              <Input placeholder="Code (e.g. EE)" value={band.code} onChange={(e) => setBand({ ...band, code: e.target.value })} required />
              <Input placeholder="Label" value={band.label} onChange={(e) => setBand({ ...band, label: e.target.value })} required />
              <Input placeholder="Min score" type="number" value={band.min_score} onChange={(e) => setBand({ ...band, min_score: e.target.value })} required />
              <Input placeholder="Max score" type="number" value={band.max_score} onChange={(e) => setBand({ ...band, max_score: e.target.value })} required />
              <Button type="submit" className="col-span-2">Add band</Button>
            </form>
            {bands.length === 0 ? <EmptyState title="No bands configured" hint="e.g. BE 0–49, AE 50–64, ME 65–79, EE 80–100" /> : (
              <ul className="divide-y divide-ink-100">
                {bands.map((b) => (
                  <li key={b.id} className="py-2 text-sm flex justify-between">
                    <span>{b.code} — {b.label}</span><span className="text-slate-400">{b.min_score}–{b.max_score}</span>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
