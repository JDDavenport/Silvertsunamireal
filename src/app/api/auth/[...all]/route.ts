import { NextRequest, NextResponse } from "next/server";

let initError: any = null;
let db: any = null;

// Try to initialize auth module
try {
  console.log("[Auth] Loading auth module...");
  const authModule = require("@/lib/auth");
  console.log("[Auth] Auth module loaded");
} catch (e: any) {
  initError = e;
  console.error("[Auth] Failed to load auth module:", e.message);
}

// Try to initialize db
try {
  console.log("[Auth] Loading db module...");
  const dbModule = require("@/lib/db");
  db = dbModule.db;
  console.log("[Auth] DB module loaded");
} catch (e: any) {
  if (!initError) initError = e;
  console.error("[Auth] Failed to load db module:", e.message);
}

export async function GET(req: NextRequest) {
  if (initError) {
    return NextResponse.json({ 
      error: "Module initialization failed", 
      message: initError?.message || String(initError),
      stack: initError?.stack?.split('\n').slice(0, 5)
    }, { status: 500 });
  }
  
  return NextResponse.json({ message: "Auth endpoint ready" });
}

export async function POST(req: NextRequest) {
  if (initError) {
    return NextResponse.json({ 
      error: "Module initialization failed", 
      message: initError?.message || String(initError),
      stack: initError?.stack?.split('\n').slice(0, 5)
    }, { status: 500 });
  }
  
  return NextResponse.json({ message: "Auth POST ready" });
}