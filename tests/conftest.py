import os

# Set dummy environment variables for testing if not set
os.environ.setdefault("BOT_TOKEN", "123456:test_token")
os.environ.setdefault("ENCRYPTION_KEY", "dGhpcy1pcy1hLW1vY2stMzItYnl0ZS1mZXJuZXQta2V5PQ==")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
