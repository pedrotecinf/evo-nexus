#!/usr/bin/env python3
"""ADW: Trends — Análise de tendências semanal via Clawdia"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("📈 Trends", "Comunidade • GitHub • Financeiro • Operacional | @clawdia")
    results = []
    results.append(run_skill("prod-trends", log_name="trends", timeout=900, agent="clawdia-assistant"))
    summary(results, "Análise de Tendências")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
