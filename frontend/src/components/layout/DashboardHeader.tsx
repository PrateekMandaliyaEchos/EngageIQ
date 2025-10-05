import React, { useEffect, useState } from 'react';
import { apiService } from '../../services/api';
import { formatNumber } from '../../utils/format';


interface MetricCardProps {
  title: string;
  value: string;
  caption: string;
  bgColor: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, caption, bgColor }) => {
  return (
    <div className={`${bgColor} rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow duration-200`}>
      <div className="grid grid-rows-3 gap-3">
        <h3 className="text-sm font-medium text-gray-700 break-words">{title}</h3>
        <p className="text-3xl font-bold text-gray-900">{value}</p>
        
      </div>
      <p className="-mt-10 text-xs text-gray-600 leading-snug break-words">{caption}</p>
    </div>
  );
};


interface DashboardHeaderProps {
  onNewCampaign: () => void;
}

const DashboardHeader: React.FC<DashboardHeaderProps> = ({ onNewCampaign }) => {
  
  
  const [metrics, setMetrics] = useState<{
    title: string;
    value: string;
    caption: string;
    bgColor: string;
  }[]>([]);


  useEffect(() => {
    let isMounted = true;
    (async () => {
      try {
        const data = await apiService.getSegmentCounts();
        if (!isMounted) return;

        const segmentCounts = data.segment_counts || {};
        const metricsData = [
          {
            title: 'Total Existing Agents',
            value: formatNumber(data.total_agents),
            caption: "",
            bgColor: 'bg-blue-50'
            
          },
          {
            title: 'Accomplished Professionals',
            value: formatNumber(segmentCounts['Accomplished Professionals'] ?? 0),
            bgColor: 'bg-teal-50',
            caption: "Age: 51 - 60 Marital Status: Married No of children:<3 Fitness Enthusiasts"
          },
          {
            title: 'Emerging Experts',
            value: formatNumber(segmentCounts['Emerging Experts'] ?? 0),
            bgColor: 'bg-teal-50',
            caption: 'Age: 41 - 50 Agent Tenue: > 5 years Travel enthusiasts '

          },
          {
            title: 'Comfortable Retirees',
            value: formatNumber(
              segmentCounts['Comfortable retirees'] ?? segmentCounts['Comfortable Retirees'] ?? 0
            ),
            bgColor: 'bg-teal-50',
            caption:"Age: 71+ Family focused: # of children: > than three children"
          },
          {
            title: 'Independent Agents',
            value: formatNumber(segmentCounts['Independent Agents'] ?? 0),
            bgColor: 'bg-teal-50',
            caption: 'Age: 18 - 40 Marital Status: Single Agent Tenure: Less than 3 years'
          }
        ];

        setMetrics(metricsData);
      } catch (err) {
        // Fallback to empty metrics if API fails
        if (!isMounted) return;
        setMetrics([]);
      }
    })();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900">EngageIQ</h1>
            <p className="mt-2 text-lg text-gray-600">Unlocking Data-Driven Marketing Decisions</p>
          </div>
          <button
            onClick={onNewCampaign}
            className="bg-teal-600 hover:bg-teal-700 text-white font-semibold py-3 px-6 rounded-xl shadow-lg transition-colors duration-200 flex items-center space-x-2 cursor-pointer"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            <span>New Campaign</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {metrics.length === 0 ? (
            Array.from({ length: 5 }).map((_, index) => (
              <div
                key={index}
                className="bg-gray-200 rounded-xl p-6 shadow-sm animate-pulse"
              >
                <div className="h-4 bg-gray-300 mb-4 rounded w-3/4"></div>
                <div className="h-6 bg-gray-300 rounded w-1/2"></div>
              </div>
            ))
          ) : (
            metrics.map((metric, index) => (
              <MetricCard
                key={index}
                title={metric.title}
                value={metric.value}
                caption={metric.caption}
                bgColor={metric.bgColor}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardHeader;