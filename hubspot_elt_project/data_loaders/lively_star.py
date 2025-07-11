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

# --- Função para extrair as propriedades do dicionario gerado na api do hubspot
def flatten_records(records):
    """
    Recebe uma lista de objetos SimplePublicObject do HubSpot e a achata
    para uma lista de dicionários planos.
    """
    if not records:
        return []
        
    flat_list = []
    for record in records: # 'record' aqui é um objeto, não um dicionário
        # Começamos com uma cópia do dicionário de propriedades do objeto
        flat_record = record.properties.copy()
        
        # Adicionamos os atributos do nível superior do objeto
        flat_record['id'] = record.id
        flat_record['created_at'] = record.created_at
        flat_record['updated_at'] = record.updated_at
        flat_record['archived'] = record.archived
        
        # Verificamos se o objeto tem associações e as processamos
        if hasattr(record, 'associations') and record.associations:
            # Acessamos as associações como atributos do objeto
            associations = record.associations
            if 'companies' in associations:
                # Acessamos a lista de resultados e pegamos a ID do primeiro
                if associations['companies'].results:
                    flat_record['associated_company_id'] = associations['companies'].results[0].id
            if 'contacts' in associations:
                if associations['contacts'].results:
                    flat_record['associated_contact_id'] = associations['contacts'].results[0].id

        flat_list.append(flat_record)
        
    return flat_list


# --- Função de Paginação Reutilizável ---
def get_all_records(client, object_type, properties, associations=None):
    """
    Busca todos os registros de um objeto do HubSpot, com suporte opcional para associações.
    """
    records = []
    after = None
    
    while True:
        try:
            # --- MUDANÇA PRINCIPAL AQUI ---
            # Agora, a função pode lidar com 'properties' e 'associations'.
            if associations:
                page = client.crm.objects.basic_api.get_page(
                    object_type,
                    limit=100,
                    after=after,
                    properties=properties,
                    associations=associations  # Passa o parâmetro de associações
                )
            else:
                page = client.crm.objects.basic_api.get_page(
                    object_type,
                    limit=100,
                    after=after,
                    properties=properties
                )
            
            records.extend(page.results)
            
            if page.paging and page.paging.next:
                after = page.paging.next.after
            else:
                break
        except Exception as e:
            print(f"Erro ao buscar dados para {object_type}: {e}")
            break
            
    
    
    return records


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
    # Substitua as listas de propriedades antigas por estas:
    contact_properties = [
        "email", 
        "firstname", 
        "lastname", 
        "createdate", 
        "lifecyclestage", 
        "lastmodifieddate"
    ]

    company_properties = [
        "domain", 
        "name", 
        "createdate", 
        "especialidade_medica", 
        "hs_lastmodifieddate"
    ]

    deal_properties = [
        "dealname", 
        "amount", 
        "closedate", 
        "createdate", 
        "pipeline", 
        "dealstage", 
        "hs_lastmodifieddate",
        "company_domain",
        "contact_email"
    ]

    print("Iniciando extração do HubSpot...")

    # 1. Extrair os dados brutos
    raw_contacts = get_all_records(client, 'contacts', contact_properties)
    raw_companies = get_all_records(client, 'companies', company_properties)
    raw_deals = get_all_records(client, 'deals', deal_properties, associations=['company', 'contact'])

    print(f"Contatos extraídos: {len(raw_contacts)}")
    print(f"Empresas extraídas: {len(raw_companies)}")
    print(f"Negócios extraídos: {len(raw_deals)}")

    

    # 2. Achatar os dados usando nossa nova função
    contacts_data = flatten_records(raw_contacts)
    companies_data = flatten_records(raw_companies)
    deals_data = flatten_records(raw_deals)

    # 3. Criar o dicionário de DataFrames para o Mage
    # Agora o Pandas receberá uma lista de dicionários planos e funcionará perfeitamente.
    data = {
        'contacts': pd.DataFrame(contacts_data),
        'companies': pd.DataFrame(companies_data),
        'deals': pd.DataFrame(deals_data)
    }

    # Retorna um dicionário de DataFrames para o próximo bloco.
    return data


@test
def test_output(output, *args) -> None:
    """
    Um teste simples para garantir que o output do bloco está correto.
    """
    assert output is not None, 'O output está indefinido.'
    assert 'contacts' in output, "A chave 'contacts' está faltando no output."
    assert 'companies' in output, "A chave 'companies' está faltando no output."
    assert 'deals' in output, "A chave 'deals' está faltando no output."