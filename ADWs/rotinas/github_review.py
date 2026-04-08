#!/usr/bin/env python3
"""ADW: GitHub Review — Status dos repositórios Evolution via Atlas"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("GitHub Review", "PRs • Issues • Stars • Releases | @atlas")
    results = []
    results.append(run_skill("int-github-review", log_name="github-review", timeout=600, agent="atlas-project"))
    summary(results, "GitHub Review")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
