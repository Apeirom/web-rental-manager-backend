import enum
from src.models.base import Base

class GuaranteeTypeEnum(str, enum.Enum):
    DEPOSIT = "deposit"
    GUARANTOR = "guarantor"
    BAIL_INSURANCE = "bail_insurance"
    BASE = "base"

