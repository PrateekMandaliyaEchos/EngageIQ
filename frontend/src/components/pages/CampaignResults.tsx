import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { apiService, type SegmentStrategy, type AgentProfilesResponse, type AgentProfile } from '../../services/api';
import { getSegmentColor, formatCurrency, computeIncrementalRevenue, formatPercentage } from '../../utils';
import StrategyNarrative from '../common/StrategyNarrative';
import { useAveragePoliciesBySegment, useAveragePremiumBySegment } from '../../hooks';

type ProfileRow = AgentProfile;

interface CampaignFilters {
  nps_min: number;
  sales_decline_pct: number;
  regions: string[];
  tenure_min: number;
}

interface CampaignResultsProps {
  campaignId: string;
  campaignName: string;
  campaign_strategy?: string;
  onBack: () => void;
  onCreateCampaign: () => void;
}

// Removed sample generator; we use real agent profiles from backend

const CampaignResults: React.FC<CampaignResultsProps> = ({
  campaignId,
  campaignName,
  onBack,
  onCreateCampaign: _onCreateCampaign
}) => {
  const [campaignData, setCampaignData] = useState<any>(null);
  const [segments, setSegments] = useState<ProfileRow[]>([]);
  const [resultsLoading, setResultsLoading] = useState(true);
  const [agentsLoading, setAgentsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters] = useState<CampaignFilters>({
    nps_min: 7,
    sales_decline_pct: 10,
    regions: [],
    tenure_min: 6
  });

  useEffect(() => {
    const fetchResults = async () => {
      try {
        setResultsLoading(true);
        setAgentsLoading(true);
        const result = await apiService.getCampaignResults(campaignId);
        console.log(result);

        // Set campaign data
        setCampaignData(result);
        setResultsLoading(false);

        // Fetch agent profiles async (no region derivation)
        try {
          const profiles: AgentProfilesResponse = await apiService.getAgentProfiles(campaignId);
          const mapped: ProfileRow[] = (profiles.agent_profiles || []).map(p => ({ ...p }));
          setSegments(mapped);
        } catch (e) {
          console.error('Error fetching agent profiles:', e);
          // Keep segments empty on failure
          setSegments([]);
        } finally {
          setAgentsLoading(false);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch results');
        setResultsLoading(false);
        setAgentsLoading(false);
      }
    };

    fetchResults();
  }, [campaignId]);

  const averagePoliciesBySegment = useAveragePoliciesBySegment({ profiles: segments });
  const averagePremiumBySegment = useAveragePremiumBySegment({ profiles: segments });
  const incrementalRevenue = useMemo(() => computeIncrementalRevenue(segments), [segments]);

  const legacyAgents = useMemo(() => segments.map(agent => ({
    agent_id: agent.agent_id,
    name: agent.name,
    email: '',
    nps_score: agent.nps_score,
    sales_current_period: 0,
    sales_previous_period: 0,
    region: '',
    tenure_months: Math.round(agent.tenure * 12),
    product_mix_score: 0,
  })), [segments]);

  const filteredAgents = legacyAgents.filter(agent => {
    const salesDecline = ((agent.sales_previous_period - agent.sales_current_period) / (agent.sales_previous_period || 1)) * 100;
    return (
      agent.nps_score >= filters.nps_min &&
      salesDecline >= filters.sales_decline_pct &&
      (filters.regions.length === 0 || filters.regions.includes(agent.region)) &&
      agent.tenure_months >= filters.tenure_min
    );
  });

  if (resultsLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
          <p className="text-gray-600">Loading campaign results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-xl shadow-sm p-8 max-w-md text-center">
          <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Results</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Campaign Results: {campaignName}</h1>
              <p className="mt-2 text-lg text-gray-600">AI-generated campaign strategy and agent segments</p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={onBack}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
              >
                Back to Dashboard
              </button>
              {/* <button
                onClick={onCreateCampaign}
                className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors"
              >
                Create Campaign
              </button> */}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-green-50 border border-green-200 rounded-xl p-6"
        >
          <div className="flex items-center">
            <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center mr-4">
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-green-800">Campaign Analysis Complete</h3>
              <p className="text-green-700">EngageIQ successfully analyzed agents and generated a comprehensive strategy targeting {campaignData?.total_agents || segments.length} agents across {Object.keys(campaignData?.segment_strategies || {}).length} segments.</p>
            </div>
          </div>
        </motion.div>

        {campaignData && (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-white rounded-xl shadow-sm p-6"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Campaign Overview</h3>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Objective:</span>
                    <span className="font-medium capitalize">{campaignData.objective}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Agents:</span>
                    <span className="font-medium">{campaignData.total_agents}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Segments:</span>
                    <span className="font-medium">{Object.keys(campaignData.segment_strategies).length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Budget:</span>
                    <span className="font-medium">{formatCurrency(Object.values(campaignData.segment_strategies as Record<string, SegmentStrategy>).reduce((sum: number, segment: SegmentStrategy) => sum + segment.budget.total_budget, 0))}</span>
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-white rounded-xl shadow-sm p-6"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Campaign Metrics</h3>
                <div className="space-y-4">

                  <div className="flex justify-between">
                    <span className="text-gray-600">Avg Budget/Agent:</span>
                    <span className="font-medium text-blue-600">{formatCurrency(Math.round(Object.values(campaignData.segment_strategies as Record<string, SegmentStrategy>).reduce((sum: number, segment: SegmentStrategy) => sum + segment.budget.budget_per_agent, 0) / Object.keys(campaignData.segment_strategies).length))}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Success Status:</span>
                    <span className="font-medium text-green-600">{campaignData.success ? 'Active' : 'Pending'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Strategy Type:</span>
                    <span className="font-medium">AI-Generated</span>
                  </div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="bg-white rounded-xl shadow-sm p-6"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Segment Distribution</h3>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={Object.entries(campaignData.segment_strategies as Record<string, SegmentStrategy>).map(([, segment]: [string, SegmentStrategy]) => ({
                          name: segment.segment_name,
                          value: segment.percentage_of_campaign,
                          color: getSegmentColor(segment.segment_name)
                        }))}
                        cx="50%"
                        cy="50%"
                        innerRadius={40}
                        outerRadius={80}
                        dataKey="value"
                      >
                        {Object.entries(campaignData.segment_strategies as Record<string, SegmentStrategy>).map(([, segment]: [string, SegmentStrategy], index) => (
                          <Cell key={`cell-${index}`} fill={getSegmentColor(segment.segment_name)} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => [formatPercentage(Number(value), 2), 'Percentage']} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </motion.div>
            </div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white rounded-xl shadow-sm p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Budget Allocation by Segment</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={Object.entries(campaignData.segment_strategies as Record<string, SegmentStrategy>).map(([, segment]: [string, SegmentStrategy]) => ({
                    segment: segment.segment_name,
                    budget: segment.budget.total_budget,
                    agents: segment.agent_count,
                    percentage: segment.percentage_of_campaign
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="segment" />
                    <YAxis />
                    <Tooltip formatter={(value, name) => [
                      name === 'budget'
                        ? `$${Number(value).toLocaleString()}`
                        : name === 'percentage'
                          ? formatPercentage(Number(value), 2)
                          : String(value),
                      name === 'budget' ? 'Budget' : name === 'agents' ? 'Agents' : 'Percentage']}
                    />
                    <Bar dataKey="budget" fill="#4f46e5" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="space-y-6"
            >
              <h3 className="text-2xl font-bold text-gray-900">Segment Strategies</h3>
              {Object.entries(campaignData.segment_strategies as Record<string, SegmentStrategy>).map(([key, segment]: [string, SegmentStrategy], index) => (
                <motion.div
                  key={key}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 + index * 0.1 }}
                  className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-indigo-500"
                >
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-xl font-semibold text-gray-900">{segment.segment_name}</h4>
                    <div className="flex space-x-4 text-sm">
                      <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
                        {segment.agent_count} agents
                      </span>
                      <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full">
                        {formatPercentage(segment.percentage_of_campaign, 2)} of campaign
                      </span>
                      <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full">
                        {formatCurrency(segment.budget.total_budget)} budget
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div>
                      <StrategyNarrative strategyNarrative={segment.strategy_narrative} />
                    </div>
                    <div className="space-y-4">
                      <div>
                        <h5 className="font-medium text-gray-700 mb-2">Messaging</h5>
                        <div className="bg-gray-50 p-3 rounded-lg">
                          <p className="text-sm text-gray-600 mb-2">
                            <span className="font-medium">Tone:</span> {segment.messaging.tone}
                          </p>
                          <p className="text-sm text-gray-600 mb-2">
                            <span className="font-medium">Key Message:</span> {segment.messaging.key_message}
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {(segment.messaging.hooks || []).map((hook, hookIndex) => (
                              <span key={hookIndex} className="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded">
                                {hook}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div>
                        <h5 className="font-medium text-gray-700 mb-2">Channels</h5>
                        <div className="flex flex-wrap gap-2">
                          {(segment.channels?.channel_sequence || []).map((channel, channelIndex) => (
                            <span key={channelIndex} className="bg-green-100 text-green-800 text-sm px-3 py-1 rounded-full">
                              {channel}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h5 className="font-medium text-gray-700 mb-2">Budget Details</h5>
                        <div className="bg-gray-50 p-3 rounded-lg">
                          <p className="text-sm text-gray-600 mb-1">
                            <span className="font-medium">Per Agent:</span> {formatCurrency(segment.budget.budget_per_agent)}
                          </p>
                          <p className="text-sm text-gray-600">
                            <span className="font-medium">Rationale:</span> {segment.budget.rationale}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4">
                    <h5 className="font-medium text-gray-700 mb-2">Key Insights</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">

                      {(segment.key_insights || []).map((insight, insightIndex) => (
                        <div key={insightIndex} className="bg-blue-50 p-2 rounded text-sm text-blue-800">
                          {insight}
                        </div>
                      ))}
                      <div className="bg-blue-50 p-2 rounded text-sm text-blue-800">
                        Avg premium: {formatCurrency(averagePremiumBySegment[segment.segment_name] ?? 0)}
                      </div>
                      <div className="bg-blue-50 p-2 rounded text-sm text-blue-800">
                        Avg policies sold: {averagePoliciesBySegment[segment.segment_name] ?? 0}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </>
        )}

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl shadow-sm p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Agent Profiles</h3>
            <button
              onClick={() => {
                const headers = ['agent_id', 'name', 'segment', 'city', 'aum', 'nps_score', 'tenure', 'policies_sold', 'premium_amount'];
                const rows = segments.map(a => [
                  a.agent_id,
                  a.name,
                  a.segment,
                  a.city,
                  a.aum,
                  a.nps_score,
                  a.tenure,
                  a.policies_sold,
                  a.premium_amount ?? ''
                ]);
                const csv = [headers.join(','), ...rows.map(r => r.map(v => {
                  const s = String(v ?? '');
                  return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
                }).join(','))].join('\n');
                const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', `agent_profiles_${campaignId}.csv`);
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
              }}
              className="px-3 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors cursor-pointer"
            >
              Download agent data as CSV
            </button>
          </div>
          {agentsLoading ? (
            <div className="text-center py-8">
              <div className="inline-flex items-center space-x-2">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
                <span className="text-gray-600">Generating agent profiles...</span>
              </div>
              <p className="text-sm text-gray-500 mt-2">This process typically takes 2-3 minutes. Please wait while we analyze and generate detailed agent profiles.</p>
              <div className="mt-4">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-indigo-600 h-2 rounded-full animate-pulse" style={{width: '60%'}}></div>
                </div>
              </div>
            </div>
          ) : segments.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-600">No target agents found for this campaign.</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white border border-gray-200 rounded-lg">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Segment</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">City</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">AUM</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">NPS</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Tenure (yrs)</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Policies</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Premium</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {segments.slice(0, 10).map((agent, index) => (
                      <tr key={index}>
                        <td className="px-3 py-2 text-sm text-gray-900">{agent.name}</td>
                        <td className="px-3 py-2 text-sm text-gray-900">{agent.segment}</td>
                        <td className="px-3 py-2 text-sm text-gray-900">{agent.city}</td>
                        <td className="px-3 py-2 text-sm text-gray-900">{agent.aum.toLocaleString()}</td>
                        <td className="px-3 py-2 text-sm text-gray-900">{agent.nps_score}</td>
                        <td className="px-3 py-2 text-sm text-gray-900">{agent.tenure}</td>
                        <td className="px-3 py-2 text-sm text-gray-900">{agent.policies_sold}</td>
                        <td className="px-3 py-2 text-sm text-gray-900">{agent.premium_amount != null ? formatCurrency(agent.premium_amount) : '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {segments.length > 10 && (
                <p className="mt-3 text-sm text-gray-600 text-center">
                  Showing first 10 rows of {segments.length} total agents
                </p>
              )}
            </>
          )}
        </motion.div>






        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Campaign Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{campaignData?.total_agents || filteredAgents.length}</div>
              <div className="text-sm text-blue-800">Targeted Agents</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{campaignData ? formatCurrency(Object.values(campaignData.segment_strategies as Record<string, SegmentStrategy>).reduce((sum: number, segment: SegmentStrategy) => sum + segment.budget.total_budget, 0)) : formatCurrency(filteredAgents.length * 500)}</div>
              <div className="text-sm text-green-800">Total Budget</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">{formatCurrency(incrementalRevenue)}</div>
              <div className="text-sm text-yellow-800">Incremental Revenue</div>
            </div>

            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">{Object.keys(campaignData?.segment_strategies || {}).length}</div>
              <div className="text-sm text-orange-800">Active Segments</div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default CampaignResults;