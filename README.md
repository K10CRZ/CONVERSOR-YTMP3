# 🎵 Conversor de YouTube para MP3 (YTMP3 Pro)

Um programa simples, rápido e elegante para converter e baixar áudios de vídeos do YouTube em formato **MP3 de alta qualidade (320 kbps)**.

---

## 🌟 Funcionalidades

- **Interface Web Moderna (Glassmorphic Dark UI):** Visual moderno, intuitivo e com prévia do vídeo.
- **Áudio em Alta Definição:** Escolha a taxa de bits desejada (**320 kbps HD**, 256 kbps, 192 kbps ou 128 kbps).
- **Player Integrado:** Ouça o MP3 diretamente no seu navegador antes ou depois de baixar.
- **Modo Terminal / CLI:** Execução direta no terminal com barra de progresso em tempo real.
- **Histórico de Downloads:** Acesse seus arquivos convertidos anteriormente com 1 clique.
- **Sem complicações:** Não exige configuração manual de FFmpeg (gerenciado automaticamente pelo sistema).

---

## 🚀 Como Usar

### Opção 1: Interface Gráfica / Web (Recomendado)
1. Dê **dois cliques** no arquivo `iniciar_conversor.bat`.
2. O programa abrirá automaticamente a página no seu navegador (`http://127.0.0.1:5000`).
3. Cole o link do YouTube, veja a prévia e clique em **Converter e Baixar MP3**.

### Opção 2: Linha de Comando (CLI)
1. Dê **dois cliques** no arquivo `iniciar_cli.bat` ou execute no terminal:
   ```bash
   python converter_cli.py
   ```
2. Cole a URL do YouTube quando solicitado.

---

## 📁 Onde os arquivos são salvos?

Todos os arquivos MP3 convertidos são armazenados na pasta `downloads/` dentro do próprio projeto. Você também pode clicar no botão **"Abrir Pasta"** na interface web para acessar os arquivos no Windows Explorer.

---

## 🛠️ Requisitos Técnicos

- **Python 3.8+**
- Pacotes Python necessários: `yt-dlp`, `flask`, `imageio-ffmpeg`, `requests`
  *(Para instalar manualmente se necessário: `pip install -r requirements.txt`)*
