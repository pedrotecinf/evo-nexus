#!/usr/bin/env python3
"""ADW: Instagram Report — Analytics dos perfis via Pixel"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("📸 Instagram Report", "Seguidores • Engagement • Posts • Insights | @pixel")
    results = []
    results.append(run_skill("social-instagram-report", log_name="instagram-report", timeout=600, agent="pixel-social-media"))
    summary(results, "Instagram Report")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
