const API_BASE_URL = window.location.origin;

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initTabs();
    initCopyButtons();
    initHighlighting();
    initScrollSpy();
    updateApiUrls();
    initDownloadSkill();
});

function updateApiUrls() {
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        let code = block.textContent;
        code = code.replace(/https:\/\/api\.tu-dominio\.com/g, API_BASE_URL);
        block.textContent = code;
    });
    
    const baseUrlDisplay = document.querySelector('.base-url-display');
    if (baseUrlDisplay) {
        baseUrlDisplay.textContent = API_BASE_URL;
    }
    
    const copyBaseUrlBtn = document.getElementById('copy-base-url-btn');
    if (copyBaseUrlBtn) {
        copyBaseUrlBtn.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(API_BASE_URL);
                copyBaseUrlBtn.classList.add('copied');
                copyBaseUrlBtn.innerHTML = '<i class="ph ph-check"></i>';
                setTimeout(() => {
                    copyBaseUrlBtn.classList.remove('copied');
                    copyBaseUrlBtn.innerHTML = '<i class="ph ph-copy"></i>';
                }, 2000);
            } catch (err) {
                console.error('Error al copiar:', err);
            }
        });
    }
    
    updateEnvironmentIndicator();
}

function updateEnvironmentIndicator() {
    const envBadge = document.getElementById('env-badge');
    const envDescription = document.getElementById('env-description');
    
    if (!envBadge || !envDescription) return;
    
    const hostname = window.location.hostname;
    const isLocal = hostname === 'localhost' || hostname === '127.0.0.1' || hostname.includes('local');
    const isProduction = hostname === 'api-biblia-py.onrender.com';
    
    if (isProduction) {
        envBadge.className = 'env-badge production';
        envBadge.innerHTML = '<i class="ph ph-check-circle"></i> Producción';
        envDescription.textContent = 'Entorno de producción en Render';
    } else if (isLocal) {
        envBadge.className = 'env-badge local';
        envBadge.innerHTML = '<i class="ph ph-code"></i> Desarrollo Local';
        envDescription.textContent = 'Entorno de desarrollo local';
    } else {
        envBadge.className = 'env-badge staging';
        envBadge.innerHTML = '<i class="ph ph-flask"></i> Staging';
        envDescription.textContent = 'Entorno de pruebas';
    }
}

function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.doc-section');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            
            sections.forEach(section => {
                section.classList.remove('active');
            });
            
            navLinks.forEach(l => l.classList.remove('active'));
            
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.classList.add('active');
                link.classList.add('active');
                
                window.scrollTo({ top: 0, behavior: 'smooth' });
                
                history.pushState(null, null, `#${targetId}`);
            }
        });
    });
    
    const hash = window.location.hash.substring(1);
    if (hash) {
        const targetLink = document.querySelector(`a[href="#${hash}"]`);
        if (targetLink) {
            targetLink.click();
        }
    }
}

function initTabs() {
    const tabGroups = document.querySelectorAll('.tabs');
    
    tabGroups.forEach(tabGroup => {
        const tabs = tabGroup.querySelectorAll('.tab-btn');
        const contentParent = tabGroup.parentElement;
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetTab = tab.dataset.tab;
                
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                const allContents = contentParent.querySelectorAll('.tab-content');
                allContents.forEach(content => {
                    content.classList.remove('active');
                });
                
                const targetContent = document.getElementById(targetTab);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
            });
        });
    });
}

function initCopyButtons() {
    const copyButtons = document.querySelectorAll('.copy-btn');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const codeBlock = button.closest('.code-block');
            const codeElement = codeBlock.querySelector('code');
            const code = codeElement.textContent;
            
            try {
                await navigator.clipboard.writeText(code);
                
                button.classList.add('copied');
                button.innerHTML = '<i class="ph ph-check"></i>';
                
                setTimeout(() => {
                    button.classList.remove('copied');
                    button.innerHTML = '<i class="ph ph-copy"></i>';
                }, 2000);
            } catch (err) {
                console.error('Error al copiar:', err);
            }
        });
    });
}

function initHighlighting() {
    if (typeof hljs !== 'undefined') {
        hljs.highlightAll();
    }
}

function initScrollSpy() {
    const sections = document.querySelectorAll('.doc-section');
    const navLinks = document.querySelectorAll('.nav-link');
    
    const observerOptions = {
        root: null,
        rootMargin: '-20% 0px -80% 0px',
        threshold: 0
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.id;
                
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${id}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }, observerOptions);
    
    sections.forEach(section => {
        observer.observe(section);
    });
}

function initDownloadSkill() {
    const downloadBtn = document.getElementById('download-skill-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            const link = document.createElement('a');
            link.href = '/download/skill';
            link.download = 'ghostroot-bible-api-skill.md';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            showToast('Skill descargado exitosamente', 'success');
        });
    }
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
