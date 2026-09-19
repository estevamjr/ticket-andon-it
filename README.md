# 🎫 Ticket-Andon-IT: API Secundária (Lógica Preditiva)

Este microsserviço é a **API Secundária** do ecossistema Andon. É responsável por toda a persistência de dados (I/O), processamento de regras de negócios complexas e classificação de telemetria via algoritmos de Machine Learning (SVM).

![Arquitetura Andon IT](./Andon%20IT%20-%20Autonomous%20Action.png)

## 📊 Indicador de Aderência Arquitetural & 🏃‍♂️ Diretrizes de Gestão Ágil de Produtos e Projetos

Este projeto adota um medidor próprio de aderência aos princípios modernos de engenharia de software, cultura DevOps e sistemas distribuídos.

**Alta Aderência: Princípios Arquiteturais e Microsserviços**
* **Coesão e Baixo Acoplamento:** O Gateway opera como a única interface de contato na borda (*Single Point of Entry*), isolando o Backend que concentra as regras de persistência e orquestração de IA.
* **Cliente-Servidor e Independência de Interface:** O front-end atua apenas como *Client-Side ETL*, processando telemetria sem acoplamento topológico com o servidor.
* **Padrão REST e RFC 9110:** Implementação estrita de semântica HTTP. O Gateway atua como um escudo semântico, garantindo que erros estruturais (400, 401) cheguem intactos ao cliente sem mascaramento de exceções (*Error Masking*).

**Alta Aderência: Qualidade, Segurança e DevSecOps**
* **Integração de Testes (CI/CD):** O PyTest bloqueia a implantação caso a acurácia do modelo preditivo (SVM) caia abaixo do threshold de 80%.
* **Segurança no Pipeline:** A telemetria é anonimizada (rótulos SENS-01) para conformidade com a LGPD/GDPR. As transações são blindadas via JWT e o vazamento de chaves é prevenido no repositório via estratégia restrita de arquivos `.env.example`.

**Média Aderência: Modelagem de Domínio e Operações**
* **Gestão de Incidentes (Fix Forward):** O próprio produto materializa a cultura de operações contínuas ao prever falhas de hardware e gerar mitigações autônomas via LLM em tempo real.
* **Infraestrutura:** O encapsulamento é garantido via Docker, porém a orquestração avançada para auto-recuperação e escalabilidade horizontal (Kubernetes) segue mapeada como evolução futura no Roadmap MLOps.

Além do rigor em engenharia, este microsserviço foi gerido sob os pilares do Agile Product Management:

* **Product Discovery e Foco no MVP:** Emprego de metodologias como *Lean Inception* para focar no que agrega valor imediato. Optamos pela persistência em SQLite especificamente para viabilizar um ambiente local de validação rápido, garantindo que o escopo de tempo não fosse consumido com *setup* de banco de dados e sim com a lógica preditiva e regras de negócio.
* **Governança de Sprints e Backlog:** Acompanhamento iterativo de demandas, equilibrando débitos técnicos mapeados (como o frontend legado) com novas features arquiteturais (como a padronização das rotas no Swagger e controllers).
* **Definition of Done (DoD) Estrito:** Entregas apenas aceitas após comprovação de isolamento no Docker, aderência total ao versionamento (`/v1/`) e contratos Swagger íntegros para consumo via Gateway.

## 🎯 RTM: Matriz de Rastreabilidade de Requisitos (MVP)
Desenvolvido em conformidade com a arquitetura do **Cenário 2.1**.

| Requisito do MVP | Implementação e Compliance no Projeto | Status |
| :--- | :--- | :--- |
| **API Secundária (3.0 pts)**| Implementada em Python (Flask) na porta 5000. Expõe os 4 métodos (`GET`, `POST`, `PUT`, `DELETE`) acessados exclusivamente via Gateway. | ✅ Atingido |
| **Persistência de Dados** | Mapeamento de dados relacional via SQLAlchemy integrado ao banco **SQLite** local. | ✅ Atingido |
| **Containerização (0.5 pt)**| `Dockerfile` independente disponibilizado na raiz deste repositório para execução isolada. | ✅ Atingido |
| **Criatividade (1.0 pt)** | Funcionalidades avançadas além do CRUD básico: autenticação JWT, tratamento global de exceções, e classificação matemática (SVM). | ✅ Atingido |
| **Documentação (0.5 pt)** | Instruções de setup e endpoints interativos documentados neste repositório via Swagger UI. | ✅ Atingido |

## 🏗️ Decisões Arquiteturais e Tech Debts

A separação deste módulo permitiu escalar a persistência e a lógica pesada de forma independente do Gateway:
* **Persistência Orientada a ORM:** Utiliza SQLAlchemy para abstrair transações SQL no **SQLite**. O uso do SQLite simplifica o *setup* do avaliador para o MVP. Contudo, a arquitetura garante **Independência de Banco de Dados**: migrar para um PostgreSQL requer apenas a alteração da variável `DATABASE_URL` no `.env`, sem impacto nas regras de negócio.
* **Componentização Preditiva:** O modelo de Machine Learning (Support Vector Machine) foi encapsulado em um Pipeline estrito do `Scikit-Learn`, mantendo a precisão acima de 80%.
* **Interface de Contrato (Swagger):** Todas as interações e contratos REST foram padronizados via OpenAPI 3 (Flasgger).
* **Versionamento Universal (API e Contratos):** Todos os *controllers* (`auth.py`, `ticket.py`, `andon.py`, `log.py`) foram refatorados para espelhar a exigência do prefixo `/api/v1/`. Isso garante que o Swagger e os endpoints orquestrados pelo Gateway falem exatamente o mesmo idioma, mitigando falhas de comunicação entre os microsserviços.
* **Dívida Técnica (Frontend):** O diretório `/frontend` presente no ecossistema é um módulo legado mantido intencionalmente via estratégia de Arquitetura Evolutiva. Está fora do escopo deste MVP e sua remoção ocorrerá no próximo ciclo.
* **Dívida Técnica (DevOps):** A atual assimetria na orquestração (Gateway via Compose vs. Backend via CLI) foi adotada para facilitar testes isolados. O plano futuro prevê um repositório guarda-chuva com um `docker-compose.yml` global.

## 💻 Instruções de Instalação e Execução

⚠️ **Pré-requisito Crítico:** Certifique-se de que o **Docker Desktop** (ou daemon do Docker) esteja em execução na sua máquina antes de iniciar os comandos.

### 1. Clonar e Configurar

    git clone https://github.com/estevamjr/ticket-andon-it.git
    cd ticket-andon-it/backend

Renomeie o arquivo `.env.example` para `.env`.
*(Nota: A `SECRET_KEY`, a chave do LLM (OpenRouter) e a **Collection do Postman** para testes serão fornecidas exclusivamente na mensagem de publicação do portal da disciplina).*

Abra o arquivo `.env` recém-criado e insira as credenciais:

    SECRET_KEY=sua_chave_jwt_aqui
    OPENROUTER_API_KEY=sua_chave_do_openrouter_aqui

### 2. Subindo o Container (Docker Manual)
O banco de dados SQLite requer um mapeamento de volume físico. Execute os comandos abaixo no diretório `backend`:

**A. Crie a rede interna (caso o gateway ainda não tenha criado):**

    docker network create andon-net

**B. Construa a imagem e suba o container da API Secundária:**

    docker build -t andon-api .
    docker run -d --name backend-andon --network andon-net -p 5000:5000 --env-file .env -v "${PWD}/instance:/app/instance" andon-api
