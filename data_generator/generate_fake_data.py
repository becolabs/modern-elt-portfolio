import pandas as pd
from faker import Faker
import random
import numpy as np

# --- CONFIGURAÇÃO ---
NUM_DOCTORS = 20
NUM_PATIENTS = 50
NUM_DEALS = 100
DUPLICATE_PATIENTS_COUNT = 3
PATIENTS_WITH_MISSING_LASTNAME = 5
DEALS_WITHOUT_DOCTOR = 10

# Inicializa o Faker
fake = Faker('pt_BR')

def generate_doctors(num_doctors):
    """Gera dados fictícios para médicos (HubSpot Companies)."""
    specialties = ['Neurologia', 'Cardiologia', 'Clínico Geral', 'Psiquiatria', 'Ortopedia', 'Neuro'] # 'Neuro' é um erro proposital
    data = []
    for _ in range(num_doctors):
        name = fake.name_male()
        # Erro Proposital 1: Formatação inconsistente na especialidade
        industry = random.choice(specialties) if random.random() > 0.1 else 'Cardiologia'
        
        data.append({
            'name': f"Dr(a). {name}",
            'domain': f"{name.split(' ')[-1].lower()}.med.br",
            'especialidade_medica': industry
        })
    
    # Erro Proposital 2: Duplicata de Médico
    if num_doctors > 0:
        data.append(data[0])

    return pd.DataFrame(data)

def generate_patients(num_patients):
    """Gera dados fictícios para pacientes (HubSpot Contacts)."""
    data = []
    for i in range(num_patients):
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        # Erro Proposital 3: Dados Faltando (sobrenome)
        if i < PATIENTS_WITH_MISSING_LASTNAME:
            last_name = None
            
        sanitized_first_name = first_name.lower().replace(' ', '.')

        # 2. Constrói o email de forma segura, tratando o caso de sobrenome nulo.
        if last_name:
            # Sanitiza o sobrenome da mesma forma.
            sanitized_last_name = last_name.lower().replace(' ', '.')
            email = f"{sanitized_first_name}.{sanitized_last_name}@{fake.free_email_domain()}"
        else:
            # Se não há sobrenome, usa apenas o primeiro nome sanitizado.
            # O email será válido. Ex: "marcos.vinicius@domain.com"
            email = f"{sanitized_first_name}@{fake.free_email_domain()}"
        # --- FIM DA CORREÇÃO ---

        data.append({
            'firstname': first_name,
            'lastname': last_name,
            'email': email
        })
        
    # Erro Proposital 4: Duplicatas de Pacientes
    for i in range(DUPLICATE_PATIENTS_COUNT):
        if data:
            data.append(data[i])
            
    return pd.DataFrame(data)

def generate_deals(num_deals, df_doctors, df_patients):
    """
    Gera dados fictícios para negócios (HubSpot Deals), usando as etapas reais do funil
    e simulando uma distribuição de funil mais realista.
    """
    # --- MUDANÇA PRINCIPAL AQUI ---
    # Usando as etapas reais extraídas da interface do HubSpot
    REAL_DEAL_STAGES = [
        'Compromisso agendado',
        'Qualificado para comprar',
        'Apresentação agendada',
        'Tomador de decisão envolvido',
        'Contrato enviado',
        'Negócio fechado',
        'Negócio perdido'
    ]

    # Simula um funil: mais negócios no topo, menos no fundo.
    # Os pesos não precisam somar 1. Eles são relativos.
    stage_weights = [20, 18, 15, 12, 10, 8, 17] # Mais peso no início e em "perdido"

    data = []

    if df_patients.empty or df_doctors.empty:
        return pd.DataFrame()

    for i in range(num_deals):
        patient = df_patients.sample(1).iloc[0]
        doctor = df_doctors.sample(1).iloc[0]

        company_domain = doctor['domain'] if i >= DEALS_WITHOUT_DOCTOR else None

        # Usa random.choices para selecionar uma etapa com base nos pesos definidos
        chosen_stage = random.choices(REAL_DEAL_STAGES, weights=stage_weights, k=1)[0]

        data.append({
            'dealname': f"Atendimento - {patient['firstname']}",
            'amount': round(random.uniform(100, 800), 2),
            'pipeline': 'Pipeline de vendas',
            'dealstage': chosen_stage, # <-- Usando a etapa real do funil
            'contact_email': patient['email'],
            'company_domain': company_domain
        })

    return pd.DataFrame(data)

if __name__ == "__main__":
    print("Gerando dados fictícios...")
    
    df_doctors = generate_doctors(NUM_DOCTORS)
    df_patients = generate_patients(NUM_PATIENTS)
    df_deals = generate_deals(NUM_DEALS, df_doctors, df_patients)
    
    # Salva em arquivos CSV prontos para importação
    df_doctors.to_csv('import_companies.csv', index=False)
    df_patients.to_csv('import_contacts.csv', index=False)
    df_deals.to_csv('import_deals.csv', index=False)
    
    print("\n--- Resumo dos Dados Gerados ---")
    print(f"Médicos (Companies): {len(df_doctors)} registros salvos em 'import_companies.csv'")
    print(f"Pacientes (Contacts): {len(df_patients)} registros salvos em 'import_contacts.csv'")
    print(f"Negócios (Deals): {len(df_deals)} registros salvos em 'import_deals.csv'")
    
    print("\n--- Problemas de Qualidade Injetados ---")
    print(f"-> {len(df_doctors[df_doctors.duplicated()])} Médico(s) duplicado(s).")
    print(f"-> Formatos de especialidade inconsistentes (ex: 'Neurologia' vs 'Neuro').")
    print(f"-> {DUPLICATE_PATIENTS_COUNT} Paciente(s) duplicado(s).")
    print(f"-> {PATIENTS_WITH_MISSING_LASTNAME} Paciente(s) com sobrenome faltando.")
    print(f"-> {DEALS_WITHOUT_DOCTOR} Negócio(s) sem médico associado.")
    
    print("\nPróximo passo: Importe os arquivos CSV para o HubSpot na seguinte ordem: 1. companies, 2. contacts, 3. deals.")