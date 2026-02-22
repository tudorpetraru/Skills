# Project-Based Agent Library Framework
*Edited conversation notes — distilled spec: roles → skills → pods → industry packs → real-world connectors.*

**Version:** 0.1  
**Date:** 22 February 2026  

## Key takeaways
- Stop thinking in job titles. Model work as reusable **skills** and attach them to **projects**.
- **Pods** are bundles of agents for a capability area; **B (Build & Ship)** becomes a family of kernels + industry packs.
- Real-world automation adds a **Reality Layer (R pods)**, **autonomy tiers**, **action contracts**, **safety envelopes**, and **audit-grade evidence**.
- **Lab automation** is a canonical example: evidence-first delivery + policy-enforcing executor + LIMS/ELN integration.

## Contents
1. [Premise: Work is project-based](#1-premise-work-is-project-based)  
2. [Roles as modes: why aggregation beats titles](#2-roles-as-modes-why-aggregation-beats-titles)  
3. [Agent library architecture: Core + Pods](#3-agent-library-architecture-core--pods)  
4. [B-kernel families (Build & Ship kernels)](#4-b-kernel-families-build--ship-kernels)  
5. [Industry mapping (40 industries → default kernels)](#5-industry-mapping-40-industries--default-kernels)  
6. [Reality layer for cyber-physical work (R pods)](#6-reality-layer-for-cyber-physical-work-r-pods)  
7. [Lab automation example pack](#7-lab-automation-example-pack)  
8. [Template schema: how to store and reuse pods/agents/skills](#8-template-schema-how-to-store-and-reuse-podsagentsskills)  

---

## 1. Premise: Work is project-based
The guiding assumption is that the future of work is not centered on permanent companies and fixed titles, but on **projects** that assemble capabilities on demand. In this paradigm, the useful unit is not a job title; it is a **library of skills and pods** that can be attached to a project as needed.

A good agent library behaves like a **dependency resolver**: given a project type, risk level, and required outputs, it selects the right pods (bundles of agents) and enforces quality and safety gates.

## 2. Roles as modes: why aggregation beats titles
We intentionally collapse traditional titles (e.g., Program Manager vs Project Manager, Product Manager vs Business Analyst) because titles are mostly organizational UI. What matters for skill generation is the **shape of work**:

- **Objective function:** outcomes vs delivery vs correctness vs risk reduction  
- **Scope graph:** single workstream vs multi-workstream dependency network  
- **Uncertainty:** discovery/strategy vs specification/traceability  
- **Evidence:** what proof is required to call something “done”

**Practical rule:** merge titles when the same rubric can judge outputs; split into modes when objectives or evidence change.

## 3. Agent library architecture: Core + Pods
Each project gets a small **Core** (always-on) and then attaches additional pods based on what the project must deliver. Pods are capability bundles; each contains agent templates and skill verbs.

### 3.1 Core (always-on)
- **Orchestrator / Chief of Staff** — decomposes scope, assigns owners, runs cadence, manages decisions/RAID, maintains the single source of truth.
- **Scribe / Documentation Steward** — turns meetings/threads into decisions and action items; maintains docs and changelog; publishes weekly updates.
- **Research & Intel** — gathers sources, compares options, produces briefings; maintains a facts vs assumptions ledger.
- **Quality / Red-Team** — critiques outputs, finds gaps, stress-tests plans, runs checklists, surfaces risks and contradictions.
- **Delivery Tracker** — milestone planning, dependency mapping, status dashboards, escalation triggers, postmortems.

### 3.2 Pods (attached per project)
Pods are “plug-ins”. A project might attach **Discovery & Definition**, **Commercial**, **Finance & Governance**, **Legal/Risk/Compliance**, **People & Talent**, **Ops & Supply**, and one or more **Build & Ship kernels**.

## 4. B-kernel families (Build & Ship kernels)
Pod **B (Build & Ship)** must become a family. Rather than creating a unique pod for every industry, define a **stable pod interface** and swap the domain kernel via **industry packs** (standards, artifacts, toolchains, evidence).

- **B-Digital Product** (apps, SaaS, platforms)
- **B-Data & Analytics** (pipelines, BI, metrics systems)
- **B-ML/AI Systems** (model lifecycle, evaluation, monitoring)
- **B-Cyber & SecOps** (detections, incident response, hardening)
- **B-Embedded & Mechatronics** (firmware, sensors, controls)
- **B-Safety-Critical Engineering** (formal V&V, safety cases)
- **B-Industrial Manufacturing** (process engineering, industrialization)
- **B-Chem/Materials Process** (formulations, scale-up, QA evidence)
- **B-Life Sciences R&D to Regulated** (evidence chains, GLxP-style discipline)
- **B-Energy & Asset Ops** (asset operations, reliability, field work)
- **B-Financial Products & Controls** (auditability, risk, models, reporting)
- **B-Construction & Infrastructure** (permits, schedule/cost, site safety)
- **B-Content Production** (media, publishing, brand assets)
- **B-Professional Services Delivery** (SoW, client governance, delivery ops)

**Universal B interface (what every B variant should still do):**  
Translate requirements → plan; produce deliverables; verification & validation; change control & traceability; readiness gates; defects → root cause → corrective actions.

## 5. Industry mapping (40 industries → default kernels)
This table bootstraps projects: choose the industry, then attach the default B kernel(s) plus industry packs as needed. Hybrids are common (e.g., digital + asset ops).

| # | Industry | Default B kernel(s) |
|---:|---|---|
| 1 | Software / SaaS | B-Digital Product |
| 2 | IT Services / Systems Integration | B-Professional Services Delivery |
| 3 | Cloud / Data Centers | B-Energy & Asset Ops + B-Digital Product |
| 4 | Cybersecurity (vendors) | B-Digital Product + B-Cyber & SecOps |
| 5 | Telecommunications | B-Energy & Asset Ops + B-Digital Product |
| 6 | Semiconductors | B-Industrial Manufacturing + B-Safety-Critical Engineering |
| 7 | Consumer Electronics | B-Embedded & Mechatronics + B-Industrial Manufacturing |
| 8 | Automotive (OEM & mobility) | B-Embedded & Mechatronics + B-Safety-Critical Engineering |
| 9 | Rail / Transit | B-Safety-Critical Engineering + B-Construction & Infrastructure |
| 10 | Aerospace | B-Safety-Critical Engineering + B-Embedded & Mechatronics |
| 11 | Space (launch/satellites) | B-Safety-Critical Engineering + B-Embedded & Mechatronics |
| 12 | Defense | B-Safety-Critical Engineering + B-Cyber & SecOps |
| 13 | Maritime / Shipping | B-Energy & Asset Ops + B-Construction & Infrastructure |
| 14 | Logistics / 3PL | B-Construction & Infrastructure + B-Data & Analytics |
| 15 | Retail (physical) | B-Data & Analytics + B-Digital Product |
| 16 | E-commerce / Marketplaces | B-Digital Product + B-Data & Analytics |
| 17 | Consumer Packaged Goods (CPG) | B-Industrial Manufacturing + B-Data & Analytics |
| 18 | Food & Beverage Manufacturing | B-Industrial Manufacturing + B-Chem/Materials Process |
| 19 | Agriculture | B-Industrial Manufacturing + B-Data & Analytics |
| 20 | Mining & Metals | B-Energy & Asset Ops + B-Industrial Manufacturing |
| 21 | Oil & Gas (upstream) | B-Energy & Asset Ops |
| 22 | Oil & Gas (midstream) | B-Energy & Asset Ops |
| 23 | Refining / Petrochemicals | B-Chem/Materials Process + B-Industrial Manufacturing |
| 24 | Chemicals (specialty/commodity) | B-Chem/Materials Process |
| 25 | Materials (advanced materials) | B-Chem/Materials Process (often hybrid) |
| 26 | Construction (GC / EPC) | B-Construction & Infrastructure |
| 27 | Real Estate (dev/property mgmt) | B-Construction & Infrastructure + B-Energy & Asset Ops |
| 28 | Utilities (electric/gas/water) | B-Energy & Asset Ops |
| 29 | Power generation (incl. nuclear) | B-Energy & Asset Ops + B-Safety-Critical Engineering |
| 30 | Renewables (wind/solar/storage) | B-Energy & Asset Ops + B-Embedded & Mechatronics |
| 31 | Healthcare Providers (hospitals/clinics) | B-Life Sciences R&D to Regulated + B-Data & Analytics |
| 32 | Health Insurance / Payers | B-Financial Products & Controls + B-Data & Analytics |
| 33 | Medical Devices | B-Safety-Critical Engineering + B-Life Sciences R&D to Regulated |
| 34 | Pharmaceuticals | B-Life Sciences R&D to Regulated |
| 35 | Biotech | B-Life Sciences R&D to Regulated |
| 36 | CRO / Clinical Trials Services | B-Life Sciences R&D to Regulated + B-Professional Services Delivery |
| 37 | Banking (retail/commercial) | B-Financial Products & Controls |
| 38 | Payments / Fintech | B-Financial Products & Controls + B-Digital Product |
| 39 | Insurance | B-Financial Products & Controls + B-Data & Analytics |
| 40 | Capital Markets / Asset Mgmt | B-Financial Products & Controls + B-ML/AI Systems |

### Using this mapping
- Start with the default kernel(s), then attach the pods needed for discovery, governance, commercial work, and operations.
- Add an **industry pack** to inject domain standards, required artifacts, and evidence rules (e.g., ISO, GLxP, SOX, etc.).
- If the project touches the physical world, attach the **Reality Layer (R pods)** and explicitly set an autonomy tier and safety envelope.

## 6. Reality layer for cyber-physical work (R pods)
Virtual-only agents produce documents and decisions. Real-world systems add actuation, safety, and irreversible consequences. To integrate robots or physical systems, introduce a Reality Layer with explicit autonomy tiers, policy-enforced action contracts, safety envelopes, and audit-grade telemetry.

### 6.1 Autonomy tiers (agency levels)
- **Tier 0 — Observe:** read sensors/logs only.
- **Tier 1 — Recommend:** generate plans/checklists; humans execute.
- **Tier 2 — Assisted Execute:** AI executes bounded actions with human confirmation (per action or per batch).
- **Tier 3 — Supervised Autonomy:** AI executes within strict safety envelope; human intervenes on exceptions.
- **Tier 4 — Autonomy:** rare; only in tightly controlled environments.

### 6.2 R pod family (Real-world / Cyber-Physical)
- **R0 Reality Interface:** wrap device/PLC/LIMS/BMS APIs into safe tools; define action schemas; create immutable audit logs.
- **R1 Perception & State Estimation:** sensor fusion, anomaly detection, calibration and drift checks.
- **R2 Execution:** compile plans into bounded steps; enforce limits; handle retries/timeouts; confirm postconditions.
- **R3 Safety & Assurance:** hazard analysis; safety envelope; two-key approvals; emergency stop integration; fail-safe defaults.
- **R4 Field Ops & Maintenance:** runbooks, preventive maintenance, incident response, spares/consumables, readiness checks.

### 6.3 Action Contracts (the critical addition)
Every physical action is executed under a strict **Action Contract** with:
- **preconditions**
- **safety bounds**
- **postconditions**
- **compensating action** (safe-state)
- **required evidence** to log
- **escalation rules**

The executor should be **deterministic and policy-enforcing**; planners can be flexible.

### 6.4 Default rollout lifecycle
- **Sim mode** (digital twin / emulator)
- **Shadow mode** (observe real system, no actuation)
- **Canary** (small scope, tight bounds, extra logging)
- **Progressive autonomy** (increase tier only after passing gates)
- **Continuous monitoring** (safety SLOs, quality, downtime)

## 7. Lab automation example pack
Lab automation is a canonical real-world example because it demands both:  
1) physical actuation across instruments and labware, and  
2) a traceable evidence chain for results, deviations, and approvals.

### 7.1 Recommended pods for a lab automation project
- **Core** (Orchestrator, Scribe, Research, Quality, Delivery Tracker)
- **B-Life Sciences R&D to Regulated** (evidence-first delivery)
- **R0 Reality Interface, R2 Execution, R3 Safety & Assurance, R4 Field Ops**
- Optional: **Data & Insight**, **Procurement/Vendor**

### 7.2 Agent templates (lab pack)
- **Study Designer** — define hypothesis/endpoints/controls; define acceptance criteria.
- **Protocol Composer** — convert run plan into structured protocol (steps, labware map, timing, dependencies).
- **Scheduler / Throughput Planner** — allocate instruments/time; optimize batching; propose canary runs.
- **Instrument Orchestrator** — coordinate devices; convert protocol spec into work orders.
- **Robot Executor (policy-enforcing)** — execute bounded actions only; enforce limits; log everything.
- **Telemetry & Evidence Collector** — capture device states, barcode scans, environment traces; build evidence bundles.
- **Safety Officer (envelope owner)** — define hard constraints; classify risk; enforce approvals; own safe-state and e-stop policy.
- **QA/QMS Steward** — traceability (sample → plate → well → result), deviations, change control, audit packaging and run release.
- **LIMS/ELN Registrar** — register runs, IDs, chain-of-custody, attach evidence bundle, maintain records.
- **Maintenance & Calibration Manager** — readiness checks, maintenance schedules, consumables tracking.

### 7.3 Example action contracts (liquid handler + peripherals)
| Action | What it does | Hard bounds examples | Evidence to log |
|---|---|---|---|
| `scan_barcode(labware)` | Verify labware identity/location | Allowed labware types only | Barcode, location, timestamp |
| `pick_up_tips(type)` | Acquire tips | Allowed tip types; tip count | Deck map, tip lot, success/fail |
| `aspirate(well, uL)` | Draw liquid | Min/max volume; allowed liquids; speed limits | Params + device state snapshot |
| `dispense(well, uL)` | Dispense liquid | Min/max; max dispense speed | Params + device state snapshot |
| `mix(well, cycles)` | Mix sample | Max cycles/speed | Params + state |
| `seal_plate(type)` | Apply seal | Allowed seal types | Seal lot, confirmation |
| `incubate(temp,time)` | Controlled incubation | Temp/time range | Temp trace, setpoint trace |
| `read_plate(mode)` | Read plate | Supported modes only | Raw file hash + metadata |
| `centrifuge(program)` | Spin plate/tubes | RPM/time bounds | Program ID + run log |
| `dispose_waste()` | Waste handling | Capacity thresholds | Waste level + confirmation |
| `safe_state()` | Park/stop system | Always available | Reason + full snapshot |

### 7.4 Recommended autonomy tiering (lab)
A pragmatic default is **Tier 2 initially (assisted execute)**: the executor can run steps, but a human approves **start-run** and any **high-risk actions**. **Tier 3** is appropriate once protocols are validated and telemetry-based exceptions are reliable.

### 7.5 Gating rules (stop-and-ask triggers)
- Protocol changed since last validated version
- Unrecognized or mismatched labware/reagent lots
- Instrument out of calibration or maintenance overdue
- Any parameter outside validated bounds (temp, RPM, volume, time)
- Abnormal telemetry (pressure/liquid detect errors, repeated pipetting failures, unexpected timeouts)
- Any deviation from plan (skipped step, retries beyond limit)

### 7.6 Evidence bundle (audit-ready run package)
- Protocol spec (versioned) + deck map
- Sample/labware IDs + chain-of-custody mapping (plate/well lineage)
- Instrument logs (raw) + normalized event timeline
- Environmental traces (e.g., temperature) if relevant
- Raw reader output files + checksums
- Deviations + approvals + operator identity + timestamps

### 7.7 Example project manifest (conceptual)
```yaml
project:
  type: lab_automation
  kernel: B-LifeSciences-Regulated
  reality:
    enabled: true
    agency_tier: 2
    pods: [R0, R2, R3, R4]
    connectors: [liquid_handler, plate_reader, incubator, lims]
    safety_envelope:
      approvals_required: [start_run, protocol_change]
      bounds:
        volume_uL: [1, 1000]
        incubation_C: [4, 37]
        centrifuge_RPM: [0, 3000]
      retry_limits:
        pipette_error: 1
        barcode_mismatch: 0
```

## 8. Template schema: how to store and reuse pods/agents/skills
To make the library composable, store templates as **interfaces**, not prose. Each agent template should declare inputs, outputs, skill verbs (what it does), quality rubric, tool access, escalation triggers, and stop conditions.

- Template ID, Name, Category (Core / Pod / Industry Pack)
- Mission (one sentence)
- Inputs expected (documents, data, constraints)
- Outputs produced (artifact list with formats)
- Skills (verb-first list: “should do”)
- Quality rubric (checks + acceptance criteria)
- Tools & permissions (connectors, read/write scope)
- Escalation triggers (conditions to ping orchestrator/safety/QA)
- Stop conditions (what completion means)

### Implementation note
For real-world projects, separate **planner agents** (flexible, creative) from a **policy-enforcing executor** (deterministic, bounded). Give all physical tools least privilege and require evidence logging by default.

### Suggested next step
- Export this framework as a machine-readable library (JSON/YAML): kernels, pods, agents, skills, rubrics, and tool permissions.
- Implement a resolver that selects pods based on: industry, kernel, risk tier, deliverables, and whether reality connectors are enabled.
- Start with a single connector adapter (one liquid handler + one LIMS) and validate the action contracts in sim/shadow/canary modes.
