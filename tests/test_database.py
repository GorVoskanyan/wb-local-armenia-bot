import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.database import Base
from models.user import User, UserRole
from models.seller import Seller
from models.product import Product
from services.product_service import ProductService
from core.security import encrypt_api_key, decrypt_api_key


@pytest.fixture
async def async_session():
    # Use in-memory SQLite database for async tests
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


def test_api_key_encryption():
    raw_key = "test_wb_api_key_12345"
    encrypted = encrypt_api_key(raw_key)
    assert encrypted != raw_key
    decrypted = decrypt_api_key(encrypted)
    assert decrypted == raw_key


@pytest.mark.asyncio
async def test_user_creation_and_language_update(async_session: AsyncSession):
    telegram_id = 99887766
    user = await ProductService.get_or_create_user(async_session, telegram_id, default_lang="hy")
    assert user.id == telegram_id
    assert user.language_preference == "hy"
    assert user.role == UserRole.BUYER

    await ProductService.update_user_language(async_session, telegram_id, "ru")
    updated_user = await ProductService.get_or_create_user(async_session, telegram_id)
    assert updated_user.language_preference == "ru"


@pytest.mark.asyncio
async def test_seller_registration_and_sync(async_session: AsyncSession):
    telegram_id = 11223344
    seller = await ProductService.register_seller(
        async_session,
        telegram_id=telegram_id,
        raw_api_key="mock_key_test",
        shop_name="Armenian Coffee Shop"
    )
    assert seller.user_id == telegram_id
    assert seller.is_verified is True

    synced_count = await ProductService.sync_seller_products(async_session, seller)
    assert synced_count > 0

    products = await ProductService.get_seller_products(async_session, seller.id)
    assert len(products) == synced_count

    categories = await ProductService.get_categories(async_session)
    assert len(categories) > 0


@pytest.mark.asyncio
async def test_product_toggle_local_stock(async_session: AsyncSession):
    telegram_id = 55667788
    seller = await ProductService.register_seller(
        async_session,
        telegram_id=telegram_id,
        raw_api_key="mock_key_test",
        shop_name="Test Shop"
    )
    await ProductService.sync_seller_products(async_session, seller)
    products = await ProductService.get_seller_products(async_session, seller.id)
    first_prod = products[0]

    initial_status = first_prod.is_local_stock
    new_status = await ProductService.toggle_product_local_stock(async_session, first_prod.id)
    assert new_status == (not initial_status)
