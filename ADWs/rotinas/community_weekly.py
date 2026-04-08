#!/usr/bin/env python3
"""ADW: Community Weekly Report — Relatório semanal da comunidade via Pulse"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("📊 Community Weekly", "WAM • Sentimento • Tópicos • Insights | @pulse")
    results = []
    results.append(run_skill("pulse-weekly", log_name="community-weekly", timeout=900, agent="pulse-community"))
    summary(results, "Community Weekly Report")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
