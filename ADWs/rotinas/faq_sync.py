#!/usr/bin/env python3
"""ADW: FAQ Sync — Atualiza FAQ da comunidade via Pulse"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("FAQ Sync", "Discord + GitHub → FAQ.md | @pulse")
    results = []
    results.append(run_skill("pulse-faq-sync", log_name="faq-sync", timeout=600, agent="pulse-community"))
    summary(results, "FAQ Sync")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
