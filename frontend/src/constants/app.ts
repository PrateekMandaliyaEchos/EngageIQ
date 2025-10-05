export const APP_CONFIG = {
  NAME: 'EngageIQ',
  VERSION: '1.0.0',
  POLLING_INTERVAL: 2000, // 2 seconds
  SUCCESS_MESSAGE_DURATION: 3000, // 3 seconds
  ERROR_MESSAGE_DURATION: 5000, // 5 seconds
} as const;

export const CAMPAIGN_STATUS = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  ERROR: 'error',
} as const;

export const SEGMENT_COLORS = {
  'Emerging Experts': '#4f46e5',
  'Independent Agents': '#059669',
  'High Performers': '#dc2626',
  'Default': '#ea580c',
} as const;

