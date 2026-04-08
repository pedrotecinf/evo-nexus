#!/usr/bin/env python3
"""ADW: Review Todoist — Organiza tarefas via Clawdia"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("📋 Review Todoist", "Categorizar • Traduzir • Organizar | @clawdia")
    results = []
    results.append(run_skill("prod-review-todoist", log_name="review-todoist", timeout=300, agent="clawdia-assistant"))
    summary(results, "Review Todoist")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
