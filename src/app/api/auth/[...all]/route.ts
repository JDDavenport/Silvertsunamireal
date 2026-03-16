import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

const handlers = toNextJsHandler(auth);

export async function GET(req: NextRequest) {
  // Health check
  if (req.url.includes('/health')) {
    let dbStatus = 'unknown';
    let dbError = '';
    let dbStack = '';
    
    try {
      const { db } = await import("@/lib/db");
      // Try a raw query
      const result = await db.query.user.findFirst();
      dbStatus = 'connected';
    } catch (e: any) {
      dbStatus = 'error';
      dbError = e.message;
      dbStack = e.stack;
    }
    
    return NextResponse.json({ 
      status: 'ok',
      env: process.env.VERCEL_ENV,
      dbConnection: dbStatus,
      dbError,
      dbStack: dbStack?.split('\n').slice(0, 3)
    });
  }
  return handlers.GET(req);
}

export async function POST(req: NextRequest) {
  return handlers.POST(req);
}