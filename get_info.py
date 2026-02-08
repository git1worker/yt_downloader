import yt_dlp
import os
import platform

# Путь к QuickJS

QUICKJS_PATH = 'C:\\msys64\\mingw64\\bin\\qjs.exe'


def check_quickjs():
    """Проверяет наличие QuickJS и возвращает путь или None"""
    if os.path.exists(QUICKJS_PATH):
        print(f"✅ QuickJS найден: {QUICKJS_PATH}")
        return QUICKJS_PATH
    else:
        print("QuickJS не найден")
        return None
    

def get_video_info(url, headers):
    """Получает информацию о видео, включая список форматов"""

    headers = get_realistic_headers()

    ydl_opts = {
        # 'nocheckcertificate': True,
        
        # Упрощаем заголовки (убираем излишнее)
        'user_agent': headers['User-Agent'],
        'http_headers': headers,
        'remote_components': ['ejs:github'],

        'cookiefile': 'exported-cookies.txt' if os.path.exists('exported-cookies.txt') else None,

        # Базовые параметры загрузки
        'retries': 10,
        'fragment_retries': 10,
        'skip_unavailable_fragments': True,

    }

    if platform.system() != 'Linux':
        # Проверяем QuickJS
        quickjs_path = check_quickjs()
        
        if quickjs_path:
            # Добавляем настройки QuickJS только если он найден
            ydl_opts.update({
                'js_runtimes': {
                    'quickjs': {
                        'path': quickjs_path
                    }
                },
                
            })
            print(f"✅ Используем QuickJS: {quickjs_path}")
        else:
            print("⚠️ Работаем без QuickJS - форматы могут быть ограничены")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("🔍 Получаем информацию о видео...")
            info = ydl.extract_info(url, download=False)
            
            if not info:
                print("❌ Не удалось получить информацию о видео")
                return None
            
            return info
            
    except Exception as e:
        print(f"❌ Ошибка при получении информации: {e}")
        return None
    
def list_formats(info):
    """Выводит список доступных форматов"""
    if not info or 'formats' not in info:
        print("❌ Нет информации о форматах")
        return [], [], []
    
    print(f"\n📺 Название: {info.get('title', 'Unknown')}")
    print(f"⏱️ Длительность: {info.get('duration', 0)} сек")
    print(f"👤 Автор: {info.get('uploader', 'Unknown')}")
    
    # Группируем форматы
    audio_formats = []
    video_formats = []
    combined_formats = []
    
    for fmt in info['formats']:
        format_id = fmt.get('format_id', 'N/A')
        ext = fmt.get('ext', 'N/A')
        resolution = fmt.get('resolution', 'N/A')
        format_note = fmt.get('format_note', '')
        filesize = fmt.get('filesize', fmt.get('filesize_approx', 0))
        
        # Размер файла
        if filesize:
            size_str = f"{filesize / 1024 / 1024:.1f} MB"
        else:
            size_str = "N/A"
        
        # Аудио информация
        acodec = fmt.get('acodec', 'none')
        abr = fmt.get('abr', 0)
        language = fmt.get('language', '')
        
        # Видео информация
        vcodec = fmt.get('vcodec', 'none')
        fps = fmt.get('fps', 0)
        
        format_info = {
            'id': format_id,
            'ext': ext,
            'resolution': resolution,
            'size': size_str,
            'note': format_note,
            'acodec': acodec,
            'vcodec': vcodec,
            'abr': abr,
            'language': language,
            'fps': fps,
        }
        
        if acodec != 'none' and vcodec != 'none':
            combined_formats.append(format_info)
        elif acodec != 'none':
            audio_formats.append(format_info)
        elif vcodec != 'none':
            video_formats.append(format_info)
    
    return audio_formats, video_formats, combined_formats

def display_formats(audio_formats, video_formats, combined_formats):
    """Отображает форматы в удобном виде"""
    all_formats = []
    current_id = 1
    
    print("\n" + "="*80)
    
    # Аудио форматы (сгруппированные по языку)
    if audio_formats:
        print(f"\n🎵 АУДИО ФОРМАТЫ ({len(audio_formats)}):")
        print("-" * 80)
        
        # Группируем по языку
        audio_by_lang = {}
        for fmt in audio_formats:
            lang = fmt['language'] or 'unknown'
            if lang not in audio_by_lang:
                audio_by_lang[lang] = []
            audio_by_lang[lang].append(fmt)
        
        for lang, formats in sorted(audio_by_lang.items()):
            print(f"\n  🌍 Язык: {lang}")
            for fmt in sorted(formats, key=lambda x: x['abr'], reverse=True):
                lang_display = f"[{fmt['language']}]" if fmt['language'] else ""
                print(f"    {current_id:>3}. ID:{fmt['id']:<6} {fmt['ext']:<6} "
                      f"{fmt['abr']:>4}kbps {fmt['size']:<12} {fmt['note']} {lang_display}")
                fmt['display_id'] = current_id
                all_formats.append(('audio', fmt))
                current_id += 1
    
    # Комбинированные форматы (видео+аудио)
    if combined_formats:
        print(f"\n🎬 ВИДЕО+АУДИО ({len(combined_formats)}):")
        print("-" * 80)
        
        for fmt in sorted(combined_formats, 
                         key=lambda x: (x['resolution'], x['fps']), 
                         reverse=True):
            lang_display = f"[{fmt['language']}]" if fmt['language'] else ""
            print(f"  {current_id:>3}. ID:{fmt['id']:<6} {fmt['ext']:<6} "
                  f"{fmt['resolution']:<12} {fmt['size']:<12} {fmt['fps']}fps "
                  f"{fmt['note']} {lang_display}")
            fmt['display_id'] = current_id
            all_formats.append(('combined', fmt))
            current_id += 1
    
    # Видео форматы (только видео)
    if video_formats:
        print(f"\n📹 ТОЛЬКО ВИДЕО ({len(video_formats)}):")
        print("-" * 80)
        
        for fmt in sorted(video_formats, 
                         key=lambda x: (x['resolution'], x['fps']), 
                         reverse=True):
            print(f"  {current_id:>3}. ID:{fmt['id']:<6} {fmt['ext']:<6} "
                  f"{fmt['resolution']:<12} {fmt['size']:<12} {fmt['fps']}fps {fmt['note']}")
            fmt['display_id'] = current_id
            all_formats.append(('video', fmt))
            current_id += 1
    
    print("\n" + "="*80)
    return all_formats

def get_realistic_headers():
    import random
    
    # Мобильные User-Agents для Android и iOS
    mobile_user_agents = [
        # Android - Chrome
        'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        
        # Android - Samsung Browser
        'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/21.0 Mobile Safari/537.36',
        
        # iOS - Safari
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1',
        
        # iOS - Chrome
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/121.0.0.0 Mobile/15E148 Safari/604.1',
        
        # Android - Firefox
        'Mozilla/5.0 (Android 14; Mobile; rv:122.0) Gecko/122.0 Firefox/122.0',
    ]
    
    user_agent = random.choice(mobile_user_agents)
    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.youtube.com/',
        'DNT': '1',
    }
    
    # Определяем платформу по User-Agent
    is_android = 'Android' in user_agent
    is_ios = 'iPhone' in user_agent or 'iPad' in user_agent or 'CPU OS' in user_agent
    
    # Добавляем заголовки в зависимости от платформы
    if 'Chrome' in user_agent and (is_android or is_ios):
        sec_ch_ua = ''
        platform = ''
        
        if is_android:
            sec_ch_ua = '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"'
            platform = '"Android"'
        elif is_ios:
            sec_ch_ua = '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"'
            platform = '"iOS"'
        
        headers.update({
            'Sec-Ch-Ua': sec_ch_ua,
            'Sec-Ch-Ua-Mobile': '?1',  # Важно: ?1 для мобильных устройств
            'Sec-Ch-Ua-Platform': platform,
        })
    
    return headers