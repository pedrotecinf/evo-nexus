#!/usr/bin/env python3
"""ADW: Memory Sync — Consolida memória via Clawdia"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_claude, banner, summary

PROMPT = """Execute a rotina de consolidação de memória:

1. Leia os últimos 3 daily logs em '01 Daily Logs/' (mais recentes primeiro)
2. Leia os summaries de reuniões dos últimos 3 dias em '09 Reuniões/summaries/'
3. Analise o git log recente: `git log --oneline --since="3 days ago"` e `git diff --stat HEAD~10` para entender o que mudou no workspace
4. Para cada fonte, extraia:
   - Decisões tomadas → salvar em memory/ como tipo 'project'
   - Pessoas novas ou contexto novo sobre pessoas → salvar como tipo 'user' ou atualizar existente
   - Feedbacks ou correções de abordagem → salvar como tipo 'feedback'
   - Termos ou referências externas novas → salvar como tipo 'reference'
   - Skills ou rotinas criadas/alteradas → atualizar referências se relevante
5. Antes de salvar, verificar se já existe memória similar — atualizar em vez de duplicar
6. Atualizar MEMORY.md com ponteiros para novos arquivos

Reportar no final: quantas memórias criadas/atualizadas por tipo.
Ser conciso — não criar memórias para coisas óbvias ou já documentadas no código."""

def main():
    banner("🧠 Memory Sync", "Logs • Reuniões → Memória | @clawdia")
    results = []
    results.append(run_claude(PROMPT, log_name="memory-sync", timeout=600, agent="clawdia-assistant"))
    summary(results, "Memory Sync")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
