#!/usr/bin/env python3
"""ADW: Social Analytics — Relatório consolidado cross-platform via Pixel"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("📊 Social Analytics", "YouTube • Instagram • LinkedIn — Cross-platform | @pixel")
    results = []
    results.append(run_skill("social-analytics-report", log_name="social-analytics", timeout=900, agent="pixel-social-media"))
    summary(results, "Social Analytics")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
