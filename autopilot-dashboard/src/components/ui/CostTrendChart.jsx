// src/components/ui/CostTrendChart.jsx

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts";

export default function CostTrendChart({ data }) {
  const hasData = data && data.length > 0;

  return (
    <div className="bg-surface p-6 rounded-xl border border-border shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-semibold text-lg">Cost Trend</h3>
        <span className="text-xs text-muted">Last 30 days</span>
      </div>

      {!hasData ? (
        <div className="h-[260px] flex items-center justify-center text-muted text-sm">
          No data available yet
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <AreaChart data={data}>
            {/* Gradient */}
            <defs>
              <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563EB" stopOpacity={0.4}/>
                <stop offset="95%" stopColor="#2563EB" stopOpacity={0}/>
              </linearGradient>
            </defs>

            {/* Grid */}
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />

            {/* Axis */}
            <XAxis
              dataKey="date"
              stroke="#94a3b8"
              fontSize={12}
            />
            <YAxis
              stroke="#94a3b8"
              fontSize={12}
              tickFormatter={(v) => `$${v}`}
            />

            {/* Tooltip */}
            <Tooltip
              contentStyle={{
                backgroundColor: "#0f172a",
                border: "none",
                borderRadius: "8px",
                color: "#fff",
              }}
              formatter={(value) => [`$${value}`, "Cost"]}
            />

            {/* Area */}
            <Area
              type="monotone"
              dataKey="cost"
              stroke="#2563EB"
              strokeWidth={3}
              fillOpacity={1}
              fill="url(#colorCost)"
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}