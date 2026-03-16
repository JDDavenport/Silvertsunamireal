import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "./schema";

const connectionString = process.env.DATABASE_URL!;

console.log("[DB] Configuring postgres client...");

const client = postgres(connectionString, {
  prepare: false,
  ssl: false,
  max: 10,
  connect_timeout: 30,
});

console.log("[DB] Postgres client created");

export const db = drizzle(client, { schema });

console.log("[DB] Drizzle initialized");