import os
import re
import imageio_ffmpeg
import yt_dlp

# Diretorio padrão para downloads
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")

def get_ffmpeg_path():
    """Obtém o caminho do executável do ffmpeg fornecido pelo imageio_ffmpeg ou pelo sistema Linux."""
    try:
        path = imageio_ffmpeg.get_ffmpeg_exe()
        if path and os.path.exists(path):
            return path
    except Exception as e:
        print(f"[AVISO] FFmpeg do imageio_ffmpeg não encontrado: {e}")
    
    # Tentar ffmpeg nativo do sistema Linux (instalado via nixpacks.toml)
    import shutil
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
        
    return None

def sanitize_filename(filename):
    """Remove caracteres inválidos e problemáticos para nomes de arquivos no Windows."""
    # Remover caracteres proibidos no Windows: \ / : * ? " < > | [ ]
    cleaned = re.sub(r'[\\/*?:"<>|\[\]]', '', filename)
    # Remover espaços duplicados
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned if cleaned else "audio"

def format_duration(seconds):
    """Converte segundos em formato de texto HH:MM:SS ou MM:SS."""
    if not seconds:
        return "Desconhecido"
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def get_common_ydl_opts():
    opts = {
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'mweb', 'web_creator']
            }
        }
    }
    cookie_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
    if os.path.exists(cookie_file):
        opts['cookiefile'] = cookie_file
    return opts

def get_video_info(url):
    """Obtém metadados do vídeo do YouTube sem baixar o arquivo."""
    ffmpeg_path = get_ffmpeg_path()
    ydl_opts = get_common_ydl_opts()
    ydl_opts['skip_download'] = True

    if ffmpeg_path:
        ydl_opts['ffmpeg_location'] = ffmpeg_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        # Tratar playlists caso o usuário envie uma playlist
        if 'entries' in info:
            info = info['entries'][0]

        return {
            'id': info.get('id', ''),
            'title': info.get('title', 'Vídeo sem título'),
            'uploader': info.get('uploader', info.get('channel', 'Desconhecido')),
            'duration': format_duration(info.get('duration', 0)),
            'duration_raw': info.get('duration', 0),
            'thumbnail': info.get('thumbnail', ''),
            'url': info.get('webpage_url', url)
        }

def download_audio(url, quality="320", progress_hook=None):
    """
    Baixa o áudio do vídeo do YouTube e converte para MP3 com a qualidade desejada (kbps).
    Retorna o dicionário com os detalhes do download e caminho do arquivo final.
    """
    ffmpeg_path = get_ffmpeg_path()
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    output_template = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')

    ydl_opts = get_common_ydl_opts()
    ydl_opts.update({
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'writethumbnail': False,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }
        ],
        'restrictfilenames': False,
    })

    if ffmpeg_path:
        ydl_opts['ffmpeg_location'] = ffmpeg_path

    if progress_hook:
        ydl_opts['progress_hooks'] = [progress_hook]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if 'entries' in info:
            info = info['entries'][0]
        
        raw_title = info.get('title', 'audio')
        safe_title = sanitize_filename(raw_title)
        
        # Procurar o arquivo mp3 gerado mais recente no diretório de downloads
        mp3_files = [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR) if f.lower().endswith('.mp3')]
        if not mp3_files:
            raise Exception("O arquivo MP3 não foi encontrado após o download.")

        latest_file = max(mp3_files, key=os.path.getmtime)
        
        # Renomear para um nome limpo com extensão .mp3 se o nome contiver caracteres estranhos
        clean_filename = f"{safe_title}.mp3"
        clean_filepath = os.path.join(DOWNLOAD_DIR, clean_filename)
        
        if latest_file != clean_filepath:
            try:
                if os.path.exists(clean_filepath):
                    os.remove(clean_filepath)
                os.rename(latest_file, clean_filepath)
                latest_file = clean_filepath
            except Exception as e:
                print(f"[AVISO] Não foi possível renomear o arquivo: {e}")

        final_filename = os.path.basename(latest_file)

        return {
            'title': raw_title,
            'uploader': info.get('uploader', 'Desconhecido'),
            'duration': format_duration(info.get('duration', 0)),
            'thumbnail': info.get('thumbnail', ''),
            'filepath': latest_file,
            'filename': final_filename
        }
