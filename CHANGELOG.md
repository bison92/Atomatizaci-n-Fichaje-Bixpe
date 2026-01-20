# Historial de Cambios

Todos los cambios notables de este proyecto se documentarán en este archivo.

## [1.1.0] - 2026-01-21

### Añadido
- **Modo Simulación** (flag `--simulate`): Permite probar el flujo completo sin fichar realmente. El script hace clic en "Cancelar" en los diálogos de confirmación en lugar de "Confirmar".
- **Checklist de Diagnóstico Pre-Clic**: Registra información detallada sobre el estado del botón antes de hacer clic (tipo de etiqueta, visibilidad, dimensiones, detección de overlay).
- **Sondeo del DOM en Fallo**: Cuando no se encuentra un botón, el script lista todos los botones visibles para ayudar a diagnosticar problemas con selectores.

### Cambiado
- **Selectores de Login**: Actualizados para usar IDs precisos (`#emailLogin`, `#passwordLogin`) basados en la documentación de Bixpe.
- **Selectores de Botones de Acción**: Actualizados para usar IDs precisos:
  - INICIO: `#btn-start-workday`
  - PAUSA: `#btn-lunch-pause`
  - REANUDAR: `#btn-resume-workday`
  - FIN: `#btn-stop-workday`
- **Manejo de Diálogo de Confirmación**: Ahora usa selectores específicos de SweetAlert2 (`button.swal2-confirm`, `button.swal2-cancel`).
- **Estrategia de Clic**: Implementado enfoque robusto de 3 capas:
  1. Esperar a que desaparezca el overlay `#processing-text`
  2. Inyección de clic por JavaScript (evita problemas de overlay/tooltip)
  3. Clic forzado de Playwright como respaldo

### Corregido
- **Error "Event Loop Closed"**: Resuelto cambiando del gestor de contexto a gestión manual del ciclo de vida de Playwright.
- **Errores de Sintaxis JavaScript**: Corregidos comentarios estilo Python (`#`) en JS embebido y envuelto código en IIFE para sentencias `return` válidas.
- **Errores de Indentación**: Corregida estructura de bloques `try/finally`.

### GitHub Actions
- Actualizados todos los workflows para usar Python 3.11 (más estable con Playwright)
- Añadido `playwright install-deps chromium` para dependencias correctas del navegador
- Mejorado logging con marcas de tiempo
- Añadida subida de artefactos de depuración en fallo (volcados HTML + capturas)
- Nombres de artefactos únicos por ejecución para evitar sobrescritura

## [1.0.0] - 2026-01-18

### Añadido
- Implementación inicial del script de automatización de Bixpe
- Workflows de GitHub Actions para entrada, inicio-pausa, fin-pausa, salida
- Funcionalidad de comprobación de festivos
- Configuración de horarios vía `schedule.json`
- Simulación de geolocalización para requisitos de Bixpe
