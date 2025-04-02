import streamlit as st
import yt_dlp
import os
import re
from pathlib import Path
import base64

def sanitize_filename(filename):
    # Remove caracteres inválidos para nome de arquivo
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Clique para baixar {file_label}</a>'
    return href

def download_media(url, media_type="audio", output_path="downloads"):
    try:
        # Configurações do yt-dlp
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        if media_type == "audio":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:  # video
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            })
        
        # Cria o diretório se não existir
        os.makedirs(output_path, exist_ok=True)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if media_type == "audio":
                filename = os.path.splitext(filename)[0] + '.mp3'
            
            return filename, None
            
    except Exception as e:
        return None, f"Erro ao baixar {media_type}: {str(e)}"

def download_playlist(url, media_type="audio", output_path="downloads"):
    try:
        downloads = []
        errors = []
        
        ydl_opts = {
            'extract_flat': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if 'entries' in info:  # É uma playlist
                for entry in info['entries']:
                    if entry:  # Algumas entradas podem ser None
                        video_url = entry.get('url')
                        if video_url:
                            filename, error = download_media(video_url, media_type, output_path)
                            if filename:
                                downloads.append(filename)
                            if error:
                                errors.append(error)
        
        return downloads, errors if errors else None
        
    except Exception as e:
        return None, str(e)

# Configuração da página
st.set_page_config(page_title="YouTube Downloader Plus", page_icon="▶️")

# Interface do usuário
st.title("📥 YouTube Downloader Plus")
st.write("Cole a URL do vídeo ou playlist abaixo para começar")

url = st.text_input("", placeholder="https://www.youtube.com/watch?v=...", key="url_input")

# Opções de download
download_type = st.radio("Tipo de download:", ["Vídeo", "Áudio", "Playlist"])

if st.button("Baixar", type="primary"):
    if not url:
        st.error("Por favor, insira uma URL válida do YouTube")
    else:
        with st.spinner("Processando... Aguarde, isso pode levar alguns minutos para playlists grandes"):
            if download_type == "Vídeo":
                filename, error = download_media(url, "video")
                if filename:
                    st.success(f"✅ Vídeo baixado com sucesso!")
                    st.markdown(get_binary_file_downloader_html(filename, "o vídeo"), unsafe_allow_html=True)
                    st.balloons()
                elif error:
                    st.error(f"❌ {error}")
            
            elif download_type == "Áudio":
                filename, error = download_media(url, "audio")
                if filename:
                    st.success(f"✅ Áudio baixado com sucesso!")
                    st.markdown(get_binary_file_downloader_html(filename, "o áudio"), unsafe_allow_html=True)
                    st.balloons()
                elif error:
                    st.error(f"❌ {error}")
            
            elif download_type == "Playlist":
                playlist_download_type = st.radio("Tipo de download para a playlist:", ["Vídeo", "Áudio"])
                
                downloads, errors = download_playlist(url, playlist_download_type.lower())
                if downloads:
                    st.success(f"✅ Playlist baixada com sucesso! {len(downloads)} itens baixados.")
                    st.write("📁 Itens disponíveis para download:")
                    for item in downloads:
                        st.markdown(get_binary_file_downloader_html(item, os.path.basename(item)), unsafe_allow_html=True)
                    st.balloons()
                if errors:
                    st.warning(f"⚠️ Alguns itens não puderam ser baixados ({len(errors)} erros):")
                    for error in errors:
                        st.write(f"- {error}")

# Rodapé
st.markdown("---")
st.markdown("### 📌 Como usar:")
st.write("1. Cole a URL do vídeo ou playlist do YouTube")
st.write("2. Selecione o tipo de download (Vídeo, Áudio ou Playlist)")
st.write("3. Clique no botão 'Baixar'")
st.write("4. Use o link que aparecerá para baixar o arquivo para seu computador")

st.markdown("### ⚠️ Observações:")
st.write("- Para playlists grandes, o download pode demorar vários minutos")
st.write("- Alguns vídeos podem ter restrições de download por decisão do autor")