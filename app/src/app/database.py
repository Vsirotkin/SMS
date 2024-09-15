from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Настройки базы данных
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Создание асинхронного движка SQLAlchemy
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True)

# Создание асинхронной сессии
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Базовый класс для моделей
Base = declarative_base()
