import { useEffect, useState } from 'react'
import { api } from '../api'
import { Severity } from './Badges'

export default function AlertsPanel(){
  const [alerts, setAlerts] = useState<any[]>([])
  useEffect(()=>{ (async()=>{ const {data}=await api.get('/alerts'); setAlerts(data) })() },[])
  return (
    <div className="p-4 rounded-2xl border border-black/10 dark:border-white/10">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Alerts</h3>
        <button className="text-sm opacity-70 hover:opacity-100" onClick={async()=>{
          await api.post('/alerts/evaluate'); const {data}=await api.get('/alerts'); setAlerts(data)
        }}>Evaluate</button>
      </div>
      {alerts.length===0 ? <p className="opacity-70">No alerts.</p> :
        <ul className="mt-3 space-y-2">{alerts.map(a=>(
          <li key={a.id} className="text-sm">
            <Severity level={a.severity||'low'}/> <b className="uppercase">{a.alert_type}</b> — {a.message}
          </li>
        ))}</ul>}
    </div>
  )
}
