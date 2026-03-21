# FastAPI Blog API

API REST assíncrona com FastAPI para autenticação JWT, gestão de usuários e CRUD de posts com autorização por proprietário.

## Principais recursos

- Login com JWT (`/auth/token`)
- Rotas públicas para leitura de posts
- Rotas protegidas para criar/editar/deletar posts
- Regra de autorização por dono do post (ou `admin`)
- Seed opcional de usuário admin via configuração
- Testes unitários + integração com alta cobertura

## Arquitetura

Estrutura em camadas:

- `src/controllers`: endpoints HTTP e composição das dependências
- `src/services`: regras de negócio
- `src/models`: tabelas SQLAlchemy
- `src/schemas`: contratos de entrada (Pydantic)
- `src/views`: contratos de saída
- `src/dependencies`: autenticação/autorização reutilizável
- `src/utils`: utilitários (JWT e senha)
- `src/config.py`: configurações por ambiente

## Requisitos

- Python `>=3.14`
- Poetry `>=2.x`

## Configuração de ambiente

As configurações são lidas de variáveis de ambiente (com suporte a arquivo `.env`).

### Variáveis disponíveis

| Variável | Padrão | Descrição |
|---|---|---|
| `APP_ENV` | `development` | Ambiente (`development`, `test`, `production`) |
| `DATABASE_URL` | `sqlite:///./blog.db` | String de conexão do banco |
| `JWT_SECRET_KEY` | `change-me-in-production` | Chave JWT (obrigatória segura em produção) |
| `JWT_ALGORITHM` | `HS256` | Algoritmo de assinatura JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Expiração do token |
| `SEED_ADMIN_ENABLED` | `true` | Habilita criação automática do admin |
| `SEED_ADMIN_USERNAME` | `admin` | Usuário inicial |
| `SEED_ADMIN_PASSWORD` | `admin` | Senha inicial |

> Em `APP_ENV=production`, a aplicação falha no startup se `JWT_SECRET_KEY` estiver insegura.

## Executando localmente

1. Instale dependências:

```zsh
poetry lock
poetry install --no-root
```

2. (Opcional) Defina variáveis em `.env`.

3. Rode a API:

```zsh
poetry run uvicorn src.main:app --reload
```

4. Abra documentação interativa:

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Fluxo rápido com cURL

### 1) Login

```zsh
curl -s -X POST 'http://127.0.0.1:8000/auth/token' \
	-H 'Content-Type: application/json' \
	-d '{"username":"admin","password":"admin"}'
```

### 2) Criar post (rota protegida)

```zsh
curl -s -X POST 'http://127.0.0.1:8000/posts/' \
	-H 'Authorization: Bearer <TOKEN>' \
	-H 'Content-Type: application/json' \
	-d '{"title":"Meu post","content":"Conteúdo","published":true}'
```

### 3) Listar posts (rota pública)

```zsh
curl -s 'http://127.0.0.1:8000/posts/?published=true&skip=0&limit=10'
```

## Regras de autorização

- `POST /posts/`: requer usuário autenticado.
- `PATCH /posts/{id}` e `DELETE /posts/{id}`:
	- permitido para o dono do post;
	- permitido para `admin`;
	- demais usuários recebem `403`.

## Testes

Rodar testes:

```zsh
poetry run pytest -q
```

Rodar com cobertura:

```zsh
poetry run pytest --cov=src --cov-report=term-missing -q
```

## Próximos passos recomendados

- Adicionar migrações com Alembic para evolução de schema em produção
- Adicionar observabilidade (logs estruturados e tracing)
- Implementar refresh token e rotação de segredo JWT
