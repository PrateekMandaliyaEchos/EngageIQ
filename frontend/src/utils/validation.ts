/**
 * Validation utilities
 */

export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const isValidCampaignName = (name: string): boolean => {
  return name.trim().length >= 3 && name.trim().length <= 100;
};

export const isValidCampaignGoal = (goal: string): boolean => {
  return goal.trim().length >= 10 && goal.trim().length <= 500;
};

export const isValidCSVFile = (file: File): boolean => {
  const allowedTypes = ['text/csv', 'application/vnd.ms-excel'];
  const maxSize = 10 * 1024 * 1024; // 10MB
  
  return allowedTypes.includes(file.type) && file.size <= maxSize;
};

