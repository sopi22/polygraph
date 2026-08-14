"""polygraph CLI entry point."""

from __future__ import annotations

import argparse
import sys

from .render import render_table
from .report import run_all_checks, write_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="polygraph",
        description=(
            "Cross-check an AI model checkpoint's declared format claim "
            "against what a sandboxed load actually observes. Every "
            "result is a flag for human review, not a finding of fact."
        ),
    )
    parser.add_argument("checkpoint", help="path to the checkpoint file")
    parser.add_argument(
        "claim", help="path to a JSON claim file, e.g. {\"declared_format\": \"safetensors\"}"
    )
    parser.add_argument(
        "-o", "--out", default="polygraph-report.json",
        help="path to write the JSON report (default: polygraph-report.json)",
    )
    parser.add_argument(
        "--no-color", action="store_true",
        help="disable ANSI color in the terminal table (JSON report is unaffected)",
    )
    args = parser.parse_args(argv)

    report = run_all_checks(args.checkpoint, args.claim)
    write_report(report, args.out)

    print(render_table(report, use_color=not args.no_color))
    print(f"\nfull JSON report: {args.out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
