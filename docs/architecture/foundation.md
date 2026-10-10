# Fundação da Plataforma Nexxus

## Escopo

A fundação implementa o Control Plane inicial da plataforma corporativa: `tenants`, `companies`, `environments`, `users`, `roles`, atribuições de papel e `audit_events`. A API FastAPI é versionada em `/v1` e segue a separação `Router -> Service -> Domain -> Repository` conforme o domínio evoluir.

## Fluxo de requisição

```text
Request -> request/trace correlation -> autenticação OIDC (futuro) -> tenant context -> RBAC -> domínio/repositório -> evento de auditoria -> resposta
```

## Multi-tenancy

Cada recurso de negócio deve ter `tenant_id`. A API recebe `X-Tenant-Id` e o endpoint de contexto valida UUID. O banco aplica foreign keys e unicidade por tenant para companies e environments. A estratégia inicial é isolamento lógico; schema por tenant (`tenant_prd`, `tenant_hml`, `tenant_dev`) permanece uma evolução controlada.

## Segurança e observabilidade

- Variáveis `NEXXUS_*` são injetadas no ambiente; `.env` não deve ser versionado.
- OIDC/OAuth2, MFA, JWKS e autorização real são marcos posteriores.
- O middleware atual emite `request_id`, `trace_id`, `tenant_id`, `user_id`, `analysis_id` e latência para logs estruturados.
- `AuditEvent` é a trilha de auditoria persistível para ações relevantes.

## Roadmap técnico

1. Fundação governada: concluída nesta branch.
2. Catálogo e semântica: domínios, métricas, glossário, regras e dashboards.
3. Knowledge/RAG: documents, chunks, embeddings, pgvector, políticas e citações.
4. Copilot analítico: conversas, `AnalysisContext`, planejamento, validação, insights e narrativa.
5. Produção: Nginx, TLS, systemd, OpenTelemetry, Prometheus, Grafana, Loki, backup e disaster recovery.

## Decisões pendentes

- Provedor de identidade e configuração de audiences/JWKS.
- Política de retenção de eventos de auditoria e dados de conhecimento.
- Modelo de filas para ingestão, chunking e embeddings.
- Estratégia final de schema por tenant e deployment por ambiente.
