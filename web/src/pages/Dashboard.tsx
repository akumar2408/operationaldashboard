// web/src/pages/Dashboard.tsx
import { useEffect, useMemo, useState } from "react";
import KpiCard from "../components/KpiCard";
import LineChart from "../components/LineChart";
import UploadCsv from "../components/UploadCsv";
import { get, post } from "../lib/api";

type KPI = {
  revenue: number;
  units: number;
  aov: number;
  skus: number;
};

type SeriesPoint = { date: string; revenue: number; units: number };
type Series = SeriesPoint[];

type AlertItem = { type: string; date: string; value: number; baseline: number };
type AlertsResp = { alerts: AlertItem[] };

export default function Dashboard() {
  const [kpis, setKpis] = useState<KPI | null>(null);
  const [series, setSeries] = useState<Series | null>(null);
  const [alerts, setAlerts] = useState<AlertsResp | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  const { startStr, endStr } = useMemo(() => {
    const start = new Date();
    start.setMonth(start.getMonth() - 3);
    return {
      startStr: start.toISOString().slice(0, 10),
      endStr: new Date().toISOString().slice(0, 10),
    };
  }, []);

  // Initial load
  useEffect(() => {
    (async () => {
      try {
        setErr(null);
        const [k, s, a] = await Promise.all([
          get<KPI>(`/kpis?start=${startStr}&end=${endStr}`),
          get<Series>(`/chart/series`),
          // alerts endpoint may be optional — fall back to empty list
          get<AlertsResp>(`/alerts`).catch(() => ({ alerts: [] })),
        ]);
        setKpis(k);
        setSeries(s);
        setAlerts(a);
      } catch (e: any) {
        setErr(e?.message ?? String(e));
      }
    })();
  }, [startStr, endStr]);

  async function refreshLight() {
    const [k, s] = await Promise.all([
      get<KPI>(`/kpis?start=${startStr}&end=${endStr}`),
      get<Series>(`/chart/series`),
    ]);
    setKpis(k);
    setSeries(s);
  }

  async function runForecast() {
    try {
      setErr(null);
      setRunning(true);
      await post(`/forecast/run`, {}); // server does the heavy lifting
      await refreshLight();
      // (Optional) re-pull alerts if your backend updates them post-forecast
      get<AlertsResp>(`/alerts`)
        .then((a) => setAlerts(a))
        .catch(() => void 0);
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-black text-white p-6">
      <header className="max-w-6xl mx-auto flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">
          Operational{" "}
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-teal-300 to-indigo-400">
            Dashboard
          </span>
        </h1>
        <button
          onClick={runForecast}
          disabled={running}
          className="rounded-2xl px-4 py-2 bg-white/10 hover:bg-white/15 ring-1 ring-white/20 disabled:opacity-50"
        >
          {running ? "Running…" : "Run Forecast"}
        </button>
      </header>

      {/* error banner */}
      {err && (
        <div className="max-w-6xl mx-auto mt-4 rounded-xl bg-red-500/10 border border-red-400/30 p-3 text-sm">
          <div className="flex items-center justify-between">
            <span>{err}</span>
            <button
              className="ml-4 px-3 py-1 rounded-lg bg-white/10 hover:bg-white/15"
              onClick={() => {
                setErr(null);
                // quick retry of the lightweight fetches
                refreshLight().catch((e) => setErr(e?.message ?? String(e)));
              }}
            >
              Retry
            </button>
          </div>
        </div>
      )}

      <main className="max-w-6xl mx-auto mt-6 grid gap-6">
        <section className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <KpiCard title="Revenue" value={fmt(kpis?.revenue)} />
          <KpiCard title="Units" value={fmt(kpis?.units)} />
          <KpiCard title="AOV" value={fmt(kpis?.aov)} />
          <KpiCard title="SKUs" value={kpis?.skus ?? "—"} />
        </section>

        <section className="rounded-2xl bg-white/5 ring-1 ring-white/10 p-5">
          <h2 className="text-lg font-semibold mb-3">Last 90 Days</h2>
          <LineChart data={series ?? []} />
          {!series?.length && (
            <p className="text-white/60 mt-2">No data yet.</p>
          )}
        </section>

        <section className="rounded-2xl bg-white/5 ring-1 ring-white/10 p-5">
          <h2 className="text-lg font-semibold mb-3">Alerts</h2>
          <ul className="space-y-2">
            {(alerts?.alerts ?? []).map((a, i) => (
              <li
                key={i}
                className="flex items-center justify-between rounded-xl bg-white/5 px-4 py-3"
              >
                <div>
                  <p className="font-medium">{a.type.replaceAll("_", " ")}</p>
                  <p className="text-sm text-white/60">{a.date}</p>
                </div>
                <div className="text-sm text-white/80">
                  today {a.value.toFixed(2)} vs 7-day {a.baseline.toFixed(2)}
                </div>
              </li>
            ))}
            {(!alerts || alerts.alerts.length === 0) && (
              <p className="text-white/60">No alerts right now.</p>
            )}
          </ul>
        </section>

        <UploadCsv
          onDone={async () => {
            // After ingest, refresh KPIs & series
            setErr(null);
            try {
              await refreshLight();
            } catch (e: any) {
              setErr(e?.message ?? String(e));
            }
          }}
        />
      </main>
    </div>
  );
}

function fmt(n?: number) {
  return typeof n === "number" ? n.toLocaleString() : "—";
}
