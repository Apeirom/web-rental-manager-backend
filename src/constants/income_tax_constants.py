from decimal import Decimal

INCOME_TAX_DEFAULT_PERIOD_DAYS = 90
INCOME_TAX_INCOME_CODE = "R01.003.001"
INCOME_TAX_INCOME_CATEGORIES = frozenset({"rent", "interest", "penalty"})
INCOME_TAX_DEDUCTION_CATEGORIES = frozenset({"administration_fee"})
INCOME_TAX_CENT = Decimal("0.01")
