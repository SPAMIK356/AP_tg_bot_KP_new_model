from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_keyboard(
        *btns: str,                  # Приймає будь-яку кількість назв кнопок
        placeholder: str = None,     # Текст-підказка у полі вводу
        sizes: tuple[int] = (2,),    # Як розміщувати кнопки по рядках (за замовчуванням по 2)
):
    '''
    Створює та повертає ReplyKeyboardMarkup.
    :param btns: Назви кнопок, перелічені через кому.
    :param placeholder: Текст, що буде відображатись у полі вводу повідомлення.
    :param sizes: Кортеж цілих чисел, що вказує, скільки кнопок розмістити у кожному рядку.
                  Наприклад, sizes=(2, 3, 1) створить три ряди: 2 кнопки, 3 кнопки, 1 кнопка.
    :return: Об'єкт ReplyKeyboardMarkup для використання у message.answer або message.reply
    '''
    keyboard = ReplyKeyboardBuilder() # Створюємо конструктор клавіатури
    # Додаємо кожну кнопку до конструктора
    for text in btns:
        keyboard.add(KeyboardButton(text=text))
    # Застосовуємо розміщення кнопок по рядках та інші налаштування
    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True,              # Дозволяє кнопкам змінювати розмір
        input_field_placeholder=placeholder # Встановлює текст-підказку
    )