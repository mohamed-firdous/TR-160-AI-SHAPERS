import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const colorMap = {
  red: "#ef4444",
  yellow: "#f59e0b",
  green: "#10b981",
};

export default function HeatmapSection({ rows = [] }) {
  const chartData = rows.map((row) => ({
    index: row.paragraph_index,
    risk: row.risk_score,
    heatmap_color: row.heatmap_color,
  }));

  return (
    <section className="rounded-2xl border border-slate-700 bg-card p-4">
      <h3 className="mb-3 text-lg font-semibold">Suspicious Section Heatmap</h3>
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <XAxis dataKey="index" stroke="#94a3b8" />
            <YAxis domain={[0, 1]} stroke="#94a3b8" />
            <Tooltip />
            <Bar dataKey="risk">
              {chartData.map((entry) => (
                <Cell key={entry.index} fill={colorMap[entry.heatmap_color] ?? "#10b981"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
