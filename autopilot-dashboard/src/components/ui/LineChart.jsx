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
      <ResponsiveContainer>
        <ReLineChart data={data}>
          <XAxis dataKey={xKey} stroke="#64748B" />
          <YAxis stroke="#64748B" />
          <Tooltip />
          <Line
            type="monotone"
            dataKey={yKey}
            stroke="#2563EB"
            strokeWidth={2}
          />
        </ReLineChart>
      </ResponsiveContainer>
    </div>
  );
}
