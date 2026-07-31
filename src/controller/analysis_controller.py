from sqlalchemy.orm import Session
from src.repository.extract_repository import ExtractRepository
from src.models import ExtractItemModel
from src.dto.analysis_dto import IncomeTaxRowDTO, ExtractItemDTO

class AnalysisController:
    def __init__(self, db: Session):
        self.extract_repository = ExtractRepository(db)

    def generate_income_tax_report(
        self, 
        start_year: int, 
        start_month: int, 
        end_year: int, 
        end_month: int,
        owner_id: int | None = None,
        tax_rate: float | None = None
    ) -> list[IncomeTaxRowDTO]:
        
        effective_tax_rate = tax_rate if tax_rate is not None else 27.5
        
        tax_multiplier = effective_tax_rate / 100.0 if effective_tax_rate > 1 else effective_tax_rate
        display_tax_rate = effective_tax_rate if effective_tax_rate > 1 else effective_tax_rate * 100

        extracts = self.extract_repository.get_by_date_range_with_relations(
            start_year, start_month, end_year, end_month, owner_id
        )
        
        report = []
        
        credit_categories = ["rent", "penalty", "interest", "other_revenues"]
        
        for extract in extracts:
            contract = extract.contract
            tenant = contract.tenant
            property_obj = contract.property
            
            total_credits = 0.0
            total_debits = 0.0
            used_items = []
            
            for item in extract.items:
                category_enum = item.category.enumerator
                amount = abs(item.amount)
                
                if category_enum in credit_categories:
                    total_credits += amount
                    item_type = "credit"
                else:
                    total_debits += amount
                    item_type = "debit"
                    
                used_items.append(ExtractItemDTO(
                    category=category_enum,
                    amount=amount,
                    type=item_type
                ))
            
            net_base = total_credits - total_debits
            calculated_tax = net_base * tax_multiplier if net_base > 0 else 0.0
            calculated_tax = round(calculated_tax,2)

            tenat_document_number = tenant.document_number
            doc_type = "CNPJ" if len(tenat_document_number) > 14 else "CPF"
            room_info = f" - {contract.room_name}" if contract.room_name else ""

            row = IncomeTaxRowDTO(
                reference_date=f"{extract.month_ref:02d}/{extract.year_ref}",
                tenant_name=tenant.name,
                tenat_document_number=tenat_document_number,
                tenat_document_type=doc_type,
                property_details=f"{property_obj.property_name}{room_info}",
                total_credits=total_credits,
                total_debits=total_debits,
                tax_rate_used=display_tax_rate,
                calculated_tax=calculated_tax,
                items=used_items
            )
            report.append(row)
            
        return report