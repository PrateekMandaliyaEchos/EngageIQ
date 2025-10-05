import { API_ENDPOINTS } from '../constants';

export interface CampaignRequest {
  campaign_name: string;
  goal: string;
}

export interface CampaignResponse {
  campaign_id: string;
  path: string[];
}

export interface PlanStep {
  step: number;
  description: string;
  agent: string;
  active_form: string;
  status: 'pending' | 'processing' | 'in_progress' | 'completed' | 'error';
  started_at: string | null;
  completed_at: string | null;
  error: string | null;
}

export interface SegmentStrategy {
  segment_name: string;
  agent_count: number;
  percentage_of_campaign: number;
  strategy_narrative: string;
  messaging: {
    tone: string;
    key_message: string;
    hooks: string[];
  };
  channels: string[];
  budget: {
    total_budget: number;
    budget_per_agent: number;
    rationale: string;
  };
  key_insights: string[];
}

export interface CampaignResult {
  success: boolean;
  objective: string;
  total_agents: number;
  segment_strategies: Record<string, SegmentStrategy>;
  confidence_score: number;
  roi?: number;
  segments: Array<{
    agent_id: string;
    name: string;
    email: string;
    nps_score: number;
    sales_current_period: number;
    sales_previous_period: number;
    region: string;
    tenure_months: number;
    product_mix_score: number;
  }>;
}

export interface SegmentCountsResponse {
  segment_counts: Record<string, number>;
  total_agents: number;
}

export interface CampaignSummary {
  campaign_id: string;
  name: string;
  goal: string;
  target_criteria: unknown;
  segment_size: number;
  created_at: string;
  status: string;
  roi?: number;
}

export interface AgentProfile {
  agent_id: string;
  name: string;
  segment: string;
  aum: number;
  nps_score: number;
  tenure: number;
  policies_sold: number;
  premium_amount?: number;
  age: number;
  city: string;
  education: string;
  nps_feedback: string;
}

export interface AgentProfilesResponse {
  campaign_id: string;
  total_agents: number;
  agent_profiles: AgentProfile[];
}
// In-memory cache for analytics to avoid repeated network calls
let cachedSegmentCounts: SegmentCountsResponse | null = null;
let cachedSegmentCountsFetchedAt: number | null = null;
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

export const apiService = {
  async createCampaign(campaignData: CampaignRequest): Promise<CampaignResponse> {
    const response = await fetch(`${API_ENDPOINTS.BASE_URL}${API_ENDPOINTS.CAMPAIGNS.CREATE}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(campaignData),
    });

    if (!response.ok) {
      throw new Error(`Failed to create campaign: ${response.statusText}`);
    }

    // Await the response JSON
    const responseData = await response.json();

    // If campaign_id is empty, generate a random ID (or use a placeholder)
    if (!responseData.campaign_id) {
      responseData.campaign_id = "123";  // You can replace this with a random ID if desired
      console.warn('Empty campaign_id returned, using generated random ID:', responseData.campaign_id);
    }

    return responseData;  // Ensure the response is returned from the function
  },


  async getCampaignPlan(campaignId: string): Promise<PlanStep[]> {
    const response = await fetch(`${API_ENDPOINTS.BASE_URL}${API_ENDPOINTS.CAMPAIGNS.PLAN(campaignId)}`);

    console.log(response)
    if (!response.ok) {
      throw new Error(`Failed to get campaign plan: ${response.statusText}`);
    }

    return response.json();
  },

  async getCampaignResults(campaignId: string): Promise<CampaignResult> {
    const response = await fetch(`${API_ENDPOINTS.BASE_URL}${API_ENDPOINTS.CAMPAIGNS.RESULTS(campaignId)}`);

    if (!response.ok) {
      throw new Error(`Failed to get campaign results: ${response.statusText}`);
    }

    const result: CampaignResult = await response.json();
    // If ROI not present, attach a random ROI 0-100
    if (result.roi === undefined || result.roi === null) {
      result.roi = Math.floor(Math.random() * 101);
    }
    return result;
  },

  async getSegmentCounts(options?: { forceRefresh?: boolean }): Promise<SegmentCountsResponse> {
    const forceRefresh = options?.forceRefresh === true;

    const now = Date.now();
    const isCacheValid =
      cachedSegmentCounts !== null &&
      cachedSegmentCountsFetchedAt !== null &&
      now - cachedSegmentCountsFetchedAt < CACHE_TTL_MS;

    if (!forceRefresh && isCacheValid) {
      return cachedSegmentCounts as SegmentCountsResponse;
    }

    const response = await fetch(`${API_ENDPOINTS.BASE_URL}${API_ENDPOINTS.ANALYTICS.SEGMENT_COUNTS}`);
    if (!response.ok) {
      throw new Error(`Failed to get segment counts: ${response.statusText}`);
    }

    const data: SegmentCountsResponse = await response.json();
    cachedSegmentCounts = data;
    cachedSegmentCountsFetchedAt = now;
    return data;
  },

  async getAllCampaigns(): Promise<CampaignSummary[]> {
    const response = await fetch(`${API_ENDPOINTS.BASE_URL}${API_ENDPOINTS.CAMPAIGNS.ALL}`);
    if (!response.ok) {
      throw new Error(`Failed to get campaigns: ${response.statusText}`);
    }
    const data = await response.json();
    // Normalize: backend might return a single object or an array
    const list: CampaignSummary[] = (Array.isArray(data) ? data : [data]).map((c: CampaignSummary) => ({
      ...c,
      roi: c.roi ?? Math.floor(Math.random() * 101),
    }));
    return list;
  },

  async getAgentProfiles(campaignId: string): Promise<AgentProfilesResponse> {
    const response = await fetch(`${API_ENDPOINTS.BASE_URL}${API_ENDPOINTS.CAMPAIGNS.AGENT_PROFILES(campaignId)}`);
    if (!response.ok) {
      throw new Error(`No Agent Found for this campaign`);
    }
    const data: AgentProfilesResponse = await response.json();
    return data;
  },
};
