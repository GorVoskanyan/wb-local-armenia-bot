import asyncio
import logging
from sqlalchemy import select
from core.database import AsyncSessionLocal, Base, engine
from models.user import User, UserRole
from models.seller import Seller
from models.product import Product
from core.security import encrypt_api_key

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MOCK_SELLERS = [
    {
        "telegram_id": 1001,
        "shop_name": "Yerevan Gourmet & Coffee",
        "api_key": "mock_yerevan_gourmet_key",
        "products": [
            {
                "wb_sku_id": 200001,
                "title": "Armenian Coffee Blend - Traditional Yerevan Roast 500g",
                "price": 5500.0,
                "discount_price": 3800.0,
                "category": "Food & Beverages",
                "stock_quantity": 50,
                "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600",
                "is_local_stock": True
            },
            {
                "wb_sku_id": 200002,
                "title": "Organic Dried Apricots & Nuts Assortment 1kg",
                "price": 8900.0,
                "discount_price": 6200.0,
                "category": "Food & Beverages",
                "stock_quantity": 30,
                "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600",
                "is_local_stock": True
            },
            {
                "wb_sku_id": 200003,
                "title": "Natural Wild Mountain Honey 500g (Lori Region)",
                "price": 6000.0,
                "discount_price": 4500.0,
                "category": "Food & Beverages",
                "stock_quantity": 25,
                "image_url": "https://images.unsplash.com/photo-1587049352847-4a222e784d38?w=600",
                "is_local_stock": True
            }
        ]
    },
    {
        "telegram_id": 1002,
        "shop_name": "Armenian Craft & Ceramics",
        "api_key": "mock_armenian_craft_key",
        "products": [
            {
                "wb_sku_id": 200004,
                "title": "Handcrafted Clay Pomegranate Ornament & Vase",
                "price": 12000.0,
                "discount_price": 7900.0,
                "category": "Home & Decor",
                "stock_quantity": 15,
                "image_url": "https://images.unsplash.com/photo-1578749556568-bc2c40e68b61?w=600",
                "is_local_stock": True
            },
            {
                "wb_sku_id": 200005,
                "title": "Traditional Armenian Pattern Ceramic Tea Cup Set (6 pcs)",
                "price": 18500.0,
                "discount_price": 12500.0,
                "category": "Home & Decor",
                "stock_quantity": 10,
                "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600",
                "is_local_stock": True
            }
        ]
    },
    {
        "telegram_id": 1003,
        "shop_name": "Ararat Fashion & Textiles",
        "api_key": "mock_ararat_fashion_key",
        "products": [
            {
                "wb_sku_id": 200006,
                "title": "100% Organic Cotton T-Shirt with Mount Ararat Print",
                "price": 9500.0,
                "discount_price": 4900.0,
                "category": "Fashion",
                "stock_quantity": 40,
                "image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600",
                "is_local_stock": True
            },
            {
                "wb_sku_id": 200007,
                "title": "Handwoven Traditional Pattern Wool Scarf",
                "price": 14000.0,
                "discount_price": 8900.0,
                "category": "Fashion",
                "stock_quantity": 20,
                "image_url": "https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?w=600",
                "is_local_stock": True
            }
        ]
    }
]


async def seed_database():
    logger.info("Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        logger.info("Seeding mock Armenian Wildberries sellers and products...")
        for seller_info in MOCK_SELLERS:
            # Check if user already exists
            res = await session.execute(select(User).where(User.id == seller_info["telegram_id"]))
            user = res.scalar_one_or_none()

            if not user:
                user = User(
                    id=seller_info["telegram_id"],
                    role=UserRole.SELLER.value,
                    language_preference="hy"
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)

            # Check if seller exists
            res_seller = await session.execute(select(Seller).where(Seller.user_id == user.id))
            seller = res_seller.scalar_one_or_none()

            if not seller:
                seller = Seller(
                    user_id=user.id,
                    wb_api_key_encrypted=encrypt_api_key(seller_info["api_key"]),
                    shop_name=seller_info["shop_name"],
                    is_verified=True
                )
                session.add(seller)
                await session.commit()
                await session.refresh(seller)

            # Add products
            for prod_data in seller_info["products"]:
                res_prod = await session.execute(select(Product).where(Product.wb_sku_id == prod_data["wb_sku_id"]))
                existing_prod = res_prod.scalar_one_or_none()

                if not existing_prod:
                    product = Product(
                        wb_sku_id=prod_data["wb_sku_id"],
                        seller_id=seller.id,
                        title=prod_data["title"],
                        price=prod_data["price"],
                        discount_price=prod_data["discount_price"],
                        category=prod_data["category"],
                        stock_quantity=prod_data["stock_quantity"],
                        image_url=prod_data["image_url"],
                        is_local_stock=prod_data["is_local_stock"]
                    )
                    session.add(product)

        await session.commit()
        logger.info("Database successfully seeded with mock Armenian Wildberries sellers and products!")


if __name__ == "__main__":
    asyncio.run(seed_database())
