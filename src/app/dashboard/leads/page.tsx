"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import {
  Search,
  Filter,
  Plus,
  MoreHorizontal,
  Mail,
  Phone,
  Star,
  Building2,
  ArrowUpDown,
  ChevronDown,
  Download,
  Trash2,
  Edit,
  Eye,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

// Mock data for leads
const mockLeads = [
  {
    id: "1",
    name: "John Smith",
    company: "TechStart Inc",
    email: "john@techstart.com",
    phone: "+1 (555) 123-4567",
    score: 92,
    status: "qualified",
    industry: "Technology",
    revenue: "$2.5M",
    location: "San Francisco, CA",
    lastContact: "2 days ago",
  },
  {
    id: "2",
    name: "Sarah Johnson",
    company: "Growth Labs",
    email: "sarah@growthlabs.com",
    phone: "+1 (555) 987-6543",
    score: 87,
    status: "contacted",
    industry: "Marketing",
    revenue: "$1.8M",
    location: "New York, NY",
    lastContact: "5 days ago",
  },
  {
    id: "3",
    name: "Michael Chen",
    company: "DataFlow Systems",
    email: "michael@dataflow.io",
    phone: "+1 (555) 456-7890",
    score: 95,
    status: "new",
    industry: "Software",
    revenue: "$4.2M",
    location: "Austin, TX",
    lastContact: "1 day ago",
  },
  {
    id: "4",
    name: "Emily Davis",
    company: "Retail Plus",
    email: "emily@retailplus.com",
    phone: "+1 (555) 234-5678",
    score: 72,
    status: "proposal",
    industry: "Retail",
    revenue: "$3.1M",
    location: "Chicago, IL",
    lastContact: "1 week ago",
  },
  {
    id: "5",
    name: "David Wilson",
    company: "BuildRight Construction",
    email: "david@buildright.com",
    phone: "+1 (555) 876-5432",
    score: 65,
    status: "closed",
    industry: "Construction",
    revenue: "$5.5M",
    location: "Denver, CO",
    lastContact: "2 weeks ago",
  },
  {
    id: "6",
    name: "Lisa Anderson",
    company: "HealthFirst Clinics",
    email: "lisa@healthfirst.com",
    phone: "+1 (555) 345-6789",
    score: 88,
    status: "qualified",
    industry: "Healthcare",
    revenue: "$6.2M",
    location: "Miami, FL",
    lastContact: "3 days ago",
  },
  {
    id: "7",
    name: "Robert Taylor",
    company: "FoodCraft Restaurants",
    email: "robert@foodcraft.com",
    phone: "+1 (555) 567-8901",
    score: 58,
    status: "new",
    industry: "Food & Beverage",
    revenue: "$1.2M",
    location: "Seattle, WA",
    lastContact: "Just now",
  },
];

const statusColors: Record<string, string> = {
  new: "bg-[#DBEAFE] text-[#2563EB] hover:bg-[#DBEAFE]",
  contacted: "bg-[#FEF3C7] text-[#D97706] hover:bg-[#FEF3C7]",
  qualified: "bg-[#D1FAE5] text-[#059669] hover:bg-[#D1FAE5]",
  proposal: "bg-[#F3E8FF] text-[#9333EA] hover:bg-[#F3E8FF]",
  closed: "bg-[#F0F0F0] text-[#6B6B6B] hover:bg-[#F0F0F0]",
};

const statusLabels: Record<string, string> = {
  new: "New",
  contacted: "Contacted",
  qualified: "Qualified",
  proposal: "Proposal",
  closed: "Closed",
};

function getScoreColor(score: number) {
  if (score >= 90) return "text-[#059669]";
  if (score >= 70) return "text-[#D97706]";
  return "text-[#DC2626]";
}

function getScoreBg(score: number) {
  if (score >= 90) return "bg-[#D1FAE5]";
  if (score >= 70) return "bg-[#FEF3C7]";
  return "bg-[#FEE2E2]";
}

function LeadsLoading() {
  return (
    <div className="space-y-4">
      <div className="h-10 bg-[#F0F0F0] animate-pulse rounded-lg" />
      <div className="h-96 bg-[#F0F0F0] animate-pulse rounded-lg" />
    </div>
  );
}

function EmptyLeads() {
  return (
    <Card className="border-[#E2E2E2]">
      <CardContent className="p-12 text-center">
        <div className="w-16 h-16 rounded-full bg-[#F0F4FA] flex items-center justify-center mx-auto mb-4">
          <Building2 className="w-8 h-8 text-[#3B5A9A]" />
        </div>
        <h3 className="text-lg font-semibold text-[#1A1A1A] mb-2">
          No leads yet
        </h3>
        <p className="text-sm text-[#6B6B6B] max-w-sm mx-auto mb-6">
          Start building your pipeline by adding your first lead. You can import
          leads or add them manually.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <Button className="bg-[#C9A227] hover:bg-[#A6851F] text-[#0A1628] font-semibold">
            <Plus className="w-4 h-4 mr-2" />
            Add Lead
          </Button>
          <Button variant="outline" className="border-[#E2E2E2] text-[#4A4A4A]">
            <Download className="w-4 h-4 mr-2" />
            Import
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function LeadsTable({ leads }: { leads: typeof mockLeads }) {
  if (leads.length === 0) {
    return <EmptyLeads />;
  }

  return (
    <Card className="border-[#E2E2E2] overflow-hidden">
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="w-[250px]">
                <div className="flex items-center gap-1 cursor-pointer">
                  Name
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </TableHead>
              <TableHead>Company</TableHead>
              <TableHead>Score</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Industry</TableHead>
              <TableHead>Revenue</TableHead>
              <TableHead>Last Contact</TableHead>
              <TableHead className="w-[50px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {leads.map((lead) => (
              <TableRow key={lead.id} className="group">
                <TableCell>
                  <div>
                    <p className="font-medium text-[#1A1A1A]">{lead.name}</p>
                    <p className="text-sm text-[#6B6B6B]">{lead.email}</p>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-[#8A8A8A]" />
                    <span className="text-[#4A4A4A]">{lead.company}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-8 h-8 rounded-full ${getScoreBg(
                        lead.score
                      )} flex items-center justify-center`}
                    >
                      <span
                        className={`text-sm font-semibold ${getScoreColor(
                          lead.score
                        )}`}
                      >
                        {lead.score}
                      </span>
                    </div>
                    <Star
                      className={`w-4 h-4 ${
                        lead.score >= 90
                          ? "text-[#C9A227] fill-[#C9A227]"
                          : "text-[#E2E2E2]"
                      }`}
                    />
                  </div>
                </TableCell>
                <TableCell>
                  <Badge
                    variant="secondary"
                    className={statusColors[lead.status]}
                  >
                    {statusLabels[lead.status]}
                  </Badge>
                </TableCell>
                <TableCell className="text-[#4A4A4A]">
                  {lead.industry}
                </TableCell>
                <TableCell className="font-medium text-[#1A1A1A]">
                  {lead.revenue}
                </TableCell>
                <TableCell className="text-[#6B6B6B]">
                  {lead.lastContact}
                </TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <MoreHorizontal className="w-4 h-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-48">
                      <DropdownMenuLabel>Actions</DropdownMenuLabel>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem>
                        <Eye className="w-4 h-4 mr-2" />
                        View Details
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        <Edit className="w-4 h-4 mr-2" />
                        Edit Lead
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        <Mail className="w-4 h-4 mr-2" />
                        Send Email
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        <Phone className="w-4 h-4 mr-2" />
                        Call
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem className="text-[#DC2626]">
                        <Trash2 className="w-4 h-4 mr-2" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </Card>
  );
}

function LeadsContent() {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const filteredLeads = mockLeads.filter((lead) => {
    const matchesSearch =
      lead.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      lead.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
      lead.email.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus =
      statusFilter === "all" || lead.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#1A1A1A]">
            Leads
          </h1>
          <p className="text-[#6B6B6B] mt-1">
            Manage and track your acquisition prospects
          </p>
        </div>
        <Button className="bg-[#C9A227] hover:bg-[#A6851F] text-[#0A1628] font-semibold">
          <Plus className="w-4 h-4 mr-2" />
          Add Lead
        </Button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <Card className="border-[#E2E2E2]">
          <CardContent className="p-4">
            <p className="text-sm text-[#6B6B6B]">Total Leads</p>
            <p className="text-2xl font-bold text-[#1A1A1A]">{mockLeads.length}</p>
          </CardContent>
        </Card>
        <Card className="border-[#E2E2E2]">
          <CardContent className="p-4">
            <p className="text-sm text-[#6B6B6B]">Qualified</p>
            <p className="text-2xl font-bold text-[#059669]">
              {mockLeads.filter((l) => l.status === "qualified").length}
            </p>
          </CardContent>
        </Card>
        <Card className="border-[#E2E2E2]">
          <CardContent className="p-4">
            <p className="text-sm text-[#6B6B6B]">In Progress</p>
            <p className="text-2xl font-bold text-[#D97706]">
              {
                mockLeads.filter((l) =>
                  ["contacted", "proposal"].includes(l.status)
                ).length
              }
            </p>
          </CardContent>
        </Card>
        <Card className="border-[#E2E2E2]">
          <CardContent className="p-4">
            <p className="text-sm text-[#6B6B6B]">Avg Score</p>
            <p className="text-2xl font-bold text-[#3B5A9A]">
              {Math.round(
                mockLeads.reduce((acc, l) => acc + l.score, 0) / mockLeads.length
              )}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8A8A8A]" />
          <Input
            placeholder="Search leads by name, company, or email..."
            className="pl-10 border-[#E2E2E2] focus-visible:ring-[#3B5A9A]"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Select value={statusFilter} onValueChange={(val) => setStatusFilter(val || "all")}>
          <SelectTrigger className="w-full sm:w-[180px] border-[#E2E2E2]">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="new">New</SelectItem>
            <SelectItem value="contacted">Contacted</SelectItem>
            <SelectItem value="qualified">Qualified</SelectItem>
            <SelectItem value="proposal">Proposal</SelectItem>
            <SelectItem value="closed">Closed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Table */}
      <LeadsTable leads={filteredLeads} />
    </div>
  );
}

export default function LeadsPage() {
  return (
    <Suspense fallback={<LeadsLoading />}>
      <LeadsContent />
    </Suspense>
  );
}
