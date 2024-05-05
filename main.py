import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (KeyboardButton, Message, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove, BotCommand)
from config import Config, load_config

config: Config = load_config()
BOT_TOKEN: str = config.tg_bot.token

# Создаем объекты бота и диспетчера
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Создаем объекты кнопок
button_1 = KeyboardButton(text='Да')
button_2 = KeyboardButton(text='Нет')
button_3 = KeyboardButton(text='Пришли мне рейтинг учеников')
button_4 = KeyboardButton(text='Сколько отличников?')
button_5 = KeyboardButton(text='Вопросов больше нет')

# Создаем объект клавиатуры, добавляя в него кнопки
keyboard = ReplyKeyboardMarkup(
    keyboard=[[button_1, button_2]],
    resize_keyboard=True
)

# Словарь для хранения результатов анализа файлов
file_results = {}

class FileAnalysisResult:
    def __init__(self, user_id, file_extension):
        self.user_id = user_id
        self.file_extension = file_extension
        self.rating = None
        self.excellent_students_count = None

async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Начать'),
        BotCommand(command='/help',
                   description='Справка по работе бота')]

    await bot.set_my_commands(main_menu_commands)

dp.startup.register(set_main_menu)

@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer('Привет! \nЯ Телеграм-бот, который спрогнозирует оценки за итоговый экзамен. \nЧтобы я мог это сделать, пришли мне Excel-файл c информацией.')

@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(
        'Правила пользования ботом:\nЧтобы начать нажми кнопку /start\nЗатем отправь файл excel или csv боту, он проанализирует его.\nПотом он отправит тебе новый файл со столбцом прогнозируемых оценок и предложит тебе узнать дополнительную информацию.'
    )


@dp.message(F.document)
async def handle_document(message: types.Message):
    document = message.document
    if document.file_name.endswith('.xlsx') or document.file_name.endswith('.xls') or document.file_name.endswith('.csv'):
        file_id = document.file_id
        file_info = await bot.get_file(file_id)
        file_url = file_info.file_path

        file_extension = document.file_name.split('.')[-1]

        file = await bot.download_file(file_url)

        file_results[message.from_user.id] = FileAnalysisResult(message.from_user.id, file_extension)

        await message.answer(f"{file_extension.upper()} файл успешно загружен.")

        # Отправляем дополнительное сообщение и клавиатуру
        additional_message = "Хочешь узнать дополнительную информацию об учениках?"
        keyboard_additional = ReplyKeyboardMarkup(
            keyboard=[
                [button_1, button_2]
            ],
            resize_keyboard=True
        )
        await message.answer(additional_message, reply_markup=keyboard_additional)
    else:
        await message.answer("Пожалуйста, пришлите Excel-файл или CSV-файл.")


@dp.message(F.text == 'Да')
async def process_answer_yes(message: Message):
    keyboard_additional = ReplyKeyboardMarkup(
        keyboard=[
            [button_3, button_4],
            [button_5]
        ],
        resize_keyboard=True
    )
    await message.answer(
        text='Отлично! Тогда выбирай вопрос, который тебя интересует?', reply_markup=keyboard_additional
    )

@dp.message(F.text == 'Нет')
async def process_answer_no(message: Message):
    await message.answer(
        text='Хорошо. Если появились вопросы по работе бота, то нажми на кнопку в меню - Справка по работе бота.',
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(F.text == 'Пришли мне рейтинг учеников')
async def process_answer_raiting(message: Message):
    user_id = message.from_user.id
    result = file_results.get(user_id)
    if result:
        await message.answer("Бот еще в разработке, ответ на ваш вопрос появится позже")
    else:
        await message.answer("Для вашего пользователя нет результатов анализа файла.")

@dp.message(F.text == 'Сколько отличников?')
async def process_answer_raiting(message: Message):
    user_id = message.from_user.id
    result = file_results.get(user_id)
    if result:
        await message.answer("Бот еще в разработке, ответ на ваш вопрос появится позже")
    else:
        await message.answer("Для вашего пользователя нет результатов анализа файла.")


@dp.message(F.text == 'Вопросов больше нет')
async def process_answer_raiting(message: Message):
    await message.answer(
        text='Хорошо. Если появились вопросы по работе бота, то нажми на кнопку в меню - Справка по работе бота.',
        reply_markup=ReplyKeyboardRemove()
    )

if __name__ == '__main__':
    dp.run_polling(bot)