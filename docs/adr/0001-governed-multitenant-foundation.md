# ADR 0001: Fundação multi-tenant governada

- Status: Accepted
- Date: 2026-10-10

## Contexto

Nexxus precisa garantir isolamento, governança e auditoria desde a primeira entrega. A especificação prevê ambientes `tenant_prd`, `tenant_hml` e `tenant_dev`, além de escopos `PLATFORM`, `TENANT` e `COMPANY`.

## Decisão

A fundação usa `tenant_id` obrigatório em recursos tenant-scoped, foreign keys e índices compostos. O contexto do tenant é recebido via `X-Tenant-Id` e deve ser validado antes do acesso a dados. Eventos de auditoria preservam `request_id`, `trace_id`, `tenant_id`, `user_id`, `analysis_id`, ação e recurso.

## Consequências

- O isolamento lógico é aplicável desde o primeiro schema.
- Repositórios e consultas futuras devem filtrar explicitamente por `tenant_id`.
- Integração OIDC/JWKS será implementada antes de expor recursos administrativos em produção.
- Schema físico por tenant é uma evolução de operação, não um pré-requisito desta fundação.
- Segredos são fornecidos somente por ambiente de deploy ou secret manager; nunca em commits.
