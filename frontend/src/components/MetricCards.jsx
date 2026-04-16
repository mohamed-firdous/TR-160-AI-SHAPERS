export default function MetricCards({ summary }) {
  const cards = [
    { label: "Paragraphs", value: summary?.paragraph_count ?? 0 },
    { label: "Avg Plagiarism", value: (summary?.avg_plagiarism ?? 0).toFixed(2) },
    { label: "Avg AI Probability", value: (summary?.avg_ai_probability ?? 0).toFixed(2) },
    { label: "High-Risk Sections", value: summary?.high_risk_sections ?? 0 },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <div key={card.label} className="rounded-xl border border-slate-700 bg-card p-4">
          <p className="text-xs uppercase tracking-wider text-slate-400">{card.label}</p>
          <p className="mt-2 text-2xl font-bold text-mint">{card.value}</p>
        </div>
      ))}
    </div>
  );
}
