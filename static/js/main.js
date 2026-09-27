document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const youtubeUrlInput = document.getElementById('youtubeUrl');
    const btnPaste = document.getElementById('btnPaste');
    const btnFetchInfo = document.getElementById('btnFetchInfo');
    const alertBox = document.getElementById('alertBox');
    const alertText = document.getElementById('alertText');
    const infoLoader = document.getElementById('infoLoader');
    
    // Preview
    const videoPreview = document.getElementById('videoPreview');
    const thumbImg = document.getElementById('thumbImg');
    const thumbDuration = document.getElementById('thumbDuration');
    const videoTitle = document.getElementById('videoTitle');
    const videoAuthor = document.getElementById('videoAuthor');
    const btnStartDownload = document.getElementById('btnStartDownload');
    
    // Progress
    const progressContainer = document.getElementById('progressContainer');
    const progressStatusText = document.getElementById('progressStatusText');
    const progressPercent = document.getElementById('progressPercent');
    const progressBar = document.getElementById('progressBar');

    // Result
    const resultCard = document.getElementById('resultCard');
    const resultFileName = document.getElementById('resultFileName');
    const audioPlayer = document.getElementById('audioPlayer');
    const btnDownloadFile = document.getElementById('btnDownloadFile');
    const btnOpenFolder = document.getElementById('btnOpenFolder');
    const btnOpenFolderHeader = document.getElementById('btnOpenFolderHeader');
    const btnReset = document.getElementById('btnReset');

    // History
    const historyList = document.getElementById('historyList');
    const btnRefreshHistory = document.getElementById('btnRefreshHistory');

    // Quality radio options
    const qualityPills = document.querySelectorAll('.quality-pill');

    let currentVideoData = null;

    // Quality Selection Pill logic
    qualityPills.forEach(pill => {
        pill.addEventListener('click', () => {
            qualityPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            const radio = pill.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
        });
    });

    // Paste button
    btnPaste.addEventListener('click', async () => {
        try {
            const text = await navigator.clipboard.readText();
            if (text) {
                youtubeUrlInput.value = text.trim();
                hideAlert();
                if (isValidYoutubeUrl(text.trim())) {
                    fetchVideoInfo();
                }
            }
        } catch (err) {
            showAlert("Permissão de colar negada. Digite ou cole manualmente com Ctrl+V.");
        }
    });

    // Fetch info on enter key
    youtubeUrlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            fetchVideoInfo();
        }
    });

    btnFetchInfo.addEventListener('click', fetchVideoInfo);
    btnStartDownload.addEventListener('click', startDownload);
    btnReset.addEventListener('click', resetUI);
    btnRefreshHistory.addEventListener('click', loadHistory);

    if (btnOpenFolder) btnOpenFolder.addEventListener('click', openDownloadsFolder);
    if (btnOpenFolderHeader) btnOpenFolderHeader.addEventListener('click', openDownloadsFolder);

    // Initial history load
    loadHistory();

    // Functions
    function isValidYoutubeUrl(url) {
        return url.includes('youtube.com/') || url.includes('youtu.be/');
    }

    function showAlert(msg) {
        alertText.textContent = msg;
        alertBox.classList.remove('hidden');
    }

    function hideAlert() {
        alertBox.classList.add('hidden');
    }

    async function fetchVideoInfo() {
        const url = youtubeUrlInput.value.trim();
        hideAlert();

        if (!url) {
            showAlert("Por favor, cole um link do YouTube.");
            return;
        }

        if (!isValidYoutubeUrl(url)) {
            showAlert("Link do YouTube inválido. Exemplo: https://www.youtube.com/watch?v=...");
            return;
        }

        // Show Loader, Hide preview & result
        infoLoader.classList.remove('hidden');
        videoPreview.classList.add('hidden');
        resultCard.classList.add('hidden');
        progressContainer.classList.add('hidden');

        try {
            const res = await fetch('/api/info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            });

            const data = await res.json();
            infoLoader.classList.add('hidden');

            if (data.success) {
                currentVideoData = data.data;
                showPreview(data.data);
            } else {
                showAlert(data.error || "Erro ao obter informações do vídeo.");
            }
        } catch (err) {
            infoLoader.classList.add('hidden');
            showAlert("Erro de conexão ao comunicar com o servidor local.");
        }
    }

    function showPreview(info) {
        thumbImg.src = info.thumbnail || '';
        thumbDuration.textContent = info.duration || '00:00';
        videoTitle.textContent = info.title || 'Vídeo sem título';
        videoAuthor.innerHTML = `<i class="fa-regular fa-user"></i> ${info.uploader || 'Canal'}`;
        videoPreview.classList.remove('hidden');
    }

    async function startDownload() {
        const url = youtubeUrlInput.value.trim();
        if (!url) return;

        const selectedQuality = document.querySelector('input[name="quality"]:checked')?.value || "320";

        // UI transitions
        videoPreview.classList.add('hidden');
        progressContainer.classList.remove('hidden');
        updateProgress(15, "Iniciando processamento e download do áudio...");

        // Simulate step progression
        let timer = setInterval(() => {
            let currentWidth = parseFloat(progressBar.style.width) || 15;
            if (currentWidth < 85) {
                let next = currentWidth + Math.random() * 8;
                if (next > 85) next = 85;
                updateProgress(next, next > 60 ? "Convertendo áudio para MP3 (320kbps)..." : "Baixando dados do vídeo...");
            }
        }, 500);

        try {
            const res = await fetch('/api/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url, quality: selectedQuality })
            });

            clearInterval(timer);
            const data = await res.json();

            if (data.success) {
                updateProgress(100, "Concluído!");
                setTimeout(() => {
                    progressContainer.classList.add('hidden');
                    showResult(data.data);
                    loadHistory();
                }, 400);
            } else {
                progressContainer.classList.add('hidden');
                showAlert(data.error || "Ocorreu um erro durante o download.");
                videoPreview.classList.remove('hidden');
            }
        } catch (err) {
            clearInterval(timer);
            progressContainer.classList.add('hidden');
            showAlert("Erro ao conectar com o servidor durante a conversão.");
            videoPreview.classList.remove('hidden');
        }
    }

    function updateProgress(percent, statusMsg) {
        progressBar.style.width = `${percent}%`;
        progressPercent.textContent = `${Math.round(percent)}%`;
        if (statusMsg) {
            progressStatusText.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin"></i> ${statusMsg}`;
        }
    }

    function showResult(data) {
        resultFileName.textContent = data.filename;
        const safeEncName = encodeURIComponent(data.filename);
        audioPlayer.src = `/api/play/${safeEncName}`;
        btnDownloadFile.href = `/api/file/${safeEncName}`;
        btnDownloadFile.setAttribute('download', data.filename);
        resultCard.classList.remove('hidden');
    }

    function resetUI() {
        youtubeUrlInput.value = '';
        currentVideoData = null;
        videoPreview.classList.add('hidden');
        resultCard.classList.add('hidden');
        progressContainer.classList.add('hidden');
        hideAlert();
        youtubeUrlInput.focus();
    }

    async function openDownloadsFolder() {
        try {
            await fetch('/api/open_folder', { method: 'POST' });
        } catch (e) {
            console.error(e);
        }
    }

    async function loadHistory() {
        try {
            const res = await fetch('/api/list');
            const data = await res.json();

            if (data.success && data.files.length > 0) {
                historyList.innerHTML = '';
                data.files.forEach(file => {
                    const item = document.createElement('div');
                    item.className = 'history-item';
                    const safeEncName = encodeURIComponent(file.filename);
                    item.innerHTML = `
                        <div class="history-item-info">
                            <i class="fa-solid fa-music history-item-icon"></i>
                            <div class="history-item-text">
                                <div class="history-item-title" title="${file.filename}">${file.filename}</div>
                                <div class="history-item-meta">${file.size_mb} MB &bull; MP3</div>
                            </div>
                        </div>
                        <div class="history-item-actions">
                            <a href="/api/file/${safeEncName}" class="btn-icon-small" title="Baixar" download="${file.filename}">
                                <i class="fa-solid fa-download"></i>
                            </a>
                            <button class="btn-icon-small btn-delete" title="Excluir" data-filename="${file.filename}">
                                <i class="fa-solid fa-trash-can"></i>
                            </button>
                        </div>
                    `;
                    historyList.appendChild(item);
                });

                // Attach delete event listeners
                document.querySelectorAll('.btn-delete').forEach(btn => {
                    btn.addEventListener('click', async (e) => {
                        const fname = e.currentTarget.getAttribute('data-filename');
                        if (confirm(`Deseja remover "${fname}" do histórico?`)) {
                            await deleteFile(fname);
                        }
                    });
                });

            } else {
                historyList.innerHTML = `
                    <div class="empty-history">
                        <i class="fa-solid fa-music"></i>
                        <p>Nenhum áudio convertido recentemente.</p>
                    </div>
                `;
            }
        } catch (e) {
            console.error("Erro ao carregar histórico:", e);
        }
    }

    async function deleteFile(filename) {
        try {
            const res = await fetch(`/api/delete/${encodeURIComponent(filename)}`, { method: 'DELETE' });
            const data = await res.json();
            if (data.success) {
                loadHistory();
            }
        } catch (e) {
            console.error("Erro ao deletar arquivo:", e);
        }
    }
});
