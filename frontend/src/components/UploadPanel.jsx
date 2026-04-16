import { useCallback } from "react";
import { useDropzone } from "react-dropzone";

export default function UploadPanel({ onFileSelected, loading }) {
  const onDrop = useCallback(
    (acceptedFiles) => {
      if (acceptedFiles?.length) {
        onFileSelected(acceptedFiles[0]);
      }
    },
    [onFileSelected]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "text/plain": [".txt"],
    },
  });

  return (
    <section className="rounded-2xl border border-slate-700 bg-card/70 p-6 shadow-glow">
      <div
        {...getRootProps()}
        className={`cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition ${
          isDragActive ? "border-emerald-300 bg-emerald-500/10" : "border-slate-600 hover:border-cyan-300"
        }`}
      >
        <input {...getInputProps()} />
        <p className="text-lg font-semibold text-slate-100">Drag & drop assignment file</p>
        <p className="mt-2 text-sm text-slate-400">Supports PDF, DOCX, TXT</p>
      </div>
      {loading && <p className="mt-4 text-sm text-amber-300">Analyzing... this can take a few seconds.</p>}
    </section>
  );
}
