# Agregar Radio

Registra una nueva estación de radio

<div class="endpoint-badge">
  <span class="method post">POST</span>
  <code class="endpoint-path">/stream/add</code>
</div>

## Request Body

```json
{
  "nombre": "Radio Aleluya",
  "url_stream": "http://servidor.com:8000/stream",
  "pais": "Costa Rica",
  "genero": "Cristiana",
  "logo_url": "https://ejemplo.com/logo.png",
  "status": "online"
}
```

| Campo | Tipo | Requerido | Default |
|-------|------|-----------|---------|
| `nombre` | string | Sí | - |
| `url_stream` | string | Sí | - |
| `pais` | string | No | "Costa Rica" |
| `genero` | string | No | "Cristiana" |
| `logo_url` | string | No | null |
| `status` | string | No | "online" |

## Respuesta

```json
{
  "status": "success",
  "id": 6,
  "mensaje": "Radio agregada"
}
```

## Ejemplo

```javascript
const addRadio = async (radioData) => {
  const response = await fetch('https://api.tu-dominio.com/stream/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(radioData)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al agregar radio');
  }

  return await response.json();
};

// Uso
const result = await addRadio({
  nombre: 'Radio Aleluya',
  url_stream: 'http://servidor.com:8000/stream',
  pais: 'Costa Rica',
  genero: 'Cristiana'
});

console.log(`Radio agregada con ID: ${result.id}`);
```
