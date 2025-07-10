from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import math # Потрібен для ceil

CALLBACK_DATA_SEPARATOR = "::"
WORDS_PER_PAGE = 10 # Скільки слів показувати на одній сторінці

def get_save_word_keyboard(original: str, translation: str) -> InlineKeyboardMarkup:
    """Створює інлайн-клавіатуру з кнопкою збереження слова, обробляючи ліміт callback_data."""
    builder = InlineKeyboardBuilder()
    base_callback = f"save_word{CALLBACK_DATA_SEPARATOR}"
    separator_len = len(CALLBACK_DATA_SEPARATOR)
    max_payload_len = 64 - len(base_callback.encode('utf-8')) - separator_len

    original_bytes = original.encode('utf-8')
    translation_bytes = translation.encode('utf-8')

    total_len = len(original_bytes) + len(translation_bytes)

    # Якщо загальна довжина в межах норми
    if total_len <= max_payload_len:
        callback_data = f"{base_callback}{original}{CALLBACK_DATA_SEPARATOR}{translation}"
    else:
        # Якщо перевищує, обрізаємо пропорційно
        if total_len > 0:
            prop_orig = len(original_bytes) / total_len
            prop_trans = 1 - prop_orig

            max_orig_len = int(max_payload_len * prop_orig)
            max_trans_len = max_payload_len - max_orig_len

            original_short = original_bytes[:max_orig_len].decode('utf-8', errors='ignore')
            translation_short = translation_bytes[:max_trans_len].decode('utf-8', errors='ignore')

            callback_data = f"{base_callback}{original_short}{CALLBACK_DATA_SEPARATOR}{translation_short}"

            if len(callback_data.encode('utf-8')) > 64:
                print(f"Warning: Callback data for 'save_word' STILL too long after shortening for: '{original}'. Button not created.")
                return builder.as_markup()
        else:
            return builder.as_markup()

    builder.button(
        text="➕ Зберегти у словник",
        callback_data=callback_data
    )
    return builder.as_markup()


# Клавіатура для списку словника з пагінацією, видаленням ТА ПОШУКОМ
def get_vocabulary_list_keyboard(
    vocabulary_page: list[tuple[int, str, str]],
    current_page: int,
    total_words: int
) -> InlineKeyboardMarkup:
    """Створює клавіатуру для навігації по словнику, видалення слів та ініціювання пошуку."""
    builder = InlineKeyboardBuilder()

    # Кнопки видалення (якщо є слова на сторінці)
    if vocabulary_page:
        for word_id, original, _ in vocabulary_page:
            max_text_len = 25
            display_text = f"❌ {original}"
            if len(display_text) > max_text_len:
                display_text = display_text[:max_text_len-1] + "…"
            callback_data_delete = f"vocab_delete{CALLBACK_DATA_SEPARATOR}{word_id}"
            builder.button(text=display_text, callback_data=callback_data_delete)
        builder.adjust(1) # Кнопки видалення по одній на рядок

    # Кнопки пагінації
    pagination_buttons = []
    if total_words > 0: # Показуємо пагінацію, тільки якщо є слова
        total_pages = math.ceil(total_words / WORDS_PER_PAGE) if total_words > 0 else 1
        if current_page > 0:
            pagination_buttons.append(
                InlineKeyboardButton(text="◀️ Попередня", callback_data=f"vocab_page{CALLBACK_DATA_SEPARATOR}{current_page - 1}")
            )
        if total_pages > 1: # Показуємо номер сторінки, якщо їх більше однієї
            pagination_buttons.append(
                 InlineKeyboardButton(text=f"{current_page + 1}/{total_pages}", callback_data="noop") # noop - no operation
             )
        if current_page < total_pages - 1:
            pagination_buttons.append(
                InlineKeyboardButton(text="Наступна ▶️", callback_data=f"vocab_page{CALLBACK_DATA_SEPARATOR}{current_page + 1}")
            )
        if pagination_buttons:
            builder.row(*pagination_buttons) # Додаємо рядок пагінації

    # Кнопка пошуку
    # Додаємо кнопку пошуку завжди, навіть якщо словник порожній, щоб можна було знайти щось додане раніше
    builder.row(InlineKeyboardButton(text="🔍 Знайти у словнику", callback_data="vocab_search_start"))

    return builder.as_markup()