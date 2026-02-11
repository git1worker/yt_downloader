import yt_dlp
import os
import ssl
from pathlib import Path
import sys
from get_info import *
import random 
import platform

print("Убедись, что запущен zapret-discord-youtube > general(FAKE TLS AUTO ALT)")

# Отключаем проверку SSL
# ssl._create_default_https_context = ssl._create_unverified_context

def download_format(url, format_id, headers, convert_to_mp3, output_path="downloads"):
    """Скачивает выбранный формат"""
    Path(output_path).mkdir(exist_ok=True)
    
    ydl_opts = {
        'format': format_id,
        'outtmpl': os.path.join(output_path, '%(title).100s.%(ext)s'),
        
        # Настройка QuickJS (ТОЧНО ТАК ЖЕ КАК В get_video_info)
        
        'remote_components': ['ejs:github'],
        # 'nocheckcertificate': True,
        
        # Упрощаем заголовки (убираем излишнее)
        'user_agent': headers['User-Agent'],
        'http_headers': headers,
        
        # Базовые параметры загрузки
        'retries': 10,
        'fragment_retries': 10,
        'skip_unavailable_fragments': True,

        # Добавляем cookies если есть
        'cookiefile': 'exported-cookies.txt' if os.path.exists('exported-cookies.txt') else None,
        
    }
    
    if platform.system != 'Linux':
        ydl_opts['js_runtimes'] = {
            'quickjs': {
                'path': QUICKJS_PATH
            }
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
    print("=== YouTube Downloader ===")
    test_connection()
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