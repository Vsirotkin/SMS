from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas, sms
from .database import engine, Base, SessionLocal  # Добавляем импорт SessionLocal
import uvicorn  # Добавляем импорт uvicorn


# Создание таблиц в базе данных
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Заполнение таблицы textsms захардкоженными текстами
async def seed_textsms(db: AsyncSession):
    texts = [
        "Никому не сообщайте код",
        "Сообщите продавцу код",
        "Для вас код",
        "Код для списания бонусов",
        "Сообщение от Мозаики",
        "Сообщение от Mosaic.",
        "Вам пришел код",
        "Для вас код списания",
        "Примите код списания",
        "Для списания бонусов код",
        "Сеть Мозаика, код",
        "Код списания",
    ]
    for text in texts:
        db_text_sms = models.TextSMS(text=text)
        db.add(db_text_sms)
    await db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Логика запуска
    await create_tables()
    async with SessionLocal() as db:
        await seed_textsms(db)
    yield
    # Логика завершения
    # await engine.dispose()  # Закрытие соединения с базой данных


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the SMS service!"}


@app.post("/send_sms/", response_model=dict)
async def send_sms_endpoint(
    sms_request: schemas.SMSRequest, db: AsyncSession = Depends(sms.get_db)
):
    """
    Эндпоинт для отправки СМС.

    :param sms_request: Запрос на отправку СМС.
    :param db: Асинхронная сессия с базой данных.
    :return: Ответ от шлюза в формате JSON.
    """
    await sms.add_to_buffer(
        sms_request.recipient, sms_request.text, sms_request.password, db
    )
    asyncio.create_task(sms.process_sms_buffer(db))
    return {"message": "Сообщение добавлено в буфер и будет отправлено с задержкой"}


@app.post("/config/", response_model=schemas.SMSConfig)
async def create_config(
    config: schemas.SMSConfigCreate, db: AsyncSession = Depends(sms.get_db)
):
    """
    Эндпоинт для создания конфигурации SMS.

    :param config: Конфигурация SMS.
    :param db: Асинхронная сессия с базой данных.
    :return: Созданная конфигурация в формате JSON.
    """
    db_config = models.SMSConfig(**config.dict())
    db.add(db_config)
    await db.commit()
    await db.refresh(db_config)
    return db_config


@app.post("/textsms/", response_model=schemas.TextSMS)
async def create_text_sms(
    text_sms: schemas.TextSMSCreate, db: AsyncSession = Depends(sms.get_db)
):
    """
    Эндпоинт для создания текста для СМС.

    :param text_sms: Текст для СМС.
    :param db: Асинхронная сессия с базой данных.
    :return: Созданный текст в формате JSON.
    """
    db_text_sms = models.TextSMS(**text_sms.dict())
    db.add(db_text_sms)
    await db.commit()
    await db.refresh(db_text_sms)
    return db_text_sms


def main():
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
