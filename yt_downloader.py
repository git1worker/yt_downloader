import yt_dlp
import os
import ssl
from pathlib import Path
import sys
from get_info import *
import random 
#                                  Windows
# 🎬 Введите URL YouTube видео (или 'quit' для выхода): https://youtu.be/jsI2aQBlldY?si=LIX3zHGWSVcnop
# fX
# ✅ QuickJS найден: C:\msys64\mingw64\bin\qjs.exe
# ✅ Используем QuickJS: C:\msys64\mingw64\bin\qjs.exe
# 🔍 Получаем информацию о видео...
# [youtube] Extracting URL: https://youtu.be/jsI2aQBlldY?si=LIX3zHGWSVcnopfX
# [youtube] jsI2aQBlldY: Downloading webpage
# WARNING: [youtube] unable to extract yt initial data; please report this issue on  https://github.co
# m/yt-dlp/yt-dlp/issues?q= , filling out the appropriate issue template. Confirm you are on the lates
# t version using  yt-dlp -U
# WARNING: [youtube] Incomplete data received in embedded initial data; re-fetching using API.
# [youtube] jsI2aQBlldY: Downloading initial data API JSON
# [youtube] jsI2aQBlldY: Downloading android vr player API JSON
# [youtube] jsI2aQBlldY: Downloading web safari player API JSON
# [youtube] jsI2aQBlldY: Downloading player 4e51e895-tv
# [youtube] [jsc:quickjs] Solving JS challenges using quickjs
# [youtube] jsI2aQBlldY: Downloading m3u8 information

# 📺 Название: 1994 STATIC DREAMS  //  Synthwave, Vaporwave, Cyberpunk, Chillwave, Retrowave, Funkwave
#  Playlist
# ⏱️ Длительность: 6629 сек
# 👤 Автор: None

# ================================================================================

# 🎵 АУДИО ФОРМАТЫ (4):
# --------------------------------------------------------------------------------

#   🌍 Язык: en
#       1. ID:251    webm   135.322kbps 106.9 MB     medium [en]
#       2. ID:140    m4a    129.472kbps 102.3 MB     medium [en]
#       3. ID:249    webm   51.384kbps 40.6 MB      low [en]
#       4. ID:139    m4a    48.782kbps 38.5 MB      low [en]

# 🎬 ВИДЕО+АУДИО (5):
# --------------------------------------------------------------------------------
#     5. ID:94     mp4    854x478      N/A          30.0fps  [en]
#     6. ID:93     mp4    640x358      N/A          30.0fps  [en]
#     7. ID:18     mp4    640x358      180.7 MB     30fps 360p [en]
#     8. ID:92     mp4    426x238      N/A          30.0fps  [en]
#     9. ID:91     mp4    256x144      N/A          30.0fps  [en]

# 📹 ТОЛЬКО ВИДЕО (12):
# --------------------------------------------------------------------------------
#    10. ID:135    mp4    854x478      50.1 MB      30fps 480p
#    11. ID:244    webm   854x478      214.6 MB     30fps 480p
#    12. ID:397    mp4    854x478      87.9 MB      30fps 480p
#    13. ID:134    mp4    640x358      32.7 MB      30fps 360p
#    14. ID:243    webm   640x358      123.4 MB     30fps 360p
#    15. ID:396    mp4    640x358      55.4 MB      30fps 360p
#    16. ID:133    mp4    426x238      18.7 MB      30fps 240p
#    17. ID:242    webm   426x238      50.7 MB      30fps 240p
#    18. ID:395    mp4    426x238      30.4 MB      30fps 240p
#    19. ID:160    mp4    256x144      10.8 MB      30fps 144p
#    20. ID:278    webm   256x144      20.0 MB      30fps 144p
#    21. ID:394    mp4    256x144      17.4 MB      30fps 144p

# ================================================================================


print("Убедись, что запущен zapret-discord-youtube 1.8.4 > general(FAKE TLS AUTO ALT)")

# Отключаем проверку SSL
# ssl._create_default_https_context = ssl._create_unverified_context

def download_format(url, format_id, headers, convert_to_mp3, output_path="downloads"):
    """Скачивает выбранный формат"""
    Path(output_path).mkdir(exist_ok=True)
    
    ydl_opts = {
        'format': format_id,
        'outtmpl': os.path.join(output_path, '%(title).100s.%(ext)s'),
        
        # Настройка QuickJS (ТОЧНО ТАК ЖЕ КАК В get_video_info)
        'js_runtimes': {
            'quickjs': {
                'path': QUICKJS_PATH
            }
        },
        'remote_components': ['ejs:github'],
        # 'nocheckcertificate': True,
        
        # Упрощаем заголовки (убираем излишнее)
        'user_agent': headers['User-Agent'],
        'http_headers': headers,
        
        # Базовые параметры загрузки
        'retries': 10,
        'fragment_retries': 10,
        'skip_unavailable_fragments': True,
        
        # Критично: отключаем extractor_args для совместимости
        # 'extractor_args': {
        #     'youtube': {
        #         'player_client': ['web'],
        #     }
        # },
        
        # Добавляем cookies если есть
        'cookiefile': 'exported-cookies.txt' if os.path.exists('exported-cookies.txt') else None,
        
    }
    
    # Добавляем конвертацию в MP3 если нужно
    if convert_to_mp3:
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"📥 Скачивание формата ID: {format_id}...")
            ydl.download([url])
            print("✅ Загрузка завершена!")
            return True
    except Exception as e:
        print(f"❌ Ошибка при скачивании: {e}")
        return False

def main():
    print("=== YouTube Downloader with QuickJS ===")
    
    while True:
        url = input("\n🎬 Введите URL YouTube видео (или 'quit' для выхода): ").strip()
        if (url == ""):
          url = "https://www.youtube.com/watch?v=HpyVBF03vI8"
        if url.lower() in ['quit', 'exit', 'q']:
            break
            
        if not url.startswith(('http://', 'https://')):
            print("❌ Пожалуйста, введите корректный URL")
            continue
        
        headers = get_realistic_headers()
        
        info = get_video_info(url, headers)
            
        if not info:
            print("❌ Не удалось получить информацию о видео")
            continue
        
        # Получаем и показываем форматы
        audio_formats, video_formats, combined_formats = list_formats(info)
        all_formats = display_formats(audio_formats, video_formats, combined_formats)
        
        if not all_formats:
            print("❌ Нет доступных форматов для скачивания")
            continue
        
        # Выбор формата
        try:
            choice = input(f"\n🎯 Выберите номер формата (1-{len(all_formats)}) или Enter для лучшего аудио: ").strip()
            
            if choice == '':
                # Автоматически выбираем лучший аудио формат
                format_type, selected_format = None, None
                
                # Ищем лучший аудио (по битрейту)
                for fmt_type, fmt_info in all_formats:
                    if fmt_type == 'audio':
                        if not selected_format or fmt_info['abr'] > selected_format['abr']:
                            selected_format = fmt_info
                            format_type = fmt_type
                
                if not selected_format:
                    print("⚠️ Аудио форматы не найдены, используем первый доступный")
                    format_type, selected_format = all_formats[0]
                
                format_id = selected_format['id']
                print(f"🎵 Автоматически выбран: ID {format_id} ({selected_format['abr']}kbps)")
                
            elif choice.isdigit() and 1 <= int(choice) <= len(all_formats):
                # Находим выбранный формат
                selected_format = None
                format_type = None
                
                for fmt_type, fmt_info in all_formats:
                    if fmt_info['display_id'] == int(choice):
                        selected_format = fmt_info
                        format_type = fmt_type
                        break
                
                if selected_format:
                    format_id = selected_format['id']
                    print(f"✅ Выбран формат: ID {format_id}")
                else:
                    print("⚠️ Формат не найден, используем лучший аудио")
                    format_id = 'bestaudio'
            else:
                print("⚠️ Неверный выбор, используем лучший аудио")
                format_id = 'bestaudio'
            
            # Спрашиваем о конвертации для аудио форматов
            convert_to_mp3 = True
            if format_type == 'audio':
                convert_option = input("🎵 Конвертировать в MP3? (y/N): ").strip().lower()
                convert_to_mp3 = convert_option == 'y' or convert_option == ""
            
            # Скачиваем
            download_format(url, format_id, headers, convert_to_mp3)
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print("Попробуйте другой формат или видео")

if __name__ == "__main__":
    main()