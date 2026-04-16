export default function ReportDownloadButton({ analysis }) {
  if (!analysis?.pdf_report_base64) {
    return null;
  }

  const onDownload = () => {
    const byteCharacters = atob(analysis.pdf_report_base64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i += 1) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }

    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: "application/pdf" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "faculty-report.pdf";
    link.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <button
      type="button"
      onClick={onDownload}
      className="rounded-xl border border-emerald-400 bg-emerald-500/20 px-4 py-2 text-sm font-semibold text-emerald-200 transition hover:bg-emerald-500/30"
    >
      Download Faculty PDF Report
    </button>
  );
}
