import React from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { CampaignResults } from '../index';

const CampaignResultsWrapper: React.FC = () => {
  const { campaignId } = useParams<{ campaignId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  
  const campaignName = location.state?.campaignName || 'Campaign';

  const handleBack = () => {
    navigate('/');
  };

  const handleCreateCampaign = () => {
    // Here you would typically create the campaign
    console.log('Creating campaign with ID:', campaignId);
    // For now, just show a success message and redirect
    alert('Campaign created successfully!');
    navigate('/');
  };

  if (!campaignId) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Campaign Not Found</h1>
          <p className="text-gray-600 mb-4">The campaign ID is missing from the URL.</p>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <CampaignResults 
      campaignId={campaignId}
      campaignName={campaignName}
      onBack={handleBack}
      onCreateCampaign={handleCreateCampaign}
    />
  );
};

export default CampaignResultsWrapper;
