import { useEffect, useState } from "react";
import { api } from "../api/client";
import { PageHeader, Card, Input, Button, Badge, EmptyState } from "../components/ui";

export default function Exams() {
  const [exams, setExams] = useState([]);
  const [name, setName] = useState("");
  const [term, setTerm] = useState("");

  const load = () => api.get("/exams").then(setExams);
  useEffect(load, []);

  const create = async (e) => {
    e.preventDefault();
    await api.post("/exams", { name, term });
    setName(""); setTerm("");
    load();
  };

  const publish = async (id) => {
    await api.post(`/exams/${id}/publish`, {});
    load();
  };

  return (
    <div>
      <PageHeader title="Exams" subtitle="Create exams, then publish once marks and report cards are ready to share" />
      <div className="p-8 grid grid-cols-3 gap-6">
        <Card title="New exam">
          <form onSubmit={create} className="space-y-3">
            <Input label="Exam name" required value={name} onChange={(e) => setName(e.target.value)} placeholder="Term 2 Mid-Term" />
            <Input label="Term" value={term} onChange={(e) => setTerm(e.target.value)} placeholder="Term 2" />
            <Button type="submit" className="w-full">Create exam</Button>
          </form>
        </Card>

        <div className="col-span-2">
          <Card title="All exams" className="p-0">
            {exams.length === 0 ? (
              <div className="p-5"><EmptyState title="No exams yet" /></div>
            ) : (
              <ul className="divide-y divide-ink-100">
                {exams.map((e) => (
                  <li key={e.id} className="px-5 py-3 flex items-center justify-between text-sm">
                    <div>
                      <p className="text-ink-950">{e.name}</p>
                      <p className="text-xs text-slate-500">{e.term}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge tone={e.is_published ? "green" : "slate"}>{e.is_published ? "Published" : "Draft"}</Badge>
                      {!e.is_published && (
                        <button onClick={() => publish(e.id)} className="text-xs text-ink-900 underline">Publish</button>
                      )}
                    </div>
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
