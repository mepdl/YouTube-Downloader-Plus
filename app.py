import streamlit as st
import yt_dlp
import os
import re
import time
from pathlib import Path
from functools import partial

# Configurações
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def sanitize_filename(filename):
    """Remove caracteres inválidos de nomes de arquivos"""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def progress_hook(progress_bar, d):
    """Função para exibir o progresso"""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0.0%').strip()
        try:
            progress_bar.progress(float(percent.replace('%',''))/100)
        except:
            pass

def download_media(url, media_type, progress_bar):
    """Baixa vídeo/áudio com configurações especiais"""
    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'progress_hooks': [partial(progress_hook, progress_bar)],
            'quiet': True,
            'no_warnings': True,
            # Configurações para contornar bloqueios
            'extract_flat': False,
            'ignoreerrors': True,
            'cookiefile': 'cookies.txt',  # Opcional: usar cookies de login
            'referer': 'https://www.youtube.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_client': ['android', 'web']
                }
            },
            'format': 'bestaudio/best' if media_type == "audio" else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }] if media_type == "audio" else []
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if media_type == "audio":
                filename = os.path.splitext(filename)[0] + '.mp3'
            
            return filename, None

    except Exception as e:
        return None, str(e)

def main():
    st.set_page_config(page_title="YouTube Downloader Pro", page_icon="🎬")
    st.title("🎬 YouTube Downloader Pro")
    st.write("Versão com proteção contra bloqueios do YouTube")

    url = st.text_input("URL do YouTube:", placeholder="https://www.youtube.com/watch?v=...")
    media_type = st.radio("Tipo de mídia:", ["Áudio MP3", "Vídeo MP4"])

    if st.button("Iniciar Download", type="primary"):
        if not url:
            st.error("Por favor, insira uma URL válida")
        else:
            progress_bar = st.progress(0)
            status_area = st.empty()
            
            with st.spinner("Preparando download..."):
                file_path, error = download_media(
                    url, 
                    "audio" if "MP3" in media_type else "video",
                    progress_bar
                )
                
                if file_path:
                    progress_bar.progress(100)
                    st.success("✅ Download concluído!")
                    
                    with open(file_path, "rb") as f:
                        st.download_button(
                            "Baixar Arquivo",
                            f,
                            file_name=os.path.basename(file_path),
                            mime="audio/mp3" if media_type == "Áudio MP3" else "video/mp4"
                        )
                    
                    if media_type == "Áudio MP3":
                        st.audio(file_path)
                    else:
                        st.video(file_path)
                else:
                    st.error(f"❌ Falha: {error}")
                    
                    # Solução alternativa sugerida
                    if "Sign in to confirm you're not a bot" in error:
                        st.warning("""
                        **Solução alternativa:**
                        1. Acesse https://ytdl-org.github.io/youtube-dl/download.html
                        2. Baixe o arquivo `cookies.txt` após fazer login no YouTube
                        3. Coloque o arquivo na mesma pasta do aplicativo
                        4. Tente novamente
                        """)

            progress_bar.empty()

if __name__ == "__main__":
    main()
