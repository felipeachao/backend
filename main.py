import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

# Configuração CORS para permitir solicitações de qualquer origem (ou configure conforme necessário)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Aceitar requisições de qualquer origem. Para segurança, substitua por uma lista de domínios específicos em produção.
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos HTTP
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)

# Servir arquivos estáticos (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_frontend():   
    return FileResponse("static/index.html")



# Diretório onde os vídeos serão salvos
TMP_DIR = "tmp"

# Certifique-se de que o diretório tmp exista
os.makedirs(TMP_DIR, exist_ok=True)

class VideoRequest(BaseModel):
    url: str

@app.post("/download")
async def download_video(request: VideoRequest):
    url = request.url  # Obtém a URL do corpo da requisição

    cookies_path = "/etc/secrets/cookies.txt"

    visitor_data = os.getenv("YT_VISITOR_DATA")

    # Configuração do yt-dlp para baixar o vídeo
    ydl_opts = {
        'format': 'best',  # Melhor qualidade
        'outtmpl': os.path.join(TMP_DIR, '%(title)s.%(ext)s'),  # Salvar com o nome do vídeo
        'quiet': True,  # Para evitar logs no terminal
        'noplaylist': True,  # Para não baixar listas de reprodução,
        'cookies': cookies_path,  # Usar cookies do arquivo,
                'extractor-args': {
            'youtube': {
                'visitor_data': visitor_data,  # Passar visitor_data aqui
            },}
    }

    try:
        # Baixar o vídeo usando yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_filename = ydl.prepare_filename(info_dict)  # Obter o caminho do arquivo baixado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao baixar o vídeo: {str(e)}")

    # Enviar o arquivo com o nome original
    return FileResponse(video_filename, media_type="video/mp4")