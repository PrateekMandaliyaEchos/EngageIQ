import React, { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { DashboardHeader, CampaignModal } from '../index';
import { apiService } from '../../services/api';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [successMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const handleNewCampaign = () => {
    setIsModalOpen(true);
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
  };

  const handleError = (error: string) => {
    setErrorMessage(error);
    setTimeout(() => {
      setErrorMessage('');
    }, 5000);
  };

  const handleCampaignCreated = (id: string, name: string) => {
    // Navigate to processing page with campaign ID
    navigate(`/processing/${id}`, {
      state: { campaignName: name }
    });
  };

  const [campaigns, setCampaigns] = useState<Array<{ campaign_id: string; name: string; segment_size: number; start_date: string; created_at: string }>>([]);
  const [loadingCampaigns, setLoadingCampaigns] = useState(false);
  const [campaignsError, setCampaignsError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      try {
        setLoadingCampaigns(true);
        setCampaignsError(null);
        const list = await apiService.getAllCampaigns();

        const formatDate = (date: string) => {
          const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: '2-digit', day: '2-digit' };
          return new Date(date).toLocaleDateString('en-GB', options);
        };
        const calculateDateDifference = (createdAt: string) => {
          // Create Date objects for current date and the provided created_at
          const currentDate = new Date();
          const createdDate = new Date(createdAt);

          // Set both dates to midnight (ignoring time) to compare only by date
          currentDate.setHours(0, 0, 0, 0);
          createdDate.setHours(0, 0, 0, 0);

          // Calculate the time difference in milliseconds
          const timeDifference = currentDate.getTime() - createdDate.getTime();

          // Convert milliseconds to days and return the number of days
          const daysDifference = Math.floor(timeDifference / (1000 * 3600 * 24));

          return daysDifference;
        };


        const processed = list
          .map(campaign => {
            const daysAgo = calculateDateDifference(campaign.created_at);
            return {
              campaign_id: campaign.campaign_id,
              name: campaign.name,
              segment_size: campaign.segment_size,
              start_date: daysAgo <= 7
                ? `${daysAgo === 1 ? `${daysAgo} day ago` : `${daysAgo} days ago`}`
                : `on ${formatDate(campaign.created_at)}`,
              created_at: campaign.created_at,
            };
          })
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

        if (!isMounted) return;
        setCampaigns(processed);
      } catch (e) {
        if (!isMounted) return;
        setCampaignsError(e instanceof Error ? e.message : 'Failed to load campaigns');
      } finally {
        if (!isMounted) return;
        setLoadingCampaigns(false);
      }
    };
    fetchData();
    return () => { isMounted = false; };
  }, []);

  const recentCampaigns = useMemo(() => campaigns.slice(0, 5), [campaigns]);

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader onNewCampaign={handleNewCampaign} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Campaigns</h3>
            {loadingCampaigns ? (
              <div className="space-y-4">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="p-4 bg-gray-50 rounded-lg animate-pulse h-16" />
                ))}
              </div>
            ) : campaignsError ? (
              <div className="text-sm text-red-600">{campaignsError}</div>
            ) : (
              <div className="space-y-4">
                {recentCampaigns.map((c, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <button
                        className="font-medium text-left text-indigo-700 hover:underline cursor-pointer"
                        onClick={() => navigate(`/campaign/${c.campaign_id}`, { state: { campaignName: c.name } })}
                      >
                        {c.name}
                      </button>
                      <p className="text-sm text-gray-600">Created {c.start_date}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-500">{c.segment_size} agents</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-2 gap-4">
              <button className="p-4 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors text-left">
                <div className="flex items-center mb-2">
                  <svg className="w-5 h-5 text-indigo-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="font-medium text-indigo-900">AI Analysis</span>
                </div>
                <p className="text-sm text-indigo-700">Generate insights</p>
              </button>
              <button className="p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors text-left">
                <div className="flex items-center mb-2">
                  <svg className="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span className="font-medium text-green-900">View Reports</span>
                </div>
                <p className="text-sm text-green-700">Campaign analytics</p>
              </button>
              <button className="p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors text-left">
                <div className="flex items-center mb-2">
                  <svg className="w-5 h-5 text-purple-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                  </svg>
                  <span className="font-medium text-purple-900">Templates</span>
                </div>
                <p className="text-sm text-purple-700">Campaign templates</p>
              </button>
              <button className="p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors text-left">
                <div className="flex items-center mb-2">
                  <svg className="w-5 h-5 text-orange-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                    <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                  </svg>
                  <span className="font-medium text-orange-900">Settings</span>
                </div>
                <p className="text-sm text-orange-700">Account settings</p>
              </button>
            </div>
          </div>
        </div>
      </div>

      <CampaignModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        onCampaignCreated={handleCampaignCreated}
        onError={handleError}
      />

      {successMessage && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="fixed top-4 right-4 bg-green-500 text-white p-4 rounded-xl shadow-lg z-50 max-w-md"
        >
          {successMessage}
        </motion.div>
      )}

      {errorMessage && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="fixed top-4 right-4 bg-red-500 text-white p-4 rounded-xl shadow-lg z-50 max-w-md"
        >
          {errorMessage}
        </motion.div>
      )}
    </div>
  );
};

export default Dashboard;
