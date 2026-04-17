import React from 'react';
import ScoreCard from '../components/ScoreCard';
import ParagraphCard from '../components/ParagraphCard';
import { ArrowLeft, Download } from 'lucide-react';

const ResultsPage = ({ result, onReset }) => {
  const [isExporting, setIsExporting] = React.useState(false);

  const handleExportPDF = async () => {
    try {
      setIsExporting(true);
      const response = await fetch('http://localhost:8000/export-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(result),
      });

      if (!response.ok) throw new Error('Failed to generate report');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'analysis_report.pdf';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export error:', error);
      alert('Failed to generate PDF report. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="w-full flex flex-col items-center">
      <div className="w-full flex justify-between items-center mb-8">
        <button 
          onClick={onReset}
          className="flex items-center space-x-2 text-slate-500 hover:text-indigo-600 bg-white hover:bg-indigo-50 px-5 py-3 rounded-xl font-bold transition-all shadow-sm ring-1 ring-slate-200"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>New Analysis</span>
        </button>

        <button 
          className={`flex items-center space-x-2 text-white bg-indigo-600 hover:bg-indigo-700 px-6 py-3 rounded-xl font-bold transition-all shadow-lg hover:shadow-indigo-500/30 transform hover:-translate-y-0.5 ${isExporting ? 'opacity-70 cursor-not-allowed' : ''}`}
          onClick={handleExportPDF}
          disabled={isExporting}
        >
          <Download className="w-5 h-5" />
          <span>{isExporting ? 'Generating...' : 'Export PDF'}</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full mb-12">
         <ScoreCard 
           title="Overall Plagiarism" 
           score={Math.round(result.overall_plagiarism_score)} 
         />
         <ScoreCard 
           title="Overall AI Probability" 
           score={Math.round(result.overall_ai_probability)} 
         />
      </div>

      <div className="w-full">
        <h2 className="text-3xl font-extrabold text-slate-800 mb-8 flex items-center space-x-4">
          <span>Paragraph Analysis</span>
          <span className="bg-indigo-100 text-indigo-700 text-sm py-1.5 px-4 rounded-full">{result.paragraph_analysis.length} blocks found</span>
        </h2>
        
        <div className="space-y-6">
          {result.paragraph_analysis.map((item, index) => (
             <ParagraphCard 
               key={index}
               index={index}
               paragraph={{
                 ...item,
                 plagiarism_score: Math.round(item.plagiarism_score),
                 ai_probability: Math.round(item.ai_probability)
               }}
             />
          ))}
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
