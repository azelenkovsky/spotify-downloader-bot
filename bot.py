import logging
from typing import Dict
import time

from telegram import ReplyKeyboardMarkup, Update, KeyboardButton, ParseMode, ChatAction
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext
)

from upload import download_music_to_server, upload_music_to_user

from functions import (
    first_menu_markup,
    search_type_buttons_markup,
    quality_menu_markup,
    music_format_menu_markup,
    final_downloading_menu_markup,
    final_menu_markup,
    uploading_type_menu_markup
)

from config import search_type_user, search_type

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING_FIRST_MENU, TYPING_SPOTIFY_LINK, TYPING_QUERY_STRING, TYPING_MUSIC_QUALITY, TYPING_MUSIC_FORMAT, FILES_DOWNLOADED_TO_SERVER, FINAL_STEP = range(7)

############################################
# main functions
############################################

def facts_to_str(user_data: Dict[str, str]) -> str:
    facts = list()

    for key, value in user_data.items():
        facts.append(f'{key} - {value}')

    return "\n".join(facts).join(['\n', '\n'])

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        '''
Меня зовут <b>Fricky</b>. Я помощник в скачивании треков из Spotify или/и Интернета:
1. Скачать любой трек/альбом/плейлист из Spotify
2. Я могу найти и скачать любой трек/альбом в Интернете

Выберете раздел в меню ниже
        ''',
        reply_markup=first_menu_markup,
        parse_mode=ParseMode.HTML
    )

    return CHOOSING_FIRST_MENU


def get_flow(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['first_choice'] = text
    if text == '📲 Скачать Трек/Альбом/Плейлист из Spotify':
        update.message.reply_text('Отправьте Spotify ссылку на плейлист, трек или альбом',parse_mode=ParseMode.HTML)
    else:
        update.message.reply_text('Укажите категорию для поиска в меню ниже', reply_markup=search_type_buttons_markup , parse_mode=ParseMode.HTML)

    return TYPING_SPOTIFY_LINK

def get_spotify_link(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['spotify_link'] = text

    update.message.reply_text('Выберете качество скачиваемых треков ниже', reply_markup=quality_menu_markup, parse_mode=ParseMode.HTML)

    return TYPING_MUSIC_QUALITY

def get_category_to_search(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['category_to_search'] = text

    update.message.reply_text('''
Отправьте наименование {0}а в формате:
<b>{1}</b>
    '''.format(text, search_type_user[text]), parse_mode=ParseMode.HTML)

    return TYPING_QUERY_STRING

def get_search_query(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['search_query_string'] = text

    update.message.reply_text('Выберете качество скачиваемых треков ниже', reply_markup=quality_menu_markup, parse_mode=ParseMode.HTML)

    return TYPING_MUSIC_QUALITY

def get_music_quality(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['music_quality'] = text
    update.message.reply_text(
        '''
        Выберете формат скачиваемых треков
        ''',
        reply_markup=music_format_menu_markup,
        parse_mode=ParseMode.HTML
    )

    return TYPING_MUSIC_FORMAT

def get_music_format(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['music_format'] = text
    bot = update.message.bot
    chat_id = update.message.chat.id
    update_message = update.message
    user_content = context.user_data

    update.message.reply_text(
        "Отлично! Ниже информация, которую Вы мне рассказали:"
        f"{facts_to_str(context.user_data)} ",
    )

    # начинаем загрузку треков на сервер
    update.message.reply_text('Скачиваем треки...')
    bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    download_music_to_server(user_content, update_message, chat_id)

    # реплика и меню выбора типа загрузки файлов в Телеграм
    update.message.reply_text('''
Выберите в каком формате вам загрузить скаченные треки:

- <b>🗂 Архив (рекомендуемо)</b> - для большого количества треков. Мы запакуем ваши треки в архив и загрузим на Яндекс.Диск (из-за ограничения 50мб в Телеграме);

- <b>🎵 Треки по отдельности</b> - для 1-5 треков. Мы загрузим ваши треки напрямую в Телеграм.
    ''', reply_markup=uploading_type_menu_markup, parse_mode=ParseMode.HTML)


    return FILES_DOWNLOADED_TO_SERVER


def uploading_downloaded_files(update: Update, context: CallbackContext) -> int:
    uploading_type = update.message.text
    music_format = context.user_data['music_format']
    context.user_data['uploading_type'] = str(uploading_type)
    bot = update.message.bot
    chat_id = update.message.chat.id
    update_message = update.message

    # начинаем uploading треков в телеграмм
    update.message.reply_text('Начинаем загрузку файлов в Телеграмм...')

    bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    upload_music_to_user(bot, chat_id, uploading_type, music_format, update_message)

    return FINAL_STEP

def done(update: Update, context: CallbackContext) -> int:

    return ConversationHandler.END


############################################
# main handler
############################################

def main() -> None:
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("your_telegram_bot_token_here", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            # состояние главного меню
            CHOOSING_FIRST_MENU: [
                # handler to run all about breeds
                MessageHandler(Filters.regex('^(📲 Скачать Трек/Альбом/Плейлист из Spotify)$'), get_flow),
                MessageHandler(Filters.regex('^(🔎 Найти и скачать Трек/Альбом/Плейлист из Интернета)$'), get_flow)
            ],

            TYPING_SPOTIFY_LINK: [
                # handler to run all about breeds
                MessageHandler(~(Filters.regex('^(📀 Альбом|🎵 Трек|🎧 Плейлист)$')), get_spotify_link),
                MessageHandler(Filters.regex('^(📀 Альбом|🎵 Трек|🎧 Плейлист)$'), get_category_to_search)
                 #MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), get_spotify_link),
            ],

            TYPING_QUERY_STRING: [
                # handler to run all about breeds
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), get_search_query),
            ],

            TYPING_MUSIC_QUALITY: [
                # handler to run all about breeds
                MessageHandler(Filters.regex('^(Лучшее|Q32K|Q96K|Q128K|Q192K|Q256K|Q320K|Худшее)$'), get_music_quality)
            ],

            TYPING_MUSIC_FORMAT: [
                # handler to run all about breeds
                MessageHandler(Filters.regex('^(MP3|AAC|FLAC|M4A|OPUS|VORBIS|WAV)$'), get_music_format),

            ],

            FILES_DOWNLOADED_TO_SERVER: [
                # handler to run all about breeds
                MessageHandler(Filters.regex('^(🗂 Архив|🎵 Треки по отдельности)$'), uploading_downloaded_files),
                #MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), uploading_downloaded_files),

            ],

            FINAL_STEP: [
                # handler to run all about breeds
                MessageHandler(Filters.regex('^(🏠На главную)$'), done),

            ],

        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
