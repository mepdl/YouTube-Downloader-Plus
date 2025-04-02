import streamlit as st
import yt_dlp
import os
import re
import time
from pathlib import Path
import logging
from functools import partial

# Configurações iniciais
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sanitize_filename(filename):
    """Remove caracteres inválidos de nomes de arquivos"""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def clean_ansi_codes(text):
    """Remove códigos ANSI de cores do texto"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def progress_hook(progress_bar, d):
    """Função para exibir o progresso limpo"""
    if d['status'] == 'downloading':
        # Limpa os códigos ANSI e formata a mensagem
        percent = clean_ansi_codes(d.get('_percent_str', '0.0%'))
        speed = clean_ansi_codes(d.get('_speed_str', '?'))
        eta = clean_ansi_codes(d.get('_eta_str', '?'))
        
        # Atualiza a barra de progresso
        try:
            percent_float = float(percent.strip('%'))/100
            progress_bar.progress(percent_float)
        except:
            pass
        
        # Exibe informações detalhadas
        st.session_state.progress_text = f"📥 Progresso: {percent} | 🚀 Velocidade: {speed} | ⏳ Tempo restante: {eta}"

def download_single(url, media_type, progress_bar):
    """Baixa um único vídeo/áudio"""
    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'progress_hooks': [partial(progress_hook, progress_bar)],
            'quiet': True,
            'no_color': True,  # Desativa cores ANSI
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
        else:
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if media_type == "audio":
                filename = os.path.splitext(filename)[0] + '.mp3'
            
            return filename, None

    except Exception as e:
        logger.error(f"Erro no download: {str(e)}")
        return None, f"Erro: {str(e)}"

def main():
    st.set_page_config(page_title="YouTube Downloader Ultra", page_icon="🎵")
    st.title("🎵 YouTube Downloader Ultra")
    st.write("Cole a URL do YouTube abaixo para baixar vídeos ou áudios")

    # Inicializa variáveis de sessão
    if 'progress_text' not in st.session_state:
        st.session_state.progress_text = "Aguardando início do download..."

    url = st.text_input("URL do YouTube:", placeholder="https://www.youtube.com/watch?v=...")
    media_type = st.radio("Tipo de mídia:", ["Áudio MP3", "Vídeo MP4"])

    if st.button("Iniciar Download", type="primary"):
        if not url:
            st.error("Por favor, insira uma URL válida")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner(f"Preparando download de {media_type}..."):
                file_path, error = download_single(url, "audio" if "MP3" in media_type else "video", progress_bar)
                
                if file_path:
                    progress_bar.progress(100)
                    st.success("✅ Download concluído com sucesso!")
                    st.balloons()
                    
                    # Mostra o botão de download
                    with open(file_path, "rb") as file:
                        btn = st.download_button(
                            label="Clique para baixar o arquivo",
                            data=file,
                            file_name=os.path.basename(file_path),
                            mime="audio/mp3" if file_path.endswith(".mp3") else "video/mp4"
                        )
                    
                    # Mostra preview
                    if media_type == "Áudio MP3":
                        st.audio(file_path)
                    else:
                        st.video(file_path)
                else:
                    st.error(f"❌ {error}")
            
            # Limpa o progresso após conclusão
            progress_bar.empty()
            status_text.empty()

    # Exibe informações de progresso atualizadas
    st.markdown(f"**Status:** {st.session_state.progress_text}")

    st.markdown("---")
    st.write("🔍 **Dicas:**")
    st.write("- Para melhores resultados, use URLs de vídeos públicos")
    st.write("- Se o download falhar, tente com um vídeo diferente")
    st.write("- Downloads podem demorar alguns minutos para vídeos longos")

if __name__ == "__main__":
    main()
