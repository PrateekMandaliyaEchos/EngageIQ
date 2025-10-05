export const ROUTES = {
  DASHBOARD: '/',
  PROCESSING: '/processing/:campaignId',
  CAMPAIGN_RESULTS: '/campaign/:campaignId',
} as const;

export const API_ENDPOINTS = {
  BASE_URL: '/api/v1',
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

