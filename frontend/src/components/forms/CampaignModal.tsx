import React, { useRef, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import CampaignForm from './CampaignForm';
import { apiService } from '../../services/api'; 

interface CampaignModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCampaignCreated: (campaignId: string, campaignName: string) => void;
  onError: (error: string) => void;
}

const CampaignModal: React.FC<CampaignModalProps> = ({
  isOpen,
  onClose,
  onCampaignCreated,
  onError
}) => {
  const [campaignData, setCampaignData] = useState({
    campaign_name: '',
    goals: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  useEffect(() => {
    if (isOpen && modalRef.current) {
      modalRef.current.focus();
    }
  }, [isOpen]);

  const handleCreateCampaign = async () => {
    if (!campaignData.campaign_name.trim() || !campaignData.goals.trim()) {
      onError('Please fill in both campaign name and goals');
      return;
    }

    setIsLoading(true);
    try {
      const response = await apiService.createCampaign({
        campaign_name: campaignData.campaign_name,
        goal: campaignData.goals
      });

      onCampaignCreated(response.campaign_id, campaignData.campaign_name);
      onClose();
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Failed to create campaign');
    } finally {
      setIsLoading(false);
    }
  };

  const isFormValid = campaignData.campaign_name.trim() && campaignData.goals.trim();

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={(e) => e.target === e.currentTarget && onClose()}
        >
          <motion.div
            ref={modalRef}
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col"
            tabIndex={-1}
          >
            <div className="flex items-center justify-between p-6 border-b border-gray-200 flex-shrink-0">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Create New Campaign</h2>
                <p className="text-gray-600">Enter your campaign details and let our EngageIQ create the perfect strategy</p>
              </div>              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
                aria-label="Close modal"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              <CampaignForm
                campaignData={campaignData}
                onCampaignDataChange={setCampaignData}
              />
            </div>

            <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50 flex-shrink-0">
              <button
                onClick={onClose}
                disabled={isLoading}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateCampaign}
                disabled={!isFormValid || isLoading}
                className={`px-6 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2 ${isFormValid && !isLoading
                  ? 'bg-indigo-600 hover:bg-indigo-700 text-white cursor-pointer'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Creating...</span>
                  </>
                ) : (
                  <span>Create Campaign</span>
                )}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default CampaignModal;