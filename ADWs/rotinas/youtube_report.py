#!/usr/bin/env python3
"""ADW: YouTube Report — Analytics do canal via Pixel"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, banner, summary

def main():
    banner("📺 YouTube Report", "Inscritos • Views • Engagement • Top Vídeos | @pixel")
    results = []
    results.append(run_skill("social-youtube-report", log_name="youtube-report", timeout=600, agent="pixel-social-media"))
    summary(results, "YouTube Report")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
