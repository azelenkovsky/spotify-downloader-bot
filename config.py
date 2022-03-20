from savify.types import Type, Format, Quality

# credentials for spotify
spotify_api_credentials=("your_spotify_token_here","your_spotify_token_here")

# token for yandex disk
yadisk_api_token = 'your_yandex_disk_token_here'

# dictionary russian download type -> savify transcription
# download_type = {
#     '🎧 Плейлист' : Type.PLAYLIST,
#     '📀 Альбом': Type.ALBOM
# }

# dictionary first step download rus -> eng
first_step = {
    '📲 Скачать Трек/Альбом/Плейлист из Spotify': 'spotify_download',
    '🔎 Найти и скачать Трек/Альбом/Плейлист из Интернета': 'internet_search_download'
}


# dictionary quality dict -> savify dict
quality_dict = {
    'Лучшее': Quality.BEST,
    'Q320K': Quality.Q320K,
    'Q256K': Quality.Q256K,
    'Q192K': Quality.Q192K,
    'Q128K': Quality.Q128K,
    'Q96K': Quality.Q96K,
    'Q32K': Quality.Q32K,
    'Худшее': Quality.WORST
}

# dictionary quality dict -> savify dict
format_dict = {
    'MP3': Format.MP3,
    'AAC': Format.AAC,
    'FLAC': Format.FLAC,
    'M4A': Format.M4A,
    'OPUS': Format.OPUS,
    'VORBIS': Format.VORBIS,
    'WAV': Format.WAV
}


# dictionary search type -> search format for user message
search_type_user = {
    '📀 Альбом': 'Исполнитель - Наименование Альбома',
    '🎵 Трек': 'Исполнитель - Наименование Трека',
    '🎧 Плейлист': 'Наименование Плейлиста'
}

# dictionary search type -> search format
search_type = {
    '📀 Альбом': Type.ALBUM,
    '🎵 Трек': Type.TRACK,
    '🎧 Плейлист': Type.PLAYLIST
}
