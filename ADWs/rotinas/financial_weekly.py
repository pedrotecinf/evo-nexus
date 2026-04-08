#!/usr/bin/env python3
"""ADW: Financial Weekly — Relatório financeiro semanal via Flux"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("📊 Financial Weekly", "Receitas • Despesas • Fluxo de Caixa • Inadimplência | @flux")
    results = []
    results.append(run_skill("fin-weekly-report", log_name="financial-weekly", timeout=900, agent="flux-financeiro"))
    summary(results, "Financial Weekly")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
