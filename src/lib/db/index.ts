import { createClient } from "@supabase/supabase-js";
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "./schema";

const connectionString = process.env.DATABASE_URL!;

// For Vercel serverless, we need special SSL handling
const isVercel = process.env.VERCEL === '1';

console.log("[DB] Connecting... isVercel:", isVercel);

const client = postgres(connectionString, {
  prepare: false,
  ssl: isVercel ? { rejectUnauthorized: false } : undefined,
  connect_timeout: 10,
  idle_timeout: 20,
});

console.log("[DB] Client created");

export const db = drizzle(client, { schema });

console.log("[DB] Drizzle ready");