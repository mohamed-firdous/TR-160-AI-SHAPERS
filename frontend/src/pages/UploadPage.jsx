import React, { useState } from 'react';
import FileUpload from '../components/FileUpload';
import { uploadFile } from '../api';
import { AlertCircle, Loader2, Sparkles } from 'lucide-react';

const UploadPage = ({ onAnalysisComplete }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setError(null);
  };

  const handleClear = () => {
    setSelectedFile(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await uploadFile(selectedFile);
      onAnalysisComplete(result);
    } catch (err) {
      const dynamicError = err.response?.data?.detail || err.message || "Failed to connect to backend.";
      setError(`Server Error: ${dynamicError}`);
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto flex flex-col items-center w-full">
      {error && (
        <div className="w-full bg-red-50 text-red-700 p-5 rounded-2xl flex items-start space-x-3 mb-6 border border-red-100 shadow-sm">
          <AlertCircle className="w-6 h-6 flex-shrink-0 text-red-500" />
          <div className="pt-0.5">
            <p className="font-bold">Analysis Failed</p>
            <p className="text-sm font-medium mt-1 opacity-90">{error}</p>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="min-h-[400px] w-full flex flex-col items-center justify-center space-y-8 rounded-[3rem] bg-indigo-600 shadow-2xl shadow-indigo-900/20 text-white relative overflow-hidden">
          {/* subtle background animation effect */}
          <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
          <div className="absolute inset-0 bg-gradient-to-t from-indigo-800/40 to-transparent"></div>
          
          <div className="relative z-10 flex flex-col items-center">
            <Loader2 className="w-16 h-16 text-white animate-spin mb-8" />
            <p className="text-white font-bold text-2xl tracking-tight">Analyzing document...</p>
            <p className="text-indigo-200 mt-2 font-medium">Scanning for AI traces & plagiarism</p>
          </div>
        </div>
      ) : (
        <div className="w-full relative">
          <FileUpload 
            onFileSelect={handleFileSelect} 
            selectedFile={selectedFile} 
            onClear={handleClear} 
          />

          <button
            onClick={handleAnalyze}
            disabled={!selectedFile}
            className={`mt-8 w-full py-5 rounded-2xl flex items-center justify-center space-x-3 text-xl font-bold transition-all duration-300 shadow-lg 
              ${selectedFile 
                ? 'bg-slate-900 hover:bg-black text-white shadow-slate-900/20 transform hover:-translate-y-1 cursor-pointer' 
                : 'bg-slate-200 text-slate-400 cursor-not-allowed shadow-none'
              }
            `}
          >
             <Sparkles className="w-6 h-6" />
             <span>Analyze Document</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default UploadPage;
