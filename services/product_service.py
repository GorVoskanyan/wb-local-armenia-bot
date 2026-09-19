import logging
from typing import List, Optional, Sequence
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserRole
from models.seller import Seller
from models.product import Product
from core.security import encrypt_api_key, decrypt_api_key
from services.wb_api import WildberriesAPIClient

logger = logging.getLogger(__name__)


class ProductService:
    @staticmethod
    async def get_or_create_user(session: AsyncSession, telegram_id: int, default_lang: str = "hy") -> User:
        result = await session.execute(select(User).where(User.id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            user = User(id=telegram_id, role=UserRole.BUYER, language_preference=default_lang)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user

    @staticmethod
    async def update_user_language(session: AsyncSession, telegram_id: int, lang: str) -> None:
        await session.execute(
            update(User).where(User.id == telegram_id).values(language_preference=lang)
        )
        await session.commit()

    @staticmethod
    async def register_seller(session: AsyncSession, telegram_id: int, raw_api_key: str, shop_name: str = "WB Seller") -> Seller:
        user = await ProductService.get_or_create_user(session, telegram_id)
        user.role = UserRole.SELLER

        encrypted_key = encrypt_api_key(raw_api_key)

        result = await session.execute(select(Seller).where(Seller.user_id == telegram_id))
        seller = result.scalar_one_or_none()

        if seller:
            seller.wb_api_key_encrypted = encrypted_key
            seller.shop_name = shop_name
            seller.is_verified = True
        else:
            seller = Seller(
                user_id=user.id,
                wb_api_key_encrypted=encrypted_key,
                shop_name=shop_name,
                is_verified=True
            )
            session.add(seller)

        await session.commit()
        await session.refresh(seller)
        return seller

    @staticmethod
    async def get_seller_by_user_id(session: AsyncSession, telegram_id: int) -> Optional[Seller]:
        result = await session.execute(select(Seller).where(Seller.user_id == telegram_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def sync_seller_products(session: AsyncSession, seller: Seller) -> int:
        """Sync seller products from WB API to Postgres."""
        raw_key = decrypt_api_key(seller.wb_api_key_encrypted)
        client = WildberriesAPIClient(api_key=raw_key)

        cards = await client.fetch_seller_cards()
        stocks = await client.fetch_seller_stocks()
        stock_map = {str(s.get("sku")): s.get("amount", 0) for s in stocks}

        synced_count = 0
        for card in cards:
            nm_id = card.get("nmID")
            if not nm_id:
                continue

            title = card.get("title") or f"WB Product #{nm_id}"
            category = card.get("category") or "General"

            photos = card.get("photos", [])
            image_url = photos[0].get("big") if photos else None

            sizes = card.get("sizes", [])
            price = 0.0
            discount_price = 0.0
            sku_str = str(nm_id)

            if sizes:
                first_size = sizes[0]
                price = float(first_size.get("price", 0))
                discount_price = float(first_size.get("discountedPrice", price))
                skus = first_size.get("skus", [])
                if skus:
                    sku_str = skus[0]

            stock_qty = stock_map.get(sku_str, 10)  # Default stock if not mapped

            # Check if product already exists
            res = await session.execute(select(Product).where(Product.wb_sku_id == nm_id))
            existing_prod = res.scalar_one_or_none()

            if existing_prod:
                existing_prod.title = title
                existing_prod.price = price
                existing_prod.discount_price = discount_price
                existing_prod.category = category
                existing_prod.stock_quantity = stock_qty
                if image_url:
                    existing_prod.image_url = image_url
            else:
                new_prod = Product(
                    wb_sku_id=nm_id,
                    seller_id=seller.id,
                    title=title,
                    price=price,
                    discount_price=discount_price,
                    category=category,
                    stock_quantity=stock_qty,
                    image_url=image_url,
                    is_local_stock=True
                )
                session.add(new_prod)
            synced_count += 1

        await session.commit()
        return synced_count

    @staticmethod
    async def get_categories(session: AsyncSession) -> Sequence[str]:
        result = await session.execute(
            select(Product.category)
            .where(Product.is_local_stock == True)
            .group_by(Product.category)
        )
        return result.scalars().all()

    @staticmethod
    async def get_products_by_category(session: AsyncSession, category: str, limit: int = 10, offset: int = 0) -> Sequence[Product]:
        result = await session.execute(
            select(Product)
            .where(Product.category == category, Product.is_local_stock == True)
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    @staticmethod
    async def get_bargain_deals(session: AsyncSession, limit: int = 10) -> Sequence[Product]:
        """Fetch local products with highest discount percentage."""
        result = await session.execute(
            select(Product)
            .where(Product.is_local_stock == True, Product.price > Product.discount_price)
            .order_by(((Product.price - Product.discount_price) / Product.price).desc())
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_seller_products(session: AsyncSession, seller_id: int) -> Sequence[Product]:
        result = await session.execute(
            select(Product).where(Product.seller_id == seller_id)
        )
        return result.scalars().all()

    @staticmethod
    async def toggle_product_local_stock(session: AsyncSession, product_id: int) -> Optional[bool]:
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if product:
            product.is_local_stock = not product.is_local_stock
            await session.commit()
            return product.is_local_stock
        return None
