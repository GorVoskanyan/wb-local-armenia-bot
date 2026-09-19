import logging
from typing import Dict, Any
from arq import cron
from arq.connections import RedisSettings
from sqlalchemy import select

from core.config import settings
from core.database import AsyncSessionLocal
from models.seller import Seller
from services.product_service import ProductService

logger = logging.getLogger(__name__)


async def sync_all_sellers_task(ctx: Dict[Any, Any]) -> None:
    """Cron task running hourly to sync all verified sellers' Wildberries inventory."""
    logger.info("Starting scheduled hourly sync for all sellers...")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Seller).where(Seller.is_verified == True))
        sellers = result.scalars().all()
        logger.info(f"Found {len(sellers)} verified sellers for sync.")

        for seller in sellers:
            try:
                count = await ProductService.sync_seller_products(session, seller)
                logger.info(f"Successfully synced {count} products for seller ID {seller.id} (User ID {seller.user_id}).")
            except Exception as e:
                logger.error(f"Error syncing products for seller ID {seller.id}: {e}")

    logger.info("Scheduled hourly sync finished.")


async def sync_single_seller_task(ctx: Dict[Any, Any], seller_id: int) -> int:
    """Task to manually sync a specific seller's inventory on demand."""
    logger.info(f"Triggering manual sync for seller ID {seller_id}...")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Seller).where(Seller.id == seller_id))
        seller = result.scalar_one_or_none()
        if not seller:
            logger.error(f"Seller ID {seller_id} not found.")
            return 0

        count = await ProductService.sync_seller_products(session, seller)
        logger.info(f"Manual sync completed for seller ID {seller_id}: {count} products synced.")
        return count


class WorkerSettings:
    functions = [sync_single_seller_task]
    cron_jobs = [
        cron(sync_all_sellers_task, minute=0)
    ]
    redis_settings = RedisSettings(
        host=settings.redis_host,
        port=settings.redis_port
    )
