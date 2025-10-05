import React, { useRef } from 'react';
import Papa from 'papaparse';

interface AgentData {
  agent_id: string;
  name: string;
  email: string;
  nps_score: number;
  sales_current_period: number;
  sales_previous_period: number;
  region: string;
  tenure_months: number;
  product_mix_score: number;
}

interface CSVUploadProps {
  csvData: AgentData[];
  onCSVDataChange: (data: AgentData[]) => void;
  isLoading: boolean;
  onLoadingChange: (loading: boolean) => void;
  error: string;
  onErrorChange: (error: string) => void;
  onCSVUpload?: (csvData: AgentData[]) => void;
}

const SAMPLE_CSV_DATA = `agent_id,name,email,nps_score,sales_current_period,sales_previous_period,region,tenure_months,product_mix_score
AG001,John Smith,john.smith@company.com,9,45000,52000,North,24,8.5
AG002,Sarah Johnson,sarah.johnson@company.com,7,38000,42000,South,18,7.2
AG003,Mike Davis,mike.davis@company.com,8,52000,48000,East,36,9.1
AG004,Lisa Wilson,lisa.wilson@company.com,6,29000,35000,West,12,6.8
AG005,David Brown,david.brown@company.com,9,61000,58000,North,30,8.9
AG006,Jennifer Lee,jennifer.lee@company.com,7,42000,46000,South,22,7.5
AG007,Robert Taylor,robert.taylor@company.com,8,48000,45000,East,28,8.2
AG008,Michelle Garcia,michelle.garcia@company.com,5,25000,32000,West,8,6.1
AG009,Christopher Martinez,chris.martinez@company.com,9,55000,52000,North,32,8.7
AG010,Amanda Rodriguez,amanda.rodriguez@company.com,6,33000,38000,South,15,7.0`;

const CSVUpload: React.FC<CSVUploadProps> = ({ 
  csvData, 
  onCSVDataChange, 
  isLoading, 
  onLoadingChange, 
  error, 
  onErrorChange,
  onCSVUpload
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (file: File) => {
    onLoadingChange(true);
    onErrorChange('');
    
    Papa.parse(file, {
      header: true,
      complete: (results) => {
        const data = results.data as any[];
        const requiredColumns = ['agent_id', 'name', 'email', 'nps_score', 'sales_current_period', 'sales_previous_period', 'region', 'tenure_months', 'product_mix_score'];
        
        if (data.length === 0) {
          onErrorChange('CSV file is empty');
          onLoadingChange(false);
          return;
        }

        const missingColumns = requiredColumns.filter(col => !data[0].hasOwnProperty(col));
        if (missingColumns.length > 0) {
          onErrorChange(`Missing required columns: ${missingColumns.join(', ')}`);
          onLoadingChange(false);
          return;
        }

        const parsedData = data.map(row => ({
          agent_id: row.agent_id,
          name: row.name,
          email: row.email,
          nps_score: parseFloat(row.nps_score) || 0,
          sales_current_period: parseFloat(row.sales_current_period) || 0,
          sales_previous_period: parseFloat(row.sales_previous_period) || 0,
          region: row.region,
          tenure_months: parseInt(row.tenure_months) || 0,
          product_mix_score: parseFloat(row.product_mix_score) || 0
        }));

        onCSVDataChange(parsedData);
        onLoadingChange(false);
        
        // Trigger processing flow when CSV is uploaded
        if (onCSVUpload && parsedData.length > 0) {
          onCSVUpload(parsedData);
        }
      },
      error: (error) => {
        onErrorChange(`Error parsing CSV: ${error.message}`);
        onLoadingChange(false);
      }
    });
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const downloadSampleCSV = () => {
    const blob = new Blob([SAMPLE_CSV_DATA], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_agents.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-gray-50 rounded-xl p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Population Upload & Preview</h3>
      
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-400 transition-colors"
      >
        <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" stroke="currentColor" fill="none" viewBox="0 0 48 48">
          <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <p className="text-gray-600 mb-2">Drag and drop your CSV file here, or</p>
        <button
          onClick={() => fileInputRef.current?.click()}
          className="text-indigo-600 hover:text-indigo-700 font-medium"
        >
          browse files
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
          className="hidden"
        />
      </div>

      <div className="mt-4 flex justify-between items-center">
        <button
          onClick={downloadSampleCSV}
          className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
        >
          Download Sample CSV
        </button>
        {csvData.length > 0 && (
          <span className="text-sm text-gray-600">
            {csvData.length} agents loaded
          </span>
        )}
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {isLoading && (
        <div className="mt-4 text-center">
          <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
          <p className="mt-2 text-gray-600">Parsing CSV...</p>
        </div>
      )}

      {csvData.length > 0 && (
        <div className="mt-6">
          <h4 className="font-medium text-gray-900 mb-3">Preview (First 10 rows)</h4>
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white border border-gray-200 rounded-lg">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">NPS</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Sales Decline %</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Region</th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Tenure</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {csvData.slice(0, 10).map((agent, index) => {
                  const salesDecline = ((agent.sales_previous_period - agent.sales_current_period) / agent.sales_previous_period) * 100;
                  return (
                    <tr key={index}>
                      <td className="px-3 py-2 text-sm text-gray-900">{agent.name}</td>
                      <td className="px-3 py-2 text-sm text-gray-900">{agent.nps_score}</td>
                      <td className="px-3 py-2 text-sm text-gray-900">{salesDecline.toFixed(1)}%</td>
                      <td className="px-3 py-2 text-sm text-gray-900">{agent.region}</td>
                      <td className="px-3 py-2 text-sm text-gray-900">{agent.tenure_months}m</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default CSVUpload;
