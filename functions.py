from telegram import ReplyKeyboardMarkup, Update, KeyboardButton, ParseMode, ChatAction


############################################
# all keyboards
############################################

# main menu keyboard options
first_menu_keyboard_buttons = [
            [KeyboardButton('📲 Скачать Трек/Альбом/Плейлист из Spotify')],
            [KeyboardButton('🔎 Найти и скачать Трек/Альбом/Плейлист из Интернета')]
]
first_menu_markup = ReplyKeyboardMarkup(first_menu_keyboard_buttons, one_time_keyboard=True)

# search type options
search_type_buttons = [
            [KeyboardButton('📀 Альбом')],
            [KeyboardButton('🎵 Трек')],
            [KeyboardButton('🎧 Плейлист')]
]
search_type_buttons_markup = ReplyKeyboardMarkup(search_type_buttons, one_time_keyboard=True)

# Quality keyboard options
quality_menu_keyboard_buttons = [
            [KeyboardButton('Лучшее'), KeyboardButton('Q320K'), KeyboardButton('Q256K')],
            [KeyboardButton('Q192K'), KeyboardButton('Q128K'), KeyboardButton('Q96K')],
            [KeyboardButton('Q32K'), KeyboardButton('Худшее')],
            [KeyboardButton('↩️ Назад')]
]

quality_menu_markup = ReplyKeyboardMarkup(quality_menu_keyboard_buttons, one_time_keyboard=True)

# Music format keyboard options
music_format_menu_keyboard_buttons = [
            [KeyboardButton('MP3'), KeyboardButton('FLAC')],
            [KeyboardButton('AAC'), KeyboardButton('M4A')],
            [KeyboardButton('OPUS'), KeyboardButton('VORBIS'), KeyboardButton('WAV')],
            [KeyboardButton('↩️ Назад')]
]

music_format_menu_markup = ReplyKeyboardMarkup(music_format_menu_keyboard_buttons, one_time_keyboard=True)

# Begin uploading music
final_downloading_menu_buttons = [
            [KeyboardButton('Начать загрузку')]
]

final_downloading_menu_markup = ReplyKeyboardMarkup(final_downloading_menu_buttons, one_time_keyboard=True)

# Uploading type menu
uploading_type_menu_buttons = [
            [KeyboardButton('🗂 Архив')],
            [KeyboardButton('🎵 Треки по отдельности')]
]

uploading_type_menu_markup = ReplyKeyboardMarkup(uploading_type_menu_buttons, one_time_keyboard=True)


# Uploading and downloading finished
final_menu_buttons = [
            [KeyboardButton('🏠На главную')]
]

final_menu_markup = ReplyKeyboardMarkup(final_menu_buttons, one_time_keyboard=True)
