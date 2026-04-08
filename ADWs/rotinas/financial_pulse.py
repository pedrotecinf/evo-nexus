#!/usr/bin/env python3
"""ADW: Financial Pulse — Snapshot financeiro diário via Flux"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("💰 Financial Pulse", "Stripe • Omie • MRR • Churn | @flux")
    results = []
    results.append(run_skill("fin-daily-pulse", log_name="financial-pulse", timeout=600, agent="flux-financeiro"))
    summary(results, "Financial Pulse")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
