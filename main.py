import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from core.config import settings
from core.database import AsyncSessionLocal
from handlers import common, buyer, seller

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DbSessionMiddleware:
    """Middleware to inject SQLAlchemy async session into handler context."""
    async def __call__(self, handler, event, data):
        async with AsyncSessionLocal() as session:
            data["session"] = session
            return await handler(event, data)


async def main():
    bot = Bot(token=settings.bot_token)
    redis = Redis.from_url(settings.redis_url)
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)

    # Middleware setup
    db_middleware = DbSessionMiddleware()
    dp.message.middleware(db_middleware)
    dp.callback_query.middleware(db_middleware)

    # Register Routers
    dp.include_router(common.router)
    dp.include_router(buyer.router)
    dp.include_router(seller.router)

    logger.info("Bot started successfully.")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
