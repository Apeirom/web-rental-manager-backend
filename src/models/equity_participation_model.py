from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship

from src.constants.property_constants import EQUITY_PARTICIPATION_PERCENTAGE_BASE
from src.models.base import Base


class EquityParticipationModel(Base):
    __tablename__ = "equity_participations"
    __table_args__ = (
        UniqueConstraint("property_id", "owner_id", name="uq_equity_participation_property_owner"),
        CheckConstraint(
            (
                "participation_percentage > 0 AND participation_percentage <= "
                f"{EQUITY_PARTICIPATION_PERCENTAGE_BASE}"
            ),
            name="ck_equity_participation_percentage",
        ),
        Index("ix_equity_participations_owner_id", "owner_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(
        Integer,
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
    )
    owner_id = Column(
        Integer,
        ForeignKey("owners.id", ondelete="CASCADE"),
        nullable=False,
    )
    participation_percentage = Column(Numeric(5, 2), nullable=False)

    property = relationship("PropertyModel", back_populates="equity_participations")
    owner = relationship("OwnerModel", back_populates="equity_participations")
