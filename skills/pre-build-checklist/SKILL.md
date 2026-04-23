---
name: pre-build-checklist
version: 1.0.0
title: "Pre-Build Checklist (7 Questions)"
description: "Decision gate before any new build. 7 questions to determine: software vs AI automation vs both, UI needs, persistence, and real-time requirements. Fires BEFORE building."
category: decision-gates
tags:
  - pre-build
  - decision-gate
  - architecture
  - planning
  - build-vs-buy
author:
  civ: Aether
  agent: system
  adapted_by: null
dependencies: []
compatibility:
  min_agents: 1
  requires_network: false
---

# Pre-Build Checklist (7 Questions)

**Version**: 1.0.0
**Source**: Aether + Jared + Chy + Morphe (PureBrain.ai)
**Purpose**: Before building ANYTHING, determine what to build and how

---

## When to Invoke

Before starting any build work. This is a Level 2 structural gate that fires BEFORE building (complementary to the 8 Adversarial Questions which fire AFTER building, before shipping).

---

## The 7 Questions

Q1: **Software, AI automation, or both?** And why?
Q2: **Must it run when no AI is active?**
Q3: **Customers or just us?**
Q4: **Recurring or one-time?**
Q5: **Real-time accuracy or periodic snapshots?**
Q6: **Does output need to persist/be queryable?**
Q7: **Will humans configure without talking to AI?**

## Decision Matrix

| Condition | Decision |
|-----------|----------|
| Q2=yes OR Q3=customers OR Q6=yes | → SOFTWARE |
| Q7=yes | → Needs UI |
| Q4=recurring + Q5=real-time | → LIVE SYSTEM |
| Q4=one-time + Q5=no | → AI AUTOMATION sufficient |

---

## Blocker Reporting

If blocked during build, report via:
```
POST https://social.purebrain.ai/api/blockers/report
Body: {"description": "what's blocked", "blocker_type": "ai_needs_human", "blocked_by": "person_name"}
```

Blockers surface before every team meeting at team.purebrain.ai.

---

*Source: Aether, Co-CEO Pure Technology — constitutional skill for all CIVs*
