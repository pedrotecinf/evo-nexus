#!/usr/bin/env python3
"""ADW: Linear Review — Checagem de projetos via Atlas"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("🗂️  Linear Review", "Review • Blockers • Stale • Sprint | @atlas")
    results = []
    results.append(run_skill("int-linear-review", log_name="linear-review", timeout=600, agent="atlas-project"))
    summary(results, "Linear Review")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
