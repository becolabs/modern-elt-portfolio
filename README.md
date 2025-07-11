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

Excelente ideia. Um bom README é um documento vivo que reflete o estado atual do projeto. Atualizá-lo agora é a atitude correta de um engenheiro que se orgulha do seu trabalho.

Vamos substituir a seção "Próximos Passos" por uma descrição do que **concluímos** e, em seguida, criar uma nova seção "Próximos Passos" para a Fase III. Também adicionaremos uma seção de "Lições Aprendidas", que é extremamente valiosa para um portfólio, pois demonstra sua capacidade de resolver problemas do mundo real.

Aqui está a sugestão de atualização para o seu `README.md`.

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

### Fase III: Transformação e Modelagem (Camada Silver) - `CONCLUÍDO`

Nesta fase, demos vida aos dados brutos, transformando-os em ativos de dados limpos, confiáveis e prontos para análise. Utilizamos o **dbt (data build tool)** para construir nossa camada de transformação, seguindo as melhores práticas de Engenharia Analítica.

#### Arquitetura e Configuração

*   **Inicialização do Projeto dbt:** Um novo projeto dbt (`dbt_hubspot`) foi inicializado na raiz do repositório, mantendo uma clara **separação de preocupações** entre a ferramenta de EL (Mage) e a ferramenta de T (dbt).
*   **Conexão com o Data Lake Local:** O dbt foi configurado para se conectar diretamente ao nosso banco de dados DuckDB (`hubspot_raw.db`), que atua como nosso Data Lake na camada Bronze. A configuração, gerenciada via `profiles.yml`, foi mantida fora do controle de versão para proteger credenciais, enquanto o caminho para o banco de dados foi definido de forma relativa para garantir a portabilidade do projeto.
*   **Ciclo de Desenvolvimento e Depuração:** Foi estabelecido um fluxo de trabalho de desenvolvimento robusto. Um notebook Jupyter (`playground.ipynb`), utilizando o kernel do ambiente virtual do projeto (`venv`), foi configurado para a exploração interativa dos dados. Esse processo se mostrou crucial para:
    *   Inspecionar a estrutura real das tabelas brutas.
    *   Identificar a necessidade de adicionar propriedades personalizadas do HubSpot (`especialidade_medica`) ao pipeline de extração.
    *   Depurar e resolver problemas de concorrência de banco de dados (locks de arquivo) entre o notebook de exploração e os processos de execução (Mage/dbt).

#### Modelagem da Camada de Staging

O coração desta fase foi a criação da camada de *staging*. O objetivo desta camada é criar uma representação 1:1 das fontes de dados brutas, aplicando apenas limpezas básicas e padronizações. Isso isola o resto do nosso projeto da complexidade e inconsistência dos dados de origem.

Foram criados três modelos de staging como `views` no DuckDB:

1.  **`stg_contacts`**:
    *   Renomeia colunas como `properties.firstname` para `first_name`.
    *   Converte (cast) campos de data de `VARCHAR` para `TIMESTAMP`.
    *   Seleciona apenas as colunas relevantes para a análise.

2.  **`stg_companies`**:
    *   Similarmente, renomeia e padroniza colunas.
    *   Inclui a propriedade personalizada `especialidade_medica`, demonstrando a capacidade do pipeline de se adaptar a novos requisitos de negócio.

3.  **`stg_deals`**:
    *   Além da renomeação e casting de datas, converte a coluna `properties.amount` para o tipo `NUMERIC`, habilitando cálculos financeiros precisos nas fases seguintes.

A construção de toda a camada de staging é orquestrada com um único comando, `dbt build --select staging.*`, garantindo que todos os modelos sejam executados e testados de forma coesa.

### Próximos Passos: Fase IV - Modelagem de Data Marts e Testes

Com a camada de staging (Silver) concluída e validada, nosso próximo objetivo é construir a camada de **Marts** (Gold). É aqui que a lógica de negócio será implementada para criar as tabelas de fatos e dimensões que responderão diretamente às nossas perguntas de negócio e servirão de base para o cálculo da métrica LTV:CAC.

*   Desenvolver modelos de marts (tabelas de fatos e dimensões) para criar uma visão de negócio coesa.
*   Implementar testes de dados no dbt (singular, de relacionamento, e personalizados) para garantir a qualidade e a integridade dos nossos modelos.
*   Integrar a execução do dbt como um novo bloco no nosso pipeline do Mage para orquestrar o processo de ponta a ponta.

