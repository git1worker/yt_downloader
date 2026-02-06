import yt_dlp
import os

# Путь к QuickJS
QUICKJS_PATH = 'C:\\msys64\\mingw64\\bin\\qjs.exe'

def get_video_info(url):
    """Получает информацию о видео, включая список форматов"""
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'skip_download': True,
        'ignoreerrors': True,
        
        # Настройка Quickjs (совпадает с download_format)
        'js_runtimes': {
            'quickjs': {
                'path': QUICKJS_PATH
            }
        },
        'remote_components': ['ejs:github'],
        'nocheckcertificate': True,
        
        # Добавляем cookies для консистентности
        'cookiefile': 'exported-cookies.txt' if os.path.exists('exported-cookies.txt') else None,
    }
    
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
    
    # Простые но эффективные User-Agents
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    ]
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',  # Фиксированный корректный язык
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
    
    # Добавляем Sec-Ch-Ua только для Chrome (опционально)
    if 'Chrome' in headers['User-Agent']:
        headers.update({
            'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
        })
    
    return headers