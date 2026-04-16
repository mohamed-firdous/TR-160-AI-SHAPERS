import { useEffect, useMemo, useState } from "react";

import EvidencePanel from "../components/EvidencePanel";
import HeatmapSection from "../components/HeatmapSection";
import MetricCards from "../components/MetricCards";
import ReportDownloadButton from "../components/ReportDownloadButton";
import UploadPanel from "../components/UploadPanel";
import { analyzeAssignment } from "../services/api";

export default function DashboardPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [customReference, setCustomReference] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [analysisStage, setAnalysisStage] = useState(0);
  const [riskFilter, setRiskFilter] = useState("all");

  const hasResults = useMemo(() => Boolean(analysis?.paragraphs?.length), [analysis]);

  useEffect(() => {
    if (!loading) {
      setAnalysisStage(0);
      return;
    }

    const timer = setInterval(() => {
      setAnalysisStage((prev) => (prev + 1) % 4);
    }, 1400);

    return () => clearInterval(timer);
  }, [loading]);

  const statusText = [
    "Parsing document structure...",
    "Running plagiarism similarity model...",
    "Scoring AI generation likelihood...",
    "Building heatmap and evidence cards...",
  ][analysisStage];

  const visibleRows = useMemo(() => {
    const rows = analysis?.paragraphs ?? [];
    if (riskFilter === "high") {
      return rows.filter((row) => row.risk_score >= 0.75);
    }
    if (riskFilter === "medium") {
      return rows.filter((row) => row.risk_score >= 0.45 && row.risk_score < 0.75);
    }
    return rows;
  }, [analysis, riskFilter]);

  const runAnalysis = async () => {
    if (!selectedFile) {
      setError("Please upload a file first.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const response = await analyzeAssignment(selectedFile, customReference);
      setAnalysis(response);
    } catch (err) {
      const message = err?.response?.data?.detail || "Analysis failed. Check backend connection.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-slate-100">
          Automated Academic Plagiarism & AI-Generated Content Detector
        </h1>
        <p className="mt-2 max-w-3xl text-slate-300">
          Upload student assignments, inspect paragraph-level plagiarism and AI confidence, and download a faculty-ready report.
        </p>
      </header>

      <section className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <UploadPanel onFileSelected={setSelectedFile} loading={loading} />
          <textarea
            value={customReference}
            onChange={(event) => setCustomReference(event.target.value)}
            placeholder="Optional custom reference corpus (one line per reference)"
            className="h-32 w-full rounded-xl border border-slate-700 bg-card p-3 text-sm text-slate-200 placeholder:text-slate-500"
          />
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={runAnalysis}
              disabled={loading}
              className="rounded-xl border border-cyan-300 bg-cyan-500/20 px-4 py-2 text-sm font-semibold text-cyan-200 transition hover:bg-cyan-500/30 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Running analysis..." : "Analyze Assignment"}
            </button>
            {selectedFile && <span className="text-xs text-slate-400">Selected: {selectedFile.name}</span>}
            <ReportDownloadButton analysis={analysis} />
          </div>
          {loading && (
            <div className="rounded-lg border border-cyan-900 bg-slate-900/70 p-3">
              <p className="text-sm text-cyan-200">{statusText}</p>
              <div className="mt-2 h-1.5 w-full overflow-hidden rounded bg-slate-700">
                <div className="loading-bar h-full w-2/5 rounded bg-cyan-400" />
              </div>
            </div>
          )}
          {error && <p className="rounded-lg bg-red-500/20 px-3 py-2 text-sm text-red-200">{error}</p>}
        </div>

        <div className="rounded-2xl border border-slate-700 bg-card p-4">
          <h2 className="text-lg font-semibold">MVP Targets</h2>
          <ul className="mt-3 space-y-2 text-sm text-slate-300">
            <li>Supports PDF, DOCX, and TXT</li>
            <li>Paragraph-level plagiarism and AI scoring</li>
            <li>Explainable red/yellow/green heatmap</li>
            <li>Faculty report download</li>
            <li>Under 20s runtime goal</li>
          </ul>
        </div>
      </section>

      {hasResults && (
        <section className="mt-8 space-y-6">
          <MetricCards summary={analysis.summary} />
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setRiskFilter("all")}
              className={`rounded-full border px-3 py-1 text-xs ${
                riskFilter === "all" ? "border-cyan-300 bg-cyan-500/20 text-cyan-200" : "border-slate-700 text-slate-300"
              }`}
            >
              All Paragraphs ({analysis.paragraphs.length})
            </button>
            <button
              type="button"
              onClick={() => setRiskFilter("high")}
              className={`rounded-full border px-3 py-1 text-xs ${
                riskFilter === "high" ? "border-red-300 bg-red-500/20 text-red-200" : "border-slate-700 text-slate-300"
              }`}
            >
              High Risk ({analysis.paragraphs.filter((row) => row.risk_score >= 0.75).length})
            </button>
            <button
              type="button"
              onClick={() => setRiskFilter("medium")}
              className={`rounded-full border px-3 py-1 text-xs ${
                riskFilter === "medium" ? "border-amber-300 bg-amber-500/20 text-amber-200" : "border-slate-700 text-slate-300"
              }`}
            >
              Medium Risk ({analysis.paragraphs.filter((row) => row.risk_score >= 0.45 && row.risk_score < 0.75).length})
            </button>
          </div>
          <div className="grid gap-6 xl:grid-cols-2">
            <HeatmapSection rows={visibleRows} />
            <EvidencePanel rows={visibleRows} />
          </div>
        </section>
      )}
    </main>
  );
}
