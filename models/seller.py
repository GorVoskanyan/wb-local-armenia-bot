from sqlalchemy import BigInteger, String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base


class Seller(Base):
    __tablename__ = "sellers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    wb_api_key_encrypted: Mapped[str] = mapped_column(String(1000), nullable=False)
    shop_name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="seller")
    products: Mapped[list["Product"]] = relationship("Product", back_populates="seller", cascade="all, delete-orphan")
