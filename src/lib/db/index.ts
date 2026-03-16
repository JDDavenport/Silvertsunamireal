import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "./schema";

const connectionString = process.env.DATABASE_URL!;

// Check if we're in production (Vercel)
const isProduction = process.env.VERCEL_ENV === 'production';

console.log("[DB] Connecting to database...");
console.log("[DB] isProduction:", isProduction);
console.log("[DB] Connection string starts with:", connectionString?.substring(0, 30));

const client = postgres(connectionString, {
  prepare: false,
  ssl: isProduction ? { rejectUnauthorized: false } : undefined,
  onnotice: (notice) => console.log("[DB Notice]", notice),
  onparameter: (key, value) => console.log("[DB Parameter]", key, value),
});

console.log("[DB] Client created");

export const db = drizzle(client, { schema });

console.log("[DB] Drizzle instance created");
