import React, { useState } from "react";

type Props = {
  apiBase: string; // e.g. "http://127.0.0.1:8000"
  onDone?: () => void; // callback to refresh KPIs/chart after upload
};

const UploadCsv: React.FC<Props> = ({ apiBase, onDone }) => {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const onPick = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] ?? null);
    setMsg(null);
  };

  const onUpload = async () => {
    if (!file) {
      setMsg("Pick a CSV first.");
      return;
    }
    setBusy(true);
    setMsg(null);
    try {
      const fd = new FormData();
      fd.append("file", file);

      // <-- point at the new local dev endpoint
      const res = await fetch(`${apiBase}/sales/upload/local`, {
        method: "POST",
        body: fd,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Upload failed (${res.status})`);
      }
      const json = await res.json();
      setMsg(`Uploaded ${json.inserted ?? 0} rows ✅`);
      if (onDone) onDone();
    } catch (err: any) {
      setMsg(err.message || "Upload failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex items-center gap-3">
      <input
        type="file"
        accept=".csv,text/csv"
        onChange={onPick}
        className="text-sm"
      />
      <button
        onClick={onUpload}
        disabled={!file || busy}
        className="px-4 py-2 rounded-xl bg-slate-700 hover:bg-slate-600 disabled:opacity-40"
      >
        {busy ? "Uploading..." : "Upload"}
      </button>
      {msg && <span className="text-sm opacity-80">{msg}</span>}
    </div>
  );
};

export default UploadCsv;
