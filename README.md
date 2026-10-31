# polygraph

**A lie detector for AI model files.**

Project page: https://sopi22.github.io/polygraph/

## What it does and why

AI model files (checkpoints) usually come with a label: a model card saying something like
*"safetensors only, no pickle, no custom code when loaded"*. Pickle files can run code the
moment you open them, so that label matters.

Today's scanners (picklescan, fickling, ModelScan, Hugging Face's own scanning) only *read*
the file; none of them actually opens it. A 2026 attack called ShadowPickle was built to fool
exactly that kind of scanner and got past them 63% of the time.

polygraph does two things:

1. **Opens the file inside a locked-down sandbox** and watches what it does. If it tries to
   write files or reach outside the sandbox, that's caught.
2. **Compares the file's label with its real format**, by reading its raw bytes.

The interesting case is a file that is **honestly** labelled "pickle". There's no lie for a
label check to catch, but it's still malicious. Only opening it in the sandbox shows that.
An honest label is not the same as a safe file.

## Example (real output)

```text
CHECKPOINT: examples/fixtures/malicious_pickle.pkl
LABEL FILE: examples/fixtures/label_pickle.json

  CHECK                        OBSERVED
  ---------------------------  --------
  sandboxed_load               FAIL
  declared_format_cross_check  PASS

  [sandboxed_load] load wrote to the sandbox's writable directory:
  ['polygraph_marker_of_compromise'] (a clean load should write nothing)
  [declared_format_cross_check] declared format 'pickle' matches actual format 'pickle'
```

The label is honest (PASS), but the file is malicious (FAIL).

## Run it

Linux only (the sandbox uses `bwrap`). Requires Python 3 and `bubblewrap`
(`sudo apt install bubblewrap` on Ubuntu).

```bash
git clone https://github.com/sopi22/polygraph.git
cd polygraph
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

pytest                                                     # 16 tests, sandbox included
polygraph examples/fixtures/malicious_pickle.pkl \
    examples/fixtures/label_pickle.json -o report.json     # the example above
polygraph examples/fixtures/malicious_pickle.pkl \
    examples/fixtures/label_mismatch.json                  # file lies about its format: both checks FAIL
```

## Features

- **`sandboxed_load`** opens a checkpoint inside a `bwrap` sandbox: the whole system is
  read-only except one scratch folder, and there's no network. It fails if anything appears
  in that folder or a blocked escape attempt shows up. Two deliberately malicious test files
  (one writing inside the scratch folder, one trying to write outside it) must both be
  caught before any PASS is trusted.
- **`declared_format_cross_check`** compares the format written in a small JSON label file
  (`{"declared_format": "safetensors"}`) with the file's real format from its raw bytes.
- One JSON report per file, and a coloured terminal table (`--no-color` for plain text).
- GitHub Actions runs every test, the live sandbox included, on each push.

## Tech

Python standard library only (no torch, no safetensors package); `pytest` for tests. The
sandbox is **bubblewrap** (`bwrap`), the same isolation tool Flatpak uses. I chose it over
Docker because it needs no setup and no admin-level service.

## Not a fork: what influenced it

Built from scratch. Before starting, I looked at whether to build on an existing project.
These shaped the design (no code copied):

- **picklescan** (mmaitre314) and **fickling** (Trail of Bits): reading pickle files without running them
- **ModelScan** (Protect AI): the same kind of read-only scanning
- **OpenSSF Package Analysis**: the closest real example of watching packages run in an
  isolated sandbox (built for npm/PyPI packages at large scale)

## What it is not

Not a general malware sandbox, and not a replacement for the scanners above; they work well
together. It never says a file is "proven safe"; a sandbox run is one piece of evidence for a
person to weigh. It covers AI model files only for now.

## Notes

- [RESEARCH.md](RESEARCH.md): planning notes and why I built instead of forking
- [RESEARCH_HYPOTHESIS.md](RESEARCH_HYPOTHESIS.md): what I expected, each check, and the results
- [DEMO_SCRIPT.txt](DEMO_SCRIPT.txt): a short demo walkthrough

## Author

Jhoana Sophia Munar ([@sopi22](https://github.com/sopi22))

## License

MIT, see [LICENSE](LICENSE). Please keep the license and copyright notice in any copy or fork.
