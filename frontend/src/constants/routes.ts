export const ROUTES = {
  DASHBOARD: '/',
  PROCESSING: '/processing/:campaignId',
  CAMPAIGN_RESULTS: '/campaign/:campaignId',
} as const;

// Dynamic API base URL based on environment
const getApiBaseUrl = () => {
  // In production (Render), use the current origin
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
    return `${window.location.origin}/api/v1`;
  }
  // In development, use localhost
  return 'http://localhost:8000/api/v1';
};

export const API_ENDPOINTS = {
  BASE_URL: getApiBaseUrl(),
  CAMPAIGNS: {
    CREATE: '/campaigns/create',
    PLAN: (id: string) => `/campaigns/${id}/plan`,
    RESULTS: (id: string) => `/campaigns/${id}/result`,
    ALL: '/campaigns/all',
    AGENT_PROFILES: (id: string) => `/campaigns/${id}/agent_profiles`,
  },
  ANALYTICS: {
    SEGMENT_COUNTS: '/analytics/segment-counts',
  },
} as const;

