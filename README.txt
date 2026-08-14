POLYGRAPH (working title -- see RESEARCH.txt Clarification Gate)
====================================================================

Project page: https://sopi22.github.io/polygraph/

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
Phase 1 complete: both checks implemented and passing against a
bounded, hand-constructed synthetic fixture set (4 checkpoint files,
3 claim files), including each check's own required deliberate
FAIL-detection case. Falsification result: SUPPORTED for the
mechanism (the combination catches a case neither check alone would),
NOT yet evidence this occurs in real, naturally-authored checkpoints
-- no real artifact tested yet. Full report in
RESEARCH_HYPOTHESIS.txt Section 4, including a real bug found and
fixed during this work (a blocked escape attempt that left no trace
in the sandbox's writable directory and exited cleanly -- caught only
by also checking stderr for the shell's own blocked-write message).

SETUP / RUN
------------
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"

    # regenerate the fixture set (already committed under
    # examples/fixtures/, only needed if you want to rebuild it)
    python3 examples/fixtures/build_fixtures.py

    # run a single checkpoint through both checks
    polygraph examples/fixtures/malicious_pickle.pkl \
        examples/fixtures/claim_pickle.json -o report.json

    # run the test suite (skips the live-sandbox tests cleanly if
    # bwrap isn't on PATH)
    pytest

CI
---
GitHub Actions (.github/workflows/ci.yml) runs the full test suite,
bwrap included, on every push/PR to main -- ubuntu-latest only,
deliberately, since bwrap is Linux-specific.

DEPENDENCIES
------------
Runtime: none beyond the Python standard library. Dev/test: pytest.
Sandbox: the system `bwrap` (bubblewrap) binary must be on PATH -- no
other setup needed, no privileged step, no Docker.

DEMO SCENARIOS (both fixtures already committed under examples/fixtures/)
---------------------------------------------------------------------------
Two named cases, both using the same rigged checkpoint
(malicious_pickle.pkl, a pickle whose __reduce__ writes a marker file
on load) with two different claim files, showing why this needs a
behavioral check and not just a format-honesty check:

  1. The obvious case -- checkpoint lies about its own format:
       polygraph examples/fixtures/malicious_pickle.pkl \
           examples/fixtures/claim_mismatch.json
     Both checks go FAIL: it claims safetensors, is actually pickle,
     AND behaves maliciously when loaded.

  2. The case that actually makes the point -- checkpoint is HONEST
     about its own format:
       polygraph examples/fixtures/malicious_pickle.pkl \
           examples/fixtures/claim_pickle.json
     declared_format_cross_check goes PASS (it truthfully says
     "pickle," and it is pickle -- no dishonesty at all), but
     sandboxed_load still goes FAIL. An honest label is not the same
     as a safe file -- this is the case RESEARCH_HYPOTHESIS.txt
     Section 4 names as the actual evidence for this project's
     hypothesis, not the obvious dishonest-label case.

Add `--no-color` to either command for plain-text output (piping to a
file, or a terminal without ANSI support).

FEATURES
---------
- `sandboxed_load` check with two required, deliberate
  FAIL-detection cases (a payload that writes into the sandbox's own
  scratch directory, and a harder one targeting a path entirely
  outside it) -- both must actually be caught, not silently pass.
- `declared_format_cross_check` check comparing a checkpoint's stated
  format claim (a small JSON sidecar file for now, see
  RESEARCH_HYPOTHESIS.txt Section 3 for why) against its real
  raw-byte format.
- A single combined JSON report per artifact, one predictable output
  location (`polygraph-report.json` by default).

AUTHOR
------
Jhoana Sophia Munar -- first-year IT student, Mapua University,
Makati (2026). (jhosophie@proton.me)

ATTRIBUTION
------------
LICENSE and copyright notices MUST remain intact in any fork or
redistribution of this repo -- no removing or replacing Jhoana Sophia
Munar's attribution.
