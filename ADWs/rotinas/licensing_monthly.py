#!/usr/bin/env python3
"""ADW: Licensing Monthly — Crescimento open source mensal via Atlas"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("📊 Licensing Monthly", "Growth Trajectory • Markets • Versions • Projections | @atlas")
    results = []
    results.append(run_skill("prod-licensing-monthly", log_name="licensing-monthly", timeout=900, agent="atlas-project"))
    summary(results, "Licensing Monthly")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
