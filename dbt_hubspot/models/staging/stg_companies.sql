-- models/staging/stg_companies.sql
with source as (

    select * from {{ source('hubspot_raw_data', 'companies') }}

),

renamed as (

    select
        -- Chave primária da empresa
        id as company_id,

        -- Propriedades da empresa
        "name" as company_name,
        "domain" as domain,
        "especialidade_medica" as especialidade_medica,

        -- Timestamps
        cast("createdate" as timestamp) as created_at,
        cast("hs_lastmodifieddate" as timestamp) as last_modified_at

    from source

)

select * from renamed