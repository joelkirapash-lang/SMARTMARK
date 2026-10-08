import { useEffect, useState } from "react";
import { api } from "../api/client";
import { PageHeader, Card, Select, Button, Badge, EmptyState } from "../components/ui";

export default function Teachers() {
  const [teachers, setTeachers] = useState([]);
  const [grades, setGrades] = useState([]);
  const [streams, setStreams] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [selected, setSelected] = useState(null);
  const [assignments, setAssignments] = useState([]);
  const [draft, setDraft] = useState({ grade_id: "", stream_id: "", subject_id: "" });

  useEffect(() => {
    api.get("/teachers").then(setTeachers);
    api.get("/grades").then(setGrades);
    api.get("/subjects").then(setSubjects);
  }, []);

  useEffect(() => {
    if (draft.grade_id) api.get(`/streams?grade_id=${draft.grade_id}`).then(setStreams);
  }, [draft.grade_id]);

  const openTeacher = async (t) => {
    setSelected(t);
    const data = await api.get(`/teachers/${t.id}/assignments`);
    setAssignments(data);
  };

  const addAssignment = () => {
    if (!draft.grade_id || !draft.subject_id) return;
    setAssignments((a) => [...a, { ...draft, id: `draft-${a.length}` }]);
    setDraft({ grade_id: "", stream_id: "", subject_id: "" });
  };

  const removeAssignment = (id) => setAssignments((a) => a.filter((x) => x.id !== id));

  const save = async () => {
    await api.put(`/teachers/${selected.id}/assignments`, {
      assignments: assignments.map(({ grade_id, stream_id, subject_id }) => ({ grade_id, stream_id: stream_id || null, subject_id })),
    });
    openTeacher(selected);
  };

  const gradeName = (id) => grades.find((g) => g.id === id)?.name || "—";
  const subjectName = (id) => subjects.find((s) => s.id === id)?.name || "—";

  return (
    <div>
      <PageHeader title="Teachers" subtitle="Assign grade, stream and subject access — teachers can't self-assign" />
      <div className="p-8 grid grid-cols-5 gap-6">
        <div className="col-span-2">
          <Card title="All teachers" className="p-0">
            {teachers.length === 0 ? (
              <div className="p-5"><EmptyState title="No teachers yet" hint="Invite one from the Invitations page." /></div>
            ) : (
              <ul className="divide-y divide-ink-100">
                {teachers.map((t) => (
                  <li key={t.id}>
                    <button
                      onClick={() => openTeacher(t)}
                      className={`w-full text-left px-5 py-3 text-sm hover:bg-parchment-100 focus-ring ${selected?.id === t.id ? "bg-parchment-100" : ""}`}
                    >
                      <p className="text-ink-950">{t.first_name} {t.second_name}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-slate-500">{t.smartmark_email}</span>
                        <Badge tone={t.status === "ACTIVE" ? "green" : "slate"}>{t.status}</Badge>
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>

        <div className="col-span-3">
          {!selected ? (
            <Card><EmptyState title="Select a teacher" hint="Choose a teacher on the left to manage their class access." /></Card>
          ) : (
            <Card title={`Assignments for ${selected.first_name} ${selected.second_name}`}>
              <div className="grid grid-cols-3 gap-2 mb-4">
                <Select value={draft.grade_id} onChange={(e) => setDraft({ ...draft, grade_id: e.target.value, stream_id: "" })}>
                  <option value="">Grade…</option>
                  {grades.map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
                </Select>
                <Select value={draft.stream_id} onChange={(e) => setDraft({ ...draft, stream_id: e.target.value })} disabled={!draft.grade_id}>
                  <option value="">Any stream</option>
                  {streams.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                </Select>
                <Select value={draft.subject_id} onChange={(e) => setDraft({ ...draft, subject_id: e.target.value })}>
                  <option value="">Subject…</option>
                  {subjects.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                </Select>
              </div>
              <Button variant="outline" onClick={addAssignment} className="mb-4">Add assignment</Button>

              {assignments.length === 0 ? (
                <EmptyState title="No class/subject access yet" hint="This teacher cannot enter marks anywhere until assigned." />
              ) : (
                <ul className="divide-y divide-ink-100 mb-4">
                  {assignments.map((a) => (
                    <li key={a.id} className="py-2 flex justify-between items-center text-sm">
                      <span>{gradeName(a.grade_id)} · {a.stream_id ? "specific stream" : "all streams"} · {subjectName(a.subject_id)}</span>
                      <button onClick={() => removeAssignment(a.id)} className="text-xs text-red-600 underline">Remove</button>
                    </li>
                  ))}
                </ul>
              )}
              <Button onClick={save}>Save assignments</Button>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
