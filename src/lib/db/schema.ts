import { pgTable, serial, varchar, text, timestamp, integer, boolean, decimal, pgEnum } from "drizzle-orm/pg-core";

export const userRoleEnum = pgEnum('user_role', ['admin', 'user']);
export const leadStatusEnum = pgEnum('lead_status', ['new', 'contacted', 'evaluating', 'offer', 'diligence', 'closed', 'archived']);
export const dealStageEnum = pgEnum('deal_stage', ['sourcing', 'screening', 'loi', 'diligence', 'closing', 'won', 'lost']);
export const activityTypeEnum = pgEnum('activity_type', ['email', 'call', 'meeting', 'note', 'task', 'document']);

// Better Auth Tables
export const user = pgTable("user", {
  id: varchar("id", { length: 36 }).primaryKey(),
  name: text("name").notNull(),
  email: varchar("email", { length: 255 }).notNull().unique(),
  emailVerified: boolean("email_verified").default(false).notNull(),
  image: text("image"),
  role: userRoleEnum("role").default('user').notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const session = pgTable("session", {
  id: varchar("id", { length: 36 }).primaryKey(),
  userId: varchar("user_id", { length: 36 }).notNull().references(() => user.id, { onDelete: "cascade" }),
  token: varchar("token", { length: 255 }).notNull().unique(),
  expiresAt: timestamp("expires_at").notNull(),
  ipAddress: text("ip_address"),
  userAgent: text("user_agent"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const account = pgTable("account", {
  id: varchar("id", { length: 36 }).primaryKey(),
  userId: varchar("user_id", { length: 36 }).notNull().references(() => user.id, { onDelete: "cascade" }),
  accountId: text("account_id").notNull(),
  providerId: text("provider_id").notNull(),
  accessToken: text("access_token"),
  refreshToken: text("refresh_token"),
  accessTokenExpiresAt: timestamp("access_token_expires_at"),
  refreshTokenExpiresAt: timestamp("refresh_token_expires_at"),
  scope: text("scope"),
  idToken: text("id_token"),
  password: text("password"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const verification = pgTable("verification", {
  id: varchar("id", { length: 36 }).primaryKey(),
  identifier: text("identifier").notNull(),
  value: text("value").notNull(),
  expiresAt: timestamp("expires_at").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

// Legacy users table - keeping for backwards compatibility
export const users = pgTable("users", {
  id: varchar("id", { length: 255 }).primaryKey(),
  email: varchar("email", { length: 255 }).notNull().unique(),
  name: varchar("name", { length: 255 }).notNull(),
  avatar: text("avatar"),
  role: userRoleEnum("role").default('user').notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const leads = pgTable("leads", {
  id: varchar("id", { length: 255 }).primaryKey(),
  title: varchar("title", { length: 255 }).notNull(),
  description: text("description"),
  askingPrice: decimal("asking_price", { precision: 15, scale: 2 }).default('0'),
  revenue: decimal("revenue", { precision: 15, scale: 2 }).default('0'),
  profit: decimal("profit", { precision: 15, scale: 2 }).default('0'),
  industry: varchar("industry", { length: 100 }),
  location: varchar("location", { length: 255 }),
  source: varchar("source", { length: 100 }),
  status: leadStatusEnum("status").default('new').notNull(),
  score: integer("score").default(0),
  owner: varchar("owner", { length: 255 }),
  employees: integer("employees").default(0),
  yearFounded: integer("year_founded"),
  website: varchar("website", { length: 255 }),
  contactName: varchar("contact_name", { length: 255 }),
  contactEmail: varchar("contact_email", { length: 255 }),
  contactPhone: varchar("contact_phone", { length: 50 }),
  userId: varchar("user_id", { length: 36 }).references(() => user.id),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const deals = pgTable("deals", {
  id: varchar("id", { length: 255 }).primaryKey(),
  leadId: varchar("lead_id", { length: 255 }).references(() => leads.id),
  title: varchar("title", { length: 255 }).notNull(),
  value: decimal("value", { precision: 15, scale: 2 }).default('0'),
  stage: dealStageEnum("stage").default('sourcing').notNull(),
  probability: integer("probability").default(0),
  expectedCloseDate: timestamp("expected_close_date"),
  assignedTo: varchar("assigned_to", { length: 36 }).references(() => user.id),
  notes: text("notes"),
  userId: varchar("user_id", { length: 36 }).references(() => user.id),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const activities = pgTable("activities", {
  id: varchar("id", { length: 255 }).primaryKey(),
  type: activityTypeEnum("type").notNull(),
  title: varchar("title", { length: 255 }).notNull(),
  description: text("description"),
  leadId: varchar("lead_id", { length: 255 }).references(() => leads.id),
  dealId: varchar("deal_id", { length: 255 }).references(() => deals.id),
  userId: varchar("user_id", { length: 36 }).references(() => user.id).notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const emailTemplates = pgTable("email_templates", {
  id: varchar("id", { length: 255 }).primaryKey(),
  name: varchar("name", { length: 255 }).notNull(),
  subject: varchar("subject", { length: 500 }).notNull(),
  body: text("body").notNull(),
  category: varchar("category", { length: 50 }),
  userId: varchar("user_id", { length: 36 }).references(() => user.id),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});
