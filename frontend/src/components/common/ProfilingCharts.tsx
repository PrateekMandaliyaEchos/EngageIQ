import React from 'react';
import { 
  RadarChart, 
  Radar, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

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

interface ProfilingChartsProps {
  filteredAgents: AgentData[];
}

const ProfilingCharts: React.FC<ProfilingChartsProps> = ({ filteredAgents }) => {
  const avgNps = filteredAgents.length > 0 ? filteredAgents.reduce((sum, agent) => sum + agent.nps_score, 0) / filteredAgents.length : 0;
  const avgSalesDecline = filteredAgents.length > 0 ? 
    filteredAgents.reduce((sum, agent) => {
      const decline = ((agent.sales_previous_period - agent.sales_current_period) / agent.sales_previous_period) * 100;
      return sum + decline;
    }, 0) / filteredAgents.length : 0;
  const avgTenure = filteredAgents.length > 0 ? filteredAgents.reduce((sum, agent) => sum + agent.tenure_months, 0) / filteredAgents.length : 0;
  const avgProductMix = filteredAgents.length > 0 ? filteredAgents.reduce((sum, agent) => sum + agent.product_mix_score, 0) / filteredAgents.length : 0;

  const radarData = [
    { metric: 'NPS Score', value: avgNps, max: 10 },
    { metric: 'Sales Growth', value: 10 - avgSalesDecline, max: 10 },
    { metric: 'Product Mix', value: avgProductMix, max: 10 },
    { metric: 'Engagement', value: avgNps * 0.8, max: 10 },
    { metric: 'Responsiveness', value: avgTenure / 3, max: 10 }
  ];

  const regions = Array.from(new Set(filteredAgents.map(agent => agent.region)));
  const regionData = regions.map(region => ({
    region,
    count: filteredAgents.filter(agent => agent.region === region).length
  })).sort((a, b) => b.count - a.count).slice(0, 5);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-gray-50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">360 Profiling</h3>
        
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <p className="text-sm text-gray-600">Avg NPS</p>
            <p className="text-2xl font-bold text-indigo-600">{avgNps.toFixed(1)}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <p className="text-sm text-gray-600">Avg Sales Decline</p>
            <p className="text-2xl font-bold text-red-600">{avgSalesDecline.toFixed(1)}%</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <p className="text-sm text-gray-600">Avg Tenure</p>
            <p className="text-2xl font-bold text-green-600">{avgTenure.toFixed(0)}m</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <p className="text-sm text-gray-600">Agent Count</p>
            <p className="text-2xl font-bold text-purple-600">{filteredAgents.length}</p>
          </div>
        </div>

        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" />
              <PolarRadiusAxis angle={90} domain={[0, 10]} />
              <Radar name="Profile" dataKey="value" stroke="#4f46e5" fill="#4f46e5" fillOpacity={0.3} />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-gray-50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Regions</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={regionData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="region" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#4f46e5" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default ProfilingCharts;
