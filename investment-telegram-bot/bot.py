import asyncio
from config import TOKEN_API
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from questions_handler import register_handlers


async def main():

    """Создание бота

    :return: None
    """

    bot = Bot(token=TOKEN_API)
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_handlers(dp)

    await dp.skip_updates()
    await dp.start_polling()
    print('Бот запущен')


if __name__ == '__main__':
    asyncio.run(main())
