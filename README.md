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
├── 📁 connectors/   # Integrações com serviços externos (ex: SupabaseStorage)
├── 📁 controller/   # Coração do sistema: Regras de negócio e orquestração
├── 📁 dto/          # Data Transfer Objects: Formatação dos dados de saída para o Frontend
├── 📁 errors/       # Tratamento de exceções customizadas e padronizadas
├── 📁 middlewares/  # Interceptadores globais (ex: Validação de Token JWT)
├── 📁 models/       # Entidades do SQLAlchemy (O espelho das tabelas do Banco)
├── 📁 repository/   # Camada de abstração do Banco de Dados (Consultas, Inserts, Updates)
├── 📁 schemas/      # Contratos de Entrada (Validação de payload via Pydantic)
├── 📁 utils/        # Ferramentas auxiliares (Segurança, Conexão com o BD)
└── 📄 app.py        # Ponto de entrada, definição das rotas e injeção de dependências