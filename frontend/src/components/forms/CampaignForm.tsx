import React from 'react';

interface CampaignFormProps {
  campaignData: {
    campaign_name: string;
    goals: string;
  };
  onCampaignDataChange: (data: any) => void;
}

const CampaignForm: React.FC<CampaignFormProps> = ({ campaignData, onCampaignDataChange }) => {
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Campaign Name</label>
          <input
            type="text"
            value={campaignData.campaign_name}
            onChange={(e) => onCampaignDataChange({...campaignData, campaign_name: e.target.value})}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            placeholder="Enter campaign name"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Campaign Goals</label>
          <textarea
            value={campaignData.goals}
            onChange={(e) => onCampaignDataChange({...campaignData, goals: e.target.value})}
            rows={6}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            placeholder="Describe your campaign goals and targeting strategy. For example: Create a campaign population targeting high NPS agents with declining sales; provide 360 profiling and Q4 targeting"
          />
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <svg className="w-5 h-5 text-blue-600 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div>
            <h4 className="text-sm font-medium text-blue-800">AI-Powered Campaign Creation</h4>
            <p className="text-sm text-blue-700 mt-1">
              Our AI will analyze your goals, create targeted segments, generate comprehensive profiles, and develop a complete campaign strategy automatically.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CampaignForm;