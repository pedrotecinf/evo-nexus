---
name: int-licensing
description: "Query Evolution Licensing API — keys, instances, telemetry, customers, commercial alerts, activation logs. Use when user asks about licenses, open source growth, instâncias ativas, distribuição geográfica, versões em uso, telemetria, alertas comerciais, 'como tá o licensing', 'quantas instâncias', 'crescimento open source', or any reference to the licensing system."
---

# Evolution Licensing API

Integração com a API de licenciamento da Evolution para monitorar crescimento open source, instâncias ativas, telemetria e alertas comerciais.

## Setup

Requer variável de ambiente (em `.env`):
```bash
LICENSING_ADMIN_TOKEN=your_token_here
```

## API Client

```bash
python3 {project-root}/.claude/skills/int-licensing/scripts/licensing_client.py <command> [args]
```

### Comandos

#### Keys (licenças)
```bash
licensing_client.py keys [--status active|expired|revoked] [--tier free|pro|enterprise]
licensing_client.py keys_all [--status active] [--tier pro]
```

#### Instances (instâncias ativas)
```bash
licensing_client.py instances [--status active] [--tier pro] [--geo BR] [--heartbeat 24h]
licensing_client.py instances_all [--status active]
licensing_client.py instance_detail INSTANCE_ID
```

#### Telemetry (resumo)
```bash
licensing_client.py telemetry --period 24h    # últimas 24h
licensing_client.py telemetry --period 7d     # últimos 7 dias
licensing_client.py telemetry --period 30d    # últimos 30 dias
```

Retorna: geo_distribution, version_distribution, product_distribution, city_distribution, heartbeat_coverage, message_metrics, feature_usage, daily_message_trend.

#### Activation Log
```bash
licensing_client.py activation_log [--api_key evo_abc123]
```

#### Commercial Alerts
```bash
licensing_client.py alerts [--resolved false]
```

#### Customers
```bash
licensing_client.py customers [--search joao] [--country BR] [--tier pro]
licensing_client.py customer_detail 42
```

#### Products
```bash
licensing_client.py products
```

## Métricas-chave para análise de crescimento

| Métrica | Endpoint | O que mede |
|---------|----------|------------|
| Instâncias ativas | `telemetry --period X` → `heartbeat_coverage.total_active` | Adoção total |
| Heartbeat 24h | `heartbeat_coverage.heartbeat_last_24h` | Instâncias realmente rodando |
| Distribuição geográfica | `geo_distribution` | Onde estão os usuários |
| Versões em uso | `version_distribution` | Adoção de versões novas |
| Mensagens enviadas | `message_metrics.total_sent` | Volume de uso real |
| Features usadas | `feature_usage` | Quais funcionalidades importam |
| Trend diário | `daily_message_trend` | Curva de crescimento |
| Alertas comerciais | `alerts` | Problemas de licença |
