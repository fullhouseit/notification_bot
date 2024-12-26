import asyncio
from aiogram import F, Bot, Dispatcher, types, Router
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message,
)
from aiogram.filters.command import Command
import aiohttp
from settings import SETTINGS

TOKEN = SETTINGS.BOT_TOKEN.get_secret_value()
APP_TOKEN = SETTINGS.APP_TOKEN.get_secret_value()
BACKEND_URL = SETTINGS.URL.get_secret_value()

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()


def get_action_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подробнее", callback_data="action_more")],
            [InlineKeyboardButton(text="Принять", callback_data="action_accept")],
            [InlineKeyboardButton(text="Отклонить", callback_data="action_reject")],
        ]
    )


@router.message(Command("start"))
async def handle_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    deep_link = None

    if len(message.text.split()) > 1:
        deep_link = message.text.split(maxsplit=1)[1]

    payload = {
        "app_token": APP_TOKEN,
        "tgid": user_id,
        "username": username,
    }
    if deep_link:
        payload["linky_token"] = deep_link

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(BACKEND_URL, json=payload) as response:
                if response.status == 200 or response.status == 201:
                    await message.answer(
                        "Добро пожаловать! Вы успешно зарегистрированы.",
                        reply_markup=get_action_keyboard(),
                    )
                else:
                    await message.answer(
                        f"Ошибка при регистрации. Код ответа: {response.status}"
                    )
        except Exception as e:
            await message.answer(f"Не удалось подключиться к серверу: {e}")


@router.callback_query(F.data == "action_more")
async def handle_more(callback_query: CallbackQuery):
    await callback_query.message.answer(
        "Здесь будет информация о выбранном предложении."
    )
    await callback_query.answer()


@router.callback_query(F.data == "action_accept")
async def handle_accept(callback_query: CallbackQuery):
    await callback_query.message.answer("Ваш выбор принят. Спасибо!")
    await callback_query.answer("Вы приняли предложение.")


@router.callback_query(F.data == "action_reject")
async def handle_reject(callback_query: CallbackQuery):
    await callback_query.message.answer("Вы отклонили предложение. Спасибо за ответ.")
    await callback_query.answer("Вы отклонили предложение.")


@router.message()
async def handle_random_message(message: Message):
    await message.answer(
        "Если у вас есть запрос к поддержке, напишите в @bloggery_support_bot"
    )


dp.include_router(router)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
