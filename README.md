# ACQUISITOR

Intelligent acquisition analysis platform for discovering, evaluating, and tracking acquisition targets.

## Architecture

```
acquisitor/
├── api/                    # Hono TypeScript backend
├── web/                    # React + Vite frontend
├── agents/                 # OpenClaw agent configurations
├── scrapers/               # Python data acquisition scripts
└── docker-compose.yml      # Infrastructure orchestration
```

## Quick Start

```bash
# Clone and enter directory
cd ~/projects/silver-tsunami-real

# Start infrastructure
docker-compose up -d postgres redis

# Install dependencies
npm install

# Start development servers
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- API: http://localhost:3001
- API Health: http://localhost:3001/health

## Services

| Service | Port | Description |
|---------|------|-------------|
| Web | 5173 | React + Vite + Tailwind |
| API | 3001 | Hono + TypeScript |
| PostgreSQL | 5432 | Database with pgvector |
| Redis | 6379 | Cache & session store |

## Development

```bash
# Run API only
npm run dev:api

# Run Web only
npm run dev:web

# Type check
npm run typecheck

# Build for production
npm run build
```

## Project Structure

### `/api` - Backend API
- Hono framework with CORS
- PostgreSQL connection via `pg`
- Redis connection via `ioredis`
- Health endpoint at `GET /health`

### `/web` - Frontend
- React 18 + TypeScript
- React Router for navigation
- Tailwind CSS styling
- EXPLORE / DASHBOARD views

### `/agents` - OpenClaw Configuration
- `SOUL.md` - System identity and values
- `AGENTS.md` - Agent registry

### `/scrapers` - Data Acquisition
- Python-based scrapers
- Base scraper class with rate limiting
- Example company scraper implementation

## Environment Variables

```env
NODE_ENV=development
PORT=3001
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/acquisitor
REDIS_URL=redis://localhost:6379
```

## License

MIT
