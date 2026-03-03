# Security Policy

## Supported Versions

Se da soporte de seguridad activo a:

- Rama `main`
- Ultima release publicada

Versiones antiguas o forks no tienen garantia de parches.

## Reporting a Vulnerability

No abras vulnerabilidades en issues publicos.

Reporta por canal privado incluyendo:

- Descripcion tecnica
- Pasos para reproducir
- Impacto esperado
- Version/commit afectado
- Evidencia (logs, payloads, capturas)

Compromiso objetivo de respuesta inicial: 72 horas.

## Buenas practicas para deploy local

- No subir `.env` al repositorio.
- Rotar claves si se filtraron.
- Ejecutar con privilegios minimos.
- Limitar el acceso de red del host cuando sea posible.
