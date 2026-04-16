export default function EvidencePanel({ rows = [] }) {
  const topRows = [...rows].sort((a, b) => b.risk_score - a.risk_score).slice(0, 6);

  return (
    <section className="rounded-2xl border border-slate-700 bg-card p-4">
      <h3 className="mb-3 text-lg font-semibold">Matched Sources & Evidence</h3>
      <div className="space-y-3">
        {topRows.map((row) => (
          <article key={row.paragraph_index} className="rounded-lg border border-slate-700 bg-slate-900/60 p-3">
            <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
              <span className="font-semibold text-slate-200">Paragraph {row.paragraph_index}</span>
              <span className="rounded bg-slate-800 px-2 py-1 text-xs text-slate-300">
                Risk {row.risk_score.toFixed(2)}
              </span>
            </div>
            <div className="mt-2 flex flex-wrap gap-2 text-xs text-slate-300">
              <span className="rounded bg-slate-800 px-2 py-1">Plag {row.plagiarism_score.toFixed(2)}</span>
              <span className="rounded bg-slate-800 px-2 py-1">AI {row.ai_probability.toFixed(2)}</span>
              <span className="rounded bg-slate-800 px-2 py-1">Burstiness {row.burstiness.toFixed(2)}</span>
              {typeof row.perplexity === "number" && (
                <span className="rounded bg-slate-800 px-2 py-1">Perplexity {row.perplexity.toFixed(1)}</span>
              )}
              {typeof row.repetition_ratio === "number" && (
                <span className="rounded bg-slate-800 px-2 py-1">Repetition {row.repetition_ratio.toFixed(2)}</span>
              )}
              {typeof row.classifier_ai_probability === "number" && (
                <span className="rounded bg-slate-800 px-2 py-1">Classifier {row.classifier_ai_probability.toFixed(2)}</span>
              )}
              {typeof row.doc_ai_prior === "number" && (
                <span className="rounded bg-slate-800 px-2 py-1">Doc Prior {row.doc_ai_prior.toFixed(2)}</span>
              )}
            </div>
            <p className="mt-2 line-clamp-3 text-sm text-slate-300">{row.paragraph}</p>
            <p className="mt-2 text-xs text-amber-300">Matched source: {row.matched_reference}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
