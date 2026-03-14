---
# ACQUISITOR Agents Registry

This directory contains agent configurations and runtime specifications for the
ACQUISITOR platform.

## Agent Definitions

### builder
**Role:** Lead Engineer
**Responsibilities:**
- API development and maintenance
- Frontend implementation
- Database schema design
- Infrastructure as code
- Code review and quality

**Configuration:**
```yaml
agent:
  name: builder
  workspace: /api, /web
  tools: [read, write, edit, exec]
  models: [anthropic/claude-opus-4, kimi-coding/kimi-for-coding]
```

### researcher
**Role:** Data Analyst
**Responsibilities:**
- Market research
- Company data aggregation
- Financial analysis
- Competitor analysis
- Source verification

**Configuration:**
```yaml
agent:
  name: researcher
  workspace: /scrapers, /data
  tools: [read, exec, browser]
  models: [perplexity/sonar, openai/gpt-4o]
```

### captain
**Role:** System Coordinator
**Responsibilities:**
- Task routing
- Priority management
- Conflict resolution
- User communication
- System monitoring

**Configuration:**
```yaml
agent:
  name: captain
  workspace: /
  tools: [read, exec, subagents]
  models: [anthropic/claude-opus-4]
```

## Agent Communication Protocol

```json
{
  "message_id": "uuid",
  "from": "agent_name",
  "to": "agent_name|broadcast",
  "timestamp": "ISO8601",
  "type": "task|response|alert|query",
  "payload": {},
  "priority": "low|normal|high|critical",
  "context": {}
}
```

## Adding New Agents

1. Create agent directory under `/agents/{name}/`
2. Add `SOUL.md` defining persona and capabilities
3. Add entry to this registry
4. Configure tools and permissions in gateway
