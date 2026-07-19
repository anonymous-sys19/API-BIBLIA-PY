# Versículo Aleatorio

Retorna un versículo completamente aleatorio (cambia en cada llamado)

<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/random</code>
</div>

## Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `version` | string | No | Versión bíblica (default: rvr1960) |

## Respuesta

```json
{
  "id": 27845,
  "book_id": 44,
  "book_name": "Hechos",
  "chapter": 26,
  "verse": 21,
  "text": "Por causa de esto los judíos, prendiéndome en el templo, intentaron matarme.",
  "version": "rvr1960"
}
```

::: info
A diferencia de `/daily`, este endpoint no usa semilla diaria — cada llamado retorna un versículo diferente.
:::

## Ejemplos de Consumo

::: code-group

```bash [cURL]
curl BASE_URL/random

# Con versión específica
curl BASE_URL/random?version=nvi
```

```javascript [JavaScript]
async function getRandomVerse(version = 'rvr1960') {
  const response = await fetch(`BASE_URL/random?version=${version}`);
  if (!response.ok) throw new Error(`Error: ${response.status}`);
  return response.json();
}
```

```python [Python]
import requests

def get_random_verse(version='rvr1960'):
    response = requests.get(f'BASE_URL/random', params={'version': version})
    response.raise_for_status()
    return response.json()
```

:::
