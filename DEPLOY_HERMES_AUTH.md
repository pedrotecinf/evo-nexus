# 🚀 Plano de Deployment Hermes Auth (Opção B)

## 📌 Contexto
- **Objetivo**: Hermes Desktop remoto via Tailscale (com Basic Auth) mantendo o iframe evo-nexus funcional (sem auth).
- **Branch**: `feature/hermes-runtime`
- **Ambiente**: Produção/Staging (via Dokploy).

## 🛠️ Passo a Passo (Server/SSH/Dokploy)

### 1. Atualizar `.env` do Container/Docker Compose
Certifique-se de que as variáveis de ambiente necessárias estejam configuradas no service `evonexus` do seu ambiente (no Dokploy na aba Environment ou diretamente no servidor no arquivo `.env` do diretório do docker-compose):

```env
# ── Hermes Dashboard Auth (remote access via Tailscale) ──
EVONEXUS_HERMES_USERNAME=hermes-admin
EVONEXUS_HERMES_PASSWORD=<sua-senha-segura-aqui>
```

### 2. Recriar/Reiniciar Container
- Se as alterações de código forem carregadas na build, realize o deploy normalmente (ex: via Git webhook no Dokploy, ou rodando `make rebuild` + `docker compose up -d`).
- Se as pastas forem volumes locais, um simples reinício (`docker compose restart` ou "Restart" no Dokploy) fará as mudanças do `start-dashboard.sh` entrarem em vigor.

### 3. Expor Porta 9119 (Apenas no Dokploy)
O Tailscale irá acessar o Hermes na porta 9119, logo ela precisa estar aberta (bindada no host).
- Vá no Dokploy UI -> Project -> Application -> `evonexus`.
- Vá na aba **Ports**.
- Adicione: `9119:9119/tcp`
- Salve e de Deploy (isso recria o container com o mapping atualizado).

---

## ✅ Testes de Aceitação Remotos (TST-1 a TST-5)

### TST-1 e TST-2: IFrame local continua funcionando
1. Acesse o **evo-nexus** normalmente pelo seu browser (`https://evo-nexus.domain.com/` ou localhost).
2. Vá até a aba "Terminal" ou "Hermes".
3. Valide: 
   - A interface do Hermes abre **sem pedir usuário/senha** na tela.
   - O chat do terminal conecta via **WebSocket** e responde comandos.

### TST-3: Bloqueio Desktop Remoto (Tailscale)
1. Certifique-se de estar conectado à sua Tailnet no seu PC ou celular.
2. Descubra o IP ou MagicDNS do servidor da EvoNexus (ex: `100.x.y.z` ou `evo-nexus.tail-xxx.ts.net`).
3. Abra uma guia **Anônima** do navegador e acesse: `http://<tailscale-ip-ou-dns>:9119/`
4. Valide: 
   - O browser deve exibir um pop-up nativo solicitando **Username** e **Password**.
   - Se cancelar, a tela do Hermes original mostrará um alerta vermelho.

### TST-4 e TST-5: Sucesso Desktop Remoto
1. No pop-up de login, insira:
   - **User**: _Valor de `EVONEXUS_HERMES_USERNAME` (padrão: `hermes-admin`)_
   - **Pass**: _Sua senha definida_
2. Valide:
   - A interface do Hermes UI carrega completamente e com sucesso (Código 200 OK).
   - Abra a gaveta de navegação lateral dentro do Hermes Desktop independente e tente mandar uma mensagem para testar o **WebSocket**. Ele não deve exibir erros de desconexão.

> 📢 **Se algo falhar:** Remova as variáveis `EVONEXUS_HERMES_USERNAME` e `EVONEXUS_HERMES_PASSWORD` e reinicie. O fallback nativo volta o Hermes para o `127.0.0.1` isolado.