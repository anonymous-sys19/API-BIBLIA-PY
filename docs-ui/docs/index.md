# Introducción

API REST para gestión y exploración de las Sagradas Escrituras

## Base URL

<div class="environment-indicator">
  <span class="env-badge" id="env-badge">Detectando...</span>
  <span class="env-description" id="env-description"></span>
</div>

```
BASE_URL
```

La URL se detecta automáticamente según tu entorno. Todos los ejemplos de código usan esta URL base.

## Descripción

GhostRoot Bible API es una solución de alto rendimiento para la gestión, exploración y estudio de las Sagradas Escrituras. Proporciona acceso a múltiples versiones bíblicas, búsqueda inteligente insensible a tildes, y gestión de contenido multimedia cristiano (radio streaming y videos).

<div class="features-grid">
  <div class="feature-card">
    <i class="ph ph-book-open-text"></i>
    <h3>8 Versiones Bíblicas</h3>
    <p>RVR1960, NVI, NTV, PDT, BAD, BLSEE, RVC, RVG</p>
  </div>
  <div class="feature-card">
    <i class="ph ph-magnifying-glass"></i>
    <h3>Búsqueda Inteligente</h3>
    <p>Búsqueda insensible a tildes y mayúsculas</p>
  </div>
  <div class="feature-card">
    <i class="ph ph-radio"></i>
    <h3>Radio Streaming</h3>
    <p>Gestión de estaciones de radio cristianas</p>
  </div>
  <div class="feature-card">
    <i class="ph ph-video-camera"></i>
    <h3>Videos YouTube</h3>
    <p>Registro automático desde URLs de YouTube</p>
  </div>
</div>

<div class="skill-download-card">
  <div class="skill-info">
    <i class="ph ph-robot"></i>
    <div>
      <h3>Skill para IA / MCP</h3>
      <p>Descarga el archivo SKILL.md para integrar esta API con asistentes de IA como Claude, ChatGPT, u otros modelos compatibles con MCP.</p>
    </div>
  </div>
  <button class="btn-download" id="download-skill-btn">
    <i class="ph ph-download-simple"></i>
    Descargar SKILL.md
  </button>
</div>

## Respuesta Estándar

Todos los endpoints retornan JSON con `Content-Type: application/json`.

```json
{
  "status": "success",
  "data": { ... },
  "message": "Operación exitosa"
}
```

## Brand Assets

Iconos oficiales de GhostRoot Bible API disponibles para uso público en tus aplicaciones.

<div class="brand-assets-grid">
  <div class="brand-asset-card">
    <div class="brand-asset-preview">
      <img src="/img/icon.svg" alt="Icono SVG">
    </div>
    <div class="brand-asset-info">
      <h3>SVG</h3>
      <p class="brand-asset-format">image/svg+xml</p>
      <p class="brand-asset-use">Escalable, ideal para web y apps</p>
      <code class="brand-asset-url">/img/icon.svg</code>
    </div>
  </div>
  <div class="brand-asset-card">
    <div class="brand-asset-preview">
      <img src="/img/icon.jpg" alt="Icono JPG">
    </div>
    <div class="brand-asset-info">
      <h3>JPG</h3>
      <p class="brand-asset-format">image/jpeg</p>
      <p class="brand-asset-use">Compatible universal, ideal para previews</p>
      <code class="brand-asset-url">/img/icon.jpg</code>
    </div>
  </div>
</div>

::: info Uso libre
Estos iconos son de uso público. Puedes usarlos para enlazar a esta API, en tu documentación, o para representar tu integración con GhostRoot Bible API.
:::
