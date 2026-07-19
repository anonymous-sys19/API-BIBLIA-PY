import { defineConfig } from 'vitepress'

export default defineConfig({
  lang: 'es',
  title: 'GhostRoot Bible API',
  description: 'Documentación oficial de la API REST para gestión y exploración de las Sagradas Escrituras',
  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/img/icon.svg' }],
    ['link', { rel: 'icon', type: 'image/jpeg', href: '/img/icon.jpg' }],
    ['link', { rel: 'apple-touch-icon', href: '/img/icon.jpg' }],
    ['link', { rel: 'stylesheet', href: 'https://unpkg.com/@phosphor-icons/web' }],
    ['script', { defer: true }, `
(function(){
  function replaceBaseUrl(){
    var baseUrl = location.origin;
    var root = document.querySelector('.vp-doc') || document.body;
    if (!root) return;
    var iter = document.createNodeIterator(root, NodeFilter.SHOW_TEXT, null, false);
    var n;
    while (n = iter.nextNode()) {
      if (n.nodeValue.indexOf('BASE_URL') !== -1) {
        n.nodeValue = n.nodeValue.replace(/BASE_URL/g, baseUrl);
      }
    }
    var local = baseUrl.indexOf('localhost') !== -1 || baseUrl.indexOf('127.0.0.1') !== -1;
    document.querySelectorAll('.env-badge').forEach(function(el){
      el.textContent = local ? 'Local' : 'Producci\u00f3n';
      el.className = 'env-badge ' + (local ? 'local' : 'production');
    });
    document.querySelectorAll('.env-description').forEach(function(el){
      el.textContent = local ? 'Entorno de desarrollo local' : 'Entorno de producci\u00f3n';
    });
    document.querySelectorAll('.base-url-display').forEach(function(el){
      el.textContent = baseUrl;
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function(){ setTimeout(replaceBaseUrl, 100); });
  } else {
    setTimeout(replaceBaseUrl, 100);
  }

  var docEl = document.querySelector('.vp-doc');
  if (docEl) {
    var obs = new MutationObserver(function(){ replaceBaseUrl(); });
    obs.observe(docEl, { childList: true, subtree: false });
  }
})();
`],
  ],

  themeConfig: {
    logo: '/img/icon.svg',
    siteTitle: 'GhostRoot Bible API',
    nav: [
      { text: 'Inicio', link: '/' },
      { text: 'Biblia', link: '/bible/daily-verse' },
      { text: 'Streaming', link: '/streaming/list-radios' },
      { text: 'Videos', link: '/videos/list-videos' },
      { text: 'Guías', link: '/guides/list-guias' },
      { text: 'Versiones', link: '/versions' },
    ],
    sidebar: [
      {
        text: 'Inicio',
        items: [
          { text: 'Introducción', link: '/' },
          { text: 'Autenticación', link: '/authentication' },
          { text: 'Rate Limiting', link: '/rate-limiting' },
          { text: 'Errores', link: '/errors' },
        ],
      },
      {
        text: 'Biblia',
        items: [
          { text: 'Versículo Diario', link: '/bible/daily-verse' },
          { text: 'Versículo Aleatorio', link: '/bible/random-verse' },
          { text: 'Lista de Testamentos', link: '/bible/list-testaments' },
          { text: 'Lista de Libros', link: '/bible/list-books' },
          { text: 'Libro por ID', link: '/bible/book-by-id' },
          { text: 'Cantidad de Capítulos', link: '/bible/chapter-count' },
          { text: 'Cantidad de Versículos', link: '/bible/verse-count' },
          { text: 'Obtener Capítulo', link: '/bible/get-chapter' },
          { text: 'Obtener Versículo', link: '/bible/get-verse' },
          { text: 'Buscar', link: '/bible/search' },
        ],
      },
      {
        text: 'Streaming',
        items: [
          { text: 'Lista de Radios', link: '/streaming/list-radios' },
          { text: 'Agregar Radio', link: '/streaming/add-radio' },
          { text: 'Actualizar Radio', link: '/streaming/update-radio' },
          { text: 'Eliminar Radio', link: '/streaming/delete-radio' },
        ],
      },
      {
        text: 'Videos',
        items: [
          { text: 'Lista de Videos', link: '/videos/list-videos' },
          { text: 'Agregar Video', link: '/videos/add-video' },
          { text: 'Actualizar Video', link: '/videos/update-video' },
          { text: 'Eliminar Video', link: '/videos/delete-video' },
        ],
      },
      {
        text: 'Guías de Estudio',
        items: [
          { text: 'Lista de Guías', link: '/guides/list-guias' },
          { text: 'Obtener Guía', link: '/guides/get-guia' },
          { text: 'Versículos de Guía', link: '/guides/guia-verses' },
          { text: 'Agregar Guía', link: '/guides/add-guia' },
          { text: 'Actualizar Guía', link: '/guides/update-guia' },
          { text: 'Eliminar Guía', link: '/guides/delete-guia' },
        ],
      },
      {
        text: 'Versiones',
        items: [
          { text: 'Versiones Disponibles', link: '/versions' },
        ],
      },
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/anomalyco/API-BIBLIA-PY' },
    ],
    footer: {
      message: 'Documentación de GhostRoot Bible API',
      copyright: '© 2026 GhostRoot Bible API',
    },
    search: {
      provider: 'local',
    },
  },
})
