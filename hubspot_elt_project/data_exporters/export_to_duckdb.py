# --- Importações Padrão ---
import duckdb
import os
import pandas as pd  # Adicionamos a importação do pandas
from pandas import DataFrame
from mage_ai.data_preparation.repo_manager import get_repo_path

# --- Importação Segura de Decoradores Mage ---
if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data_to_duckdb(data: dict, **kwargs) -> None:
    """
    Exporta um dicionário de dados para tabelas separadas em um banco de dados DuckDB.
    Converte as listas recebidas de volta para DataFrames antes de salvar.
    """
    project_path = get_repo_path()
    db_path = os.path.join(project_path, 'hubspot_raw.db')
    
    print(f"Iniciando exportação de dados para o banco de dados DuckDB em: {db_path}")

    with duckdb.connect(database=db_path, read_only=False) as con:
        for table_name, data_list in data.items():
            
            # --- A CORREÇÃO CRUCIAL ESTÁ AQUI ---
            # Verificamos se recebemos uma lista e se ela não está vazia.
            if isinstance(data_list, list) and data_list:
                # Convertemos a lista de dicionários de volta para um DataFrame.
                df = pd.DataFrame(data_list)
                print(f"Escrevendo tabela: '{table_name}' com {len(df)} linhas...")
                con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
            else:
                # A lógica de ignorar permanece a mesma para dados inválidos.
                print(f"Ignorando '{table_name}', não é uma lista válida ou está vazia.")
    
    print("Exportação para DuckDB concluída com sucesso.")