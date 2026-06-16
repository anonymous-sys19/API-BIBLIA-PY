const API_BASE = window.location.origin;

const state = {
    videos: [],
    radios: [],
    currentTab: 'videos',
    wsConnected: { videos: false, streams: false }
};

const elements = {
    tabs: document.querySelectorAll('.tab-btn'),
    sections: document.querySelectorAll('.section'),
    videosGrid: document.getElementById('videos-grid'),
    radiosGrid: document.getElementById('radios-grid'),
    videosCount: document.getElementById('videos-count'),
    radiosCount: document.getElementById('radios-count'),
    modalOverlay: document.getElementById('modal-overlay'),
    modal: document.getElementById('modal'),
    modalTitle: document.getElementById('modal-title'),
    modalBody: document.getElementById('modal-body'),
    modalClose: document.getElementById('modal-close'),
    toastContainer: document.getElementById('toast-container'),
    addVideoBtn: document.getElementById('add-video-btn'),
    addRadioBtn: document.getElementById('add-radio-btn'),
    playerOverlay: document.getElementById('player-overlay'),
    playerModal: document.getElementById('player-modal'),
    playerTitle: document.getElementById('player-title'),
    playerBody: document.getElementById('player-body'),
    playerWrapper: document.getElementById('player-wrapper'),
    playerClose: document.getElementById('player-close')
};

// --- CLIENTE WEBSOCKET EN TIEMPO REAL ---

class RealtimeClient {
    constructor(channel, handlers) {
        this.channel = channel;
        this.handlers = handlers;
        this.ws = null;
        this.reconnectDelay = 1000;
        this.connect();
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.ws = new WebSocket(`${protocol}//${window.location.host}/ws/${this.channel}`);

        this.ws.onopen = () => {
            this.reconnectDelay = 1000;
            state.wsConnected[this.channel] = true;
        };

        this.ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                const handler = this.handlers[msg.type];
                if (handler) handler(msg.data, msg);
            } catch (e) {
                console.warn(`WS ${this.channel}: mensaje inválido`, event.data);
            }
        };

        this.ws.onclose = () => {
            state.wsConnected[this.channel] = false;
            setTimeout(() => {
                this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
                this.connect();
            }, this.reconnectDelay);
        };

        this.ws.onerror = () => {
            this.ws.close();
        };
    }

    send(data) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(typeof data === 'string' ? data : JSON.stringify(data));
        }
    }
}

// --- MANEJADORES DE EVENTOS EN TIEMPO REAL ---

function setupRealtime() {
    new RealtimeClient('videos', {
        'video:created': (data) => {
            state.videos.unshift(data);
            renderVideos();
        },
        'video:updated': (data) => {
            const idx = state.videos.findIndex(v => v.id === data.id);
            if (idx !== -1) {
                state.videos[idx] = data;
                renderVideos();
            }
        },
        'video:deleted': (data) => {
            state.videos = state.videos.filter(v => v.id !== data.id);
            renderVideos();
        }
    });

    new RealtimeClient('streams', {
        'stream:created': (data) => {
            state.radios.push(data);
            renderRadios();
        },
        'stream:updated': (data) => {
            const idx = state.radios.findIndex(r => r.id === data.id);
            if (idx !== -1) {
                state.radios[idx] = data;
                renderRadios();
            }
        },
        'stream:deleted': (data) => {
            state.radios = state.radios.filter(r => r.id !== data.id);
            renderRadios();
        }
    });
}

function init() {
    setupTabs();
    setupModal();
    setupPlayer();
    setupButtons();
    setupRealtime();
    loadVideos();
}

function setupTabs() {
    elements.tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;
            switchTab(targetTab);
        });
    });
}

function switchTab(tabName) {
    state.currentTab = tabName;
    
    elements.tabs.forEach(t => {
        t.classList.toggle('active', t.dataset.tab === tabName);
    });
    
    elements.sections.forEach(s => {
        s.classList.toggle('active', s.id === `${tabName}-section`);
    });
    
    if (tabName === 'videos' && state.videos.length === 0) {
        loadVideos();
    } else if (tabName === 'radios' && state.radios.length === 0) {
        loadRadios();
    }
}

function setupModal() {
    elements.modalClose.addEventListener('click', closeModal);
    elements.modalOverlay.addEventListener('click', (e) => {
        if (e.target === elements.modalOverlay) closeModal();
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
}

const playerElements = {
    typeBadge: document.getElementById('player-type-badge'),
    artist: document.getElementById('player-artist'),
    embedInput: document.getElementById('embed-url-input'),
    embedCopyBtn: document.getElementById('embed-copy-btn'),
};

function setupPlayer() {
    elements.playerClose.addEventListener('click', closePlayer);
    elements.playerOverlay.addEventListener('click', (e) => {
        if (e.target === elements.playerOverlay) closePlayer();
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closePlayer();
    });
    playerElements.embedCopyBtn.addEventListener('click', copyEmbedUrl);
}

function openPlayer(video) {
    const isYoutube = video.tipo === 'youtube' || video.tipo === 'video';
    const isSpotify = video.tipo === 'spotify';
    const typeName = isSpotify ? 'Spotify' : 'YouTube';

    elements.playerTitle.textContent = video.titulo;
    playerElements.typeBadge.textContent = typeName;
    playerElements.typeBadge.className = `player-badge ${isSpotify ? 'spotify' : 'youtube'}`;
    playerElements.artist.textContent = video.canal_autor || '';

    let embedUrl, playerUrl;
    if (isYoutube) {
        embedUrl = `https://www.youtube.com/embed/${video.video_id}?autoplay=1`;
        playerUrl = `https://www.youtube.com/watch?v=${video.video_id}`;
    } else if (isSpotify) {
        embedUrl = `https://open.spotify.com/embed/track/${video.video_id}`;
        playerUrl = `https://open.spotify.com/track/${video.video_id}`;
    }

    playerElements.embedInput.value = playerUrl || '';

    elements.playerWrapper.className = `player-wrapper ${isYoutube ? 'youtube' : 'spotify'}`;
    elements.playerWrapper.innerHTML = embedUrl
        ? `<iframe src="${embedUrl}" allow="autoplay; encrypted-media" allowfullscreen loading="lazy"></iframe>`
        : '';

    elements.playerOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closePlayer() {
    elements.playerOverlay.classList.remove('active');
    document.body.style.overflow = '';
    elements.playerWrapper.innerHTML = '';
}

function copyEmbedUrl() {
    const input = playerElements.embedInput;
    input.select();
    navigator.clipboard.writeText(input.value).then(() => {
        playerElements.embedCopyBtn.classList.add('copied');
        playerElements.embedCopyBtn.innerHTML = '<i class="ph ph-check"></i>';
        setTimeout(() => {
            playerElements.embedCopyBtn.classList.remove('copied');
            playerElements.embedCopyBtn.innerHTML = '<i class="ph ph-copy-simple"></i>';
        }, 2000);
    });
}

function setupButtons() {
    elements.addVideoBtn.addEventListener('click', () => openVideoForm());
    elements.addRadioBtn.addEventListener('click', () => openRadioForm());
}

async function loadVideos() {
    try {
        elements.videosGrid.innerHTML = `
            <div class="loading-state">
                <i class="ph ph-spinner-gap spin"></i>
                <p>Cargando videos...</p>
            </div>
        `;
        
        const response = await fetch(`${API_BASE}/videos`);
        if (!response.ok) throw new Error('Error al cargar videos');
        
        state.videos = await response.json();
        renderVideos();
    } catch (error) {
        elements.videosGrid.innerHTML = `
            <div class="empty-state">
                <i class="ph ph-warning-circle"></i>
                <p>Error al cargar videos</p>
            </div>
        `;
        showToast('Error al cargar videos', 'error');
    }
}

async function loadRadios() {
    try {
        elements.radiosGrid.innerHTML = `
            <div class="loading-state">
                <i class="ph ph-spinner-gap spin"></i>
                <p>Cargando radios...</p>
            </div>
        `;
        
        const response = await fetch(`${API_BASE}/stream`);
        if (!response.ok) throw new Error('Error al cargar radios');
        
        state.radios = await response.json();
        renderRadios();
    } catch (error) {
        elements.radiosGrid.innerHTML = `
            <div class="empty-state">
                <i class="ph ph-warning-circle"></i>
                <p>Error al cargar radios</p>
            </div>
        `;
        showToast('Error al cargar radios', 'error');
    }
}

async function refreshAfterMutate(channel) {
    if (!state.wsConnected[channel]) {
        if (channel === 'videos') await loadVideos();
        else await loadRadios();
    }
}

function renderVideos() {
    elements.videosCount.textContent = state.videos.length;
    
    if (state.videos.length === 0) {
        elements.videosGrid.innerHTML = `
            <div class="empty-state">
                <i class="ph ph-video-camera-slash"></i>
                <p>No hay videos registrados</p>
                <p>Agrega tu primer video con el boton de arriba</p>
            </div>
        `;
        return;
    }
    
    elements.videosGrid.innerHTML = state.videos.map((video, index) => {
        const isYoutube = video.tipo === 'youtube';
        const isSpotify = video.tipo === 'spotify';
        const typeIcon = isYoutube ? 'ph-video-camera' : 'ph-music-note';
        const typeLabel = isYoutube ? 'YouTube' : 'Spotify';
        return `
        <div class="card" style="--index: ${index}" onclick="openPlayer(state.videos[${index}])">
            <div class="card-thumbnail">
                ${video.miniatura_url 
                    ? `<img src="${video.miniatura_url}" alt="${video.titulo}" loading="lazy">`
                    : `<div class="card-thumbnail-placeholder"><i class="ph ${typeIcon}"></i></div>`
                }
            </div>
            <div class="card-body">
                <h3 class="card-title">${video.titulo}</h3>
                <div class="card-meta">
                    <i class="ph ph-user-circle"></i>
                    <span>${video.canal_autor || 'Sin canal'}</span>
                </div>
                <div class="card-tags">
                    <span class="tag ${isSpotify ? 'tag-green' : 'tag-blue'}">${typeLabel}</span>
                    <span class="tag tag-blue">${video.video_id}</span>
                    ${video.fecha_registro ? `<span class="tag tag-yellow">${formatDate(video.fecha_registro)}</span>` : ''}
                </div>
            </div>
            <div class="card-actions" onclick="event.stopPropagation()">
                <button class="btn-icon" onclick="openVideoForm(${video.id})" title="Editar">
                    <i class="ph ph-pencil-simple"></i>
                </button>
                <button class="btn-icon danger" onclick="deleteVideo(${video.id})" title="Eliminar">
                    <i class="ph ph-trash"></i>
                </button>
            </div>
        </div>
    `}).join('');
    
    observeCards();
}

function renderRadios() {
    elements.radiosCount.textContent = state.radios.length;
    
    if (state.radios.length === 0) {
        elements.radiosGrid.innerHTML = `
            <div class="empty-state">
                <i class="ph ph-radio"></i>
                <p>No hay estaciones de radio</p>
                <p>Agrega tu primera estacion con el boton de arriba</p>
            </div>
        `;
        return;
    }
    
    elements.radiosGrid.innerHTML = state.radios.map((radio, index) => `
        <div class="card radio-card" style="--index: ${index}">
            <div class="card-body">
                <div class="card-header-info">
                    <div class="radio-logo">
                        ${radio.logo_url 
                            ? `<img src="${radio.logo_url}" alt="${radio.nombre}" loading="lazy">`
                            : `<div class="radio-logo-placeholder"><i class="ph ph-radio"></i></div>`
                        }
                    </div>
                    <div class="radio-info">
                        <h3>${radio.nombre}</h3>
                        <p>${radio.genero || 'Genero no especificado'}</p>
                    </div>
                </div>
                <div class="radio-details">
                    <div class="detail-row">
                        <i class="ph ph-globe"></i>
                        <span>${radio.pais || 'Pais no especificado'}</span>
                    </div>
                    <div class="detail-row">
                        <i class="ph ph-link"></i>
                        <span style="word-break: break-all; font-family: var(--font-mono); font-size: 0.75rem;">${radio.url_stream}</span>
                    </div>
                    <div class="detail-row">
                        <div class="status-indicator">
                            <span class="status-dot ${radio.status !== 'online' ? 'offline' : ''}"></span>
                            <span>${radio.status || 'online'}</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="card-actions">
                <button class="btn-icon" onclick="openRadioForm(${radio.id})" title="Editar">
                    <i class="ph ph-pencil-simple"></i>
                </button>
                <button class="btn-icon danger" onclick="deleteRadio(${radio.id})" title="Eliminar">
                    <i class="ph ph-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
    
    observeCards();
}

function observeCards() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, index * 80);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.card').forEach(card => observer.observe(card));
}

function openVideoForm(videoId = null) {
    const video = videoId ? state.videos.find(v => v.id === videoId) : null;
    const isEdit = !!video;
    
    elements.modalTitle.textContent = isEdit ? 'Editar Video' : 'Agregar Video';
    
    elements.modalBody.innerHTML = `
        <form id="video-form">
            ${!isEdit ? `
                <div class="form-group">
                    <label class="form-label">URL de YouTube / Spotify</label>
                    <input type="url" class="form-input" name="url" placeholder="https://www.youtube.com/watch?v=... o https://open.spotify.com/track/..." required>
                </div>
            ` : `
                <div class="form-group">
                    <label class="form-label">Titulo</label>
                    <input type="text" class="form-input" name="titulo" value="${video.titulo}" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Canal / Autor</label>
                    <input type="text" class="form-input" name="canal_autor" value="${video.canal_autor || ''}">
                </div>
                <div class="form-group">
                    <label class="form-label">URL de Miniatura</label>
                    <input type="url" class="form-input" name="miniatura_url" value="${video.miniatura_url || ''}">
                </div>
            `}
            <div class="form-actions">
                <button type="button" class="btn-secondary" onclick="closeModal()">Cancelar</button>
                <button type="submit" class="btn-submit">${isEdit ? 'Guardar Cambios' : 'Agregar'}</button>
            </div>
        </form>
    `;
    
    document.getElementById('video-form').addEventListener('submit', (e) => {
        e.preventDefault();
        if (isEdit) {
            updateVideo(videoId, new FormData(e.target));
        } else {
            createVideo(new FormData(e.target));
        }
    });
    
    openModal();
}

async function createVideo(formData) {
    const url = formData.get('url');
    
    try {
        const response = await fetch(`${API_BASE}/videos/add?url=${encodeURIComponent(url)}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error al crear video');
        }
        
        closeModal();
        showToast('Video agregado exitosamente', 'success');
        refreshAfterMutate('videos');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function updateVideo(videoId, formData) {
    const data = {
        id: videoId,
        video_id: state.videos.find(v => v.id === videoId).video_id,
        titulo: formData.get('titulo'),
        canal_autor: formData.get('canal_autor') || null,
        tipo: state.videos.find(v => v.id === videoId).tipo,
        miniatura_url: formData.get('miniatura_url') || null
    };
    
    try {
        const response = await fetch(`${API_BASE}/videos/${videoId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) throw new Error('Error al actualizar video');
        
        closeModal();
        showToast('Video actualizado exitosamente', 'success');
        refreshAfterMutate('videos');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function deleteVideo(videoId) {
    if (!confirm('Estas seguro de eliminar este video?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/videos/${videoId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Error al eliminar video');
        
        showToast('Video eliminado', 'success');
        refreshAfterMutate('videos');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function openRadioForm(radioId = null) {
    const radio = radioId ? state.radios.find(r => r.id === radioId) : null;
    const isEdit = !!radio;
    
    elements.modalTitle.textContent = isEdit ? 'Editar Radio' : 'Agregar Radio';
    
    elements.modalBody.innerHTML = `
        <form id="radio-form">
            <div class="form-group">
                <label class="form-label">Nombre de la Estacion</label>
                <input type="text" class="form-input" name="nombre" value="${radio?.nombre || ''}" placeholder="Radio Aleluya" required>
            </div>
            <div class="form-group">
                <label class="form-label">URL del Stream</label>
                <input type="url" class="form-input" name="url_stream" value="${radio?.url_stream || ''}" placeholder="http://servidor.com:8000/stream" required>
            </div>
            <div class="form-group">
                <label class="form-label">Pais</label>
                <input type="text" class="form-input" name="pais" value="${radio?.pais || ''}" placeholder="Costa Rica">
            </div>
            <div class="form-group">
                <label class="form-label">Genero</label>
                <input type="text" class="form-input" name="genero" value="${radio?.genero || ''}" placeholder="Cristiana">
            </div>
            <div class="form-group">
                <label class="form-label">URL del Logo</label>
                <input type="url" class="form-input" name="logo_url" value="${radio?.logo_url || ''}" placeholder="https://...">
            </div>
            <div class="form-group">
                <label class="form-label">Estado</label>
                <select class="form-select" name="status">
                    <option value="online" ${radio?.status === 'online' ? 'selected' : ''}>Online</option>
                    <option value="offline" ${radio?.status === 'offline' ? 'selected' : ''}>Offline</option>
                </select>
            </div>
            <div class="form-actions">
                <button type="button" class="btn-secondary" onclick="closeModal()">Cancelar</button>
                <button type="submit" class="btn-submit">${isEdit ? 'Guardar Cambios' : 'Agregar'}</button>
            </div>
        </form>
    `;
    
    document.getElementById('radio-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        if (isEdit) {
            updateRadio(radioId, formData);
        } else {
            createRadio(formData);
        }
    });
    
    openModal();
}

async function createRadio(formData) {
    const data = {
        id: null,
        nombre: formData.get('nombre'),
        url_stream: formData.get('url_stream'),
        pais: formData.get('pais') || 'Costa Rica',
        genero: formData.get('genero') || 'Cristiana',
        logo_url: formData.get('logo_url') || null,
        status: formData.get('status') || 'online'
    };
    
    try {
        const response = await fetch(`${API_BASE}/stream/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) throw new Error('Error al crear radio');
        
        closeModal();
        showToast('Radio agregada exitosamente', 'success');
        refreshAfterMutate('streams');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function updateRadio(radioId, formData) {
    const data = {
        id: radioId,
        nombre: formData.get('nombre'),
        url_stream: formData.get('url_stream'),
        pais: formData.get('pais'),
        genero: formData.get('genero'),
        logo_url: formData.get('logo_url') || null,
        status: formData.get('status')
    };
    
    try {
        const response = await fetch(`${API_BASE}/stream/${radioId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) throw new Error('Error al actualizar radio');
        
        closeModal();
        showToast('Radio actualizada exitosamente', 'success');
        refreshAfterMutate('streams');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function deleteRadio(radioId) {
    if (!confirm('Estas seguro de eliminar esta radio?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/stream/${radioId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Error al eliminar radio');
        
        showToast('Radio eliminada', 'success');
        refreshAfterMutate('streams');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function openModal() {
    elements.modalOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    elements.modalOverlay.classList.remove('active');
    document.body.style.overflow = '';
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="ph ph-${type === 'success' ? 'check-circle' : 'warning-circle'}"></i>
        <span>${message}</span>
    `;
    elements.toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(20px)';
        setTimeout(() => toast.remove(), 200);
    }, 3000);
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('es-ES', { 
        day: '2-digit', 
        month: 'short',
        year: 'numeric'
    });
}

document.addEventListener('DOMContentLoaded', init);
