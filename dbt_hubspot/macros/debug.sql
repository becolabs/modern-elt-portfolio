{% macro get_column_names(table_name) %}
  {{ log(dbt_utils.get_column_values(table=ref(table_name), column='COLUMN_NAME'), info=True) }}
{% endmacro %}

-- Uma macro mais simples para apenas listar as colunas de uma fonte
{% macro list_source_columns(source_name, table_name) %}
    {% set source_relation = source(source_name, table_name) %}
    {% set columns = adapter.get_columns_in_relation(source_relation) %}
    {% for column in columns %}
        {{ log(column.name, info=True) }}
    {% endfor %}
{% endmacro %}