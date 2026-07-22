from sqlalchemy.orm import Session
from sqlalchemy import text
from src.database.config import SessionLocal

from src.models import ContractModel
from src.repository.guarantee_repository import GuaranteeRepository
from src.repository.contract_repository import ContractRepository

def run_migration():
    db: Session = SessionLocal()
    
    # Instanciamos os novos repositórios que você acabou de criar
    guarantee_repo = GuaranteeRepository(db)
    contract_repo = ContractRepository(db)
    
    try:
        print("Iniciando migração de dados via Repositories...")

        # ==========================================
        # 1. MIGRAÇÃO DAS CALÇÕES DOS CONTRATOS
        # ==========================================
        # Como o ContractModel ainda tem a coluna rental_deposit no código
        # (antes de você removê-la definitivamente), podemos ler via ORM.
        contracts = db.query(ContractModel).filter(ContractModel.rental_deposit > 0).all()
        
        for contract in contracts:
            # 1.1 - Usa o repositório para criar a Calção nova
            new_deposit = guarantee_repo.create_deposit(
                amount=contract.rental_deposit,
                paid_in_cash=False,
                deposit_date=None
            )
            
            # 1.2 - Vincula ao contrato existente
            contract.guarantee = new_deposit
            print(f"Contrato {contract.key}: Calção de {contract.rental_deposit} criada via Repository.")

        # ==========================================
        # 2. MIGRAÇÃO DOS FIADORES
        # ==========================================
        # Lemos os dados brutos da tabela antiga para não confundir o ORM
        # ATENÇÃO: Substitua "guarantors_old" pelo nome da sua tabela antiga no banco de dados
        old_guarantors = db.execute(text("SELECT key, name, document_number FROM guarantors_old")).fetchall()
        
        for old_g in old_guarantors:
            # 2.1 - Usa o repositório para criar na estrutura nova
            new_guarantor = guarantee_repo.create_guarantor(
                name=old_g.name,
                document_number=old_g.document_number
            )
            
            # 2.2 - IMPORTANTE: Sobrescrevemos a chave UUID que o repositório gerou 
            # com a chave antiga, para não quebrar links que o Frontend já tenha salvos.
            new_guarantor.key = old_g.key
            print(f"Fiador {old_g.name} migrado para a nova estrutura.")

        # ==========================================
        # 3. MIGRAÇÃO DOS SEGUROS FIANÇA
        # ==========================================
        # ATENÇÃO: Substitua "bail_insurances_old" pelo nome correto da tabela
        old_insurances = db.execute(text("SELECT key, value, validity, insurance_company FROM bail_insurances_old")).fetchall()
        
        for old_i in old_insurances:
            # 3.1 - Usa o repositório para criar na estrutura nova
            new_insurance = guarantee_repo.create_bail_insurance(
                value=old_i.value,
                validity=old_i.validity,
                insurance_company=old_i.insurance_company
            )
            
            # 3.2 - Mantém a chave UUID antiga
            new_insurance.key = old_i.key
            print(f"Seguro {old_i.insurance_company} migrado para a nova estrutura.")

        # Efetiva todas as operações de uma vez!
        db.commit()
        print("\n✅ Migração concluída com sucesso usando os Repositórios!")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro durante a migração. O banco foi revertido. Erro: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()