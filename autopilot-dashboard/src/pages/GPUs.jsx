// src/pages/GPUs.jsx

import { useEffect, useState } from "react";
import { getGPUInventory } from "../api/gpu.api";
import Card from "../components/ui/Card";
import Spinner from "../components/ui/Spinner";
import Badge from "../components/ui/Badge";

export default function GPUs() {
  const [summary, setSummary] = useState(null);
  const [gpus, setGpus] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getGPUInventory()
      .then((data) => {
        setSummary(data.summary);
        setGpus(data.gpus);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spinner />;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">GPU Fleet</h1>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card title="Total GPUs">{summary?.total ?? 0}</Card>
        <Card title="Active">{summary?.active ?? 0}</Card>
        <Card title="Idle">{summary?.idle ?? 0}</Card>
        <Card title="Monthly Cost">
          ${summary?.monthly_cost ?? 0}
        </Card>
      </div>

      {/* GPU List */}
      <Card title="GPU Instances">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left">
              <th className="py-2">Instance</th>
              <th>Provider</th>
              <th>Region</th>
              <th>GPU Model</th>
              <th>Memory</th>
              <th>Utilization</th>
              <th>Status</th>
              <th>Attached To</th>
              <th>Hourly Cost</th>
              <th>Monthly Cost</th>
            </tr>
          </thead>

          <tbody>
            {gpus.map((gpu) => (
              <tr
                key={gpu.id}
                className="border-b hover:bg-muted/20"
              >
                <td className="py-3 font-medium">
                  {gpu.name}
                </td>

                <td>
                  {gpu.provider}
                </td>

                <td>
                  {gpu.region}
                </td>

                <td>
                  {gpu.model}
                </td>

                <td>
                  {gpu.memory_gb
                    ? `${gpu.memory_gb} GB`
                    : "-"}
                </td>

                <td>
                  {gpu.utilization}%
                </td>

                <td>
                  <Badge
                    variant={
                      gpu.status === "running"
                        ? "green"
                        : gpu.status === "stopped"
                        ? "gray"
                        : "yellow"
                    }
                  >
                    {gpu.status}
                  </Badge>
                </td>

                <td>
                  {gpu.attached_to || "-"}
                </td>

                <td>
                  ${gpu.cost_per_hour}
                </td>

                <td className="font-semibold">
                  ${gpu.monthly_cost}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
