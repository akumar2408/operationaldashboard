import { API } from "../lib/api";
import { useState } from "react";

export default function UploadCsv(){
  const [busy,setBusy]=useState(false);
  const [msg,setMsg]=useState<string|undefined>();
  return (
    <section className="rounded-2xl bg-white/5 ring-1 ring-white/10 p-5">
      <h2 className="text-lg font-semibold mb-3">Upload Sales CSV</h2>
      <form onSubmit={async e=>{
        e.preventDefault();
        const file = (e.target as HTMLFormElement).csv.files[0] as File;
        if(!file) return;
        setBusy(true); setMsg(undefined);
        const fd = new FormData(); fd.append("file", file);
        try {
          const res = await fetch(`${API}/upload`, { method:"POST", body: fd, credentials:"include" });
          if(!res.ok) throw new Error(res.statusText);
          const j = await res.json(); setMsg(`Imported ${j.rows} rows`);
        } catch(err:any){ setMsg(err.message||"Upload failed"); }
        setBusy(false);
      }}>
        <input name="csv" type="file" accept=".csv" className="block mb-3" />
        <button disabled={busy} className="rounded-2xl px-4 py-2 bg-white/10 hover:bg-white/15 ring-1 ring-white/20">
          {busy? "Uploading..." : "Upload"}
        </button>
        {msg && <p className="mt-2 text-sm text-white/70">{msg}</p>}
      </form>
    </section>
  );
}
