export default function KpiCard({title, value}:{title:string; value:React.ReactNode}){
  return (
    <div className="rounded-2xl bg-white/5 ring-1 ring-white/10 p-4">
      <p className="text-sm text-white/60">{title}</p>
      <p className="mt-1 text-2xl font-semibold">{value ?? "—"}</p>
    </div>
  )
}
