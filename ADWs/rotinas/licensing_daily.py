#!/usr/bin/env python3
"""ADW: Licensing Daily — Crescimento open source diário via Atlas"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("📊 Licensing Daily", "Instâncias • Geo • Versões • Alertas | @atlas")
    results = []
    results.append(run_skill("prod-licensing-daily", log_name="licensing-daily", timeout=600, agent="atlas-project"))
    summary(results, "Licensing Daily")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
