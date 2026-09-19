from datetime import datetime, timezone
import enum
from sqlalchemy import BigInteger, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base


class UserRole(str, enum.Enum):
    BUYER = "buyer"
    SELLER = "seller"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram User ID
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="userrole", values_callable=lambda x: [e.value for e in x]),
        default=UserRole.BUYER,
        nullable=False
    )
    language_preference: Mapped[str] = mapped_column(String(5), default="hy", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    seller: Mapped["Seller"] = relationship("Seller", back_populates="user", uselist=False, cascade="all, delete-orphan")
