const API_BASE = window.location.origin;
// const PRODUCTION_HOSTNAME = 'api-biblia-py.onrender.com'; // Define your production hostname here
const state = {
    videos: [],
    radios: [],
    guias: [],
    currentTab: 'videos',
    wsConnected: { videos: false, streams: false, biblia: false }
};

function setupGuideViewer() {
    const overlay = document.getElementById('guia-viewer-overlay');
    const closeBtn = document.getElementById('guia-viewer-close');
    closeBtn.addEventListener('click', () => {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    });
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') overlay.classList.remove('active');
    });
}

function openGuideViewer(guideId) {
    const overlay = document.getElementById('guia-viewer-overlay');
    const titleEl = document.getElementById('guia-viewer-title');
    const metaEl = document.getElementById('guia-viewer-meta');
    const contentEl = document.getElementById('guia-viewer-content');
    const versesListEl = document.getElementById('guia-verses-list');

    fetch(`${API_BASE}/guide/${guideId}?html=true`)
        .then(r => r.json())
        .then(guide => {
            titleEl.textContent = guide.title;
            metaEl.innerHTML = `
                <div class="guia-meta-row">
                    <span><i class="ph ph-user"></i> ${guide.author || 'Anónimo'}</span>
                    <span><i class="ph ph-tag"></i> ${guide.tag_list?.join(', ') || guide.tags || 'Sin tags'}</span>
                    <span><i class="ph ph-calendar"></i> ${guide.created_at ? new Date(guide.created_at).toLocaleDateString() : ''}</span>
                </div>
            `;
            contentEl.innerHTML = guide.content_html || guide.content.replace(/\n/g, '<br>');

            if (guide.versiculos && guide.versiculos.length > 0) {
                versesListEl.innerHTML = guide.versiculos.map(ref => {
                    const bookSlug = ref.book_name
                        ? ref.book_name.toLowerCase()
                            .replace(/[éÉ]/g, 'e').replace(/[íÍ]/g, 'i') // ejemplo cuando: "1 Samuel" -> "1 samuel"
                            .replace(/[óÓ]/g, 'o').replace(/[úÚ]/g, 'u') // ejemplo cuando: "1 Samuel" -> "1 samuel"
                            .replace(/[áÁ]/g, 'a').replace(/\s+/g, ' ') // ejemplo cuando: "1 Samuel" -> "1%samuel"
                        // cambiamos el 1-juan por 1 juan: 
                            .replace(/-/g, ' ')
                        : `bible/${ref.book_id}`;
                    return `
                    <a href="/${bookSlug}/${ref.chapter}/${ref.verse_start}" target="_blank" class="guia-verse-ref" data-book="${ref.book_id}" data-chapter="${ref.chapter}" data-verse="${ref.verse_start}">
                        <i class="ph ph-book-open"></i>
                        ${ref.reference}
                    </a>`;
                }).join('');
                document.getElementById('guia-viewer-verses').style.display = 'block';
            } else {
                document.getElementById('guia-viewer-verses').style.display = 'none';
            }

            overlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        })
        .catch(err => {
            showToast('Error al cargar guía: ' + err.message, 'error');
        });
}

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
    addGuiaBtn: document.getElementById('add-guia-btn'),
    importBtn: document.getElementById('import-video-btn'),
    importOverlay: document.getElementById('import-overlay'),
    importModal: document.getElementById('import-modal'),
    importTitle: document.getElementById('import-title'),
    importClose: document.getElementById('import-close'),
    importForm: document.getElementById('import-form'),
    importSubmit: document.getElementById('import-submit-btn'),
    importPreviewBtn: document.getElementById('import-preview-btn'),
    importResults: document.getElementById('import-results'),
    importSummary: document.getElementById('import-summary'),
    importList: document.getElementById('import-list'),
    importLoading: document.getElementById('import-loading'),
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
    new RealtimeClient('biblia', {
        'guide:created': (data) => {
            state.guias.unshift(data);
            renderGuias();
        },
        'guide:updated': (data) => {
            const idx = state.guias.findIndex(g => g.id === data.id);
            if (idx !== -1) {
                state.guias[idx] = data;
                renderGuias();
            }
        },
        'guide:deleted': (data) => {
            state.guias = state.guias.filter(g => g.id !== data.id);
            renderGuias();
        }
    });

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
    setupGuideViewer();
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
    } else if (tabName === 'guias' && state.guias.length === 0) {
        loadGuias();
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

let _importPreviewData = null;

function setupButtons() {
    elements.addVideoBtn.addEventListener('click', () => openVideoForm());
    elements.addRadioBtn.addEventListener('click', () => openRadioForm());
    elements.addGuiaBtn.addEventListener('click', () => openGuiaForm());
    elements.importBtn.addEventListener('click', () => openImport());
    elements.importClose.addEventListener('click', closeImport);
    elements.importOverlay.addEventListener('click', (e) => {
        if (e.target === elements.importOverlay) closeImport();
    });
    elements.importPreviewBtn.addEventListener('click', () => {
        const url = new FormData(elements.importForm).get('url');
        if (!url) return showToast('Ingresa una URL', 'error');
        previewImport(url);
    });
    elements.importForm.addEventListener('submit', (e) => {
        e.preventDefault();
        if (!_importPreviewData) return;
        confirmImport();
    });
}

function openImport() {
    _importPreviewData = null;
    elements.importResults.style.display = 'none';
    elements.importLoading.style.display = 'none';
    elements.importSubmit.style.display = 'none';
    elements.importPreviewBtn.style.display = '';
    elements.importForm.reset();
    elements.importOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeImport() {
    _importPreviewData = null;
    elements.importOverlay.classList.remove('active');
    document.body.style.overflow = '';
    const toolbar = document.querySelector('.import-toolbar');
    if (toolbar) toolbar.remove();
}

async function previewImport(url) {
    elements.importLoading.style.display = 'block';
    elements.importResults.style.display = 'none';
    elements.importSubmit.style.display = 'none';
    elements.importPreviewBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/videos/import/preview`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            const detail = err.detail;
            const msg = Array.isArray(detail) ? detail.map(d => d.msg || d).join('; ') : (detail || 'Error al obtener vista previa');
            throw new Error(msg);
        }
        const data = await response.json();
        _importPreviewData = data;

        const total = data.total || data.videos?.length || 0;
        elements.importSummary.textContent = `${total} videos encontrados`;

        elements.importList.innerHTML = (data.videos || []).map((v, i) => `
            <label class="import-list-item">
                <input type="checkbox" class="import-checkbox" data-idx="${i}" checked>
                ${v.miniatura_url ? `<img src="${v.miniatura_url}" class="import-thumb" loading="lazy">` : ''}
                <span class="import-title">${v.titulo}</span>
            </label>
        `).join('') || '<p style="color:var(--color-text-muted);text-align:center;padding:2rem">No se encontraron videos</p>';

        const toolbar = document.createElement('div');
        toolbar.className = 'import-toolbar';
        toolbar.innerHTML = `
            <span class="import-selected-count" id="import-selected-count">${total} seleccionados</span>
            <button class="import-toggle-all" id="import-toggle-all">Deselect all</button>
        `;
        elements.importList.parentNode.insertBefore(toolbar, elements.importList);

        document.getElementById('import-toggle-all').addEventListener('click', () => {
            const checkboxes = elements.importList.querySelectorAll('.import-checkbox');
            const allChecked = Array.from(checkboxes).every(cb => cb.checked);
            checkboxes.forEach(cb => cb.checked = !allChecked);
            document.getElementById('import-toggle-all').textContent = allChecked ? 'Select all' : 'Deselect all';
            updateImportCount();
        });

        elements.importList.addEventListener('change', updateImportCount);

        elements.importResults.style.display = 'block';
        elements.importSubmit.style.display = '';
        updateImportCount();
        elements.importSubmit.disabled = total === 0;

        elements.importPreviewBtn.disabled = false;
        elements.importLoading.style.display = 'none';
    } catch (error) {
        elements.importLoading.style.display = 'none';
        elements.importPreviewBtn.disabled = false;
        showToast(error.message, 'error');
    }
}

function updateImportCount() {
    const checked = elements.importList.querySelectorAll('.import-checkbox:checked').length;
    const total = elements.importList.querySelectorAll('.import-checkbox').length;
    const counter = document.getElementById('import-selected-count');
    if (counter) counter.textContent = `${checked} de ${total} seleccionados`;
    elements.importSubmit.innerHTML = `<i class="ph ph-download-simple"></i> Importar Seleccionados (${checked})`;
    elements.importSubmit.disabled = checked === 0;
}

async function confirmImport() {
    if (!_importPreviewData?.videos?.length) return;

    const checkedBoxes = elements.importList.querySelectorAll('.import-checkbox:checked');
    const selected = Array.from(checkedBoxes).map(cb => _importPreviewData.videos[parseInt(cb.dataset.idx)]);
    if (!selected.length) return showToast('Selecciona al menos un video', 'error');

    elements.importSubmit.disabled = true;
    elements.importSubmit.innerHTML = '<i class="ph ph-spinner-gap spin"></i> Importando...';

    try {
        const response = await fetch(`${API_BASE}/videos/import/selected`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ videos: selected })
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Error al importar');
        }
        const result = await response.json();
        closeImport();
        const msg = result.skipped > 0
            ? `${result.imported} importados, ${result.skipped} omitidos (ya existían)`
            : `${result.imported} videos importados`;
        showToast(msg, 'success');
    } catch (error) {
        elements.importSubmit.disabled = false;
        elements.importSubmit.innerHTML = '<i class="ph ph-download-simple"></i> Importar Seleccionados';
        showToast(error.message, 'error');
    }
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

// --- GUÍAS DE ESTUDIO ---

async function loadGuias() {
    try {
        elements.guiasGrid = document.getElementById('guias-grid');
        elements.guiasGrid.innerHTML = `
            <div class="loading-state">
                <i class="ph ph-spinner-gap spin"></i>
                <p>Cargando guías...</p>
            </div>
        `;
        const response = await fetch(`${API_BASE}/guide`);
        if (!response.ok) throw new Error('Error al cargar guías');
        const result = await response.json();
        state.guias = result.data || result;
        renderGuias();
    } catch (error) {
        elements.guiasGrid.innerHTML = `
            <div class="empty-state">
                <i class="ph ph-warning-circle"></i>
                <p>Error al cargar guías</p>
            </div>
        `;
        showToast('Error al cargar guías', 'error');
    }
}

function renderGuias() {
    const countEl = document.getElementById('guias-count');
    if (countEl) countEl.textContent = state.guias.length;

    if (state.guias.length === 0) {
        elements.guiasGrid.innerHTML = `
            <div class="empty-state">
                <i class="ph ph-book-open-text"></i>
                <p>No hay guías de estudio</p>
                <p>Agrega tu primera guía con el botón de arriba</p>
            </div>
        `;
        return;
    }

    elements.guiasGrid.innerHTML = state.guias.map((guia, index) => `
        <div class="card guia-card" style="--index: ${index}" onclick="openGuideViewer(${guia.id})">
            <div class="card-body">
                <div class="guia-card-header">
                    <h3 class="card-title">${guia.title}</h3>
                    ${guia.author ? `<p class="card-subtitle"><i class="ph ph-user"></i> ${guia.author}</p>` : ''}
                </div>
                <div class="card-tags">
                    ${(guia.tag_list || []).map(t => `<span class="tag tag-purple">${t}</span>`).join('')}
                    ${!guia.tag_list?.length && guia.tags ? guia.tags.split(',').map(t => `<span class="tag tag-purple">${t.trim()}</span>`).join('') : ''}
                    <span class="tag tag-yellow">${formatDate(guia.created_at)}</span>
                </div>
            </div>
            <div class="card-actions" onclick="event.stopPropagation()">
                <button class="btn-icon" onclick="openGuiaForm(${guia.id})" title="Editar">
                    <i class="ph ph-pencil-simple"></i>
                </button>
                <button class="btn-icon danger" onclick="deleteGuia(${guia.id})" title="Eliminar">
                    <i class="ph ph-trash"></i>
                </button>
            </div>
        </div>
    `).join('');

    observeCards();
}

function openGuiaForm(guiaId = null) {
    const guia = guiaId ? state.guias.find(g => g.id === guiaId) : null;
    const isEdit = !!guia;

    elements.modalTitle.textContent = isEdit ? 'Editar Guía' : 'Agregar Guía';

    elements.modalBody.innerHTML = `
        <form id="guia-form">
            <div class="form-group">
                <label class="form-label">Título</label>
                <input type="text" class="form-input" name="title" value="${guia?.title || ''}" placeholder="Guía de Estudio Bíblico" required>
            </div>
            <div class="form-group">
                <label class="form-label">Autor</label>
                <input type="text" class="form-input" name="author" value="${guia?.author || ''}" placeholder="Autor de la guía">
            </div>
            <div class="form-group">
                <label class="form-label">Contenido (Markdown)</label>
                <textarea class="form-textarea" name="content" rows="15" placeholder="Contenido completo de la guía..." required>${guia?.content || ''}</textarea>
            </div>
            <div class="form-group">
                <label class="form-label">Tags (separados por coma)</label>
                <input type="text" class="form-input" name="tags" value="${guia?.tags || ''}" placeholder="discipulado, oracion, fe (dejar vacío para auto-extraer)">
                <p class="form-hint">Si se deja vacío, los tags se extraerán automáticamente del contenido</p>
            </div>
            <div class="form-group">
                <label class="form-label">Estado</label>
                <select class="form-select" name="status">
                    <option value="published" ${guia?.status === 'published' ? 'selected' : ''}>Publicado</option>
                    <option value="draft" ${guia?.status === 'draft' ? 'selected' : ''}>Borrador</option>
                </select>
            </div>
            <div class="form-actions">
                <button type="button" class="btn-secondary" onclick="closeModal()">Cancelar</button>
                <button type="submit" class="btn-submit">${isEdit ? 'Guardar Cambios' : 'Agregar'}</button>
            </div>
        </form>
    `;

    document.getElementById('guia-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        if (isEdit) {
            updateGuia(guiaId, formData);
        } else {
            createGuia(formData);
        }
    });

    openModal();
}

async function createGuia(formData) {
    const data = {
        id: null,
        title: formData.get('title'),
        author: formData.get('author') || '',
        content: formData.get('content'),
        tags: formData.get('tags') || '',
        status: formData.get('status') || 'published'
    };

    try {
        const response = await fetch(`${API_BASE}/guide/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error('Error al crear guía');

        closeModal();
        showToast('Guía agregada exitosamente', 'success');
        refreshAfterMutate('biblia');
        loadGuias();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function updateGuia(guiaId, formData) {
    const data = {
        id: guiaId,
        title: formData.get('title'),
        author: formData.get('author') || '',
        content: formData.get('content'),
        tags: formData.get('tags') || '',
        status: formData.get('status') || 'published'
    };

    try {
        const response = await fetch(`${API_BASE}/guide/${guiaId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error('Error al actualizar guía');

        closeModal();
        showToast('Guía actualizada exitosamente', 'success');
        refreshAfterMutate('biblia');
        loadGuias();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function deleteGuia(guiaId) {
    if (!confirm('¿Estás seguro de eliminar esta guía?')) return;

    try {
        const response = await fetch(`${API_BASE}/guide/${guiaId}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Error al eliminar guía');

        showToast('Guía eliminada', 'success');
        refreshAfterMutate('biblia');
        loadGuias();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

document.addEventListener('DOMContentLoaded', init);
