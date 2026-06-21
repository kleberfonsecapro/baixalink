🔹 1. Stack Tecnológica
Python como linguagem principal.

FastAPI para criar a API (rápida, moderna, suporte nativo a JWT).

yt-dlp para baixar vídeos e áudios de YouTube, Facebook, Instagram e Kwai.

Docker para containerização.

Traefik como proxy reverso e servidor web.

JWT para login seguro.

PWA com botão “Adicionar à tela inicial” para transformar em app.

🔹 2. Estrutura da Aplicação
Código
project/
│── backend/
│   ├── main.py          # FastAPI app
│   ├── auth.py          # JWT login
│   ├── downloader.py    # Funções yt-dlp
│   ├── requirements.txt
│── frontend/
│   ├── index.html       # PWA
│   ├── app.js           # Service Worker + botão instalar
│   ├── manifest.json    # Configuração PWA
│── traefik/
│   ├── traefik.yml      # Configuração Traefik
│── docker-compose.yml
🔹 3. Backend (FastAPI + JWT)
Endpoints:

POST /login → gera token JWT.

POST /download → recebe URL + tipo (mp4/mp3).

GET /status/{id} → status do download.

Middleware para validar JWT em todas as rotas protegidas.

🔹 4. Download de Vídeos/Áudios
Biblioteca: yt-dlp.

Funções:

download_video(url) → salva em .mp4.

download_audio(url) → salva em .mp3.

Suporte a múltiplas plataformas (YouTube, Facebook, Instagram, Kwai).

🔹 5. Containerização
Dockerfile para backend.

docker-compose.yml:

Serviço backend (FastAPI).

Serviço traefik (proxy reverso).

Labels para Traefik rotear /api → backend.

🔹 6. Proxy com Traefik
Configuração em traefik.yml:

HTTPS via Let’s Encrypt.

Roteamento automático.

Dashboard habilitado.

🔹 7. PWA + Botão “Transformar em App”
manifest.json define ícone, nome e comportamento.

service-worker.js para cache offline.

Botão “Adicionar à tela inicial” implementado em app.js.

Melhor ferramenta: Workbox (Google) para simplificar cache e instalação.

🔹 8. Fluxo do Usuário
Usuário acessa app via navegador.

Faz login → recebe JWT.

Insere URL do vídeo/áudio.

Backend baixa com yt-dlp.

Usuário baixa arquivo pronto.

PWA oferece botão “Adicionar à tela inicial” → vira app.

🔹 9. Segurança
JWT com expiração curta.

HTTPS obrigatório via Traefik.

Rate limiting para evitar abuso.
