from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from logic import main


available_answers = ["да", "нет"]
available_periods = ["менее 1 года", "1-3 года", "более 3х лет"]


class QuestionAnswer(StatesGroup):
    waiting_for_first_answer = State()
    waiting_for_sum = State()
    waiting_for_period = State()


async def start_command(message: types.Message, state: FSMContext):

    """Обработка команды старт

    :param message: Сообщение пользователя.
    :param state: Состояние пользователя.
    :return: None
    """

    await state.finish()
    await message.answer(f"""
Привет, {message.from_user.first_name}! Я твой карманный инвестиционный помощник.
Я помогу тебе составить эффективный устойчивый инвестиционный портфель!
""")
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = KeyboardButton("Да")
    button_2 = KeyboardButton("Нет")
    kb.add(button_1).insert(button_2)

    await state.set_state(QuestionAnswer.waiting_for_first_answer.state)

    await message.answer(text="Начнем?", reply_markup=kb)


async def user_start_answer(message: types.Message, state: FSMContext):

    """Обработка ответа на первый вопрос.

    :param message: Сообщение пользователя.
    :param state: Состояние пользователя.
    :return: None
    """

    if message.text.lower() not in available_answers:
        await message.answer("Пожалуйста, выберите ответ, используя клавиатуру ниже.")
        return

    if message.text == "Да":
        await message.answer(text="Погнали!",
                             reply_markup=ReplyKeyboardRemove())

        await message.answer(text="Для начала введите сумму инвестирования в долларах 💵\n"
                                  "Минимальная сумма инвестирования 1000 долларов.")

        await state.set_state(QuestionAnswer.waiting_for_sum.state)

    elif message.text == "Нет":
        await message.answer(text="Хорошо! Отправь любое сообщение, когда буду нужен.",
                             reply_markup=ReplyKeyboardRemove())
        await state.finish()


async def choose_sum(message: types.Message, state: FSMContext):

    """Обработка ответа на вопрос выбора суммы инвестирования.

    :param message: Сообщение пользователя.
    :param state: Состояние пользователя.
    :return: None
    """

    try:
        invest_sum = int(message.text)
        if invest_sum < 1000:
            await message.answer("Сумма инвестирования слишком маленькая. Введите сумму больше 1000 долларов.")
            return
        else:
            await state.update_data(chosen_sum=invest_sum)

            kb = ReplyKeyboardMarkup(resize_keyboard=True)
            button_1 = KeyboardButton("менее 1 года")
            button_2 = KeyboardButton("1-3 года")
            button_3 = KeyboardButton("более 3х лет")
            kb.add(button_1).insert(button_2).insert(button_3)

            await message.answer("Теперь выберите срок инвестирования с помощью кнопок внизу.",
                                 reply_markup=kb)
            await state.set_state(QuestionAnswer.waiting_for_period.state)

    except ValueError:
        await message.answer("Некорректный ввод. Попробуйте еще раз.")
        return


async def choose_period(message: types.Message, state: FSMContext):

    """Обработка ответа на вопрос выбора периода инвестирования.

    :param message: Сообщение пользователя.
    :param state: Состояние пользователя.
    :return: None
    """

    if message.text not in available_periods:
        await message.answer("Пожалуйста, выберите ответ, используя клавиатуру ниже.")
        return

    await state.update_data(chosen_period=message.text)
    user_data = await state.get_data()
    await message.answer(f"Ваша сумма инвестирования: {user_data['chosen_sum']}.\n"
                         f"Период инвестирования: {user_data['chosen_period']}",
                         reply_markup=ReplyKeyboardRemove())
    await message.answer("Формируем портфель...")

    portfolio_text = main(int(user_data['chosen_sum']), user_data['chosen_period'])

    await message.answer(portfolio_text, parse_mode="HTML")
    await state.finish()


def register_handlers(dp: Dispatcher):

    """Добавление хэндлеров в бот.

    :param dp: Диспатчер.
    :return: None
    """

    dp.register_message_handler(start_command, commands="start", state="*")
    dp.register_message_handler(user_start_answer, state=QuestionAnswer.waiting_for_first_answer)
    dp.register_message_handler(choose_sum, state=QuestionAnswer.waiting_for_sum)
    dp.register_message_handler(choose_period, state=QuestionAnswer.waiting_for_period)
