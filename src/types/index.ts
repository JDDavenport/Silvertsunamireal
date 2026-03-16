// Types for ACQUISITOR

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: 'admin' | 'user';
  createdAt: Date;
  updatedAt: Date;
}

export interface Lead {
  id: string;
  title: string;
  description: string;
  askingPrice: number;
  revenue: number;
  profit: number;
  industry: string;
  location: string;
  source: string;
  status: 'new' | 'contacted' | 'evaluating' | 'offer' | 'diligence' | 'closed' | 'archived';
  score: number;
  owner: string;
  employees: number;
  yearFounded?: number;
  website?: string;
  contactName?: string;
  contactEmail?: string;
  contactPhone?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Deal {
  id: string;
  leadId: string;
  title: string;
  value: number;
  stage: 'sourcing' | 'screening' | 'loi' | 'diligence' | 'closing' | 'won' | 'lost';
  probability: number;
  expectedCloseDate?: Date;
  assignedTo: string;
  notes: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Activity {
  id: string;
  type: 'email' | 'call' | 'meeting' | 'note' | 'task' | 'document';
  title: string;
  description?: string;
  leadId?: string;
  dealId?: string;
  userId: string;
  createdAt: Date;
}

export interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  body: string;
  category: 'outreach' | 'follow-up' | 'offer' | 'diligence';
}

export interface PipelineStage {
  id: string;
  name: string;
  order: number;
  color: string;
  deals: Deal[];
}

export interface DashboardStats {
  totalLeads: number;
  newLeadsThisWeek: number;
  activeDeals: number;
  totalDealValue: number;
  avgDealSize: number;
  winRate: number;
}
