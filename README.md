# 🏢 Rental Manager API

Uma API RESTful robusta desenvolvida para a gestão completa de locações imobiliárias. O sistema gerencia inquilinos, propriedades, contratos, seguros fiança, pagamentos e repasses financeiros (extratos), além de gerar relatórios automatizados de imposto de renda.

## 🛠️ Tecnologias Utilizadas

* **Framework Web:** [FastAPI](https://fastapi.tiangolo.com/) (Alta performance e documentação Swagger automática)
* **Banco de Dados:** PostgreSQL hospedado no [Supabase](https://supabase.com/)
* **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
* **Validação de Dados:** [Pydantic](https://docs.pydantic.dev/)
* **Armazenamento de Arquivos:** Supabase Storage (Buckets para contratos e extratos)
* **Testes:** [Pytest](https://docs.pytest.org/) com simulação (Mocking) de serviços externos
* **Autenticação:** JWT (JSON Web Tokens) com senhas cacheadas via Bcrypt

---

## 🏗️ Arquitetura e Estrutura de Pastas

O projeto segue os princípios de **Clean Architecture** e **Separation of Concerns (Separação de Responsabilidades)**. A regra de negócio não se mistura com a regra de banco de dados ou com a definição de rotas.

```text
📁 src/
├── 📁 connectors/   # Integrações com serviços externos (ex: S3StorageConnector)
├── 📁 controller/   # Coração do sistema: Regras de negócio e orquestração
├── 📁 dto/          # Data Transfer Objects: Formatação dos dados de saída para o Frontend
├── 📁 errors/       # Tratamento de exceções customizadas e padronizadas
├── 📁 middlewares/  # Interceptadores globais (ex: Validação de Token JWT)
├── 📁 models/       # Entidades do SQLAlchemy (O espelho das tabelas do Banco)
├── 📁 repository/   # Camada de abstração do Banco de Dados (Consultas, Inserts, Updates)
├── 📁 routers/      # Definição de endpoints e rotas modulares (ex: tenant_router)
├── 📁 schemas/      # Contratos de Entrada (Validação de payload via Pydantic)
├── 📁 utils/        # Ferramentas auxiliares (Segurança, Conexão com o BD, Rate Limit)
└── 📄 app.py        # Ponto de entrada do sistema, orquestração de middlewares e registro das rotas
```

---

## 🚀 Execução em Desenvolvimento Padrão

```bash
uvicorn src.app:app --reload
```
Swagger interativo da API: https://web-retal-manager-backend.onrender.com/docs

## 🗄️ Migrações do Banco (Alembic)

O Alembic é o único fluxo ativo para versionar e aplicar alterações no schema.
Revise cada revisão gerada antes de executá-la com `alembic upgrade head`.
Os scripts SQL em `migrations/` são artefatos legados e não devem ser executados;
eles podem divergir do estado atual do schema e das revisões Alembic.

---

## 🧪 Ambiente de Testes Local (Isolado e Seguro)

Para testar a API e o Frontend localmente sem apontar para o banco de produção, execute o script de inicialização local:

```bash
python run_local.py
```

### O que esse comando faz:
1. Cria e conecta a API a um banco de dados SQLite local isolado (`dev_local.db`).
2. Executa automaticamente todas as migrações do Alembic (`alembic upgrade head`).
3. Alimenta o banco com dados realistas de teste (seeds):
   - **Usuário Administrador Master:** `admin@rentalmanager.com` | Senha: `admin123`
   - Imobiliária padrão, Proprietários, Imóveis com participações societárias, Inquilinos, Garantias e Contratos ativos.
4. Sobe o servidor FastAPI em `http://localhost:8000` com documentação interativa em `http://localhost:8000/docs`.
