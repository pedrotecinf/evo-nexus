#!/usr/bin/env python3
"""ADW: LinkedIn Report — Analytics via Pixel"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("💼 LinkedIn Report", "Perfil • Posts • Org | @pixel")
    results = []
    results.append(run_skill("social-linkedin-report", log_name="linkedin-report", timeout=600, agent="pixel-social-media"))
    summary(results, "LinkedIn Report")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
