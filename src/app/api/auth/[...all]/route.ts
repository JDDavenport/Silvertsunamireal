import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";

export async function GET(req: NextRequest) {
  console.log("[Auth] GET received");
  try {
    const response = await auth.handler(req);
    console.log("[Auth] GET handler success");
    return response;
  } catch (error: any) {
    console.error("[Auth] GET error:", error.message);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  console.log("[Auth] POST received");
  try {
    const response = await auth.handler(req);
    console.log("[Auth] POST handler success");
    return response;
  } catch (error: any) {
    console.error("[Auth] POST error:", error.message);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}