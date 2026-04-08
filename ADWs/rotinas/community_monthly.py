#!/usr/bin/env python3
"""ADW: Community Monthly — Relatório mensal da comunidade via Pulse"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("📊 Community Monthly", "Discord • WhatsApp • Sentimento • Produto • Docs Gaps | @pulse")
    results = []
    results.append(run_skill("pulse-monthly", log_name="community-monthly", timeout=900, agent="pulse-community"))
    summary(results, "Community Monthly")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
