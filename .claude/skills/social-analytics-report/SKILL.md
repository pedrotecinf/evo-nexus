---
name: social-analytics-report
description: "Unified social media analytics report — consolidates YouTube, Instagram, and LinkedIn data into one cross-platform HTML dashboard. Compares engagement, followers, top content across all platforms. Use when user says 'social analytics', 'social media report', 'social report', 'social metrics', 'cross-platform', or any reference to unified social media performance."
---

# Social Analytics — Consolidated Cross-Platform Report

Routine that pulls data from ALL connected social platforms (YouTube, Instagram, LinkedIn) and generates a single comparative HTML report.

**Always respond in English.**
**Agente:** @pixel

## Workflow

### Step 1 — Collect data from all platforms (silently)

Executar os scripts de cada integração e capturar os resultados:

#### YouTube (todas as contas)
```bash
python3 {project-root}/.claude/skills/int-youtube/scripts/youtube_client.py summary
python3 {project-root}/.claude/skills/int-youtube/scripts/youtube_client.py recent_videos 1 10
```

#### Instagram (todas as contas)
```bash
python3 {project-root}/.claude/skills/int-instagram/scripts/instagram_client.py summary
python3 {project-root}/.claude/skills/int-instagram/scripts/instagram_client.py recent_posts your_account 10
python3 {project-root}/.claude/skills/int-instagram/scripts/instagram_client.py recent_posts secondary_account 10
```

#### LinkedIn (todas as contas)
```bash
python3 {project-root}/.claude/skills/int-linkedin/scripts/linkedin_client.py summary
```

Se alguma plataforma falhar ou não tiver dados, incluir no relatório como "Sem dados — plataforma não configurada ou API limitada" sem quebrar o relatório.

### Step 2 — Consolidar métricas cross-platform

Calcular:

1. **Total seguidores** (soma de todas as contas de todas as plataformas)
2. **Total publicações** no período (YouTube vídeos + Instagram posts)
3. **Engagement rate médio** ponderado por plataforma
4. **Plataforma com maior crescimento** (delta de seguidores, se houver relatório anterior)
5. **Plataforma com maior engagement** (comparar engagement rates)

### Step 3 — Montar tabela comparativa

Uma row por conta:

| Plataforma | Conta | Seguidores | Delta | Posts | Engagement | Melhor Conteúdo |
|------------|-------|-----------|-------|-------|------------|-----------------|
| YouTube | Your Channel | 7.450 | — | 27 | 7.0% | "Evo v3 chegando" |
| Instagram | your_account | 686 | — | 18 | 3.9% | "Evo V3 funcionalidades" |
| Instagram | secondary_account | 273 | — | 76 | — | — |
| LinkedIn | Your Profile | — | — | — | — | Perfil apenas |

### Step 4 — Top conteúdos cross-platform

Rankear os top 10 conteúdos de TODAS as plataformas por engagement (likes + comments / views ou followers). Mostrar:
- Plataforma
- Título/caption (resumo)
- Views ou alcance
- Engagement %
- Link

### Step 5 — Compare with previous period

Ler o relatório anterior em `workspace/social/reports/consolidated/` if it exists. Calculate deltas de:
- Seguidores por plataforma
- Engagement médio
- Volume de publicações

### Step 6 — Insights cross-platform

Gerar análise com:
- Qual plataforma cresce mais?
- Qual tipo de conteúdo performa melhor onde? (vídeo no YouTube vs imagem no Instagram)
- Frequência de publicação por plataforma
- Recomendações: onde investir mais conteúdo, que formato priorizar
- Plataformas sem dados (LinkedIn posts, etc) — o que falta pra destravar

### Step 7 — Generate HTML

Ler template `.claude/templates/html/social-analytics-report.html` e preencher todos os `{{PLACEHOLDER}}`.

`{{REPORT_TYPE}}` depende da frequência:
- Diário: "Daily"
- Semanal: "Weekly" 
- Mensal: "Monthly"

Para rows da tabela comparativa:
```html
<tr>
  <td><span class="badge blue">YouTube</span></td>
  <td>Your Channel</td>
  <td class="right">7.450</td>
  <td class="right delta up">+32</td>
  <td class="right">27</td>
  <td class="right">7.0%</td>
  <td>Evo v3 chegando...</td>
</tr>
```

Para plataformas sem dados:
```html
<tr style="opacity:0.5">
  <td><span class="badge muted">LinkedIn</span></td>
  <td>Your Profile</td>
  <td class="right">—</td>
  <td class="right">—</td>
  <td class="right">—</td>
  <td class="right">—</td>
  <td style="color:var(--text-muted)">API limitada — perfil apenas</td>
</tr>
```

Para `{{MISSING_INTEGRATIONS}}` — se alguma plataforma não está configurada:
```html
<div class="highlight-card" style="border-color: rgba(102,112,133,0.3);">
  <div class="title" style="color: var(--text-muted);">Integrações Pendentes</div>
  <div class="body">
    <ul style="list-style:none;padding:0;">
      <li>LinkedIn — Posts e Company Page (requer Community Management API)</li>
      <li>Twitter — Não configurado</li>
    </ul>
  </div>
</div>
```

### Step 8 — Save

```
workspace/social/reports/consolidated/[C] YYYY-MM-DD-social-analytics.html
```

Criar diretório if it does not exist.

### Step 9 — Telegram

Notify: `reply(chat_id="YOUR_CHAT_ID", text="...")`
Format:
```
📊 Social Analytics — {period}
👥 Total seguidores: {N} ({delta})
📹 YouTube: {subs} sub | {eng}% eng
📸 Instagram: {followers} seg | {eng}% eng  
💼 LinkedIn: perfil conectado
🏆 Top: "{melhor conteúdo}" ({plataforma}, {eng}%)
```
