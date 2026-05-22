from sqlalchemy.orm import Session
from src.repository.extract_repository import ExtractRepository
from src.dto.analysis_dto import IncomeTaxRowDTO

class AnalysisController:
    def __init__(self, db: Session):
        self.extract_repository = ExtractRepository(db)

    def generate_income_tax_report(self, start_year: int, start_month: int, end_year: int, end_month: int) -> list[IncomeTaxRowDTO]:
        extracts = self.extract_repository.get_by_date_range_with_relations(start_year, start_month, end_year, end_month)
        
        report = []
        
        for extract in extracts:
            contract = extract.contract
            tenant = contract.tenant
            property_obj = contract.property
            real_estate = contract.real_estate
            
            rent = extract.rent_amount or 0.0
            agreement = extract.agreement or 0.0
            iptu = extract.iptu or 0.0
            water = extract.water or 0.0
            
            commission_rate = real_estate.commission if real_estate else 0.0
            
            base_income = rent + agreement
            commission_amount = base_income * commission_rate
            net_income = base_income - commission_amount

            tenat_document_number = tenant.document_number
            doc_type = "CNPJ" if len(tenat_document_number) > 14 else "CPF"
            
            room_info = f" - {contract.room_name}" if contract.room_name else ""

            row = IncomeTaxRowDTO(
                reference_date=f"{extract.month_ref:02d}/{extract.year_ref}",
                tenant_name=tenant.name,
                tenat_document_number=tenat_document_number,
                tenat_document_type=doc_type,
                property_details=f"{property_obj.property_name}-{room_info}",
                rent_amount=rent,
                iptu=iptu,
                water=water,
                agreement=agreement,
                commission_amount=commission_amount,
                net_income=net_income
            )
            report.append(row)
            
        return report