"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  Kanban,
  Settings,
  Menu,
  X,
  LogOut,
  Building2,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { authClient } from "@/lib/auth-client";

interface DashboardLayoutProps {
  children: React.ReactNode;
  user: {
    name?: string | null;
    email?: string | null;
  };
}

const navItems = [
  {
    name: "Overview",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Leads",
    href: "/dashboard/leads",
    icon: Users,
  },
  {
    name: "Pipeline",
    href: "/dashboard/pipeline",
    icon: Kanban,
  },
  {
    name: "Settings",
    href: "/dashboard/settings",
    icon: Settings,
  },
];

export function DashboardSidebar({ className }: { className?: string }) {
  const pathname = usePathname();

  return (
    <div
      className={cn(
        "flex flex-col h-full bg-[#0A1628] w-64 border-r border-[#1E3160]",
        className
      )}
    >
      {/* Logo */}
      <div className="p-6 border-b border-[#1E3160]">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#C9A227] to-[#D4B43D] flex items-center justify-center">
            <Building2 className="w-5 h-5 text-[#0A1628]" />
          </div>
          <span className="text-xl font-bold text-white tracking-tight">
            ACQUISITOR
          </span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-[#C9A227] text-[#0A1628]"
                  : "text-[#BCCCE6] hover:bg-[#162544] hover:text-white"
              )}
            >
              <item.icon className={cn("w-5 h-5", isActive && "text-[#0A1628]")} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-[#1E3160]">
        <button
          onClick={async () => {
            await authClient.signOut();
            window.location.href = "/login";
          }}
          className="flex items-center gap-3 px-4 py-3 w-full rounded-lg text-sm font-medium text-[#BCCCE6] hover:bg-[#162544] hover:text-white transition-all duration-200"
        >
          <LogOut className="w-5 h-5" />
          Sign Out
        </button>
      </div>
    </div>
  );
}

export function MobileSidebar() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger>
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden text-[#1A1A1A] hover:bg-[#F0F0F0]"
        >
          <Menu className="w-5 h-5" />
          <span className="sr-only">Toggle menu</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="p-0 w-64 bg-[#0A1628] border-r border-[#1E3160]">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-6 border-b border-[#1E3160]">
            <Link
              href="/dashboard"
              className="flex items-center gap-3"
              onClick={() => setOpen(false)}
            >
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#C9A227] to-[#D4B43D] flex items-center justify-center">
                <Building2 className="w-5 h-5 text-[#0A1628]" />
              </div>
              <span className="text-xl font-bold text-white tracking-tight">
                ACQUISITOR
              </span>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setOpen(false)}
                  className={cn(
                    "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200",
                    isActive
                      ? "bg-[#C9A227] text-[#0A1628]"
                      : "text-[#BCCCE6] hover:bg-[#162544] hover:text-white"
                  )}
                >
                  <item.icon
                    className={cn("w-5 h-5", isActive && "text-[#0A1628]")}
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-[#1E3160]">
            <button
              onClick={async () => {
                await authClient.signOut();
                window.location.href = "/login";
              }}
              className="flex items-center gap-3 px-4 py-3 w-full rounded-lg text-sm font-medium text-[#BCCCE6] hover:bg-[#162544] hover:text-white transition-all duration-200"
            >
              <LogOut className="w-5 h-5" />
              Sign Out
            </button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}

export function DashboardHeader({ user }: { user: { name?: string | null; email?: string | null } }) {
  const displayName = user.name || user.email || "User";
  const initials = displayName
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <header className="h-16 bg-white border-b border-[#E2E2E2] px-4 sm:px-6 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-4">
        <MobileSidebar />
        <h1 className="text-lg font-semibold text-[#1A1A1A] hidden sm:block">
          Dashboard
        </h1>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#3B5A9A] to-[#5B7BB8] flex items-center justify-center text-white font-medium text-sm">
            {initials}
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-medium text-[#1A1A1A]">{displayName}</p>
            <p className="text-xs text-[#6B6B6B]">Business Buyer</p>
          </div>
        </div>
      </div>
    </header>
  );
}

export default function DashboardLayout({ children, user }: DashboardLayoutProps) {
  return (
    <div className="flex h-screen bg-[#F5F5F3]">
      {/* Desktop Sidebar */}
      <aside className="hidden md:block">
        <DashboardSidebar />
      </aside>

      {/* Main Content */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <DashboardHeader user={user} />
        <main className="flex-1 overflow-auto p-4 sm:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">{children}</div>
        </main>
      </div>
    </div>
  );
}
