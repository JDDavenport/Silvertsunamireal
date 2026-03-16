import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "./schema";

const connectionString = process.env.DATABASE_URL!;

// Check if we're in production (Vercel)
const isProduction = process.env.VERCEL_ENV === 'production';

const client = postgres(connectionString, {
  prepare: false,
  ssl: isProduction ? { rejectUnauthorized: false } : undefined,
});
export const db = drizzle(client, { schema });
