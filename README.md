# 🛡️ Andon System (MVP) - Arquitetura de Microsserviços

Este repositório contém o ecossistema completo do **Andon System**, operando sob o padrão de arquitetura de microsserviços. O projeto é composto por um **API Gateway** (Proxy Reverso e orquestrador) e uma **API Secundária** (Persistência e Inteligência Preditiva), integrados a serviços externos de Inteligência Artificial para mitigação autônoma de incidentes.

## 🎯 RTM: Matriz de Rastreabilidade de Requisitos
Este projeto atende integralmente ao **Cenário 2.1** das diretrizes de Arquitetura de Software.

| Requisito do MVP | Implementação e Compliance no Projeto | Status |
| :--- | :--- | :--- |
| **API Principal (5.0 pts)** | Gateway em Python/Flask (Porta 8080). Orquestra rotas, implementa os 4 métodos REST (`GET`, `POST`, `PUT`, `DELETE`) e atua como Proxy Transparente. | ✅ Atingido |
| **API Secundária (3.0 pts)** | Backend em Python/Flask (Porta 5000). Acessado via Gateway. Gerencia persistência (SQLite/SQLAlchemy) e classificação preditiva (Machine Learning/SVM). | ✅ Atingido |
| **API Externa (1.0 pt)** | Integração via `POST` com o serviço de LLM da **OpenRouter**. Dados de mitigação processados e devolvidos nativamente em JSON. | ✅ Atingido |
| **Containerização (1.5 pts)**| Imagens Docker isoladas e rede manual configurada para garantir a comunicação entre os microsserviços. | ✅ Atingido |
| **Criatividade (1.0 pt)** | Tratamento rigoroso da RFC 9110 (barrando mascaramento de Erro 500 no Gateway), autenticação JWT Global e Classificação SVM (Scikit-Learn). | ✅ Atingido |
| **Documentação (1.5 pts)** | RTM inclusa, passo a passo de execução "Plug & Play", Swagger UI integrado na API secundária e fluxograma de arquitetura. | ✅ Atingido |

## 🏗️ Arquitetura e Padrões de Projeto

O sistema adota a componentização estrita de serviços:
* **Proxy Transparente & Borda:** O Gateway centraliza a entrada, intercepta cabeçalhos de autorização e repassa as requisições sem mutação de payload.
* **Tratamento RFC 9110:** Implementa blindagem semântica. Erros estruturais ou falhas de JWT são devolvidos com os HTTP Status corretos (`401`, `422`, `404`), impedindo o mascaramento genérico de exceções.
* **Persistência Orientada a ORM:** Utiliza SQLAlchemy para abstrair transações no SQLite, garantindo proteção contra injeções (SQL Injection).

## 💻 Instruções de Execução e Teste (Plug & Play)

O projeto foi configurado para exigir o mínimo de atrito. As variáveis de ambiente (como a chave da API do OpenRouter, segredos do JWT e rede) já estão pré-configuradas nos arquivos `.env` para facilitar a avaliação do professor.

### 1. Subindo a Arquitetura (Docker Manual)
A arquitetura depende de uma rede virtual Docker para a comunicação entre o Gateway e o Backend. Abra o terminal e execute os passos abaixo na ordem:

**A. Crie a rede interna (se ainda não existir):**

    docker network create andon-net

**B. Construa a imagem e suba o container da API Secundária (Backend):**
Navegue até a pasta do backend e execute:

    docker build -t andon-api .
    docker run -d --name backend-andon --network andon-net -p 5000:5000 --env-file .env -v "${PWD}/instance:/app/instance" andon-api

**C. Construa a imagem e suba o container do Gateway:**
Navegue até a pasta do gateway e execute:

    docker build -t andon-gateway .
    docker run -d --name andon-gateway --network andon-net -p 8080:8080 --env-file app/.env andon-gateway

O banco de dados SQLite será instanciado automaticamente. O **Gateway** estará orquestrando as requisições na porta **8080**.

### 2. Fluxo de Autenticação e Teste Local
Como o banco de dados inicia limpo na API Secundária, siga os três passos abaixo utilizando o Postman ou Insomnia para validar a API na porta 8080:

**Passo 1: Criar um Usuário**
* **Método/URL:** `POST http://localhost:8080/api/auth/register`
* **Payload (JSON):** `{"username": "admin", "password": "123"}`

**Passo 2: Gerar o Token JWT**
* **Método/URL:** `POST http://localhost:8080/api/auth/login`
* **Payload (JSON):** `{"username": "admin", "password": "123"}`
* *Copie o `access_token` retornado no JSON.*

**Passo 3: Acessar a Rota Preditiva (IA Andon)**
* **Método/URL:** `POST http://localhost:8080/api/v1/telemetry/analyze`
* **Header:** `Authorization: Bearer <seu_access_token_aqui>`
* **Payload (JSON):** Envie um payload de telemetria válido para testar o gatilho do LLMService e a geração da mitigação.

### 3. Swagger UI (Contratos da API)
Para visualizar a documentação interativa dos contratos REST da API Secundária, acesse o painel gerado pelo Flasgger diretamente na porta do backend:
👉 `http://localhost:5000/apidocs`

> **⚠️ Nota Técnica sobre o Requisito de API Gratuita:**
> Embora a plataforma OpenRouter atenda ao requisito do escopo por oferecer modelos *free tier*, os testes de estresse na infraestrutura comprovaram que a latência extrema dessas opções gratuitas inviabiliza o tempo de resposta em tempo real exigido por um sistema Andon. Por decisão de arquitetura e foco na resiliência do sistema, a integração em produção consome um modelo de *tier* pago. **A chave de API configurada no ambiente e enviada para esta avaliação possui saldo ativo**. O avaliador não precisará realizar cadastros, alterar variáveis ou lidar com falhas de *timeout*; o sistema está pronto para ser testado integralmente sem custos.