import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { Suspense } from "react";
import DashboardLayout from "./layout-client";
import {
  LayoutDashboard,
  Users,
  Kanban,
  Settings,
  TrendingUp,
  Mail,
  CheckCircle,
  ArrowUpRight,
  ArrowDownRight,
  Plus,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";

// Loading component
function StatsLoading() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
      {[...Array(4)].map((_, i) => (
        <Card key={i} className="border-[#E2E2E2]">
          <CardContent className="p-6">
            <div className="h-10 w-10 rounded-lg bg-[#F0F0F0] animate-pulse mb-4" />
            <div className="h-8 w-24 bg-[#F0F0F0] animate-pulse mb-2" />
            <div className="h-4 w-16 bg-[#F0F0F0] animate-pulse" />
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

// Stats data (mock data for now)
async function getStats() {
  // TODO: Replace with actual data fetching
  return {
    leadsDiscovered: 24,
    leadsChange: { value: 12, direction: "up" as const },
    emailsSent: 18,
    emailsChange: { value: 8, direction: "up" as const },
    dealsClosed: 2,
    dealsChange: { value: 0, direction: "neutral" as const },
    pipelineValue: "$1.2M",
    pipelineChange: { value: 15, direction: "up" as const },
  };
}

function StatCard({
  title,
  value,
  change,
  icon: Icon,
  description,
}: {
  title: string;
  value: string | number;
  change?: { value: number; direction: "up" | "down" | "neutral" };
  icon: React.ElementType;
  description?: string;
}) {
  return (
    <Card className="border-[#E2E2E2] hover:shadow-md transition-shadow duration-200">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="p-2 rounded-lg bg-[#F0F4FA]">
            <Icon className="w-5 h-5 text-[#3B5A9A]" />
          </div>
          {change && change.direction !== "neutral" && (
            <div
              className={cn(
                "flex items-center gap-1 text-xs font-medium",
                change.direction === "up"
                  ? "text-[#059669]"
                  : "text-[#DC2626]"
              )}
            >
              {change.direction === "up" ? (
                <ArrowUpRight className="w-3 h-3" />
              ) : (
                <ArrowDownRight className="w-3 h-3" />
              )}
              {change.value}%
            </div>
          )}
        </div>
        <div className="mt-4">
          <p className="text-2xl font-bold text-[#1A1A1A] font-data">{value}</p>
          <p className="text-sm text-[#6B6B6B] mt-1">{title}</p>
          {description && (
            <p className="text-xs text-[#8A8A8A] mt-1">{description}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function cn(...classes: (string | undefined | false)[]) {
  return classes.filter(Boolean).join(" ");
}

// Empty state for recent activity
function EmptyActivity() {
  return (
    <Card className="border-[#E2E2E2]">
      <CardContent className="p-8 text-center">
        <div className="w-16 h-16 rounded-full bg-[#F0F4FA] flex items-center justify-center mx-auto mb-4">
          <TrendingUp className="w-8 h-8 text-[#3B5A9A]" />
        </div>
        <h3 className="text-lg font-semibold text-[#1A1A1A] mb-2">
          No recent activity
        </h3>
        <p className="text-sm text-[#6B6B6B] max-w-sm mx-auto mb-4">
          Start by discovering leads or reaching out to potential acquisitions.
          Your recent activity will appear here.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <Link href="/dashboard/leads">
            <Button className="bg-[#C9A227] hover:bg-[#A6851F] text-[#0A1628] font-semibold">
              <Plus className="w-4 h-4 mr-2" />
              Add Lead
            </Button>
          </Link>
          <Link href="/dashboard/pipeline">
            <Button variant="outline" className="border-[#E2E2E2] text-[#4A4A4A]">
              View Pipeline
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}

async function StatsContent() {
  const stats = await getStats();

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
      <StatCard
        title="Leads Discovered"
        value={stats.leadsDiscovered}
        change={stats.leadsChange}
        icon={Users}
        description="This month"
      />
      <StatCard
        title="Emails Sent"
        value={stats.emailsSent}
        change={stats.emailsChange}
        icon={Mail}
        description="Outreach campaigns"
      />
      <StatCard
        title="Deals Closed"
        value={stats.dealsClosed}
        change={stats.dealsChange}
        icon={CheckCircle}
        description="Acquisitions completed"
      />
      <StatCard
        title="Pipeline Value"
        value={stats.pipelineValue}
        change={stats.pipelineChange}
        icon={TrendingUp}
        description="Total deal value"
      />
    </div>
  );
}

async function DashboardContent({ user }: { user: { name?: string | null; email?: string | null } }) {
  const displayName = user.name?.split(" ")[0] || "there";

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-[#1A1A1A]">
          Welcome back, {displayName}!
        </h1>
        <p className="text-[#6B6B6B] mt-1">
          Here&apos;s what&apos;s happening with your acquisitions today.
        </p>
      </div>

      {/* Stats */}
      <Suspense fallback={<StatsLoading />}>
        <StatsContent />
      </Suspense>

      {/* Quick Actions & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <Card className="border-[#E2E2E2] lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-[#1A1A1A]">
              Quick Actions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link href="/dashboard/leads">
              <Button
                variant="outline"
                className="w-full justify-start border-[#E2E2E2] text-[#4A4A4A] hover:bg-[#F0F4FA] hover:text-[#3B5A9A]"
              >
                <Users className="w-4 h-4 mr-3 text-[#3B5A9A]" />
                Add New Lead
              </Button>
            </Link>
            <Link href="/dashboard/pipeline">
              <Button
                variant="outline"
                className="w-full justify-start border-[#E2E2E2] text-[#4A4A4A] hover:bg-[#F0F4FA] hover:text-[#3B5A9A]"
              >
                <Kanban className="w-4 h-4 mr-3 text-[#3B5A9A]" />
                Update Pipeline
              </Button>
            </Link>
            <Link href="/dashboard/settings">
              <Button
                variant="outline"
                className="w-full justify-start border-[#E2E2E2] text-[#4A4A4A] hover:bg-[#F0F4FA] hover:text-[#3B5A9A]"
              >
                <Settings className="w-4 h-4 mr-3 text-[#3B5A9A]" />
                Configure Settings
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <div className="lg:col-span-2">
          <h2 className="text-lg font-semibold text-[#1A1A1A] mb-4">
            Recent Activity
          </h2>
          <EmptyActivity />
        </div>
      </div>
    </div>
  );
}

export default async function DashboardPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    redirect("/login");
  }

  return (
    <DashboardLayout user={session.user}>
      <DashboardContent user={session.user} />
    </DashboardLayout>
  );
}
