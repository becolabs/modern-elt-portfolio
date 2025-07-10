# --- Importações Padrão ---
import hubspot
import pandas as pd
from hubspot.crm.contacts import ApiException
import os
from dotenv import load_dotenv

# --- Importação Segura de Decoradores Mage ---
# Este padrão é crucial para o Mage reconhecer os decoradores.
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


# --- Função de Paginação Reutilizável ---
def get_all_records(api_client, object_type, properties):
    """
    Busca todos os registros para um determinado tipo de objeto do HubSpot,
    lidando com a paginação automaticamente.
    """
    all_records = []
    after = None
    
    api_map = {
        'contacts': api_client.crm.contacts.basic_api,
        'companies': api_client.crm.companies.basic_api,
        'deals': api_client.crm.deals.basic_api
    }

    if object_type not in api_map:
        raise ValueError(f"Tipo de objeto inválido: {object_type}")

    api_instance = api_map[object_type]

    while True:
        try:
            page = api_instance.get_page(
                limit=100,
                after=after,
                properties=properties,
                archived=False
            )
            
            if page.results:
                all_records.extend(result.to_dict() for result in page.results)

            if page.paging and page.paging.next:
                after = page.paging.next.after
            else:
                break
        except ApiException as e:
            print(f"Exceção ao chamar a API de {object_type}: {e}\n")
            break
            
    return all_records


# --- Ponto de Entrada do Bloco Mage ---
@data_loader
def load_data_from_hubspot(*args, **kwargs):
    """
    Extrai dados do HubSpot. Carrega o token de acesso manualmente do .env
    para contornar problemas com o io_config.yaml.
    """
    # --- NOSSA SOLUÇÃO ROBUSTA ---
    # Carrega as variáveis do arquivo .env para o ambiente do processo.
    load_dotenv()
    # Lê a variável diretamente do ambiente.
    access_token = os.getenv("HUBSPOT_ACCESS_TOKEN")

    # Verificação de segurança para garantir que a chave foi carregada.
    if not access_token:
        raise ValueError("A variável de ambiente HUBSPOT_ACCESS_TOKEN não foi encontrada. Verifique seu arquivo .env.")
    # -----------------------------
    
    client = hubspot.Client.create(access_token=access_token)

    # Define as propriedades a serem extraídas, conforme a Tabela 1 do nosso documento.
    contact_properties = ["email", "firstname", "lastname", "createdate", "lifecyclestage", "hs_object_id"]
    company_properties = ["domain", "name", "createdate", "industry", "hs_object_id"]
    deal_properties = ["dealname", "amount", "closedate", "createdate", "pipeline", "dealstage", "hs_object_id"]

    print("Iniciando extração do HubSpot...")

    contacts_data = get_all_records(client, 'contacts', contact_properties)
    companies_data = get_all_records(client, 'companies', company_properties)
    deals_data = get_all_records(client, 'deals', deal_properties)

    # Converte os resultados em DataFrames do Pandas, achatando a estrutura JSON.
    df_contacts = pd.json_normalize(contacts_data)
    df_companies = pd.json_normalize(companies_data)
    df_deals = pd.json_normalize(deals_data)
    
    print(f"Contatos extraídos: {len(df_contacts)}")
    print(f"Empresas extraídas: {len(df_companies)}")
    print(f"Negócios extraídos: {len(df_deals)}")

    # Retorna um dicionário de DataFrames para o próximo bloco.
    return {
        'contacts': df_contacts,
        'companies': df_companies,
        'deals': df_deals
    }


@test
def test_output(output, *args) -> None:
    """
    Um teste simples para garantir que o output do bloco está correto.
    """
    assert output is not None, 'O output está indefinido.'
    assert 'contacts' in output, "A chave 'contacts' está faltando no output."
    assert 'companies' in output, "A chave 'companies' está faltando no output."
    assert 'deals' in output, "A chave 'deals' está faltando no output."