import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";
import ReportCardView from "../components/ReportCardView";
import { Button } from "../components/ui";

export default function PublicReportCard() {
  const { token } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get(`/reports/shared/${token}`)
      .then(setData)
      .catch((err) => setError(err.message));
  }, [token]);

  return (
    <div className="min-h-screen bg-parchment-50 py-10 px-4">
      {error && (
        <div className="max-w-md mx-auto bg-white border border-red-200 rounded-lg p-8 text-center text-red-700">
          {error}
        </div>
      )}
      {data && (
        <>
          <div className="max-w-2xl mx-auto mb-4 flex justify-end no-print">
            <Button variant="outline" onClick={() => window.print()}>Save as PDF / Print</Button>
          </div>
          <ReportCardView data={data} />
        </>
      )}
    </div>
  );
}
