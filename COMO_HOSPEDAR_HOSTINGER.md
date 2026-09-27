# ☁️ Como Hospedar o Conversor de YouTube para MP3 na Hostinger

Para rodar uma aplicação Python que faz download e conversão de áudio usando `yt-dlp` e `ffmpeg`, o tipo de hospedagem correto faz toda a diferença.

---

## 📌 Requisito Fundamental: Qual plano da Hostinger escolher?

| Tipo de Hospedagem Hostinger | É compatível? | Motivo |
| :--- | :---: | :--- |
| **VPS (Servidor Virtual Privado)** | ✅ **100% RECOMENDADO** | Dá acesso root total para instalar o `ffmpeg`, rodar serviços em segundo plano (Systemd/Gunicorn) e usar portas personalizadas. |
| **Hospedagem Compartilhada / Cloud** | ⚠️ **LIMITADO / NÃO RECOMENDADO** | Planos compartilhados bloqueiam a execução de binares externos como `ffmpeg` via terminal e possuem limites rígidos de subprocessos. |

---

## 🚀 Passo a Passo: Hospedando na VPS Hostinger (Ubuntu / Debian)

### 1. Conectar à VPS via SSH
Abra o seu terminal (CMD, PowerShell ou PuTTY) e conecte ao seu servidor Hostinger:
```bash
ssh root@IP_DO_SEU_SERVIDOR
```
*(Substitua `IP_DO_SEU_SERVIDOR` pelo IP fornecido no painel da Hostinger).*

---

### 2. Instalar o Python e o FFmpeg no Servidor
Execute os comandos abaixo para atualizar o sistema e instalar o Python, PIP, Nginx e o FFmpeg:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv ffmpeg nginx git
```

Verifique se o FFmpeg foi instalado com sucesso:
```bash
ffmpeg -version
```

---

### 3. Enviar o Código do Projeto para o Servidor
Você pode enviar a pasta via SFTP (FileZilla) para `/var/www/ytmp3` ou clonar via Git:
```bash
mkdir -p /var/www/ytmp3
cd /var/www/ytmp3
```
*Copie todos os arquivos do projeto (`app.py`, `utils_yt.py`, `templates/`, `static/`, `requirements.txt`) para este diretório.*

---

### 4. Criar o Ambiente Virtual Python e Instalar Dependências
No diretório `/var/www/ytmp3`:
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências e o servidor de produção Gunicorn
pip install -r requirements.txt
pip install gunicorn
```

---

### 5. Criar um Serviço no Linux (Systemd) para rodar 24/7
Crie o arquivo de serviço para que a aplicação fique sempre ativa em segundo plano:
```bash
sudo nano /etc/systemd/system/ytmp3.service
```

Cole a seguinte configuração:
```ini
[Unit]
Description=Servidor YTMP3 Pro Flask
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/ytmp3
ExecStart=/var/www/ytmp3/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Salve e feche o arquivo (`Ctrl + O`, `Enter`, `Ctrl + X`).

Agora inicie e ative o serviço:
```bash
sudo systemctl daemon-reload
sudo systemctl start ytmp3
sudo systemctl enable ytmp3
```

Para verificar se o aplicativo está rodando:
```bash
sudo systemctl status ytmp3
```

---

### 6. Configurar o Nginx como Proxy Reverso
Abra o arquivo de configuração do Nginx:
```bash
sudo nano /etc/nginx/sites-available/ytmp3
```

Cole o código abaixo (substitua `seu-dominio.com` pelo seu domínio ou IP):
```nginx
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Ative a configuração no Nginx e reinicie o servidor web:
```bash
sudo ln -s /etc/nginx/sites-available/ytmp3 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### 7. Ativar Certificado SSL Grátis (HTTPS)
Para que seu site abra com `https://` com o cadeado de segurança verde:
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

---

1. **Render.com:** Suporta Web Services em Python com `ffmpeg` via Docker ou Buildpacks sem os limites rígidos de tempo da Vercel.
2. **Railway.app:** Implantação direta de repositórios Python com suporte a contêineres Docker.

---

## ❓ É possível rodar na Vercel?

**Não é recomendado** para este tipo de aplicação. A Vercel é feita para sites estáticos e APIs Serverless curtas. 

### Motivos técnicos pelos quais a Vercel não funciona bem:
1. **Timeout de 10-15 segundos:** Funções na Vercel expiram após 10 a 15 segundos. O download e conversão de vídeos longos estoura esse limite e dá erro `504 Gateway Timeout`.
2. **Falta do FFmpeg:** A Vercel não possui o `ffmpeg` instalado no ambiente serverless.
3. **Sem Armazenamento Persistente:** O disco da Vercel é somente leitura (exceto `/tmp`), logo os arquivos baixados na pasta `downloads/` somem a cada requisição.
4. **Bloqueios do YouTube:** Os IPs de funções serverless da Vercel (AWS) são frequentemente bloqueados pelo YouTube.

> 💡 **Conclusão:** Para aplicações com **Python + yt-dlp + FFmpeg**, use **VPS Hostinger** (para produção) ou **Render.com / Railway.app** (para testes gratuitos).
