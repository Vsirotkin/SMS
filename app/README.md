# SMS Service README

## Задание

### Требования:

1. **Реализовать отправку СМС через собственный шлюз в личном кабинете сайта "Мозаики".**
2. **В случае возврата от шлюза любой ошибки переключиться на механизм отправки СМС и звонки через сервис SMS.RU.**
3. **В программе POST-запрос для отправки СМС будет выглядеть примерно так:**
   ```
   http://10.100.1.115:8000/sendsms?recipient=89036003526&text=без автостарта&password=pokachtotakoy
   ```
4. **Предусмотреть возможность хранения параметров для POST-запроса, т.к. в зависимости от региона параметры могут отличаться (в Грузии например).**

### ДОРАБОТКА:

1. **Делать каждое сообщение уникальным. Т.е. добавить к цифровому коду текст, например: "Никому не сообщайте код XXXX".**
2. **Создать в БД таблицу с подобными текстами и при отправке СМС выбирать их по очереди, в цикле. Чем больше будет разнообразного текста, тем лучше. Добявлять текст только к сообщению с четырехзначным кодом.**
3. **Делать паузы при отправке СМС так, чтобы походило на ручной ввод текста: пауза на каждом номере (всего их 4), например 10 секунд.**
4. **Для этого входящую от Ромашек информацию (а также возможную массовую рассылку) записывать в таблицу-буфер и рассылать СМС с задержкой, перебирая исходящие номера (1..4).**
5. **Примеры текста для СМС (табл. textsms):**

   | №  | Текст                        |
   |----|------------------------------|
   | 1  | Никому не сообщайте код      |
   | 2  | Сообщите продавцу код        |
   | 3  | Для вас код                  |
   | 4  | Код для списания бонусов     |
   | 5  | Сообщение от Мозаики         |
   | 6  | Сообщение от Mosaic.         |
   | 7  | Вам пришел код               |
   | 8  | Для вас код списания         |
   | 9  | Примите код списания         |
   | 10 | Для списания бонусов код     |
   | 11 | Сеть Мозаика, код            |
   | 12 | Код списания                 |

## Архитектура и логика реализации

### 1. Архитектура проекта

Проект состоит из следующих компонентов:

- **FastAPI**: Веб-фреймворк для создания API.
- **SQLAlchemy**: ORM для работы с базой данных.
- **PostgreSQL**: База данных для хранения конфигурации и текстов.
- **uvicorn**: Сервер для запуска FastAPI приложения.
- **uv**: Утилита для управления зависимостями.

### 2. Структура проекта

```
project/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   └── sms.py
├── config.json
├── pyproject.toml
└── start.sh
```

### 3. Описание файлов и директорий

- **app/main.py**: Основной файл приложения FastAPI. Содержит эндпоинты для отправки СМС и управления конфигурацией.
- **app/models.py**: Определение моделей SQLAlchemy для работы с базой данных.
- **app/schemas.py**: Определение схем Pydantic для валидации данных.
- **app/database.py**: Настройка подключения к базе данных и создание сессии SQLAlchemy.
- **app/sms.py**: Логика отправки СМС через основной и резервный шлюзы, а также обработка буфера сообщений.
- **config.json**: Файл конфигурации для хранения параметров.
- **pyproject.toml**: Файл для управления зависимостями с помощью `uv`.
- **start.sh**: Скрипт для запуска приложения с использованием `uvicorn`.

### 4. Логика реализации

#### 4.1. Отправка СМС через основной шлюз

1. **POST-запрос**: Приложение принимает POST-запрос с параметрами `recipient`, `text` и `password`.
2. **Основной шлюз**: Приложение пытается отправить СМС через основной шлюз, используя URL и параметры из конфигурации.
3. **Резервный шлюз**: В случае ошибки от основного шлюза, приложение переключается на резервный шлюз SMS.RU.

#### 4.2. Добавление текста к сообщению

1. **Таблица textsms**: В базе данных создается таблица `textsms` для хранения текстов, которые будут добавляться к сообщениям с четырехзначными кодами.
2. **Выбор текста**: При отправке СМС, если текст содержит четырехзначный код, приложение выбирает текст из таблицы `textsms` по очереди и добавляет его к сообщению.

#### 4.3. Паузы при отправке СМС

1. **Таблица-буфер**: Входящие запросы на отправку СМС записываются в таблицу-буфер `sms_buffer`.
2. **Обработка буфера**: Приложение периодически обрабатывает сообщения из буфера, отправляя их с задержкой в 10 секунд между каждым сообщением.

### 5. Установка и запуск

#### 5.1. Установка зависимостей

1. Установите `uv` для управления зависимостями:
   ```bash
   pip install uv
   ```
2. Установите зависимости проекта:
   ```bash
   uv install
   ```

#### 5.2. Запуск приложения

1. Запустите приложение с помощью скрипта `start.sh`:
   ```bash
   ./start.sh
   ```

### 6. Пример использования

#### 6.1. Отправка СМС

Отправьте POST-запрос на эндпоинт `/send_sms/` с телом запроса в формате JSON:

```json
{
    "recipient": "89036003526",
    "text": "1234",
    "password": "pokachtotakoy"
}
```

Приложение добавит текст к сообщению с четырехзначным кодом и отправит его через основной или резервный шлюз.

### 7. Заключение

Проект реализует отправку СМС через основной и резервный шлюзы, добавляет текст к сообщениям с четырехзначными кодами и обеспечивает паузы между отправкой СМС, чтобы имитировать ручной ввод текста. Конфигурация и тексты хранятся в базе данных PostgreSQL, а управление зависимостями осуществляется с помощью `uv`.