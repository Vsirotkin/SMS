import aiohttp
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .database import SessionLocal
from .models import SMSConfig, TextSMS, SMSBuffer


async def get_db() -> AsyncSession:
    """
    Создает асинхронную сессию с базой данных.
    """
    async with SessionLocal() as session:
        yield session


async def send_sms_main_gateway(url: str, params: dict) -> dict:
    """
    Отправляет СМС через основной шлюз.

    :param url: URL основного шлюза.
    :param params: Параметры запроса.
    :return: Ответ от шлюза в формате JSON.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            print(f"Ошибка при отправке СМС через основной шлюз: {e}")
            return None


async def send_sms_backup_gateway(url: str, params: dict) -> dict:
    """
    Отправляет СМС через резервный шлюз.

    :param url: URL резервного шлюза.
    :param params: Параметры запроса.
    :return: Ответ от шлюза в формате JSON.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            print(f"Ошибка при отправке СМС через резервный шлюз: {e}")
            return None


async def send_sms(recipient: str, text: str, password: str, db: AsyncSession) -> dict:
    """
    Отправляет СМС через основной шлюз, а в случае ошибки — через резервный шлюз.

    :param recipient: Номер получателя.
    :param text: Текст сообщения.
    :param password: Пароль для основного шлюза.
    :param db: Асинхронная сессия с базой данных.
    :return: Ответ от шлюза в формате JSON.
    """
    config = await db.execute(select(SMSConfig).limit(1))
    config = config.scalars().first()
    if not config:
        return {"error": "Конфигурация не найдена"}

    main_gateway_url = config.main_gateway_url
    backup_gateway_url = config.backup_gateway_url
    params = {"recipient": recipient, "text": text, "password": password}

    # Попытка отправить СМС через основной шлюз
    response = await send_sms_main_gateway(main_gateway_url, params)
    if response is not None:
        print("СМС успешно отправлено через основной шлюз")
        return response

    # Если основной шлюз не сработал, переключаемся на резервный
    params["api_id"] = config.backup_gateway_api_id
    response = await send_sms_backup_gateway(backup_gateway_url, params)
    if response is not None:
        print("СМС успешно отправлено через резервный шлюз")
        return response

    print("Не удалось отправить СМС через оба шлюза")
    return None


async def add_text_to_code(text: str, code: str) -> str:
    """
    Добавляет текст к четырехзначному коду.

    :param text: Текст для добавления.
    :param code: Четырехзначный код.
    :return: Обновленный текст сообщения.
    """
    return f"{text} {code}"


async def get_next_text(db: AsyncSession) -> str:
    """
    Получает следующий текст из таблицы textsms по очереди.

    :param db: Асинхронная сессия с базой данных.
    :return: Текст для добавления к сообщению.
    """
    texts = await db.execute(select(TextSMS))
    texts = texts.scalars().all()
    if not texts:
        return ""
    return texts[0].text


async def process_sms_buffer(db: AsyncSession):
    """
    Обрабатывает сообщения из таблицы-буфера с задержкой.

    :param db: Асинхронная сессия с базой данных.
    """
    while True:
        buffer_items = await db.execute(select(SMSBuffer))
        buffer_items = buffer_items.scalars().all()
        if not buffer_items:
            break

        for item in buffer_items:
            text = item.text
            if len(text) == 4:
                text = await add_text_to_code(await get_next_text(db), text)

            response = await send_sms(item.recipient, text, item.password, db)
            if response is not None:
                await db.delete(item)
                await db.commit()

            await asyncio.sleep(10)  # Пауза на каждом номере


async def add_to_buffer(recipient: str, text: str, password: str, db: AsyncSession):
    """
    Добавляет сообщение в таблицу-буфер.

    :param recipient: Номер получателя.
    :param text: Текст сообщения.
    :param password: Пароль для основного шлюза.
    :param db: Асинхронная сессия с базой данных.
    """
    buffer_item = SMSBuffer(recipient=recipient, text=text, password=password)
    db.add(buffer_item)
    await db.commit()
