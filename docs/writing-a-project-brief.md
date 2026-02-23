# Writing a Good Project Brief

A well-structured `project_brief.md` helps Skill Autopilot select the right pods, kernels, and skills for your project. Here's how to write one that gets the best results.

## Minimum Structure

Your brief needs three sections with headers:

```markdown
# Goals
- What you want to build or achieve.
- Be specific about outcomes, not just activities.

# Constraints
- Technical, budget, or timeline limits.
- Compliance or regulatory requirements.

# Deliverables
- Concrete outputs: files, services, reports, deployments.
```

## What Makes a Brief *Good*

### Be specific about your domain
The system auto-detects your industry from 41 supported industries and selects kernels and pods accordingly. Mention your domain explicitly (see `docs/pod-system.md` for the full industry list):

> ❌ "Build an app"
> ✅ "Build a patient intake portal for a dental clinic"

### State the project type
Different project types activate different B-kernels:

> ❌ "Make improvements"
> ✅ "Build and ship a SaaS analytics dashboard" → activates Digital Product kernel
> ✅ "Train a custom NER model for legal documents" → activates ML/AI Systems kernel

### Include constraints that matter
Constraints drive pod selection. The system looks for signals like:

| You write... | System activates... |
|-|-|
| "SOC2 compliance required" | Legal/Risk pod |
| "Budget under $5k/month" | Finance & Governance pod |
| "Team of 3 engineers" | People & Talent pod |
| "Must integrate with SAP" | Ops & Supply pod |
| "GDPR data residency" | Legal/Risk + Data & Insight pods |

### Be explicit about deliverables
Vague deliverables produce vague tasks. Compare:

> ❌ "Working system"
> ✅ "REST API with OpenAPI spec, PostgreSQL schema, Docker compose file, and CI pipeline"

## Optional Sections (Recommended)

```markdown
# Risk
- What could go wrong and how critical it is.
- Data sensitivity level (public, internal, confidential).

# Evidence
- Links to existing docs, repos, APIs, or designs.
- Reference implementations or prior art.
```

## Example Brief

```markdown
# Goals
- Build a real-time inventory tracking system for a chain of 12 retail stores.
- Provide store managers with a mobile-friendly dashboard showing stock levels.
- Alert purchasing team when items drop below reorder threshold.

# Constraints
- Must integrate with existing Square POS system via their API.
- Budget: $3k/month cloud infrastructure max.
- Timeline: MVP in 6 weeks, full rollout in 12 weeks.
- Team: 2 backend engineers, 1 frontend engineer.
- PCI-DSS compliance for any payment-adjacent data.

# Deliverables
- REST API (Node.js/Express) with WebSocket for real-time updates.
- React Native mobile app for store managers.
- Admin dashboard (Next.js) for purchasing team.
- PostgreSQL database with migration scripts.
- Terraform IaC for AWS deployment.
- Integration test suite with >80% coverage.

# Risk
- Square API rate limits may require local caching strategy.
- Multi-store sync latency could cause phantom stock alerts.
- PCI scope must be minimized — no card data storage.
```

This brief would activate:
- **B-Digital Product** kernel (software build & ship)
- **Commercial** pod (retail/POS integration)
- **Finance & Governance** pod (budget constraint + PCI)
- **Ops & Supply** pod (inventory/supply chain)

## Using Claude Desktop / Cowork to Write Your Brief

You can ask Claude to help you draft the brief interactively:

1. **Start a conversation** in Claude Desktop and describe your project informally.
2. **Ask Claude to structure it** as a `project_brief.md` with Goals, Constraints, and Deliverables.
3. **Iterate** — Claude will ask clarifying questions about scope, team, timeline, and tech stack.
4. **Save** the file as `project_brief.md` in your project workspace root.
5. **Run** `sa_start_project` with your `workspace_path` to kick off the plan.

> **Tip:** You don't need to get the brief perfect on the first try. If you update it later, call `sa_reroute_project` and the system will re-select pods and regenerate the plan based on your changes.
