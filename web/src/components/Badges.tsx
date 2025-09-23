export function Severity({level}:{level:string}){
    const cls = level==="high" ? "bg-red-600"
              : level==="medium" ? "bg-amber-500"
              : "bg-slate-500"
    return <span className={`text-white text-xs px-2 py-0.5 rounded-full ${cls}`}>{level}</span>
  }
  