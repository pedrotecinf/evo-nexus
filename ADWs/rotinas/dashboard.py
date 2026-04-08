#!/usr/bin/env python3
"""ADW: Dashboard Consolidado — Visão 360 via Clawdia"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("📊 Dashboard Consolidado", "Produto • Comunidade • Financeiro • Rotinas | @clawdia")
    results = []
    results.append(run_skill("prod-dashboard", log_name="dashboard", timeout=900, agent="clawdia-assistant"))
    summary(results, "Dashboard Consolidado")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
