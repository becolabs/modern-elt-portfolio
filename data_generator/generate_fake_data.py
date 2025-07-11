import pandas as pd
from faker import Faker
import random
import numpy as np

# --- CONFIGURAÇÃO DA SIMULAÇÃO ---
NUM_DOCTORS = 10  # Um grupo menor e mais realista de médicos
NUM_UNIQUE_PATIENTS = 80 # Número de pacientes distintos
TOTAL_DEALS = 100 # Total de negócios a serem gerados
# Implícito: 20 negócios serão de pacientes recorrentes

# Inicializa o Faker
fake = Faker('pt_BR')

def generate_doctors(num_doctors):
    """Gera dados fictícios para médicos (HubSpot Companies)."""
    specialties = ['Neurologia', 'Cardiologia', 'Clínico Geral', 'Psiquiatria', 'Ortopedia', 'Neuro']
    data = []
    for _ in range(num_doctors):
        name = fake.name_male()
        data.append({
            'name': f"Dr(a). {name}",
            'domain': f"{name.split(' ')[-1].lower().replace('.', '')}.med.br",
            'especialidade_medica': random.choice(specialties)
        })
    return pd.DataFrame(data)

def generate_patients(num_patients):
    """Gera dados fictícios para pacientes (HubSpot Contacts)."""
    data = []
    for _ in range(num_patients):
        first_name = fake.first_name()
        last_name = fake.last_name()
        sanitized_first_name = first_name.lower().replace(' ', '.')
        sanitized_last_name = last_name.lower().replace(' ', '.')
        email = f"{sanitized_first_name}.{sanitized_last_name}@{fake.free_email_domain()}"
        data.append({
            'firstname': first_name,
            'lastname': last_name,
            'email': email
        })
    return pd.DataFrame(data)

def generate_connected_data(num_doctors, num_unique_patients, total_deals):
    """
    Orquestra a geração de dados conectados, garantindo que deals se refiram
    a doctors e patients existentes e simulando recorrência.
    """
    print("1. Gerando Médicos (Companies)...")
    df_doctors = generate_doctors(num_doctors)
    
    print("2. Gerando Pacientes (Contacts)...")
    df_patients = generate_patients(num_unique_patients)

    print("3. Orquestrando Negócios (Deals) com recorrência...")
    
    # --- Lógica de Recorrência ---
    num_recurring_deals = total_deals - num_unique_patients
    
    # Lista de todos os pacientes que terão um deal
    patient_list_for_deals = df_patients['email'].tolist()
    
    # Adiciona pacientes recorrentes escolhendo aleatoriamente da lista existente
    recurring_patients = random.choices(patient_list_for_deals, k=num_recurring_deals)
    patient_list_for_deals.extend(recurring_patients)
    
    # Embaralha a lista final para que os deals recorrentes não fiquem no final
    random.shuffle(patient_list_for_deals)
    
    # --- Geração dos Deals ---
    REAL_DEAL_STAGES = [
        'Compromisso agendado', 'Qualificado para comprar', 'Apresentação agendada',
        'Tomador de decisão envolvido', 'Contrato enviado', 'Negócio fechado', 'Negócio perdido'
    ]
    stage_weights = [20, 18, 15, 12, 10, 8, 17]
    deals_data = []

    # Dicionários para busca rápida em vez de usar .loc em um loop (mais performático)
    patients_dict = df_patients.set_index('email').to_dict('index')
    doctors_list = df_doctors.to_dict('records')

    for patient_email in patient_list_for_deals:
        # Associa um médico aleatório a cada deal
        doctor = random.choice(doctors_list)
        patient_firstname = patients_dict[patient_email]['firstname']
        
        chosen_stage = random.choices(REAL_DEAL_STAGES, weights=stage_weights, k=1)[0]

        deals_data.append({
            'dealname': f"Atendimento - {patient_firstname}",
            'amount': round(random.uniform(100, 800), 2),
            'pipeline': 'Pipeline de vendas',
            'dealstage': chosen_stage,
            # Chaves de associação que serão usadas no mapeamento do HubSpot
            'contact_email': patient_email,
            'associated_company_domain': doctor['domain']
        })
        
    df_deals = pd.DataFrame(deals_data)
    
    return df_doctors, df_patients, df_deals

if __name__ == "__main__":
    print("Iniciando a geração de dados de negócio simulados e conectados...")
    
    df_doctors, df_patients, df_deals = generate_connected_data(
        NUM_DOCTORS, 
        NUM_UNIQUE_PATIENTS, 
        TOTAL_DEALS
    )
    
    # Salva em arquivos CSV prontos para importação
    df_doctors.to_csv('import_companies.csv', index=False)
    df_patients.to_csv('import_contacts.csv', index=False)
    df_deals.to_csv('import_deals.csv', index=False)
    
    print("\n--- Resumo dos Dados Gerados ---")
    print(f"Médicos (Companies): {len(df_doctors)} registros salvos em 'import_companies.csv'")
    print(f"Pacientes (Contacts): {len(df_patients)} registros salvos em 'import_contacts.csv'")
    print(f"Negócios (Deals): {len(df_deals)} registros salvos em 'import_deals.csv'")
    
    num_recurring = len(df_deals) - len(df_deals['contact_email'].unique())
    print(f"\n-> Simulação de Recorrência: {len(df_deals)} deals para {len(df_patients)} pacientes únicos ({num_recurring} deals recorrentes).")
    print("-> Cada deal está conectado a um paciente e a um médico.")
    
    print("\nPróximo passo: Importe os arquivos CSV para o HubSpot na seguinte ordem: 1. companies, 2. contacts, 3. deals.")