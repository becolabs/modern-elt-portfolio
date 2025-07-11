-- models/staging/stg_deals.sql
with source as (

    -- Usamos a macro 'source' para referenciar a tabela bruta carregada pelo Mage
    select * from {{ source('hubspot_raw_data', 'deals') }}

),

renamed as (

    select
        -- Chave primária do negócio
        id as deal_id,

        -- Chaves de negócio que usaremos para fazer os joins na camada de 'marts'
        "company_domain",
        "contact_email",

        -- Propriedades do negócio
        "dealname" as deal_name,
        "dealstage" as deal_stage,
        "pipeline",

        -- Convertemos o valor para um tipo numérico para permitir cálculos.
        -- try_cast é mais seguro pois retorna NULL se a conversão falhar.
        try_cast("amount" as numeric(18, 2)) as amount,

        -- Convertemos as datas para timestamps para análises temporais
        cast("createdate" as timestamp) as created_at,
        cast("closedate" as timestamp) as closed_at,
        cast("hs_lastmodifieddate" as timestamp) as last_modified_at

    from source

)

select * from renamed