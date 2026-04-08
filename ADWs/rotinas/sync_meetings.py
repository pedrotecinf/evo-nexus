#!/usr/bin/env python3
"""ADW: Sync Meetings — Fathom → JSON + Summary + Todoist via Clawdia"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("🎙️  Sync Meetings", "Fathom → Salvar → Todoist | @clawdia")
    results = []
    results.append(run_skill("int-sync-meetings", log_name="sync-meetings", timeout=600, agent="clawdia-assistant"))
    summary(results, "Sync Meetings")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
