import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { 
  Dashboard, 
  ProcessingPageWrapper, 
  CampaignResultsWrapper 
} from './components';

const App: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/processing/:campaignId" element={<ProcessingPageWrapper />} />
      <Route path="/campaign/:campaignId" element={<CampaignResultsWrapper />} />
    </Routes>
  );
};

export default App;