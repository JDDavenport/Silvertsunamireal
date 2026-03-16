import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

const handler = toNextJsHandler(auth);

export async function GET(req: Request) {
  try {
    return await handler.GET(req);
  } catch (error) {
    console.error("Auth GET error:", error);
    return new Response(JSON.stringify({ error: "Auth error", details: String(error) }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}

export async function POST(req: Request) {
  try {
    return await handler.POST(req);
  } catch (error) {
    console.error("Auth POST error:", error);
    return new Response(JSON.stringify({ error: "Auth error", details: String(error) }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}
