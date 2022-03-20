import os
import glob
import telegram
from telegram import ReplyKeyboardMarkup, KeyboardButton, ParseMode

import logging
from savify import Savify
from savify.types import Type, Format, Quality
from savify.utils import PathHolder
from savify.logger import Logger

from config import spotify_api_credentials, yadisk_api_token, format_dict, quality_dict, search_type
import yadisk

# libraries for yadisk_async
import asyncio
import posixpath
import os
import yadisk_async

import shutil

from functions import final_menu_markup



def download_music_to_server(user_content, update_message, chat_id):

    # downloading variables
    if user_content['first_choice'] == '📲 Скачать Трек/Альбом/Плейлист из Spotify':
        spotify_link = user_content['spotify_link']
    else:
        search_type_query = str(user_content['category_to_search'])
        search_type_query_code = search_type[search_type_query]
        search_string_query = str(user_content['search_query_string'])

    music_quality = user_content['music_quality']
    music_format = user_content['music_format']

    mq = quality_dict[music_quality]
    fm = format_dict[music_format]

    logger = Logger(log_location='.', log_level=None)
    s = Savify(api_credentials=spotify_api_credentials,
                quality=mq,
                download_format=fm,
                path_holder=PathHolder(downloads_path='./{0}'.format(str(chat_id))),
                skip_cover_art=False,
                logger=logger)

    if user_content['first_choice'] == '📲 Скачать Трек/Альбом/Плейлист из Spotify':
        s.download(spotify_link)
    else:
        s.download(search_string_query, search_type_query_code)
    update_message.reply_text('Все треки скачены', reply_markup = ReplyKeyboardMarkup([[KeyboardButton('Начать загрузку в Телеграм')]], one_time_keyboard=True))
    # bot.send_message(chat_id=chat_id, 'Все треки скачены')

def clean_user_yadisk_dir(chat_id, yadisk_token):
    y = yadisk.YaDisk(token=yadisk_token)

    user_files = y.listdir('fricky/{0}'.format(chat_id))

    for n in user_files:
        path_str = 'fricky/{0}/{1}'.format(chat_id, str(n['name']))
        print('removing file - {0} - {1}'.format(str(n['name']), path_str))
        y.remove(path_str, permanently=True)


# делаем функцию clean_user_yadisk_dir асинхронной
def clean_user_yadisk_dir_async(chat_id, yadisk_token, n_parallel_requests=5):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    y = yadisk_async.YaDisk(token=yadisk_token)
    ya = yadisk.YaDisk(token=yadisk_token)

    user_files = ya.listdir('fricky/{0}'.format(chat_id))

    try:

        async def delete_files(queue):
            while queue:
                path_str = queue.pop(0)

                print("Deleting %s" % (path_str))

                try:
                    await y.remove(path_str, permanently=True)
                except:
                    pass

        delete_queue = []

        for n in user_files:
            path_str = 'fricky/{0}/{1}'.format(chat_id, str(n['name']))
            delete_queue.append(path_str)

        tasks = [delete_files(delete_queue) for i in range(n_parallel_requests)]
        loop.run_until_complete(asyncio.gather(*tasks))

    finally:
        loop.run_until_complete(y.close())


def recursive_upload(from_dir, to_dir, yadisk_token, n_parallel_requests=5):
    # loop = asyncio.get_event_loop()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    y = yadisk_async.YaDisk(token=yadisk_token)

    try:
        async def upload_files(queue):
            while queue:
                in_path, out_path = queue.pop(0)

                print("Uploading %s -> %s" % (in_path, out_path))

                try:
                    await y.upload(in_path, out_path)
                except yadisk_async.exceptions.PathExistsError:
                    print("%s already exists" % (out_path,))

        async def create_dirs(queue):
            while queue:
                path = queue.pop(0)

                print("Creating directory %s" % (path,))

                try:
                    await y.mkdir(path)
                except yadisk_async.exceptions.PathExistsError:
                    print("%s already exists" % (path,))

        mkdir_queue = []
        upload_queue = []

        print("Creating directory %s" % (to_dir,))

        try:
            loop.run_until_complete(y.mkdir(to_dir))
        except yadisk_async.exceptions.PathExistsError:
            print("%s already exists" % (to_dir,))

        for root, dirs, files in os.walk(from_dir):
            rel_dir_path = root.split(from_dir)[1].strip(os.path.sep)
            rel_dir_path = rel_dir_path.replace(os.path.sep, "/")
            dir_path = posixpath.join(to_dir, rel_dir_path)

            for dirname in dirs:
                mkdir_queue.append(posixpath.join(dir_path, dirname))

            for filename in files:
                out_path = posixpath.join(dir_path, filename)
                rel_dir_path_sys = rel_dir_path.replace("/", os.path.sep)
                in_path = os.path.join(from_dir, rel_dir_path_sys, filename)

                upload_queue.append((in_path, out_path))

            tasks = [upload_files(upload_queue) for i in range(n_parallel_requests)]
            tasks.extend(create_dirs(mkdir_queue) for i in range(n_parallel_requests))

            loop.run_until_complete(asyncio.gather(*tasks))
    finally:
        loop.run_until_complete(y.close())

def upload_music_to_user(bot, chat_id, uploading_type, music_format, update_message):

    if uploading_type == '🗂 Архив':


        yadisk_upload_from = '{0}'.format(chat_id)
        yadisk_upload_to = 'fricky/{0}'.format(chat_id)


        print('удаление файлов юзера с яндекс диска...')
        clean_user_yadisk_dir_async(chat_id, yadisk_api_token, n_parallel_requests=5)

        print('загрузка на яндекс диск...')
        recursive_upload(yadisk_upload_from, yadisk_upload_to, yadisk_api_token, 5)

        print('загрузка на яндекс диск завершена')
        y = yadisk.YaDisk(token=yadisk_api_token)
        download_link = y.get_download_link('fricky/{0}'.format(chat_id))

        os.system('rm -rf {0}'.format(str(chat_id)))

        update_message.reply_text('ссылка на скачивание архива - <a href="{0}">здесь</a>'.format(download_link), parse_mode=ParseMode.HTML)



    else:

        # get list of tracks
        lista = glob.glob('{0}/*.mp3'.format(str(chat_id)))
        list = [s.replace('{0}/'.format(str(chat_id)), '') for s in lista]

        # get array len
        music_len = len(list)

        # for loop
        at = music_len - 1
        aw = 0

        # os.system("find -size +45M -exec rm -f {} \;") # Удаляем файлы больше 50мб из-за ограничений Телеграмма

        os.system(f"find {chat_id}/ -size +45M -exec rm -f {{}} \;") # Удаляем файлы больше 50мб из-за ограничений Телеграмма

        while aw <= at:
            track = list[aw]
            bot.send_audio(chat_id=chat_id, audio=open('./' + str(chat_id) + '/' + track, 'rb'), timeout=1000)
            aw = aw + 1
        else:
            os.system('rm -rf {0}/*.mp3'.format(str(chat_id)))

# os.system('rm -rf {0}/*.mp3'.format(str(chat_id)))

# print('архивирование треков...')
# os.system('find {0}/ -name *{1}* | zip -r -X {0}/{0}.zip -@'.format(chat_id, music_format.lower()))
# # shutil.make_archive('./{0}/{0}'.format(chat_id), 'zip', './{0}'.format(chat_id))
# y = yadisk.YaDisk(token=yadisk_api_token)
# yadisk_upload_from = '{0}/{0}.zip'.format(chat_id)
# yadisk_upload_to = 'fricky/{0}.zip'.format(chat_id)
# try:
#     print('удаление прошлого архива...')
#     y.remove(yadisk_upload_to, permanently=True)
# except:
#     pass
# print('загрузка на яндекс диск...')
# try:
#     y.upload(yadisk_upload_from, yadisk_upload_to, overwrite=True)
# except:
#     pass
# print('загрузка на яндекс диск завершена')
#
# download_link = y.get_download_link('fricky/{0}.zip'.format(chat_id))
#
# update_message.reply_text('ссылка на скачивание архива - <a href="{0}">здесь</a>'.format(download_link), parse_mode=ParseMode.HTML)
