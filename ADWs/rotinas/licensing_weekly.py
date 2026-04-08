#!/usr/bin/env python3
"""ADW: Licensing Weekly — Crescimento open source semanal via Atlas"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("📊 Licensing Weekly", "Growth • Geo Expansion • Version Adoption • Trends | @atlas")
    results = []
    results.append(run_skill("prod-licensing-weekly", log_name="licensing-weekly", timeout=900, agent="atlas-project"))
    summary(results, "Licensing Weekly")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
