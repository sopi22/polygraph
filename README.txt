POLYGRAPH
===========
A lie detector for AI models.

Project page: https://sopi22.github.io/polygraph/

WHAT IT DOES AND WHY
----------------------
Polygraph checks an AI model checkpoint's own claim about itself (e.g.
a model card saying "safetensors only, no pickle, no custom code on
load") against what the checkpoint actually does when loaded inside an
isolated sandbox. It exists because every static scanner in this space
-- picklescan, fickling, ModelScan, Hugging Face's own Hub scanning --
never actually runs the file, so none of them has a behavioral signal
to check a claim against; a 2026 attack called ShadowPickle was built
specifically to beat that entire category of tool and bypassed it 63%
of the time. Polygraph's own falsification-first research log
(RESEARCH_HYPOTHESIS.txt) found a real case a claims-only check
structurally cannot catch: a checkpoint that is HONESTLY labeled
"pickle" -- no dishonesty at all -- can still be malicious, and only
running it in a sandbox reveals that.

TECH STACK
-----------
Python, standard library only at runtime -- no torch, no safetensors
package, no third-party dependency of any kind (pytest is a dev-only
dependency, for the test suite). Sandbox: bubblewrap (`bwrap`), a
Linux namespace-isolation primitive (the same one Flatpak uses to
sandbox desktop apps), invoked as a subprocess. Docker is deliberately
NOT used -- bwrap already provides the isolation this project needs
with zero setup, and adding Docker would mean a privileged host-level
step for no functional gain. See RESEARCH.txt's Clarification Gate for
the full reasoning.

NOT A FORK -- DESIGN INFLUENCES ONLY
---------------------------------------
This is an independent build, not a fork of anything. Before building,
a real reuse evaluation (RESEARCH.txt Section 4) checked whether to
fork an existing project instead -- these four were read in full and
credited as design influences, not code ancestry:
  - picklescan (mmaitre314) and fickling (Trail of Bits) -- static
    pickle-opcode analysis; informed Polygraph's own structural
    format-detection logic, without executing anything.
  - ModelScan (Protect AI) -- same static-analysis category.
  - OSSF Package Analysis -- the closest real-world precedent for a
    network-isolated, behavior-observing sandbox, though built for
    generic npm/PyPI packages at internet scale (gVisor, GCP,
    BigQuery), not a single-machine ML-checkpoint check.
No code was copied from any of the four; no license compatibility
question applies as a result (all four are permissively licensed
anyway -- MIT, LGPL-3.0, or Apache-2.0).

SETUP / RUN
------------
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"

    polygraph examples/fixtures/malicious_pickle.pkl \
        examples/fixtures/claim_pickle.json -o report.json

No Docker path exists or is needed -- see TECH STACK above. Requires
the system `bwrap` (bubblewrap) binary on PATH; nothing else.

EXAMPLE OUTPUT (real, captured by actually running the command above)
-------------------------------------------------------------------------
    CHECKPOINT: examples/fixtures/malicious_pickle.pkl
    CLAIM FILE: examples/fixtures/claim_pickle.json

      CHECK                        OBSERVED
      ---------------------------  --------
      sandboxed_load               FAIL
      declared_format_cross_check  PASS

      [sandboxed_load] load wrote to the sandbox's writable directory:
      ['polygraph_marker_of_compromise'] (a clean load should write
      nothing)
      [declared_format_cross_check] declared format 'pickle' matches
      actual format 'pickle'

The checkpoint honestly says it's a pickle file -- no lie for the
format check to catch. It's still malicious. That's the whole point:
an honest label is not the same thing as a safe file. See DEMO
SCENARIOS below for the full pair (this one, plus the obvious
dishonest-label case), and DEMO_SCRIPT.txt for the walkthrough.

FEATURES
---------
- `sandboxed_load` -- loads a checkpoint inside a bwrap sandbox (real
  filesystem entirely read-only except one scratch directory, network
  fully unshared) and reports FAIL if anything appears in that
  directory or a blocked escape attempt shows up in stderr. Ships with
  two required, deliberately-triggered FAIL-detection cases (a payload
  that writes into its own scratch directory, and a harder one
  targeting a path entirely outside it) -- both must actually be
  caught before any PASS result is trusted.
- `declared_format_cross_check` -- compares a checkpoint's claimed
  format (a small JSON sidecar file for now, see
  RESEARCH_HYPOTHESIS.txt Section 3) against its real raw-byte format,
  detected with stdlib `pickletools`/`struct`/`json` only.
- A single combined JSON report per artifact, one predictable output
  location.
- A colored claimed-vs-observed terminal table (`--no-color` for plain
  text).
- CI: GitHub Actions runs the full test suite, live bwrap sandbox
  tests included, on every push/PR to main.

DEMO SCENARIOS (both fixtures already committed under examples/fixtures/)
---------------------------------------------------------------------------
Two named cases, both using the same rigged checkpoint
(malicious_pickle.pkl, a pickle whose __reduce__ writes a marker file
on load) with two different claim files:

  1. The obvious case -- checkpoint lies about its own format:
       polygraph examples/fixtures/malicious_pickle.pkl \
           examples/fixtures/claim_mismatch.json
     Both checks go FAIL: it claims safetensors, is actually pickle,
     AND behaves maliciously when loaded.

  2. The case that actually makes the point -- see EXAMPLE OUTPUT
     above (that's this exact scenario). RESEARCH_HYPOTHESIS.txt
     Section 4 names it as the actual evidence for this project's
     hypothesis, not the obvious dishonest-label case above.

NON-GOALS
---------
Not a general-purpose malware sandbox. Not a replacement for
picklescan/fickling/ModelScan -- their static analysis is
complementary, not competing. Not an LLM-judged safety review. Does
not itself claim to "verify," "prove," "guarantee," or "confirm" a
checkpoint is safe -- a sandboxed observation is one data point for
human review, not a finding of fact. Not (yet) general Python/npm
package auditing -- scoped to AI model checkpoints first.

RESEARCH
---------
Full falsification-first methodology in RESEARCH.txt (project brief,
novelty firewall, fork-vs-build reasoning) and RESEARCH_HYPOTHESIS.txt
(hypothesis, entropy budget, per-check justification, falsification
report). DEMO_SCRIPT.txt has the pitch/demo walkthrough.

RESEARCH LINEAGE
------------------
Polygraph follows the same falsification-first, novelty-firewall
methodology used in Jhoana's other research logs: PULSE EXPERIMENT
001 -- RESEARCH LOG and CLAIM CARD -- RESEARCH LOG. Both state a
hypothesis and a falsification criterion before running anything,
search for existing solutions before building, and log negative or
partial results honestly rather than only positive ones. See
RESEARCH.txt Section 15 for exactly where this repo applies that same
discipline, with citations, not just this claim restated.

CI
---
GitHub Actions (.github/workflows/ci.yml) runs the full test suite,
bwrap included, on every push/PR to main -- ubuntu-latest only,
deliberately, since bwrap is Linux-specific.

LICENSE
--------
MIT. See LICENSE.

AUTHOR
------
Jhoana Sophia Munar -- first-year IT student, Mapua University,
Makati (2026). (jhosophie@proton.me)

ATTRIBUTION
------------
LICENSE and copyright notices MUST remain intact in any fork or
redistribution of this repo -- no removing or replacing Jhoana Sophia
Munar's attribution.
