import { useEffect, useState } from 'react'
import { api } from '../api'
import ForecastChart from './ForecastChart'
import AlertsPanel from './AlertsPanel'

export default function Dashboard(){
  const [tenant, setTenant] = useState<any>()
  const [forecast, setForecast] = useState<any[]>([])
  const [kpis, setKpis] = useState<any>({today:0, last7:0, products:0})

  useEffect(()=>{
    (async ()=>{
      const t = await api.get('/tenant/me'); setTenant(t.data)
      const fc = await api.get('/forecast'); setForecast(fc.data)
      const cov = await api.get('/products/coverage'); 
      setKpis({ products: cov.data.length, last7: Math.round(avg(fc.data,7)), today: Math.round(avg(fc.data,1)) })
    })()
  },[])
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Dashboard {tenant?`– ${tenant.name}`:''}</h2>
      <div className="grid grid-cols-3 gap-4">
        <KPI label="Forecast for Today" val={kpis.today}/>
        <KPI label="Avg Next 7 Days" val={kpis.last7}/>
        <KPI label="Products" val={kpis.products}/>
      </div>
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 p-4 rounded-2xl border border-black/10 dark:border-white/10">
          <ForecastChart rows={forecast}/>
        </div>
        <AlertsPanel/>
      </div>
    </div>
  )
}

function avg(rows:any[], days:number){
  if(!rows?.length) return 0
  return rows.slice(0,days).reduce((a,r)=>a+Number(r.units_forecast||0),0)/Math.max(1,days)
}
function KPI({label,val}:{label:string,val:number}){
  return (
    <div className="p-4 rounded-2xl border border-black/10 dark:border-white/10 bg-white dark:bg-neutral-900">
      <div className="text-sm opacity-70">{label}</div>
      <div className="text-3xl font-semibold mt-1">{val}</div>
    </div>
  )
}
