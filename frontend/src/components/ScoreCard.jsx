import React from 'react';

const ScoreCard = ({ title, score }) => {
  const isHighRisk = score >= 70;
  const isMediumRisk = score >= 30 && score < 70;
  
  let colorClass = 'text-green-500';
  let bgClass = 'bg-green-50/50';
  let borderClass = 'border-green-200';
  let riskText = 'Low Risk';

  if (isHighRisk) {
    colorClass = 'text-red-600';
    bgClass = 'bg-red-50/50';
    borderClass = 'border-red-200';
    riskText = 'High Risk';
  } else if (isMediumRisk) {
    colorClass = 'text-yellow-600';
    bgClass = 'bg-yellow-50/50';
    borderClass = 'border-yellow-200';
    riskText = 'Medium Risk';
  }

  // Visual circular progress representation
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className={`flex flex-col items-center justify-center p-8 rounded-[2rem] border ${borderClass} ${bgClass} shadow-sm relative overflow-hidden transition-all hover:shadow-md`}>
      <h3 className="text-xl font-bold text-slate-800 mb-6">{title}</h3>
      
      <div className="relative w-36 h-36 mb-6 flex items-center justify-center">
        <svg className="absolute w-full h-full transform -rotate-90 drop-shadow-sm">
          <circle
            cx="72"
            cy="72"
            r={radius}
            stroke="currentColor"
            strokeWidth="12"
            fill="none"
            className="text-white opacity-60"
          />
          <circle
            cx="72"
            cy="72"
            r={radius}
            stroke="currentColor"
            strokeWidth="12"
            fill="none"
            strokeLinecap="round"
            style={{
              strokeDasharray: circumference,
              strokeDashoffset: strokeDashoffset,
              transition: 'stroke-dashoffset 1s ease-in-out',
            }}
            className={colorClass}
          />
        </svg>
        <div className="flex flex-col items-center justify-center z-10">
          <span className={`text-4xl font-black ${colorClass} drop-shadow-sm leading-none`}>
            {score}%
          </span>
        </div>
      </div>
      
      <div className={`px-5 py-2 rounded-xl text-sm font-bold tracking-wide uppercase ${colorClass} bg-white shadow-sm ring-1 ring-black/5`}>
        {riskText}
      </div>
    </div>
  );
};

export default ScoreCard;
