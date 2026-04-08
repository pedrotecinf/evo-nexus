#!/usr/bin/env python3
"""ADW: Monthly Close Kickoff — Fechamento mensal via Flux"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("📋 Monthly Close Kickoff", "DRE • Checklist • NFs • Pendências Samara | @flux")
    results = []
    results.append(run_skill("fin-monthly-close-kickoff", log_name="monthly-close", timeout=900, agent="flux-financeiro"))
    summary(results, "Monthly Close Kickoff")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
