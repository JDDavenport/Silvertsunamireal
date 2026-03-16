import { NextRequest, NextResponse } from "next/server";

console.log("[Auth Route] Module loading...");
console.log("[Auth Route] DATABASE_URL exists:", !!process.env.DATABASE_URL);
console.log("[Auth Route] NEXT_PUBLIC_APP_URL:", process.env.NEXT_PUBLIC_APP_URL);

try {
  const { auth } = await import("@/lib/auth");
  console.log("[Auth Route] Auth imported successfully");
  console.log("[Auth Route] Auth handler exists:", !!auth.handler);
  
  export async function GET(req: NextRequest) {
    console.log("[Auth Route] GET request received");
    try {
      const response = await auth.handler(req);
      console.log("[Auth Route] GET handler succeeded");
      return response;
    } catch (error: any) {
      console.error("[Auth Route] GET error:", error);
      return NextResponse.json({ 
        error: "Auth GET error", 
        message: error.message,
        stack: error.stack 
      }, { status: 500 });
    }
  }

  export async function POST(req: NextRequest) {
    console.log("[Auth Route] POST request received");
    try {
      const response = await auth.handler(req);
      console.log("[Auth Route] POST handler succeeded");
      return response;
    } catch (error: any) {
      console.error("[Auth Route] POST error:", error);
      return NextResponse.json({ 
        error: "Auth POST error", 
        message: error.message,
        stack: error.stack 
      }, { status: 500 });
    }
  }
} catch (importError: any) {
  console.error("[Auth Route] Failed to import auth:", importError);
  
  const errorResponse = () => NextResponse.json({
    error: "Auth initialization failed",
    message: importError.message,
    stack: importError.stack
  }, { status: 500 });
  
  export const GET = errorResponse;
  export const POST = errorResponse;
}