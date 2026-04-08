#!/usr/bin/env python3
"""ADW: Strategy Digest — Resumo estratégico semanal via Sage"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("🎯 Strategy Digest", "Financeiro • Produto • Comunidade • Mercado | @sage")
    results = []
    results.append(run_skill("sage-strategy-digest", log_name="strategy-digest", timeout=900, agent="sage-strategy"))
    summary(results, "Strategy Digest")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
