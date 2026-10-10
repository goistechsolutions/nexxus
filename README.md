# Nexxus Backend Auth + RLS

Substituição direta do backend anterior, mantendo `app/`, `migrations/` e `tests/` em suas posições corretas.

## Segurança implementada

- JWT de acesso com permissões, tenant e versão de revogação.
- Refresh token rotativo, com JTI armazenado somente como SHA-256.
- Login, refresh e logout.
- RBAC por permissões persistidas no banco.
- Administração de usuários e papéis protegida por permissões.
- RLS transacional via `set_config(..., true)` dentro de `session.begin()`.
- Limpeza defensiva de variáveis RLS no checkout da conexão.

## Aplicação

```bash
cp .env.example .env
pip install -e '.[dev]'
alembic upgrade head
uvicorn app.main:app --reload
pytest
```

## Requisito crítico

A conexão da aplicação deve usar papel PostgreSQL sem `SUPERUSER` e sem `BYPASSRLS`. Para bootstrap inicial, crie tenant, administrador, papel e permissões por uma ferramenta administrativa separada e auditada. Não use a conexão administrativa para tráfego da API.

O teste real de isolamento permanece marcado como integração e exige PostgreSQL descartável com pgvector no pipeline.
