import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

export default function Nav(){
  const { pathname } = useLocation();
  const [open, setOpen] = useState(true);
  const Item = ({to,label}:{to:string,label:string}) => (
    <Link to={to}
      className={`block px-4 py-2 rounded-xl hover:bg-black/5 dark:hover:bg-white/10
        ${pathname===to?'bg-black/5 dark:bg-white/10 font-semibold':''}`}>
      {label}
    </Link>
  );
  return (
    <aside className={`h-screen sticky top-0 p-3 ${open?'w-64':'w-16'} transition-all`}>
      <button onClick={()=>setOpen(!open)} className="mb-3 text-sm opacity-70">☰</button>
      <Item to="/" label="Dashboard"/>
      <Item to="/sales" label="Sales"/>
      <Item to="/forecasts" label="Forecasts"/>
      <Item to="/alerts" label="Alerts"/>
      <Item to="/inventory" label="Inventory"/>
    </aside>
  );
}
