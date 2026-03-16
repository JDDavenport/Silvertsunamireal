"use client";

import { Suspense, useState } from "react";
import {
  Plus,
  MoreHorizontal,
  Calendar,
  DollarSign,
  Building2,
  User,
  ArrowRight,
  ArrowLeft,
  Filter,
  Search,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
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
import { cn } from "@/lib/utils";

// Pipeline stages
const stages = [
  { id: "new", name: "New", color: "#DBEAFE", textColor: "#2563EB" },
  { id: "contacted", name: "Contacted", color: "#FEF3C7", textColor: "#D97706" },
  { id: "qualified", name: "Qualified", color: "#D1FAE5", textColor: "#059669" },
  { id: "proposal", name: "Proposal", color: "#F3E8FF", textColor: "#9333EA" },
  { id: "closed", name: "Closed", color: "#F0F0F0", textColor: "#6B6B6B" },
] as const;

// Mock deals data
const mockDeals = [
  {
    id: "1",
    title: "TechStart Inc Acquisition",
    company: "TechStart Inc",
    contact: "John Smith",
    value: 2500000,
    probability: 75,
    stage: "qualified",
    expectedClose: "2026-04-15",
    industry: "Technology",
  },
  {
    id: "2",
    title: "Growth Labs Purchase",
    company: "Growth Labs",
    contact: "Sarah Johnson",
    value: 1800000,
    probability: 60,
    stage: "contacted",
    expectedClose: "2026-05-01",
    industry: "Marketing",
  },
  {
    id: "3",
    title: "DataFlow Systems Buyout",
    company: "DataFlow Systems",
    contact: "Michael Chen",
    value: 4200000,
    probability: 40,
    stage: "new",
    expectedClose: "2026-06-30",
    industry: "Software",
  },
  {
    id: "4",
    title: "Retail Plus Takeover",
    company: "Retail Plus",
    contact: "Emily Davis",
    value: 3100000,
    probability: 85,
    stage: "proposal",
    expectedClose: "2026-03-30",
    industry: "Retail",
  },
  {
    id: "5",
    title: "BuildRight Construction",
    company: "BuildRight Construction",
    contact: "David Wilson",
    value: 5500000,
    probability: 100,
    stage: "closed",
    expectedClose: "2026-02-28",
    industry: "Construction",
  },
  {
    id: "6",
    title: "HealthFirst Clinics",
    company: "HealthFirst Clinics",
    contact: "Lisa Anderson",
    value: 6200000,
    probability: 70,
    stage: "qualified",
    expectedClose: "2026-04-30",
    industry: "Healthcare",
  },
  {
    id: "7",
    title: "FoodCraft Restaurants",
    company: "FoodCraft Restaurants",
    contact: "Robert Taylor",
    value: 1200000,
    probability: 30,
    stage: "new",
    expectedClose: "2026-07-15",
    industry: "Food & Beverage",
  },
];

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

function getProbabilityColor(probability: number) {
  if (probability >= 80) return "text-[#059669]";
  if (probability >= 50) return "text-[#D97706]";
  return "text-[#DC2626]";
}

function PipelineLoading() {
  return (
    <div className="flex gap-4 overflow-x-auto pb-4">
      {[...Array(5)].map((_, i) => (
        <div
          key={i}
          className="shrink-0 w-80 h-[calc(100vh-12rem)] bg-[#F0F0F0] animate-pulse rounded-lg"
        />
      ))}
    </div>
  );
}

function DealCard({
  deal,
  stageColor,
}: {
  deal: (typeof mockDeals)[0];
  stageColor: string;
}) {
  return (
    <Card className="border-[#E2E2E2] cursor-pointer hover:shadow-md transition-shadow duration-200 group">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div
            className="w-2 h-2 rounded-full mt-2"
            style={{ backgroundColor: stageColor }}
          />
          <DropdownMenu>
            <DropdownMenuTrigger>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <MoreHorizontal className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-40">
              <DropdownMenuItem>View Details</DropdownMenuItem>
              <DropdownMenuItem>Edit Deal</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>Move Left</DropdownMenuItem>
              <DropdownMenuItem>Move Right</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-[#DC2626]">Delete</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <h4 className="font-semibold text-[#1A1A1A] mb-1 line-clamp-2">
          {deal.title}
        </h4>

        <div className="flex items-center gap-2 text-sm text-[#6B6B6B] mb-3">
          <Building2 className="w-3.5 h-3.5" />
          {deal.company}
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-sm">
              <DollarSign className="w-3.5 h-3.5 text-[#8A8A8A]" />
              <span className="font-medium text-[#1A1A1A]">
                {formatCurrency(deal.value)}
              </span>
            </div>
            <span
              className={cn(
                "text-sm font-medium",
                getProbabilityColor(deal.probability)
              )}
            >
              {deal.probability}%
            </span>
          </div>

          <div className="flex items-center gap-1.5 text-xs text-[#8A8A8A]">
            <User className="w-3 h-3" />
            {deal.contact}
          </div>

          <div className="flex items-center gap-1.5 text-xs text-[#8A8A8A]">
            <Calendar className="w-3 h-3" />
            Close: {formatDate(deal.expectedClose)}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function PipelineColumn({
  stage,
  deals,
}: {
  stage: (typeof stages)[number];
  deals: typeof mockDeals;
}) {
  const columnDeals = deals.filter((deal) => deal.stage === stage.id);
  const totalValue = columnDeals.reduce((sum, deal) => sum + deal.value, 0);

  return (
    <div className="flex flex-col shrink-0 w-80">
      {/* Column Header */}
      <div className="flex items-center justify-between mb-3 px-1">
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: stage.color }}
          />
          <span className="font-semibold text-[#1A1A1A]">{stage.name}</span>
          <Badge
            variant="secondary"
            className="bg-[#F0F0F0] text-[#6B6B6B] font-medium"
          >
            {columnDeals.length}
          </Badge>
        </div>
        <span className="text-sm text-[#6B6B6B]">
          {formatCurrency(totalValue)}
        </span>
      </div>

      {/* Add Deal Button */}
      <Button
        variant="outline"
        className="mb-3 border-dashed border-[#E2E2E2] text-[#6B6B6B] hover:bg-[#F0F4FA] hover:text-[#3B5A9A] justify-start"
      >
        <Plus className="w-4 h-4 mr-2" />
        Add Deal
      </Button>

      {/* Deals List */}
      <div className="flex-1 space-y-3 overflow-y-auto min-h-[200px]">
        {columnDeals.map((deal) => (
          <DealCard key={deal.id} deal={deal} stageColor={stage.color} />
        ))}
      </div>
    </div>
  );
}

function PipelineContent() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStage, setFilterStage] = useState<string>("all");

  const filteredDeals = mockDeals.filter((deal) => {
    const matchesSearch =
      deal.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      deal.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
      deal.contact.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStage = filterStage === "all" || deal.stage === filterStage;
    return matchesSearch && matchesStage;
  });

  const totalPipelineValue = filteredDeals.reduce(
    (sum, deal) => sum + deal.value * (deal.probability / 100),
    0
  );

  return (
    <div className="space-y-6 h-full">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#1A1A1A]">
            Pipeline
          </h1>
          <p className="text-[#6B6B6B] mt-1">
            Track your acquisition deals through each stage
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <p className="text-sm text-[#6B6B6B]">Weighted Pipeline</p>
            <p className="text-2xl font-bold text-[#C9A227]">
              {formatCurrency(totalPipelineValue)}
            </p>
          </div>
          <Button className="bg-[#C9A227] hover:bg-[#A6851F] text-[#0A1628] font-semibold">
            <Plus className="w-4 h-4 mr-2" />
            New Deal
          </Button>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <Card className="border-[#E2E2E2]">
          <CardContent className="p-4">
            <p className="text-sm text-[#6B6B6B]">Total Deals</p>
            <p className="text-2xl font-bold text-[#1A1A1A]">
              {filteredDeals.length}
            </p>
          </CardContent>
        </Card>
        <Card className="border-[#E2E2E2]">
          <CardContent className="p-4">
            <p className="text-sm text-[#6B6B6B]">Total Value</p>
            <p className="text-2xl font-bold text-[#3B5A9A]">
              {formatCurrency(
                filteredDeals.reduce((sum, deal) => sum + deal.value, 0)
              )}
            </p>
          </CardContent>
        </Card>
        <Card className="border-[#E2E2E2]">
          <CardContent className="p-4">
            <p className="text-sm text-[#6B6B6B]">Avg Probability</p>
            <p className="text-2xl font-bold text-[#059669]">
              {Math.round(
                filteredDeals.length > 0
                  ? filteredDeals.reduce((sum, d) => sum + d.probability, 0) /
                      filteredDeals.length
                  : 0
              )}
              %
            </p>
          </CardContent>
        </Card>
        <Card className="border-[#E2E2E2]">
          <CardContent className="p-4">
            <p className="text-sm text-[#6B6B6B]">Closing This Month</p>
            <p className="text-2xl font-bold text-[#9333EA]">
              {
                filteredDeals.filter((d) => {
                  const closeDate = new Date(d.expectedClose);
                  const now = new Date();
                  return (
                    closeDate.getMonth() === now.getMonth() &&
                    closeDate.getFullYear() === now.getFullYear()
                  );
                }).length
              }
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8A8A8A]" />
          <Input
            placeholder="Search deals by name, company, or contact..."
            className="pl-10 border-[#E2E2E2] focus-visible:ring-[#3B5A9A]"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Select value={filterStage} onValueChange={(val) => setFilterStage(val || "all")}>
          <SelectTrigger className="w-full sm:w-[180px] border-[#E2E2E2]">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue placeholder="Filter by stage" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Stages</SelectItem>
            {stages.map((stage) => (
              <SelectItem key={stage.id} value={stage.id}>
                {stage.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Kanban Board */}
      <div className="overflow-x-auto pb-4">
        <div className="flex gap-6 min-w-max">
          {stages.map((stage) => (
            <PipelineColumn
              key={stage.id}
              stage={stage}
              deals={filteredDeals}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default function PipelinePage() {
  return (
    <Suspense fallback={<PipelineLoading />}>
      <PipelineContent />
    </Suspense>
  );
}
