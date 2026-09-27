import sys
import os
import time
from utils_yt import get_video_info, download_audio, DOWNLOAD_DIR

def print_header():
    print("=" * 60)
    print("         CONVERSOR DE YOUTUBE PARA MP3 (HD 320 kbps)")
    print("=" * 60)
    print()

def progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
        downloaded = d.get('downloaded_bytes', 0)
        speed = d.get('speed', 0)
        eta = d.get('eta', 0)

        if total > 0:
            percent = downloaded / total * 100
            bar_length = 30
            filled = int(bar_length * downloaded // total)
            bar = '█' * filled + '░' * (bar_length - filled)
            speed_mb = (speed or 0) / (1024 * 1024)
            sys.stdout.write(f"\r[BAIXANDO] [{bar}] {percent:.1f}% ({speed_mb:.2f} MB/s) Restam: {eta}s")
            sys.stdout.flush()
        else:
            sys.stdout.write("\r[BAIXANDO] Processando dados do fluxo de áudio...")
            sys.stdout.flush()
    elif d['status'] == 'finished':
        print("\n[CONVERTENDO] Convertendo áudio para MP3 alta qualidade (320kbps)...")

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    print_header()

    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Cole a URL do vídeo do YouTube: ").strip()

    if not url:
        print("[ERRO] URL não fornecida!")
        return

    print("\n[INFO] Obter informações do vídeo...")
    try:
        info = get_video_info(url)
        print(f"\n🎵 Título:   {info['title']}")
        print(f"👤 Canal:    {info['uploader']}")
        print(f"⏱️ Duração:  {info['duration']}\n")
    except Exception as e:
        print(f"[AVISO] Não foi possível carregar prévia: {e}")
        print("[INFO] Continuando com o download direto...")

    print("Iniciando download e conversão...")
    start_time = time.time()
    try:
        res = download_audio(url, quality="320", progress_hook=progress_hook)
        elapsed = time.time() - start_time
        print("\n" + "=" * 60)
        print(" SUCCESS: CONVERSÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print(f"📁 Arquivo salvo em: {res['filepath']}")
        print(f"⏱️ Tempo decorrido: {elapsed:.2f} segundos")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"\n❌ [ERRO AO PROCESSAR]: {e}")

if __name__ == "__main__":
    main()
    input("Pressione ENTER para sair...")
