#!/usr/bin/env python3
"""ADW: Weekly Review — Revisão semanal via Clawdia"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_claude, banner, summary

PROMPT = """Execute a revisão semanal completa:

1. **Reuniões da semana** — use /int-sync-meetings com período da semana
2. **Tarefas** — use /prod-review-todoist, depois liste concluídas, atrasadas e próxima semana
3. **Agenda próxima semana** — use /gog-calendar para listar eventos
4. **Memória** — revise daily logs da semana, consolide decisões/aprendizados

Salvar o relatório em dois formatos:
- **HTML:** leia o template '.claude/templates/html/weekly-review.html', preencha todos os {{PLACEHOLDER}} com os dados coletados e salve em '01 Daily Logs/[C] YYYY-WXX-weekly-review.html'
- **MD:** salve também a versão markdown em '01 Daily Logs/[C] YYYY-WXX-weekly-review.md' usando o template em .claude/templates/weekly-review.md

Criar o diretório '01 Daily Logs/' se não existir."""

def main():
    banner("📊 Weekly Review", "Reuniões • Tarefas • Agenda • Memória | @clawdia")
    results = []
    results.append(run_claude(PROMPT, log_name="weekly-review", timeout=900, agent="clawdia-assistant"))
    summary(results, "Weekly Review")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
