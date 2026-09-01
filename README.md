# 🎫 Ticket-Andon-IT: API Secundária (Lógica Preditiva)

Este microsserviço é a **API Secundária** do ecossistema Andon. É responsável por toda a persistência de dados (I/O), processamento de regras de negócios complexas e classificação de telemetria via algoritmos de Machine Learning (SVM).

![Arquitetura Andon IT](./Andon%20IT%20-%20Autonomous%20Action.png)

## 📊 Indicador de Aderência Arquitetural

Este projeto adota um medidor próprio de aderência aos princípios modernos de engenharia de software, cultura DevOps e sistemas distribuídos.

**Alta Aderência: Princípios Arquiteturais e Microsserviços**
* **Coesão e Baixo Acoplamento:** O Gateway opera unicamente como Proxy Transparente na borda, isolando o Backend que concentra as regras de persistência e orquestração de IA.
* **Cliente-Servidor e Independência de Interface:** O front-end atua apenas como *Client-Side ETL*, processando telemetria sem acoplamento topológico com o servidor[cite: 3].
* **Padrão REST e RFC 9110:** Implementação estrita de semântica HTTP. O Gateway repassa dados sem mascaramento de erros (*Error Masking*), garantindo que status estruturais (400, 401) cheguem intactos ao cliente.

**Alta Aderência: Qualidade, Segurança e DevSecOps**
* **Integração de Testes (CI/CD):** O PyTest bloqueia a implantação caso a acurácia do modelo preditivo (SVM) caia abaixo do threshold de 80%[cite: 3].
* **Segurança no Pipeline:** A telemetria é anonimizada (rótulos SENS-01) para conformidade com a LGPD/GDPR[cite: 3]. As transações são blindadas via JWT e o vazamento de chaves é prevenido no repositório via estratégia restrita de arquivos `.env.example`.

**Média Aderência: Modelagem de Domínio e Operações**
* **Gestão de Incidentes (Fix Forward):** O próprio produto materializa a cultura de operações contínuas ao prever falhas de hardware[cite: 3] e gerar mitigações autônomas via LLM em tempo real.
* **Infraestrutura:** O encapsulamento é garantido via Docker, porém a orquestração avançada para auto-recuperação e escalabilidade horizontal (Kubernetes) segue mapeada como evolução futura no Roadmap MLOps[cite: 3].

**Trade-offs (Padrões Não Aplicados)**
* **GraphQL e RPC:** Omitidos intencionalmente. O protocolo REST síncrono atendeu integralmente aos requisitos de latência e integração entre os componentes deste MVP, evitando excesso de engenharia (*overengineering*).

## 🎯 RTM: Matriz de Rastreabilidade de Requisitos (MVP)
Desenvolvido em conformidade com a arquitetura do **Cenário 2.1**.

| Requisito do MVP | Implementação e Compliance no Projeto | Status |
| :--- | :--- | :--- |
| **API Secundária (3.0 pts)**| Implementada em Python (Flask) na porta 5000. Expõe os 4 métodos (`GET`, `POST`, `PUT`, `DELETE`) acessados exclusivamente via Gateway. | ✅ Atingido |
| **Persistência de Dados** | Mapeamento de dados relacional via SQLAlchemy integrado ao banco **SQLite** local. | ✅ Atingido |
| **Containerização (0.5 pt)**| `Dockerfile` independente disponibilizado na raiz deste repositório para execução isolada. | ✅ Atingido |
| **Criatividade (1.0 pt)** | Funcionalidades avançadas além do CRUD básico: autenticação JWT, tratamento global de exceções, e classificação matemática (SVM). | ✅ Atingido |
| **Documentação (0.5 pt)** | Instruções de setup e endpoints interativos documentados neste repositório via Swagger UI. | ✅ Atingido |

## 🏗️ Decisões Arquiteturais

A separação deste módulo permitiu escalar a persistência e a lógica pesada de forma independente do Gateway:
* **Persistência Orientada a ORM:** Utiliza SQLAlchemy para abstrair transações SQL no SQLite, garantindo proteção contra injeções.
* **Componentização Preditiva:** O modelo de Machine Learning (Support Vector Machine) foi encapsulado em um Pipeline estrito do `Scikit-Learn`, mantendo a precisão acima de 80%.
* **Interface de Contrato (Swagger):** Como a arquitetura dispensa Front-End visual, todas as interações e contratos REST foram padronizados via OpenAPI 3 (Flasgger).

## 💻 Instruções de Instalação e Execução

O projeto segue boas práticas de segurança, não versionando segredos de infraestrutura.

### 1. Clonar e Configurar

    git clone https://github.com/estevamjr/ticket-andon-it.git
    cd ticket-andon-it

Renomeie o arquivo `.env.example` para `.env` e insira a chave JWT de segurança (fornecida no memorial de entrega):

    SECRET_KEY=sua_chave_jwt_aqui

### 2. Subindo o Container (Docker Manual)
O banco de dados SQLite requer um mapeamento de volume físico. Execute os comandos abaixo:

**A. Crie a rede interna (caso o gateway ainda não tenha criado):**

    docker network create andon-net

**B. Construa a imagem e suba o container da API Secundária:**

    docker build -t andon-api .
    docker run -d --name backend-andon --network andon-net -p 5000:5000 --env-file .env -v "${PWD}/instance:/app/instance" andon-api

### 3. Interface de Testes (Swagger UI)
Com o container em execução na porta 5000, acesse a documentação interativa para visualizar os contratos, gerar seu Token JWT e testar os endpoints diretamente pelo navegador:
👉 `http://127.0.0.1:5000/apidocs`
