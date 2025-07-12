-- models/marts/mart_companies.sql

-- 1. Selecionamos os dados de deals e companies usando a função 'ref'
with companies as (
    select * from {{ ref('stg_companies') }}
),

deals as (
    select * from {{ ref('stg_deals') }}
),

-- 2. Juntamos deals com companies para ter o contexto de cada negócio
company_deals as (
    select
        c.company_id,
        c.company_name,
        c.domain,
        c.especialidade_medica,
        d.deal_id,
        d.deal_stage,
        d.amount
    from companies c
    left join deals d on c.domain = d.company_domain -- Usamos a chave de negócio para o join
),

-- 3. Agregamos as métricas por empresa
final_metrics as (
    select
        company_id,
        company_name,
        domain,
        especialidade_medica,

        -- Contagem total de negócios associados a esta empresa
        count(deal_id) as total_deals,

        -- Contagem de negócios ganhos (onde a receita é real)
        sum(case when deal_stage = 'closedwon' then 1 else 0 end) as total_won_deals,

        -- Receita total (LTV) - somamos apenas o valor dos negócios ganhos
        sum(case when deal_stage = 'closedwon' then amount else 0 end) as total_revenue,

        -- Valor médio por negócio ganho. Usamos NULLIF para evitar divisão por zero.
        avg(case when deal_stage = 'closedwon' then amount else null end) as average_deal_value

    from company_deals
    group by 1, 2, 3, 4 -- Agrupamos por todas as colunas da empresa
)

-- 4. Selecionamos o resultado final
select * from final_metrics