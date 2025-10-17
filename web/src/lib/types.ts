export type KPI = { total_revenue:number; total_units:number; aov:number; sku_count:number; };
export type Point = { date:string; revenue:number; units:number; };
export type Series = { series: Point[] };
export type AlertsResp = { alerts: { type:string; date:string; value:number; baseline:number }[] };
