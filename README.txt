POLYGRAPH (working title -- see RESEARCH.txt Clarification Gate)
====================================================================

WHAT IT DOES AND WHY
----------------------
Polygraph checks whether an AI model checkpoint's own declared safety
claim (a model card saying "safetensors only, no pickle," "no custom
code executed on load," etc.) actually matches what the checkpoint
does when it's loaded inside an isolated sandbox -- a claims-vs-
behavior cross-check. As of this project's own novelty-firewall search
(RESEARCH.txt Section 4), no shipped tool does this specific
combination for ML checkpoints: every static scanner in this space
(picklescan, fickling, ModelScan, Hugging Face's own Hub scanning)
never actually executes the file, so none has a behavioral signal to
check a claim against; the one real precedent for sandboxed behavioral
execution (OSSF's Package Analysis) has no claims layer and isn't
scoped to ML checkpoints at all.

See RESEARCH.txt for the full project brief (operator context,
autonomy protocol, security/privacy rules, the fork-vs-build decision
and its reasoning) and RESEARCH_HYPOTHESIS.txt for the falsification-
first hypothesis, entropy budget, and per-check justification.

TECH STACK
-----------
Python, standard library only at runtime (no torch, no safetensors
package -- both formats this project needs to tell apart are simple
enough to detect from raw bytes with stdlib `pickletools`/`struct`/
`json` alone). Sandbox mechanism: bubblewrap (`bwrap`), already
available in the target environment with no privileged setup.
Containerization (Docker) was considered and is explicitly NOT used
for Phase 1 -- see RESEARCH.txt Clarification Gate for the reasoning
and RESEARCH.txt Section 3 for why this is a judgment call, not a
default.

DESIGN INFLUENCES (not code ancestry -- independent build, not a
fork; see RESEARCH.txt Section 4 for the full reuse evaluation)
-----------------------------------------------------------------
- picklescan (mmaitre314) and fickling (Trail of Bits) -- static
  pickle-opcode analysis; informed this project's own structural
  format-detection logic (Check 2), without executing anything.
- ModelScan (Protect AI) -- same static-analysis category.
- OSSF Package Analysis -- the closest real-world precedent for a
  network-isolated, behavior-observing sandbox (though built for
  generic npm/PyPI packages at internet scale, not ML checkpoints on
  one machine).

NON-GOALS
---------
Not a general-purpose malware sandbox. Not a replacement for
picklescan/fickling/ModelScan -- their static analysis is
complementary, not competing. Not an LLM-judged safety review. Does
not itself claim to "verify," "prove," "guarantee," or "confirm" a
checkpoint is safe -- a sandboxed observation is one data point for
human review, not a finding of fact. Not (yet) general Python/npm
package auditing -- scoped to AI model checkpoints first (see
RESEARCH.txt Section 4 for why).

CURRENT PHASE
--------------
Phase 0: project brief complete (this file, RESEARCH.txt,
RESEARCH_HYPOTHESIS.txt, LICENSE). No check code written yet -- same
order her other two projects (FOSS Pulse, Claim Card) followed.

SETUP / RUN
------------
Not applicable yet -- Phase 0 is scoping only.

FEATURES (planned, Phase 1)
-----------------------------
- `sandboxed_load` check with a required, deliberate FAIL-detection
  case (a synthetic malicious pickle payload that must actually be
  caught, not silently pass).
- `declared_format_cross_check` check comparing a checkpoint's stated
  format claim against its real raw-byte format.
- A single combined JSON report per artifact, one predictable output
  location.

AUTHOR
------
Jhoana Sophia Munar -- first-year IT student, Mapua University,
Makati (2026). (jhosophie@proton.me)
