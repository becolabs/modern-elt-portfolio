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


---

### Fase II: Extração e Carregamento com Mage (Concluído)

Esta fase do projeto está concluída. Foi implementado um pipeline EL (Extract-Load) completo e robusto dentro do orquestrador Mage, responsável por buscar dados brutos da API do HubSpot e carregá-los em nosso data warehouse local.

O pipeline `hubspot_to_duckdb` consiste em dois blocos principais:

1.  **`load_hubspot_data.py` (Data Loader):**
    *   Conecta-se de forma segura à API do HubSpot usando um token de acesso carregado a partir de um arquivo `.env` local.
    *   Implementa uma função de paginação robusta para extrair **todos** os registros dos objetos `Contacts`, `Companies` e `Deals`.
    *   Normaliza a resposta JSON da API em DataFrames do Pandas para fácil manipulação.

2.  **`export_to_duckdb.py` (Data Exporter):**
    *   Recebe os dados do bloco anterior.
    *   Converte os dados (que o Mage passa como listas) de volta para DataFrames do Pandas.
    *   Conecta-se a um arquivo de banco de dados DuckDB local chamado `hubspot_raw.db`.
    *   Usa a instrução `CREATE OR REPLACE TABLE` para carregar os dados, tornando o pipeline **idempotente** (pode ser executado várias vezes sem causar erros ou duplicatas).

O resultado final desta fase é um arquivo `hubspot_raw.db` populado, que representa nossa camada **Bronze** de dados brutos, pronto para a transformação.

### Executando o Pipeline de Extração e Carregamento

1.  Certifique-se de que seu ambiente virtual (`venv`) está ativado e que todas as dependências foram instaladas com `pip install -r requirements.txt`.
2.  Verifique se o arquivo `.env` existe na raiz do projeto (`modern-elt-portfolio/`) e contém seu `HUBSPOT_ACCESS_TOKEN`.
3.  A partir do diretório raiz do projeto (`modern-elt-portfolio`), inicie o servidor do Mage:
    ```bash
    mage start hubspot_elt_project
    ```
4.  Acesse a UI do Mage em `http://localhost:6789`.
5.  Navegue até o pipeline `hubspot_to_duckdb`.
6.  Para garantir que todos os blocos sejam executados sem usar cache, clique na seta (▼) ao lado do botão de execução e selecione **"Run once"**.
7.  Após a execução bem-sucedida, você encontrará o arquivo `hubspot_raw.db` no diretório `hubspot_elt_project/`.

### Desafios e Lições Aprendidas na Fase II

A implementação revelou vários desafios práticos e lições valiosas sobre o framework Mage e a engenharia de dados em geral:

*   **Gerenciamento de Dependências:** Um conflito com a versão `2.0` da biblioteca `NumPy` foi resolvido fixando a versão em `numpy<2.0` no `requirements.txt`, garantindo um ambiente de desenvolvimento estável e reprodutível.
*   **Peculiaridades do Mage:**
    *   **Estrutura de Arquivos:** Descobrimos que os blocos de código de um pipeline precisam ser criados a partir da tela de edição do pipeline para que os arquivos `.py` sejam gerados na pasta correta (`pipelines/pipeline_name/`).
    *   **Importação de Decoradores:** A maneira mais confiável de importar decoradores como `@data_loader` é usando o padrão de verificação `if 'decorator' not in globals(): ...`.
    *   **Transferência de Dados:** O Mage converte DataFrames do Pandas para listas Python ao passá-los entre blocos. A solução foi reconverter a lista de volta para um DataFrame no bloco receptor.
*   **Carregamento de Segredos:** O mecanismo padrão `io_config.yaml` se mostrou instável. A solução mais robusta foi carregar o `.env` manualmente no código usando a biblioteca `python-dotenv`, uma abordagem que é segura e também compatível com ambientes de produção na nuvem.

### Fase III e IV: Transformação, Testes e Modelagem de Negócio (CONCLUÍDO)

Nesta fase crucial, o projeto evolui da simples posse de dados brutos para a criação de **ativos de dados confiáveis e prontos para análise**. Utilizamos o **dbt (data build tool)** para construir uma pipeline de transformação robusta, seguindo as melhores práticas de Engenharia Analítica e adotando uma mentalidade de **Desenvolvimento Orientado a Testes (TDD)** desde o início.

#### Arquitetura da Transformação

O processo de transformação foi dividido em duas camadas lógicas, um padrão da indústria para clareza e manutenibilidade:

1.  **Camada de Staging (Silver):** O primeiro passo da transformação. O objetivo desta camada é criar uma representação 1:1 das fontes de dados, aplicando apenas limpezas básicas e padronizações. Isso isola o resto do nosso projeto da complexidade e inconsistência dos dados de origem. Foram criados os modelos `stg_contacts`, `stg_companies` e `stg_deals`, que realizam tarefas como:
    *   Renomeação de colunas para um padrão `snake_case` limpo (ex: `properties.firstname` -> `first_name`).
    *   Conversão de tipos de dados (casting) para formatos analíticos (ex: `VARCHAR` -> `TIMESTAMP`, `VARCHAR` -> `NUMERIC`).
    *   Seleção apenas das colunas relevantes para a análise.

2.  **Camada de Marts (Gold):** A camada final, onde o valor de negócio é materializado. Os modelos de staging são unidos e agregados para criar tabelas de fatos e dimensões que respondem diretamente às perguntas de negócio. Foi criado o modelo `mart_companies`, que:
    *   Une `stg_companies` e `stg_deals` usando chaves de negócio (`domain`).
    *   Calcula métricas de negócio essenciais por empresa, como:
        *   `total_deals`: Contagem total de atendimentos.
        *   `total_won_deals`: Contagem de negócios ganhos.
        *   `total_revenue`: A soma da receita de negócios ganhos, representando o **Lifetime Value (LTV)**.
        *   `average_deal_value`: O valor médio por negócio ganho.

#### Desenvolvimento Orientado a Testes (TDD)

A qualidade dos dados é a espinha dorsal deste projeto. Em vez de tratar os testes como uma etapa posterior, eles foram desenvolvidos **junto com os modelos**. Uma suíte de **19 testes automatizados** foi implementada usando `dbt` e o pacote `dbt_expectations` para garantir:

*   **Singularidade e Não Nulidade:** As chaves primárias de todos os modelos são garantidamente únicas e não nulas.
*   **Integridade Referencial:** Um teste de `relationships` valida que todo negócio em `stg_deals` (que deveria ter uma empresa) corresponde a uma empresa existente em `stg_companies`, prevenindo "negócios órfãos".
*   **Validade de Formato:** Testes de expressão regular (`regex`) validam o formato de campos como `email`.
*   **Consistência de Negócio:** Testes personalizados garantem que regras de negócio sejam cumpridas, como `total_won_deals <= total_deals`.

Este conjunto de testes é executado a cada `dbt test`, fornecendo um feedback imediato sobre a saúde do pipeline e garantindo que qualquer regressão ou problema de qualidade nos dados de origem seja detectado instantaneamente.

#### Como Executar a Transformação

1.  Certifique-se de que o pipeline do Mage foi executado e o arquivo `hubspot_raw.db` existe.
2.  Navegue até o diretório do projeto dbt:
    ```bash
    cd dbt_hubspot
    ```
3.  Instale os pacotes de teste (só precisa ser feito uma vez):
    ```bash
    dbt deps
    ```
4.  Execute os modelos e os testes. O comando `build` faz isso de forma conveniente:
    ```bash
    dbt build
    ```
    *Este comando irá rodar os modelos e, em seguida, os testes, em uma única execução.*

### Próximos Passos

Com o pipeline de dados local totalmente funcional e testado, o projeto está pronto para a próxima grande fase: **implantação na nuvem e automação**.

*   **Containerização:** "Dockerizar" as aplicações Mage e dbt para criar ambientes portáteis e reprodutíveis.
*   **Infraestrutura como Código (IaC):** Usar **Terraform** para provisionar a infraestrutura necessária na **AWS** (ex: S3 para o Data Lake, ECR para as imagens Docker, ECS Fargate para a execução dos containers).
*   **CI/CD:** Criar um pipeline de Integração e Entrega Contínua (provavelmente com GitHub Actions) para automatizar o teste e o deploy de novas versões do pipeline de dados.

---


