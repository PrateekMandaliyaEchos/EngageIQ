import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { apiService } from '../../services/api';
import { APP_CONFIG } from '../../constants';
import type { PlanStep } from '../../services/api';

interface ProcessingStepProps {
  step: PlanStep;
  isActive: boolean;
}

const ProcessingStep: React.FC<ProcessingStepProps> = ({ step, isActive }) => {
  const getStatusIcon = () => {
    switch (step.status) {
      case 'completed':
        return (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center"
          >
            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </motion.div>
        );
      case 'processing':
      case 'in_progress':
        return (
          <div className="w-8 h-8 bg-indigo-500 rounded-full flex items-center justify-center">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
          </div>
        );
      case 'error':
        return (
          <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </div>
        );
      default:
        return (
          <div className={`w-8 h-8 rounded-full border-2 ${isActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 bg-gray-50'} flex items-center justify-center`}>
            {isActive ? (
              <div className="relative">
                <svg className="w-5 h-5 text-indigo-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                </svg>
                <div className="absolute inset-0 animate-spin">
                  <div className="w-5 h-5 border-2 border-transparent border-t-indigo-500 rounded-full"></div>
                </div>
              </div>
            ) : (
              <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
              </svg>
            )}
          </div>
        );
    }
  };

  const getStatusText = () => {
    switch (step.status) {
      case 'completed':
        return { text: 'Completed', color: 'text-green-600' };
      case 'processing':
      case 'in_progress':
        return { text: step.active_form || 'Processing...', color: 'text-indigo-600' };
      case 'error':
        return { text: 'Error', color: 'text-red-600' };
      default:
        return { text: 'Pending', color: 'text-gray-500' };
    }
  };

  const statusInfo = getStatusText();

  return (
    <div className="flex items-center space-x-4 py-4">
      <div className="flex-shrink-0">
        {getStatusIcon()}
      </div>
      <div className="flex-1">
        <h3 className={`text-lg font-medium ${step.status === 'completed' || step.status === 'processing' || step.status === 'in_progress' ? 'text-gray-900' : 'text-gray-500'}`}>
          {step.active_form}
        </h3>
        <p className={`text-sm mt-1 ${statusInfo.color}`}>
          {statusInfo.text}
        </p>
        {step.agent && (
          <p className="text-xs text-gray-500 mt-1">Agent: {step.agent}</p>
        )}
        {step.error && (
          <p className="text-xs text-red-600 mt-1">Error: {step.error}</p>
        )}
      </div>
    </div>
  );
};

interface ProcessingPageProps {
  campaignId: string;
  onComplete: () => void;
  onError: (error: string) => void;
}

const ProcessingPage: React.FC<ProcessingPageProps> = ({ campaignId, onComplete, onError }) => {
  const [planSteps, setPlanSteps] = useState<PlanStep[]>([]);
  const [isPolling, setIsPolling] = useState(true);

  useEffect(() => {
    const pollPlanStatus = async () => {
      try {
        const steps = await apiService.getCampaignPlan(campaignId);
        setPlanSteps(steps);

        const allCompleted = steps.every(step => step.status === 'completed');
        const hasError = steps.some(step => step.status === 'error');

        if (hasError) {
          setIsPolling(false);
          onError('Campaign processing encountered an error');
          return;
        }

        if (allCompleted) {
          setIsPolling(false);
          setTimeout(() => {
            onComplete();
          }, 2000);
        }
      } catch (error) {
        setIsPolling(false);
        onError(error instanceof Error ? error.message : 'Failed to fetch plan status');
      }
    };

    const interval = setInterval(pollPlanStatus, APP_CONFIG.POLLING_INTERVAL);
    pollPlanStatus(); // Initial poll

    return () => clearInterval(interval);
  }, [campaignId, onComplete, onError]);

  // Calculate the active step dynamically based on the current plan steps
  const activeStepIndex = planSteps.findIndex(step => step.status === 'processing' || step.status === 'in_progress');
  const firstPendingIndex = planSteps.findIndex(step => step.status === 'pending');
  const actualActiveStepIndex = activeStepIndex !== -1 ? activeStepIndex : firstPendingIndex;

  const completedSteps = planSteps.filter(step => step.status === 'completed').length;
  const totalSteps = planSteps.length;
  const progressPercentage = totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0;

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-3xl">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">AI Campaign Processing</h1>
          <p className="text-gray-600">Our AI agents are analyzing your goals and creating the perfect campaign strategy</p>
        </div>

        <div className="border-l-2 border-gray-200 space-y-2 mb-8">
          {planSteps.map((step, index) => {
            const isActive = index === actualActiveStepIndex;

            return (
              <div key={step.step} className="pl-6 relative">
                {index < planSteps.length - 1 && (
                  <div className="absolute left-0 top-8 w-0.5 h-16"></div>
                )}
                <ProcessingStep
                  step={step}
                  isActive={isActive}
                />
              </div>
            );
          })}
        </div>

        <div className="p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
            <span>Processing Campaign: {campaignId}</span>
            <span>{Math.round(progressPercentage)}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <motion.div
              className="bg-indigo-600 h-2 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progressPercentage}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-2">
            {completedSteps} of {totalSteps} steps completed
          </p>
        </div>

        {!isPolling && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 text-center"
          >
            <div className="inline-flex items-center px-4 py-2 bg-green-100 text-green-800 rounded-lg">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Processing Complete! Redirecting to results...
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default ProcessingPage;
