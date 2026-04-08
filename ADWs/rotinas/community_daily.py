#!/usr/bin/env python3
"""ADW: Community Daily Pulse — Relatório diário da comunidade via Pulse"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("📣 Community Pulse", "Discord • Atividade • Sentimento • Suporte | @pulse")
    results = []
    results.append(run_skill("pulse-daily", log_name="community-daily", timeout=600, agent="pulse-community"))
    summary(results, "Community Daily Pulse")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
