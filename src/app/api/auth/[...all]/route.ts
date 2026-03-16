import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";
import { sql } from "drizzle-orm";

const handlers = toNextJsHandler(auth);

export async function GET(req: NextRequest) {
  // Health check
  if (req.url.includes('/health')) {
    // Test database connection
    let dbStatus = 'unknown';
    let dbError = '';
    try {
      // Dynamic import to test
      const { db } = await import("@/lib/db");
      console.log("[Health] DB module loaded");
      
      // Try a simple query
      const result = await db.execute(sql`SELECT 1 as test`);
      console.log("[Health] Query result:", result);
      dbStatus = 'connected';
    } catch (e: any) {
      dbStatus = 'error';
      dbError = e.message;
      console.error("[Health] DB error:", e);
    }
    
    return NextResponse.json({ 
      status: 'ok',
      database: !!process.env.DATABASE_URL,
      dbConnection: dbStatus,
      dbError,
      secret: !!process.env.BETTER_AUTH_SECRET,
      baseUrl: process.env.NEXT_PUBLIC_APP_URL
    });
  }
  return handlers.GET(req);
}

export async function POST(req: NextRequest) {
  return handlers.POST(req);
}