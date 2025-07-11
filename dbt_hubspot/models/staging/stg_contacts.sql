-- models/staging/stg_contacts.sql

with source as (

    select * from {{ source('hubspot_raw_data', 'contacts') }}

),

renamed as (

    select
        -- IDs
        id as contact_id,
        
        -- Propriedades do Contato (usando os nomes corretos com aspas duplas)
        "firstname" as first_name,
        "lastname" as last_name,
        "email" as email,
        
        -- Timestamps (convertendo de VARCHAR para TIMESTAMP)
        cast("createdate" as timestamp) as created_at,
        cast("lastmodifieddate" as timestamp) as last_modified_at,
        
        -- Propriedade de negócio importante
        "lifecyclestage" as lifecycle_stage

    from source

)

select * from renamed