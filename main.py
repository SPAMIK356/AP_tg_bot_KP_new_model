import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import find_dotenv, load_dotenv
from common.db import init_db
from handlers.user_private import user_private_router, send_reminders
from common.bot_cmds_list import private

# Завантаження змінних середовища
load_dotenv(find_dotenv())

ALLOWED_UPDATES = ['message', 'edited_message', 'callback_query']

# Отримання токенів
bot_token = os.getenv("TOKEN")

# Перевірка токена бота
if not bot_token:
    exit("Помилка: Не знайдено змінну середовища TOKEN")

# Ініціалізація бота та диспетчера
bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Підключаємо обробник команд з handlers
dp.include_router(user_private_router)

async def main():
    init_db() # Ініціалізуємо базу даних
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await bot.get_me() # Перевірка зв'язку
        await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
        print("Бот готовий до роботи...")
    except Exception as e:
        print(f"Помилка підключення до Telegram або встановлення команд: {e}")
        return

    # Запускаємо фоновий процес нагадувань
    reminder_task = asyncio.create_task(send_reminders(bot))

    # Запускаємо бота
    try:
        await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)
    except Exception as e:
        print(f"Критична помилка під час роботи бота: {e}")
    finally:
        print("Зупинка бота...")
        try:
            if reminder_task and not reminder_task.done():
                 reminder_task.cancel()
                 await asyncio.sleep(0.1)
        except asyncio.CancelledError:
             print("Фонову задачу нагадувань успішно скасовано.")
        except Exception as e:
             print(f"Помилка при зупинці фонової задачі: {e}")

        await bot.session.close() # Коректно закриваємо сесію бота
        print("Бот зупинено.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Роботу бота примусово зупинено.")
    except Exception as e:
        print(f"Непередбачена помилка на верхньому рівні: {e}")