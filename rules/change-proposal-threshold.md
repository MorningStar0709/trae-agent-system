---
alwaysApply: true
description: When considering changes to rules, skills, or core config, self-triage using cost/benefit/risk/alternative analysis before presenting options to the user. Does not apply when user explicitly asks "what should I change?".
---

# Change Proposal Threshold

When considering whether to propose changes to rules, skills, or core infrastructure config, self-triage before presenting options to the user.

Use this lightweight framework to decide:

| Dimension | Ask yourself | If YES → | If NO → |
|:----------|:-------------|:---------|:--------|
| **Problem clarity** | Is there a concrete, recurring pain point this solves? | Continue | Do not propose. Hypothetical fixes for hypothetical problems are not worth it. |
| **Impact** | Does it affect multiple workflows or save multiple back-and-forth rounds? | Continue | Probably not worth it. |
| **Cost** | Does the change cost more to maintain than the problem it solves? (Complex new structures, cross-file sync burden, frequent updates) | Do not propose | Continue |
| **Risk** | Could this break existing workflows or create ambiguity where there was none? | Propose with risk mitigation or reconsider | Continue |
| **Alternative** | Is there a simpler path? (Clarify existing content vs. restructure, merge vs. create new) | Take the simpler path | The change is likely warranted. |

**Decision rules:**
- If the net benefit is clearly positive: propose it directly with a one-paragraph rationale.
- If the net benefit is marginal or ambiguous: mention it briefly as an observation, not a recommendation. Let the user decide if they want to pursue it.
- If the net benefit is negative (cost > benefit, risk too high, simpler alternative available): do not propose. The agent should internalize the decision and move on.

**Applicability:** This threshold applies when the agent initiates a proposal to change rules, skills, or configuration. It does not apply when the user explicitly asks "what should I change?" — in that case, present all findings with honest assessments.

**See also:** `question-threshold.md` for when to ask the user vs deduce, and `review-and-completion-gates.md` for the Proactive Review Gate that triggers this threshold during branch wrap-up.
