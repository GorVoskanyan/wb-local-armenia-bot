from sqlalchemy import BigInteger, String, Numeric, Integer, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    wb_sku_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    seller_id: Mapped[int] = mapped_column(Integer, ForeignKey("sellers.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(255), default="General", nullable=False, index=True)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    image_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    is_local_stock: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    seller: Mapped["Seller"] = relationship("Seller", back_populates="products")

    __table_args__ = (
        Index("idx_category_local", "category", "is_local_stock"),
    )
