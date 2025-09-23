import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

type Props = { rows: any[] };

export default function ForecastChart({ rows }: Props){
  const data = rows.map(r=>({ date: r.horizon_date, units: r.units_forecast }));
  return (
    <div style={{height: 360}}>
      <h3>30‑day Unit Forecast</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="units" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
