# Autenticación

La API es pública para lectura, autenticación requerida para escritura

## Endpoints Públicos (GET)

Todos los endpoints `GET` son públicos y no requieren autenticación.

::: info
Los endpoints de lectura están disponibles para cualquier cliente sin necesidad de API keys.
:::

## Endpoints de Escritura (POST, PUT, DELETE)

Actualmente los endpoints de escritura están abiertos para desarrollo. En producción se recomienda implementar autenticación.

::: warning Importante
Para despliegue en producción, implementa autenticación mediante API Key o JWT.
:::
