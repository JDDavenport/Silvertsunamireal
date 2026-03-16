import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value);
}

export function formatDate(date: Date | string): string {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(date));
}

export function formatRelativeDate(date: Date | string): string {
  const now = new Date();
  const target = new Date(date);
  const diffInDays = Math.floor((now.getTime() - target.getTime()) / (1000 * 60 * 60 * 24));
  
  if (diffInDays === 0) return 'Today';
  if (diffInDays === 1) return 'Yesterday';
  if (diffInDays < 7) return `${diffInDays} days ago`;
  if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`;
  
  return formatDate(date);
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

export function getInitials(name: string): string {
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

export function calculateLeadScore(lead: {
  revenue: number;
  profit: number;
  employees: number;
  yearFounded?: number;
}): number {
  let score = 0;
  
  // Revenue scoring (0-30)
  if (lead.revenue >= 5000000) score += 30;
  else if (lead.revenue >= 2000000) score += 25;
  else if (lead.revenue >= 1000000) score += 20;
  else if (lead.revenue >= 500000) score += 15;
  else score += 10;
  
  // Profit margin scoring (0-30)
  const margin = lead.revenue > 0 ? (lead.profit / lead.revenue) * 100 : 0;
  if (margin >= 30) score += 30;
  else if (margin >= 20) score += 25;
  else if (margin >= 15) score += 20;
  else if (margin >= 10) score += 15;
  else score += 10;
  
  // Business age scoring (0-20)
  if (lead.yearFounded) {
    const age = new Date().getFullYear() - lead.yearFounded;
    if (age >= 10) score += 20;
    else if (age >= 5) score += 15;
    else if (age >= 3) score += 10;
    else score += 5;
  } else {
    score += 10;
  }
  
  // Team size scoring (0-20)
  if (lead.employees >= 20) score += 20;
  else if (lead.employees >= 10) score += 15;
  else if (lead.employees >= 5) score += 10;
  else score += 5;
  
  return Math.min(100, Math.max(0, score));
}

export function getScoreColor(score: number): string {
  if (score >= 80) return 'bg-emerald-500';
  if (score >= 60) return 'bg-blue-500';
  if (score >= 40) return 'bg-amber-500';
  return 'bg-red-500';
}

export function getScoreTextColor(score: number): string {
  if (score >= 80) return 'text-emerald-600 dark:text-emerald-400';
  if (score >= 60) return 'text-blue-600 dark:text-blue-400';
  if (score >= 40) return 'text-amber-600 dark:text-amber-400';
  return 'text-red-600 dark:text-red-400';
}
