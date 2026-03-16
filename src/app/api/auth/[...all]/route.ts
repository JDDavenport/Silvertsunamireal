import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

const handlers = toNextJsHandler(auth);

export async function GET(req: NextRequest) {
  // Health check
  if (req.url.includes('/health')) {
    return NextResponse.json({ 
      status: 'ok',
      database: !!process.env.DATABASE_URL,
      secret: !!process.env.BETTER_AUTH_SECRET,
      baseUrl: process.env.NEXT_PUBLIC_APP_URL
    });
  }
  return handlers.GET(req);
}

export async function POST(req: NextRequest) {
  return handlers.POST(req);
}