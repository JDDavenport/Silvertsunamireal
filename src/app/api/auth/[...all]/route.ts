import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  console.log("[Auth] GET hit");
  return NextResponse.json({ message: "Auth GET works" });
}

export async function POST(req: NextRequest) {
  console.log("[Auth] POST hit");
  try {
    const body = await req.json();
    console.log("[Auth] POST body:", body);
    return NextResponse.json({ message: "Auth POST works", received: body });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 400 });
  }
}