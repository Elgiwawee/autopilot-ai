// src/components/ui/SavingsChart.jsx

import {
  BarChart,
  Bar,
  XAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

const data = [
  { name: "GPU Rightsizing", value: 8200 },
  { name: "Spot Usage", value: 6100 },
  { name: "Idle Reduction", value: 4100 },
];

export default function SavingsChart() {
  return (
    <div className="bg-surface border border-border rounded-xl p-6 shadow-sm h-72">
      <div className="flex justify-between mb-4">
        <h3 className="font-semibold text-lg">Savings Breakdown</h3>
        <span className="text-xs text-muted">This month</span>
      </div>

      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />

          <XAxis
            dataKey="name"
            stroke="#94a3b8"
            fontSize={12}
          />

          <Tooltip
            contentStyle={{
              backgroundColor: "#0f172a",
              border: "none",
              borderRadius: "8px",
              color: "#fff",
            }}
            formatter={(value) => [`$${value}`, "Savings"]}
          />

          <Bar
            dataKey="value"
            radius={[6, 6, 0, 0]}
            fill="#2563EB"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}