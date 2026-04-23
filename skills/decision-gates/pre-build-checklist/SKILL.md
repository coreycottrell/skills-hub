---
name: pre-build-checklist
description: 7-question checklist before building ANYTHING. Determines software vs AI automation vs both. TRIGGER before any new build, feature, or system design.
version: 1.0.0
source: Aether + Jared + Chy + Morphe (PureBrain constitutional skill)
adopted: 2026-04-19
allowed-tools: Read
---

# Pre-Build Checklist (7 Questions)

**Status**: Active — Constitutional requirement
**Applies to**: ALL agents before building anything
**Source**: Aether (PureBrain Co-CEO) + Jared + quartet (Chy, Morphe)

---

## Before Building ANYTHING, Answer These 7 Questions:

```
Q1: Software, AI automation, or both? And why?
Q2: Must it run when no AI is active?
Q3: Customers or just us?
Q4: Recurring or one-time?
Q5: Real-time accuracy or periodic snapshots?
Q6: Does output need to persist/be queryable?
Q7: Will humans configure without talking to AI?
```

## Decision Matrix

| Condition | Result |
|-----------|--------|
| Q2=yes OR Q3=customers OR Q6=yes | SOFTWARE |
| Q7=yes | Needs UI |
| Q4=recurring + Q5=real-time | LIVE SYSTEM |
| Q4=one-time + Q5=no | AI AUTOMATION sufficient |

## Integration with Critical Thinking Framework

This skill is a Level 2 (Structural Enforcement) mechanism — it makes the wrong build decision architecturally harder by forcing explicit answers before any code is written.

## Blocker Reporting API

When blocked, report to team system:
```
POST https://social.purebrain.ai/api/blockers/report
Body: {
  "description": "what's blocked",
  "blocker_type": "ai_needs_human",
  "blocked_by": "person_name"
}
```

Blockers surface before every team.purebrain.ai meeting.

---

## Attribution

Adopted from Aether's email 2026-04-19. Original authors: Jared + Aether + Chy + Morphe.
