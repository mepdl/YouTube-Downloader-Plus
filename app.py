import streamlit as st
import yt_dlp
import os
import re
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

def safe_download(url, ydl_opts):
    """Executa o download com tratamento de erros robusto"""
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Primeiro verifica se o vídeo está disponível
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return None, "Não foi possível obter informações do vídeo"
            
            # Executa o download
            result = ydl.download([url])
            if result != 0:
                return None, "Falha no processo de download"
            
            filename = ydl.prepare_filename(info)
            return filename, None
            
    except yt_dlp.utils.DownloadError as e:
        return None, f"Erro no download: {str(e)}"
    except yt_dlp.utils.ExtractorError as e:
        return None, f"Erro ao extrair informações: {str(e)}"
    except Exception as e:
        return None, f"Erro inesperado: {str(e)}"

def download_media(url, media_type, progress_bar):
    """Configura e executa o download"""
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'progress_hooks': [partial(progress_hook, progress_bar)],
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'extractor_args': {'youtube': {'skip': ['hls']}},
        'format': 'bestaudio/best' if media_type == "audio" else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if media_type == "audio" else [],
        'retries': 3,
        'fragment_retries': 3,
        'skip_unavailable_fragments': True
    }

    filename, error = safe_download(url, ydl_opts)
    if filename and media_type == "audio":
        filename = os.path.splitext(filename)[0] + '.mp3'
    
    return filename, error

def main():
    st.set_page_config(page_title="YouTube Downloader Pro", page_icon="🎬")
    st.title("🎬 YouTube Downloader Pro")
    st.write("Versão com tratamento de erros aprimorado")

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
                    
                    # Soluções alternativas
                    st.warning("""
                    **Tente estas soluções:**
                    1. Verifique se a URL está correta
                    2. Tente um vídeo diferente
                    3. Atualize o yt-dlp: `pip install --upgrade yt-dlp`
                    4. Espere alguns minutos e tente novamente
                    """)

            progress_bar.empty()

if __name__ == "__main__":
    main()
