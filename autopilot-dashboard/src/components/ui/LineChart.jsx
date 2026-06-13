// src/components/ui/LineChart.jsx

import {
  LineChart as ReLineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from "recharts";

export default function LineChart({ data, xKey, yKey }) {
  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height={320}>
        <ReLineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis
            dataKey={xKey}
            tick={{ fontSize: 12 }}
          />

          <YAxis
            tickFormatter={(v) => `$${v}`}
          />

          <Tooltip
            formatter={(v) => [`$${v}`, "Savings"]}
          />

          <Line
            type="monotone"
            dataKey={yKey}
            strokeWidth={3}
            dot={false}
          />
        </ReLineChart>
      </ResponsiveContainer>
    </div>
  );
}
