// src/components/StrategyNarrative.tsx

import React from 'react';
import ReactMarkdown from 'react-markdown';

interface StrategyNarrativeProps {
  strategyNarrative: string; // This expects a string of markdown content
}

const StrategyNarrative: React.FC<StrategyNarrativeProps> = ({ strategyNarrative }) => {
  // Preprocess the strategy narrative to replace numbered lists with markdown syntax
  const processed = strategyNarrative.replace(/^(\d+)\.\s([^\n]+)/gm, (match, number, content) => {
    return `${number}. ${content}`; // You may modify this further if needed
  });

  return (
    <div className="space-y-6"> {/* Add space between sections */}
      <h5 className="font-medium text-gray-700 mb-4">Strategy Narrative</h5>
      <div className="prose prose-sm max-w-none text-gray-600 space-y-4"> {/* Space between paragraphs */}
        {/* Pass the processed markdown content to ReactMarkdown */}
        <ReactMarkdown>{processed}</ReactMarkdown>
      </div>
    </div>
  );
};

export default StrategyNarrative;
