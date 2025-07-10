# Projeto de Pipeline ELT Moderno: Análise de LTV:CAC do HubSpot com Mage, DuckDB e dbt

*Status do Projeto: Em Desenvolvimento*

## Visão Geral

Este projeto implementa um pipeline de dados ELT (Extract, Load, Transform) de ponta a ponta, projetado para resolver problemas comuns de fragmentação de dados em CRMs como o HubSpot. O objetivo final é extrair dados de Contatos, Empresas e Negócios, carregá-los em um data warehouse DuckDB e transformá-los usando dbt para calcular métricas de negócios cruciais, especificamente a razão LTV:CAC (Lifetime Value to Customer Acquisition Cost).

O projeto é desenvolvido primeiro localmente e depois será implantado inteiramente na AWS usando Terraform e CI/CD, demonstrando um ciclo de vida de desenvolvimento de software completo.

## O Problema de Negócio

Empresas que dependem do HubSpot muitas vezes enfrentam desafios de qualidade de dados (duplicatas, registros incompletos, associações ausentes). Esses problemas técnicos impedem a capacidade de calcular métricas financeiras precisas como o LTV:CAC, levando a decisões de negócios mal informadas. Este pipeline aborda diretamente esses problemas criando uma única fonte da verdade para os dados do CRM.

## Arquitetura da Solução (Planejada)

O fluxo de dados seguirá um padrão ELT moderno:
1.  **Extract & Load:** O **Mage** orquestra um script Python que extrai dados da API do HubSpot e os carrega em formato bruto para um banco de dados **DuckDB**.
2.  **Transform:** O **dbt** é acionado pelo Mage para executar modelos SQL que limpam, unem e agregam os dados brutos, construindo um modelo dimensional e calculando a razão LTV:CAC.
3.  **Analyze:** Uma ferramenta de BI (como Metabase) se conectará ao DuckDB para visualizar os resultados em um dashboard interativo.

## Tech Stack

*   **Linguagem:** Python 3.10+
*   **Geração de Dados:** Faker, Pandas
*   **Orquestração:** Mage
*   **Fonte de Dados:** HubSpot API
*   **Data Warehouse:** DuckDB
*   **Transformação:** dbt (data build tool)
*   **Infraestrutura como Código (Planejado):** Terraform
*   **Nuvem (Planejado):** AWS (ECS Fargate, S3, ECR, Secrets Manager)
*   **Controle de Versão:** Git

---

## Progresso Atual (Fase I Concluída)

Nesta fase inicial, focamos em estabelecer uma base sólida para o projeto, com ênfase na criação de um ambiente de dados realista.

1.  **Setup do Ambiente Local:** O ambiente de desenvolvimento foi configurado usando WSL, Python 3.10 e um ambiente virtual (`venv`).
2.  **Estratégia de Dados:** Foi definido um cenário de negócio customizado (empresa de saúde que conecta médicos e pacientes para tratamentos com canabidiol) e mapeado para os objetos padrão do HubSpot:
    *   Médicos (PJ) -> **Companies**
    *   Pacientes -> **Contacts**
    *   Consultas/Vendas -> **Deals**
3.  **Geração de Dados Programática:** Foi criado o script `generate_fake_data.py` utilizando a biblioteca `Faker` para popular nosso ambiente de desenvolvimento com dados realistas e em volume controlável.
4.  **Simulação de Problemas de Qualidade:** O script de geração de dados foi projetado para injetar intencionalmente problemas de qualidade de dados que o pipeline precisará resolver:
    *   **Registros Duplicados:** Contatos e Empresas com dados idênticos.
    *   **Dados Incompletos:** Pacientes sem sobrenome.
    *   **Formatação Inconsistente:** Especialidades médicas escritas de formas diferentes (ex: 'Neurologia' vs 'Neuro').
    *   **Associações Ausentes:** Negócios criados sem um médico (Empresa) associado.
5.  **Adaptação ao Esquema da Fonte:** Durante a importação manual dos dados via CSV, foram encontrados e resolvidos erros de validação do HubSpot, levando a melhorias no script:
    *   Criação de uma **propriedade personalizada** "Especialidade Médica" para Empresas, em vez de sobrecarregar o campo padrão "Industry".
    *   Adição da propriedade obrigatória **"Pipeline"** na geração de Negócios.
    *   Refatoração da lógica de criação de emails para ser mais robusta e lidar com nomes compostos.
6.  **Setup do Orquestrador:** O Mage foi instalado e um novo projeto (`hubspot_elt_project`) foi iniciado. O gerenciamento de segredos foi configurado usando um arquivo `.env` e o `io_config.yaml`.

## Como Executar o Projeto (Estado Atual)

Estes passos permitem replicar o ambiente de desenvolvimento e popular o HubSpot com os dados de teste.

**Pré-requisitos:**
*   WSL 2 (ou ambiente Linux/macOS)
*   Python 3.10+
*   Conta do HubSpot com permissões de administrador

**Passos:**

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/modern-elt-portfolio.git
    cd modern-elt-portfolio
    ```

2.  **Crie e ative o ambiente virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure suas credenciais do HubSpot:**
    *   Crie um arquivo chamado `.env` na raiz do projeto.
    *   Adicione seu token de acesso de um Aplicativo Privado do HubSpot:
      ```
      HUBSPOT_ACCESS_TOKEN=pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
      ```

5.  **Gere os dados de teste:**
    ```bash
    python generate_fake_data.py
    ```
    *   Isso criará três arquivos: `import_companies.csv`, `import_contacts.csv`, e `import_deals.csv`.

6.  **Importe os dados para o HubSpot:**
    *   Faça login no seu portal HubSpot.
    *   Importe os arquivos CSV **nesta ordem**: 1º Empresas, 2º Contatos, 3º Negócios.
    *   Durante a importação, mapeie as colunas do arquivo para as propriedades correspondentes no HubSpot.

7.  **Inicie o Mage:**
    ```bash
    mage start hubspot_elt_project
    ```
    *   Acesse a interface do Mage em `http://localhost:6789`.

## Próximos Passos

O próximo grande objetivo é construir o pipeline de **Extração e Carregamento** dentro do Mage.
*   Criar um bloco **Data Loader** para se conectar à API do HubSpot usando o token de acesso.
*   Implementar a lógica de paginação para buscar todos os registros dos objetos `Companies`, `Contacts` e `Deals`.
*   Criar um bloco **Data Exporter** para carregar os dados extraídos em um arquivo de banco de dados DuckDB local.