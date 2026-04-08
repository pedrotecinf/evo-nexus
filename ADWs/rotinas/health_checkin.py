#!/usr/bin/env python3
"""ADW: Health Check-in — Check-in semanal de saúde via Kai"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_claude, banner, summary

PROMPT = """Execute o check-in semanal de saúde:

1. Leia os dados mais recentes em '06 Pessoal/' (último check-in, evolução, baseline)
2. Pergunte sobre:
   - Peso atual (se tiver balança por perto)
   - Como está a alimentação essa semana
   - Frequência de treino (quantos dias treinou)
   - Hidratação (estimativa de litros/dia)
   - Qualidade do sono (1-10)
   - Nível de energia/disposição geral (1-10)
   - Medicação (se aplicável na semana)
3. Compare com o último check-in e identifique tendências
4. Gere um relatório curto com semáforo (verde/amarelo/vermelho) para cada item
5. Salve o check-in em HTML: leia o template '.claude/templates/html/health-checkin.html', preencha todos os {{PLACEHOLDER}} com os dados coletados, e salve o HTML completo em '06 Pessoal/health-checkins/reports/[C] YYYY-MM-DD-health.html'. Criar o diretório se não existir.
6. Salve também a versão markdown em '06 Pessoal/health-checkins/reports/YYYY-MM-DD.md'
7. Atualize o arquivo de evolução se houver mudanças relevantes

Ser direto e prático — foco na evolução e consistência dos hábitos."""

def main():
    banner("🏥 Health Check-in", "Saúde • Hábitos • Evolução | @kai")
    results = []
    results.append(run_claude(PROMPT, log_name="health-checkin", timeout=600, agent="kai-personal-assistant"))
    summary(results, "Health Check-in")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Cancelado.")
