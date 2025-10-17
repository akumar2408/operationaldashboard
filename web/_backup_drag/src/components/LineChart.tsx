import { LineChart as RCLineChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts";

export default function LineChart({data}:{data:{date:string; revenue:number; units:number}[]}){
  if(!data?.length) return <p className="text-white/60">No data yet.</p>;
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <RCLineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="revenue" stroke="#8884d8" dot={false} />
        </RCLineChart>
      </ResponsiveContainer>
    </div>
  )
}
