import { useEffect, useState } from "react";
import KpiCard from "../components/KpiCard";
import LineChart from "../components/LineChart";
import UploadCsv from "../components/UploadCsv";
import { get, post } from "../lib/api";
import type { KPI, Series, AlertsResp } from "../lib/types";

export default function Dashboard(){
  const [kpis, setKpis] = useState<KPI | null>(null);
  const [series, setSeries] = useState<Series | null>(null);
  const [alerts, setAlerts] = useState<AlertsResp | null>(null);

  const start = new Date(); start.setMonth(start.getMonth() - 3);
  const startStr = start.toISOString().slice(0,10);
  const endStr = new Date().toISOString().slice(0,10);

  useEffect(()=>{
    get<KPI>(`/kpis?start=${startStr}&end=${endStr}`).then(setKpis).catch(console.error);
    get<Series>(`/chart/series`).then(setSeries).catch(console.error);
    get<AlertsResp>(`/alerts`).then(setAlerts).catch(console.error);
  },[]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-black text-white p-6">
      <header className="max-w-6xl mx-auto flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">
          Operational <span className="bg-clip-text text-transparent bg-gradient-to-r from-teal-300 to-indigo-400">Dashboard</span>
        </h1>
        <button onClick={()=>post(`/forecast/run`, {})} className="rounded-2xl px-4 py-2 bg-white/10 hover:bg-white/15 ring-1 ring-white/20">
          Run Forecast
        </button>
      </header>

      <main className="max-w-6xl mx-auto mt-6 grid gap-6">
        <section className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <KpiCard title="Revenue" value={fmt(kpis?.total_revenue)} />
          <KpiCard title="Units" value={fmt(kpis?.total_units)} />
          <KpiCard title="AOV" value={fmt(kpis?.aov)} />
          <KpiCard title="SKUs" value={kpis?.sku_count ?? "—"} />
        </section>

        <section className="rounded-2xl bg-white/5 ring-1 ring-white/10 p-5">
          <h2 className="text-lg font-semibold mb-3">Last 90 Days</h2>
          <LineChart data={series?.series ?? []} />
        </section>

        <section className="rounded-2xl bg-white/5 ring-1 ring-white/10 p-5">
          <h2 className="text-lg font-semibold mb-3">Alerts</h2>
          <ul className="space-y-2">
            {(alerts?.alerts ?? []).map((a,i)=>(
              <li key={i} className="flex items-center justify-between rounded-xl bg-white/5 px-4 py-3">
                <div>
                  <p className="font-medium">{a.type.replace('_',' ')}</p>
                  <p className="text-sm text-white/60">{a.date}</p>
                </div>
                <div className="text-sm text-white/80">today {a.value.toFixed(2)} vs 7-day {a.baseline.toFixed(2)}</div>
              </li>
            ))}
            {(!alerts || alerts.alerts.length===0) && <p className="text-white/60">No alerts right now.</p>}
          </ul>
        </section>

        <UploadCsv />
      </main>
    </div>
  )
}
function fmt(n?:number){ return typeof n==="number" ? n.toLocaleString() : "—"; }
