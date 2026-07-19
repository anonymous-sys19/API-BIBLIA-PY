# Lista de Testamentos

Retorna todos los testamentos disponibles

<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/list/testaments</code>
</div>

## Respuesta

```json
[
  {
    "id": 1,
    "name": "Old Testament"
  },
  {
    "id": 2,
    "name": "New Testament"
  },
  {
    "id": 3,
    "name": "Apocrypha"
  }
]
```

## Ejemplo de Consumo

```javascript
const getTestaments = async () => {
  const response = await fetch('https://api.tu-dominio.com/list/testaments');
  const testaments = await response.json();

  testaments.forEach(t => {
    console.log(`${t.id}: ${t.name}`);
  });

  return testaments;
};
```
